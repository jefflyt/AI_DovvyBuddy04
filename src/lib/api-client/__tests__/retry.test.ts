/**
 * Retry Logic Tests
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { withRetry } from '../retry';
import { ApiClientError } from '../error-handler';

describe('withRetry', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  it('should return result on first success', async () => {
    const fn = vi.fn().mockResolvedValue('success');

    const promise = withRetry(fn, {
      maxAttempts: 3,
      baseDelay: 1000,
    });

    await vi.runAllTimersAsync();
    const result = await promise;

    expect(result).toBe('success');
    expect(fn).toHaveBeenCalledTimes(1);

    vi.useRealTimers();
  });

  it('should retry on retryable error (5xx)', async () => {
    const fn = vi
      .fn()
      .mockRejectedValueOnce(
        new ApiClientError('LLM_SERVICE_UNAVAILABLE', 503, 'Service unavailable')
      )
      .mockRejectedValueOnce(
        new ApiClientError('LLM_SERVICE_UNAVAILABLE', 503, 'Service unavailable')
      )
      .mockResolvedValueOnce('success');

    const promise = withRetry(fn, {
      maxAttempts: 3,
      baseDelay: 1000,
    });

    await vi.runAllTimersAsync();
    const result = await promise;

    expect(result).toBe('success');
    expect(fn).toHaveBeenCalledTimes(3);

    vi.useRealTimers();
  });

  it('should not retry on non-retryable error (4xx)', async () => {
    const fn = vi.fn().mockRejectedValue(
      new ApiClientError('VALIDATION_ERROR', 400, 'Bad request')
    );

    const promise = withRetry(fn, {
      maxAttempts: 3,
      baseDelay: 1000,
    });

    await vi.runAllTimersAsync();

    await expect(promise).rejects.toThrow(ApiClientError);
    expect(fn).toHaveBeenCalledTimes(1);

    vi.useRealTimers();
  });

  it('should use exponential backoff', async () => {
    const fn = vi
      .fn()
      .mockRejectedValueOnce(
        new ApiClientError('INTERNAL_ERROR', 500, 'Server error')
      )
      .mockRejectedValueOnce(
        new ApiClientError('INTERNAL_ERROR', 500, 'Server error')
      )
      .mockResolvedValueOnce('success');

    const promise = withRetry(fn, {
      maxAttempts: 3,
      baseDelay: 1000,
    });

    // First attempt fails immediately
    await vi.advanceTimersByTimeAsync(0);
    expect(fn).toHaveBeenCalledTimes(1);

    // Second attempt after 1000ms (1000 * 2^0)
    await vi.advanceTimersByTimeAsync(1000);
    expect(fn).toHaveBeenCalledTimes(2);

    // Third attempt after 2000ms (1000 * 2^1)
    await vi.advanceTimersByTimeAsync(2000);
    expect(fn).toHaveBeenCalledTimes(3);

    const result = await promise;
    expect(result).toBe('success');

    vi.useRealTimers();
  });

  it('should respect max delay', async () => {
    const fn = vi
      .fn()
      .mockRejectedValueOnce(
        new ApiClientError('INTERNAL_ERROR', 500, 'Server error')
      )
      .mockRejectedValueOnce(
        new ApiClientError('INTERNAL_ERROR', 500, 'Server error')
      )
      .mockResolvedValueOnce('success');

    const promise = withRetry(fn, {
      maxAttempts: 3,
      baseDelay: 10000, // Very high base delay
      maxDelay: 2000, // But capped at 2000ms
    });

    // First retry should be capped at maxDelay
    await vi.advanceTimersByTimeAsync(2000);
    expect(fn).toHaveBeenCalledTimes(2);

    await vi.runAllTimersAsync();
    const result = await promise;
    expect(result).toBe('success');

    vi.useRealTimers();
  });

  it('should throw last error after all retries fail', async () => {
    const lastError = new ApiClientError(
      'INTERNAL_ERROR',
      500,
      'Persistent error'
    );

    const fn = vi.fn().mockRejectedValue(lastError);

    const promise = withRetry(fn, {
      maxAttempts: 3,
      baseDelay: 1000,
    });

    await vi.runAllTimersAsync();

    await expect(promise).rejects.toThrow(lastError);
    expect(fn).toHaveBeenCalledTimes(3);

    vi.useRealTimers();
  });

  it('should respect abort signal', async () => {
    const controller = new AbortController();
    const fn = vi.fn().mockRejectedValue(
      new ApiClientError('INTERNAL_ERROR', 500, 'Server error')
    );

    const promise = withRetry(fn, {
      maxAttempts: 3,
      baseDelay: 1000,
      signal: controller.signal,
    });

    // Start first attempt
    await vi.advanceTimersByTimeAsync(0);
    expect(fn).toHaveBeenCalledTimes(1);

    // Abort after first attempt
    controller.abort();

    // Try to continue
    await vi.runAllTimersAsync();

    await expect(promise).rejects.toThrow('Request cancelled');
    expect(fn).toHaveBeenCalledTimes(1); // Should not retry after abort

    vi.useRealTimers();
  });

  it('should retry on network errors', async () => {
    const fn = vi
      .fn()
      .mockRejectedValueOnce(new TypeError('Failed to fetch'))
      .mockResolvedValueOnce('success');

    const promise = withRetry(fn, {
      maxAttempts: 3,
      baseDelay: 1000,
    });

    await vi.runAllTimersAsync();
    const result = await promise;

    expect(result).toBe('success');
    expect(fn).toHaveBeenCalledTimes(2);

    vi.useRealTimers();
  });
});
