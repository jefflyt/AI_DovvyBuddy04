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
  DB_ERROR: 'Unable to process your request. Please try again.',
  CONFIG_ERROR: 'Service is temporarily unavailable. Please try again later.',
  SESSION_NOT_FOUND:
    'Your session has expired. Please start a new conversation.',
  SESSION_EXPIRED: 'Your session has expired. Please start a new conversation.',
  TIMEOUT: 'Your request took too long. Please try a simpler question.',
  NETWORK_ERROR:
    'Unable to connect to the server. Please check your internet connection.',
  INTERNAL_ERROR: 'Something went wrong. Please try again.',
  UNKNOWN: 'An unexpected error occurred. Please try again.',
  UNKNOWN_ERROR: 'An unexpected error occurred. Please try again.',
}

const API_ERROR_CODES: ReadonlySet<ApiErrorCode> = new Set<ApiErrorCode>(
  Object.keys(ERROR_MESSAGES) as ApiErrorCode[]
)

function isApiErrorCode(value: string): value is ApiErrorCode {
  return API_ERROR_CODES.has(value as ApiErrorCode)
}

function inferCodeFromStatus(
  status: number,
  message?: string,
  details?: unknown
): ApiErrorCode {
  if (status === 400 || status === 422 || Array.isArray(details)) {
    return 'VALIDATION_ERROR'
  }
  if (status === 404) {
    if (message?.toLowerCase().includes('session')) {
      return 'SESSION_NOT_FOUND'
    }
    return 'UNKNOWN_ERROR'
  }
  if (status === 408) {
    return 'TIMEOUT'
  }
  if (status === 503) {
    return 'LLM_SERVICE_UNAVAILABLE'
  }
  if (status >= 500) {
    return 'INTERNAL_ERROR'
  }
  return 'UNKNOWN_ERROR'
}

function normalizeValidationDetails(
  details: unknown
): Array<{ field: string; message: string }> | undefined {
  if (!Array.isArray(details)) return undefined

  return details
    .map((item) => {
      if (!item || typeof item !== 'object') return null
      const value = item as Record<string, unknown>

      // FastAPI default validation shape: { loc: [...], msg: "...", type: "..." }
      if (Array.isArray(value.loc) && typeof value.msg === 'string') {
        const locPath = value.loc
          .map((part) => String(part))
          .filter((part) => part !== 'body')
        const field = locPath.length > 0 ? locPath.join('.') : 'request'
        return { field, message: value.msg }
      }

      // Existing normalized shape: { field: "...", message: "..." }
      if (typeof value.field === 'string' && typeof value.message === 'string') {
        return { field: value.field, message: value.message }
      }

      return null
    })
    .filter((item): item is { field: string; message: string } => item !== null)
}

function parseFastApiDetail(detail: unknown): {
  message?: string
  code?: string
  details?: unknown
} {
  if (typeof detail === 'string') {
    return { message: detail }
  }

  if (Array.isArray(detail)) {
    return { details: detail }
  }

  if (detail && typeof detail === 'object') {
    const data = detail as Record<string, unknown>
    return {
      message: typeof data.error === 'string' ? data.error : undefined,
      code: typeof data.code === 'string' ? data.code : undefined,
      details: data.details,
    }
  }

  return {}
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

  const detailParsed = parseFastApiDetail(errorData.detail)
  const message =
    errorData.error ||
    detailParsed.message ||
    `HTTP ${response.status}: ${response.statusText}`

  const detailsRaw = errorData.details ?? detailParsed.details
  const normalizedDetails = normalizeValidationDetails(detailsRaw) ?? detailsRaw

  const codeRaw =
    (typeof errorData.code === 'string' ? errorData.code : undefined) ??
    detailParsed.code
  const code = codeRaw && isApiErrorCode(codeRaw)
    ? codeRaw
    : inferCodeFromStatus(response.status, message, normalizedDetails)

  return new ApiClientError(
    code,
    response.status,
    message,
    normalizedDetails
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
