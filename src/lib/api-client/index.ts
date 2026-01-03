/**
 * API Client
 * Export all API client modules
 */

export { ApiClient, apiClient } from './client';
export { API_CONFIG, API_ENDPOINTS } from './config';
export type { ApiClientConfig } from './config';
export {
  ApiClientError,
  parseApiError,
  createNetworkError,
  createTimeoutError,
} from './error-handler';
export { withRetry } from './retry';
export type { RetryOptions } from './retry';
export type {
  ChatRequest,
  ChatResponse,
  ChatMetadata,
  SessionResponse,
  LeadRequest,
  LeadResponse,
  ApiError,
  ApiErrorCode,
  ValidationDetail,
  RequestOptions,
} from './types';
