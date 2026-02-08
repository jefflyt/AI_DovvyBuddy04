/**
 * API Client Tests
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ApiClient } from '../client';
import { ApiClientError } from '../error-handler';
import type { ChatResponse, SessionResponse, LeadResponse } from '../types';

// Mock fetch globally
const mockFetch = vi.fn();
// eslint-disable-next-line @typescript-eslint/no-explicit-any
global.fetch = mockFetch as any;

describe('ApiClient', () => {
  let client: ApiClient;

  beforeEach(() => {
    client = new ApiClient({
      baseURL: 'http://localhost:8000',
      timeout: 5000,
      retryAttempts: 3,
      retryDelay: 100,
      credentials: 'include',
    });
    mockFetch.mockClear();
  });

  afterEach(() => {
    vi.clearAllTimers();
  });

  describe('chat', () => {
    it('should send chat message successfully', async () => {
      const mockResponse: ChatResponse = {
        sessionId: '123e4567-e89b-12d3-a456-426614174000',
        message: 'Hello! How can I help you with diving today?',
        metadata: {
          tokensUsed: 150,
          model: 'gemini-2.5-flash-lite',
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await client.chat({
        message: 'What is Open Water certification?',
      });

      expect(result).toEqual(mockResponse);
      expect(mockFetch).toHaveBeenCalledTimes(1);
      
      // Check call arguments (ignore signal)
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toBe('http://localhost:8000/api/chat');
      expect(options.method).toBe('POST');
      expect(options.credentials).toBe('include');
      expect(options.headers['Content-Type']).toBe('application/json');
      expect(options.body).toBe(JSON.stringify({
        message: 'What is Open Water certification?',
      }));
    });

    it('should include session ID in request', async () => {
      const mockResponse: ChatResponse = {
        sessionId: '123e4567-e89b-12d3-a456-426614174000',
        message: 'Sure, let me explain more...',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      await client.chat({
        sessionId: '123e4567-e89b-12d3-a456-426614174000',
        message: 'Tell me more',
      });

      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toBe('http://localhost:8000/api/chat');
      expect(options.body).toBe(JSON.stringify({
        sessionId: '123e4567-e89b-12d3-a456-426614174000',
        message: 'Tell me more',
      }));
    });

    it('should handle validation error (400)', async () => {
      // Mock for both the expect rejection and the try/catch
      mockFetch.mockResolvedValue({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => ({
          error: 'Invalid request',
          code: 'VALIDATION_ERROR',
          details: [
            { field: 'message', message: 'Message is required' },
          ],
        }),
      });

      try {
        await client.chat({ message: '' });
        expect.fail('Should have thrown error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiClientError);
        expect((error as ApiClientError).code).toBe('VALIDATION_ERROR');
        expect((error as ApiClientError).statusCode).toBe(400);
        expect((error as ApiClientError).isValidationError()).toBe(true);
      }
    });

    it('should retry on 503 error', async () => {
      vi.useFakeTimers();

      // First two attempts fail with 503
      mockFetch
        .mockResolvedValueOnce({
          ok: false,
          status: 503,
          statusText: 'Service Unavailable',
          json: async () => ({
            error: 'Service unavailable',
            code: 'LLM_SERVICE_UNAVAILABLE',
          }),
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 503,
          statusText: 'Service Unavailable',
          json: async () => ({
            error: 'Service unavailable',
            code: 'LLM_SERVICE_UNAVAILABLE',
          }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            sessionId: '123e4567-e89b-12d3-a456-426614174000',
            message: 'Success after retry',
          }),
        });

      const promise = client.chat({ message: 'Test retry' });

      // Fast-forward through retry delays
      await vi.runAllTimersAsync();

      const result = await promise;

      expect(result.message).toBe('Success after retry');
      expect(mockFetch).toHaveBeenCalledTimes(3);

      vi.useRealTimers();
    });

    it('should not retry on 400 error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          error: 'Invalid request',
          code: 'VALIDATION_ERROR',
        }),
      });

      await expect(
        client.chat({ message: '' })
      ).rejects.toThrow(ApiClientError);

      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    it('should handle network error', async () => {
      mockFetch.mockRejectedValueOnce(new TypeError('Failed to fetch'));

      try {
        await client.chat({ message: 'Test' });
        expect.fail('Should have thrown error');
      } catch (error) {
        expect(error).toBeInstanceOf(ApiClientError);
        expect((error as ApiClientError).code).toBe('NETWORK_ERROR');
      }
    });

    it.skip('should handle timeout', async () => {
      vi.useFakeTimers();

      // Mock fetch that never resolves
      mockFetch.mockImplementationOnce(
        () => new Promise(() => {})
      );

      const promise = client.chat({ message: 'Test timeout' });

      // Fast-forward past timeout
      await vi.advanceTimersByTimeAsync(6000);

      await expect(promise).rejects.toThrow(ApiClientError);

      try {
        await promise;
      } catch (error) {
        expect(error).toBeInstanceOf(ApiClientError);
        expect((error as ApiClientError).code).toBe('TIMEOUT');
      }

      vi.useRealTimers();
    });
  });

  describe('getSession', () => {
    it('should get session information', async () => {
      const mockResponse: SessionResponse = {
        sessionId: '123e4567-e89b-12d3-a456-426614174000',
        createdAt: '2026-01-03T00:00:00Z',
        lastActivity: '2026-01-03T01:00:00Z',
        messageCount: 5,
        isExpired: false,
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await client.getSession('123e4567-e89b-12d3-a456-426614174000');

      expect(result).toEqual(mockResponse);
      
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toBe('http://localhost:8000/api/session/123e4567-e89b-12d3-a456-426614174000');
      expect(options.method).toBe('GET');
    });

    it('should handle session not found (404)', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          error: 'Session not found',
          code: 'SESSION_NOT_FOUND',
        }),
      });

      await expect(
        client.getSession('invalid-session-id')
      ).rejects.toThrow(ApiClientError);
    });
  });

  describe('createLead', () => {
    it('should create lead successfully', async () => {
      const mockResponse: LeadResponse = {
        success: true,
        leadId: '123e4567-e89b-12d3-a456-426614174000',
        message: 'Thank you! We will contact you soon.',
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await client.createLead({
        sessionId: '123e4567-e89b-12d3-a456-426614174000',
        email: 'test@example.com',
        name: 'John Doe',
      });

      expect(result).toEqual(mockResponse);
      
      const [url, options] = mockFetch.mock.calls[0];
      expect(url).toBe('http://localhost:8000/api/leads');
      expect(options.method).toBe('POST');
      expect(options.body).toBe(JSON.stringify({
        sessionId: '123e4567-e89b-12d3-a456-426614174000',
        email: 'test@example.com',
        name: 'John Doe',
      }));
    });
  });
});
