/**
 * API Client
 * HTTP client wrapper for backend API communication
 */

import { API_CONFIG, API_ENDPOINTS } from './config';
import {
  ChatRequest,
  ChatResponse,
  SessionResponse,
  LeadRequest,
  LeadResponse,
  RequestOptions,
} from './types';
import {
  parseApiError,
  createNetworkError,
  createTimeoutError,
} from './error-handler';
import { withRetry } from './retry';

/**
 * API Client class
 * Provides methods for all backend API endpoints
 */
export class ApiClient {
  private baseURL: string;
  private timeout: number;
  private retryAttempts: number;
  private retryDelay: number;
  private credentials: RequestCredentials;

  constructor(config = API_CONFIG) {
    this.baseURL = config.baseURL;
    this.timeout = config.timeout;
    this.retryAttempts = config.retryAttempts;
    this.retryDelay = config.retryDelay;
    this.credentials = config.credentials;
  }

  /**
   * Make HTTP request with timeout and retry logic
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit & RequestOptions = {}
  ): Promise<T> {
    const {
      timeout = this.timeout,
      retryAttempts = this.retryAttempts,
      retryDelay = this.retryDelay,
      signal,
      ...fetchOptions
    } = options;

    // Create abort controller for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    // Combine signals if provided
    const abortSignal = signal
      ? this.combineSignals([signal, controller.signal])
      : controller.signal;

    try {
      // Wrap fetch in retry logic
      const response = await withRetry(
        async () => {
          try {
            const url = `${this.baseURL}${endpoint}`;
            const response = await fetch(url, {
              ...fetchOptions,
              credentials: this.credentials,
              signal: abortSignal,
              headers: {
                'Content-Type': 'application/json',
                ...fetchOptions.headers,
              },
            });

            // Check for HTTP errors
            if (!response.ok) {
              throw await parseApiError(response);
            }

            return response;
          } catch (error) {
            // Handle network errors
            if (error instanceof TypeError && error.message.includes('fetch')) {
              throw createNetworkError(error);
            }
            throw error;
          }
        },
        {
          maxAttempts: retryAttempts,
          baseDelay: retryDelay,
          signal: abortSignal,
        }
      );

      // Parse response
      const data = await response.json();
      return data as T;
    } catch (error) {
      // Handle timeout
      if (error instanceof Error && error.name === 'AbortError') {
        throw createTimeoutError();
      }
      throw error;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * Combine multiple abort signals
   */
  private combineSignals(signals: AbortSignal[]): AbortSignal {
    const controller = new AbortController();

    for (const signal of signals) {
      if (signal.aborted) {
        controller.abort();
        break;
      }
      signal.addEventListener('abort', () => controller.abort());
    }

    return controller.signal;
  }

  /**
   * Send chat message
   * 
   * @param request Chat request
   * @param options Request options
   * @returns Chat response with session ID and message
   */
  async chat(
    request: ChatRequest,
    options?: RequestOptions
  ): Promise<ChatResponse> {
    return this.request<ChatResponse>(API_ENDPOINTS.chat, {
      method: 'POST',
      body: JSON.stringify(request),
      ...options,
    });
  }

  /**
   * Get session information
   * 
   * @param sessionId Session ID
   * @param options Request options
   * @returns Session information
   */
  async getSession(
    sessionId: string,
    options?: RequestOptions
  ): Promise<SessionResponse> {
    return this.request<SessionResponse>(
      API_ENDPOINTS.session(sessionId),
      {
        method: 'GET',
        ...options,
      }
    );
  }

  /**
   * Create lead (contact form submission)
   * 
   * @param request Lead request
   * @param options Request options
   * @returns Lead response
   */
  async createLead(
    request: LeadRequest,
    options?: RequestOptions
  ): Promise<LeadResponse> {
    return this.request<LeadResponse>(API_ENDPOINTS.lead, {
      method: 'POST',
      body: JSON.stringify(request),
      ...options,
    });
  }
}

/**
 * Default API client instance
 */
export const apiClient = new ApiClient();
