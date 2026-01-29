import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  initErrorMonitoring,
  captureException,
  captureMessage,
  setUserContext,
  clearUserContext,
  addBreadcrumb,
  __resetErrorHandlerForTesting,
} from './error-handler'

describe('ErrorHandler', () => {
  let originalEnv: NodeJS.ProcessEnv
  let originalWindow: any

  beforeEach(() => {
    // Save original environment
    originalEnv = { ...process.env }
    originalWindow = global.window

    // Reset error handler singleton
    __resetErrorHandlerForTesting()
  })

  afterEach(() => {
    // Restore environment
    process.env = originalEnv
    global.window = originalWindow
  })

  describe('initErrorMonitoring', () => {
    it('should initialize without Sentry DSN (disabled mode)', () => {
      delete process.env.SENTRY_DSN
      vi.stubEnv('NODE_ENV', 'development')
      const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {})

      initErrorMonitoring()

      expect(logSpy).toHaveBeenCalledWith(
        expect.stringContaining('error monitoring disabled')
      )

      logSpy.mockRestore()
    })

    it('should not initialize twice', () => {
      delete process.env.SENTRY_DSN
      const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {})

      initErrorMonitoring()
      initErrorMonitoring() // Second call should be no-op

      logSpy.mockRestore()
    })
  })

  describe('captureException', () => {
    it('should warn if not initialized', () => {
      const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      const testError = new Error('Test error')
      captureException(testError)

      expect(warnSpy).toHaveBeenCalledWith(
        expect.stringContaining('Not initialized')
      )
      expect(errorSpy).toHaveBeenCalledWith(testError, undefined)

      warnSpy.mockRestore()
      errorSpy.mockRestore()
    })

    it('should log error after initialization (no Sentry)', () => {
      delete process.env.SENTRY_DSN
      vi.stubEnv('NODE_ENV', 'development')
      const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      initErrorMonitoring()

      const testError = new Error('Test error')
      const context = { userId: '123', page: '/test' }
      captureException(testError, context)

      expect(errorSpy).toHaveBeenCalledWith(
        expect.stringContaining('Exception'),
        testError,
        context
      )

      errorSpy.mockRestore()
    })
  })

  describe('captureMessage', () => {
    it('should warn if not initialized', () => {
      const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {})

      captureMessage('Test message', 'info')

      expect(warnSpy).toHaveBeenCalledWith(
        expect.stringContaining('Not initialized')
      )
      expect(logSpy).toHaveBeenCalledWith('Test message', 'info', undefined)

      warnSpy.mockRestore()
      logSpy.mockRestore()
    })

    it('should log message after initialization (no Sentry)', () => {
      delete process.env.SENTRY_DSN
      vi.stubEnv('NODE_ENV', 'development')
      const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {})

      initErrorMonitoring()

      const context = { feature: 'test' }
      captureMessage('Test message', 'warning', context)

      expect(logSpy).toHaveBeenCalledWith(
        expect.stringContaining('Message [warning]'),
        'Test message',
        context
      )

      logSpy.mockRestore()
    })

    it('should use console.error for error level messages', () => {
      delete process.env.SENTRY_DSN
      vi.stubEnv('NODE_ENV', 'development')
      const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      initErrorMonitoring()

      captureMessage('Error message', 'error')

      expect(errorSpy).toHaveBeenCalledWith(
        expect.stringContaining('Message [error]'),
        'Error message',
        undefined
      )

      errorSpy.mockRestore()
    })
  })

  describe('setUserContext', () => {
    it('should warn if not initialized', () => {
      const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

      setUserContext('test123', 'test@example.com')

      expect(warnSpy).toHaveBeenCalledWith(
        expect.stringContaining('Not initialized')
      )

      warnSpy.mockRestore()
    })

    it('should not error after initialization (no Sentry)', () => {
      delete process.env.SENTRY_DSN
      initErrorMonitoring()

      // Should not throw
      expect(() => {
        setUserContext('user123', 'test@example.com')
      }).not.toThrow()
    })
  })

  describe('clearUserContext', () => {
    it('should not error if not initialized', () => {
      // Should not throw
      expect(() => {
        clearUserContext()
      }).not.toThrow()
    })

    it('should not error after initialization (no Sentry)', () => {
      delete process.env.SENTRY_DSN
      initErrorMonitoring()

      // Should not throw
      expect(() => {
        clearUserContext()
      }).not.toThrow()
    })
  })

  describe('addBreadcrumb', () => {
    it('should not error if not initialized', () => {
      // Should not throw
      expect(() => {
        addBreadcrumb('Test breadcrumb', 'navigation')
      }).not.toThrow()
    })

    it('should log breadcrumb after initialization (no Sentry)', () => {
      delete process.env.SENTRY_DSN
      vi.stubEnv('NODE_ENV', 'development')
      const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {})

      initErrorMonitoring()

      const data = { url: '/test' }
      addBreadcrumb('Page navigation', 'navigation', data)

      expect(logSpy).toHaveBeenCalledWith(
        expect.stringContaining('Breadcrumb:'),
        'Page navigation',
        'navigation',
        data
      )

      logSpy.mockRestore()
    })
  })
})
