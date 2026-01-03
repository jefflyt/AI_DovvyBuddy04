/**
 * Error Handler Tests
 */

import { describe, it, expect } from 'vitest';
import {
  ApiClientError,
  parseApiError,
  createNetworkError,
  createTimeoutError,
} from '../error-handler';

describe('ApiClientError', () => {
  it('should create error with user-friendly message', () => {
    const error = new ApiClientError(
      'VALIDATION_ERROR',
      400,
      'Message is required'
    );

    expect(error.code).toBe('VALIDATION_ERROR');
    expect(error.statusCode).toBe(400);
    expect(error.message).toBe('Message is required');
    expect(error.userMessage).toBe('Please check your input and try again.');
  });

  it('should identify validation errors', () => {
    const error = new ApiClientError(
      'VALIDATION_ERROR',
      400,
      'Invalid input'
    );

    expect(error.isValidationError()).toBe(true);
  });

  it('should identify retryable errors (5xx)', () => {
    const error503 = new ApiClientError(
      'LLM_SERVICE_UNAVAILABLE',
      503,
      'Service unavailable'
    );

    const error500 = new ApiClientError(
      'INTERNAL_ERROR',
      500,
      'Internal server error'
    );

    const error400 = new ApiClientError(
      'VALIDATION_ERROR',
      400,
      'Bad request'
    );

    expect(error503.isRetryable()).toBe(true);
    expect(error500.isRetryable()).toBe(true);
    expect(error400.isRetryable()).toBe(false);
  });

  it('should not retry timeout errors', () => {
    const error = new ApiClientError(
      'TIMEOUT',
      408,
      'Request timeout'
    );

    expect(error.isRetryable()).toBe(false);
  });

  it('should extract validation details', () => {
    const details = [
      { field: 'email', message: 'Invalid email format' },
      { field: 'message', message: 'Message is required' },
    ];

    const error = new ApiClientError(
      'VALIDATION_ERROR',
      400,
      'Validation failed',
      details
    );

    const validationDetails = error.getValidationDetails();
    expect(validationDetails).toEqual(details);
  });

  it('should return null for non-validation errors', () => {
    const error = new ApiClientError(
      'INTERNAL_ERROR',
      500,
      'Internal server error'
    );

    expect(error.getValidationDetails()).toBeNull();
  });
});

describe('parseApiError', () => {
  it('should parse API error response', async () => {
    const response = new Response(
      JSON.stringify({
        error: 'Invalid request',
        code: 'VALIDATION_ERROR',
        details: [{ field: 'message', message: 'Required' }],
      }),
      { status: 400 }
    );

    const error = await parseApiError(response);

    expect(error).toBeInstanceOf(ApiClientError);
    expect(error.code).toBe('VALIDATION_ERROR');
    expect(error.statusCode).toBe(400);
    expect(error.message).toBe('Invalid request');
  });

  it('should handle invalid JSON response', async () => {
    const response = new Response('Not JSON', { status: 500 });

    const error = await parseApiError(response);

    expect(error).toBeInstanceOf(ApiClientError);
    expect(error.code).toBe('UNKNOWN_ERROR');
    expect(error.statusCode).toBe(500);
  });

  it('should handle missing error code', async () => {
    const response = new Response(
      JSON.stringify({ error: 'Something went wrong' }),
      { status: 500 }
    );

    const error = await parseApiError(response);

    expect(error.code).toBe('UNKNOWN_ERROR');
  });
});

describe('createNetworkError', () => {
  it('should create network error', () => {
    const originalError = new TypeError('Failed to fetch');
    const error = createNetworkError(originalError);

    expect(error).toBeInstanceOf(ApiClientError);
    expect(error.code).toBe('NETWORK_ERROR');
    expect(error.statusCode).toBe(0);
    expect(error.userMessage).toContain('internet connection');
  });
});

describe('createTimeoutError', () => {
  it('should create timeout error', () => {
    const error = createTimeoutError();

    expect(error).toBeInstanceOf(ApiClientError);
    expect(error.code).toBe('TIMEOUT');
    expect(error.statusCode).toBe(408);
    expect(error.userMessage).toContain('too long');
  });
});
