/**
 * API Error Handler
 * Maps API errors to user-friendly messages
 */

import { ApiError, ApiErrorCode } from './types'

/**
 * User-friendly error messages for each error code
 */
const ERROR_MESSAGES: Record<ApiErrorCode, string> = {
  VALIDATION_ERROR: 'Please check your input and try again.',
  LLM_API_ERROR:
    'Our AI service is temporarily unavailable. Please try again in a moment.',
  LLM_SERVICE_UNAVAILABLE:
    'Our AI service is temporarily unavailable. Please try again in a moment.',
  ADK_UNAVAILABLE:
    'Our AI service is temporarily unavailable. Please try again in a moment.',
  DATABASE_ERROR: 'Unable to process your request. Please try again.',
  SESSION_NOT_FOUND:
    'Your session has expired. Please start a new conversation.',
  SESSION_EXPIRED: 'Your session has expired. Please start a new conversation.',
  TIMEOUT: 'Your request took too long. Please try a simpler question.',
  NETWORK_ERROR:
    'Unable to connect to the server. Please check your internet connection.',
  INTERNAL_ERROR: 'Something went wrong. Please try again.',
  UNKNOWN_ERROR: 'An unexpected error occurred. Please try again.',
}

/**
 * API Client Error
 * Extends Error with API-specific fields
 */
export class ApiClientError extends Error {
  public readonly code: ApiErrorCode
  public readonly statusCode: number
  public readonly details?: unknown
  public readonly userMessage: string

  constructor(
    code: ApiErrorCode,
    statusCode: number,
    message: string,
    details?: unknown
  ) {
    super(message)
    this.name = 'ApiClientError'
    this.code = code
    this.statusCode = statusCode
    this.details = details
    this.userMessage = ERROR_MESSAGES[code] || ERROR_MESSAGES.UNKNOWN_ERROR
  }

  /**
   * Check if error is a validation error
   */
  isValidationError(): boolean {
    return this.code === 'VALIDATION_ERROR'
  }

  /**
   * Check if error is retryable (5xx errors)
   */
  isRetryable(): boolean {
    return (
      this.statusCode >= 500 && this.statusCode < 600 && this.code !== 'TIMEOUT'
    )
  }

  /**
   * Get validation details if available
   */
  getValidationDetails(): Array<{ field: string; message: string }> | null {
    if (!this.isValidationError() || !Array.isArray(this.details)) {
      return null
    }
    return this.details as Array<{ field: string; message: string }>
  }
}

/**
 * Parse API error response and create ApiClientError
 */
export async function parseApiError(
  response: Response
): Promise<ApiClientError> {
  let errorData: ApiError

  try {
    errorData = await response.json()
  } catch {
    // Failed to parse error response
    return new ApiClientError(
      'UNKNOWN_ERROR',
      response.status,
      `HTTP ${response.status}: ${response.statusText}`
    )
  }

  return new ApiClientError(
    errorData.code || 'UNKNOWN_ERROR',
    response.status,
    errorData.error || 'Unknown error',
    errorData.details
  )
}

/**
 * Create network error
 */
export function createNetworkError(error: Error): ApiClientError {
  return new ApiClientError(
    'NETWORK_ERROR',
    0,
    `Network error: ${error.message}`
  )
}

/**
 * Create timeout error
 */
export function createTimeoutError(): ApiClientError {
  return new ApiClientError('TIMEOUT', 408, 'Request timeout')
}
