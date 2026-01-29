/**
 * Error monitoring and handling
 * Integrates with Sentry for production error tracking
 */

type ErrorLevel = 'info' | 'warning' | 'error' | 'fatal'

interface ErrorContext {
  [key: string]: any
}

class ErrorHandler {
  private initialized: boolean = false
  private debug: boolean = false

  constructor(debug: boolean = false) {
    this.debug = debug
  }

  /**
   * Initialize error monitoring
   * Call this once in the root layout
   */
  init(): void {
    if (this.initialized) return

    const sentryDsn = process.env.SENTRY_DSN

    if (!sentryDsn) {
      if (this.debug) {
        console.log('[ErrorHandler] Sentry DSN not found, error monitoring disabled')
      }
      this.initialized = true
      return
    }

    // Sentry is initialized via next.config.js with @sentry/nextjs
    // This just marks the handler as ready
    if (this.debug) {
      console.log('[ErrorHandler] Sentry initialized')
    }

    this.initialized = true
  }

  /**
   * Capture an exception
   */
  captureException(error: Error, context?: ErrorContext): void {
    if (this.debug) {
      console.error('[ErrorHandler] Exception:', error, context)
    }

    if (typeof window !== 'undefined' && (window as any).Sentry) {
      if (context) {
        ;(window as any).Sentry.withScope((scope: any) => {
          Object.entries(context).forEach(([key, value]) => {
            scope.setContext(key, value)
          })
          ;(window as any).Sentry.captureException(error)
        })
      } else {
        ;(window as any).Sentry.captureException(error)
      }
    } else {
      // Fallback: log to console
      console.error('[ErrorHandler] Exception (no Sentry):', error, context)
    }
  }

  /**
   * Capture a message
   */
  captureMessage(message: string, level: ErrorLevel = 'info', context?: ErrorContext): void {
    if (this.debug) {
      console.log(`[ErrorHandler] Message [${level}]:`, message, context)
    }

    if (typeof window !== 'undefined' && (window as any).Sentry) {
      if (context) {
        ;(window as any).Sentry.withScope((scope: any) => {
          Object.entries(context).forEach(([key, value]) => {
            scope.setContext(key, value)
          })
          ;(window as any).Sentry.captureMessage(message, level)
        })
      } else {
        ;(window as any).Sentry.captureMessage(message, level)
      }
    } else {
      // Fallback: log to console
      const logMethod = level === 'error' || level === 'fatal' ? console.error : console.log
      logMethod(`[ErrorHandler] Message [${level}] (no Sentry):`, message, context)
    }
  }

  /**
   * Set user context for error reports
   */
  setUserContext(userId?: string, email?: string): void {
    if (typeof window !== 'undefined' && (window as any).Sentry) {
      ;(window as any).Sentry.setUser({
        id: userId,
        email: email,
      })
    }
  }

  /**
   * Clear user context
   */
  clearUserContext(): void {
    if (typeof window !== 'undefined' && (window as any).Sentry) {
      ;(window as any).Sentry.setUser(null)
    }
  }

  /**
   * Add breadcrumb for debugging
   */
  addBreadcrumb(message: string, category?: string, data?: ErrorContext): void {
    if (this.debug) {
      console.log('[ErrorHandler] Breadcrumb:', message, category, data)
    }

    if (typeof window !== 'undefined' && (window as any).Sentry) {
      ;(window as any).Sentry.addBreadcrumb({
        message,
        category: category || 'default',
        data,
        level: 'info',
      })
    }
  }
}

// Singleton instance
let errorHandlerInstance: ErrorHandler | null = null

/**
 * Reset error handler instance (for testing only)
 * @internal
 */
export function __resetErrorHandlerForTesting(): void {
  errorHandlerInstance = null
}

/**
 * Initialize error monitoring
 * Call this once in the root layout
 */
export function initErrorMonitoring(): void {
  if (errorHandlerInstance) return

  const debug = process.env.NODE_ENV === 'development'
  errorHandlerInstance = new ErrorHandler(debug)
  errorHandlerInstance.init()
}

/**
 * Capture an exception
 */
export function captureException(error: Error, context?: ErrorContext): void {
  if (!errorHandlerInstance) {
    console.warn('[ErrorHandler] Not initialized, call initErrorMonitoring() first')
    console.error(error, context)
    return
  }
  errorHandlerInstance.captureException(error, context)
}

/**
 * Capture a message
 */
export function captureMessage(
  message: string,
  level: ErrorLevel = 'info',
  context?: ErrorContext
): void {
  if (!errorHandlerInstance) {
    console.warn('[ErrorHandler] Not initialized, call initErrorMonitoring() first')
    console.log(message, level, context)
    return
  }
  errorHandlerInstance.captureMessage(message, level, context)
}

/**
 * Set user context for error reports
 */
export function setUserContext(userId?: string, email?: string): void {
  if (!errorHandlerInstance) {
    console.warn('[ErrorHandler] Not initialized, call initErrorMonitoring() first')
    return
  }
  errorHandlerInstance.setUserContext(userId, email)
}

/**
 * Clear user context
 */
export function clearUserContext(): void {
  if (!errorHandlerInstance) return
  errorHandlerInstance.clearUserContext()
}

/**
 * Add breadcrumb for debugging
 */
export function addBreadcrumb(
  message: string,
  category?: string,
  data?: ErrorContext
): void {
  if (!errorHandlerInstance) return
  errorHandlerInstance.addBreadcrumb(message, category, data)
}
