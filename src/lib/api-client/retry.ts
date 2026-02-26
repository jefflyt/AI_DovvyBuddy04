/**
 * Retry Logic
 * Exponential backoff retry for transient failures
 */

import { ApiClientError } from './error-handler'

export interface RetryOptions {
  maxAttempts: number
  baseDelay: number
  maxDelay?: number
  signal?: AbortSignal
}

/**
 * Sleep for specified milliseconds
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * Calculate exponential backoff delay
 * delay = baseDelay * (2 ^ attempt)
 */
function calculateDelay(
  baseDelay: number,
  attempt: number,
  maxDelay: number = 10000
): number {
  const delay = baseDelay * Math.pow(2, attempt)
  return Math.min(delay, maxDelay)
}

/**
 * Check if error is retryable
 */
function isRetryableError(error: unknown): boolean {
  if (error instanceof ApiClientError) {
    return error.isRetryable()
  }

  // Network errors are retryable
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return true
  }

  return false
}

/**
 * Retry function with exponential backoff
 *
 * @param fn Function to retry
 * @param options Retry options
 * @returns Promise resolving to function result
 * @throws Last error if all retries fail
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions
): Promise<T> {
  const { maxAttempts, baseDelay, maxDelay, signal } = options
  let lastError: unknown

  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    // Check if request was cancelled
    if (signal?.aborted) {
      throw new Error('Request cancelled')
    }

    try {
      return await fn()
    } catch (error) {
      lastError = error

      // Don't retry on last attempt
      if (attempt === maxAttempts - 1) {
        break
      }

      // Don't retry if error is not retryable
      if (!isRetryableError(error)) {
        throw error
      }

      // Calculate delay and wait before retry
      const delay = calculateDelay(baseDelay, attempt, maxDelay)

      // Log retry attempt (only in development)
      if (process.env.NODE_ENV === 'development') {
        console.warn(
          `Retry attempt ${attempt + 1}/${maxAttempts} after ${delay}ms`,
          error instanceof Error ? error.message : error
        )
      }

      await sleep(delay)
    }
  }

  // All retries failed, throw last error
  throw lastError
}
