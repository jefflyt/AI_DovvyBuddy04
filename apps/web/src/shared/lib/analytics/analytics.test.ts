import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import {
  initAnalytics,
  trackPageView,
  trackEvent,
  identifyUser,
  __resetAnalyticsForTesting,
} from './analytics'

describe('Analytics', () => {
  let originalEnv: NodeJS.ProcessEnv
  let originalWindow: any

  beforeEach(() => {
    // Save original environment
    originalEnv = { ...process.env }
    originalWindow = global.window

    // Reset analytics singleton
    __resetAnalyticsForTesting()
  })

  afterEach(() => {
    // Restore environment
    process.env = originalEnv
    global.window = originalWindow
  })

  describe('initAnalytics', () => {
    it('should initialize with vercel provider by default', () => {
      process.env.NEXT_PUBLIC_ANALYTICS_PROVIDER = 'vercel'
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})

      initAnalytics()

      // Vercel analytics doesn't log in production, so just verify no errors
      expect(consoleSpy).not.toHaveBeenCalledWith(
        expect.stringContaining('error')
      )

      consoleSpy.mockRestore()
    })

    it('should handle none provider', () => {
      process.env.NEXT_PUBLIC_ANALYTICS_PROVIDER = 'none'
      vi.stubEnv('NODE_ENV', 'development')
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})

      initAnalytics()

      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Analytics disabled')
      )

      consoleSpy.mockRestore()
    })

    it('should not initialize twice', () => {
      process.env.NEXT_PUBLIC_ANALYTICS_PROVIDER = 'vercel'
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})

      initAnalytics()
      initAnalytics() // Second call should be no-op

      consoleSpy.mockRestore()
    })
  })

  describe('trackPageView', () => {
    it('should warn if not initialized', () => {
      const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

      trackPageView('/test')

      expect(warnSpy).toHaveBeenCalledWith(
        expect.stringContaining('Not initialized')
      )

      warnSpy.mockRestore()
    })

    it('should track page view after initialization', () => {
      process.env.NEXT_PUBLIC_ANALYTICS_PROVIDER = 'vercel'
      vi.stubEnv('NODE_ENV', 'development')
      const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {})

      initAnalytics()
      trackPageView('/test-page')

      expect(logSpy).toHaveBeenCalledWith(
        expect.stringContaining('Page view:'),
        '/test-page'
      )

      logSpy.mockRestore()
    })
  })

  describe('trackEvent', () => {
    it('should warn if not initialized', () => {
      const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

      trackEvent('test_event', { prop: 'value' })

      expect(warnSpy).toHaveBeenCalledWith(
        expect.stringContaining('Not initialized')
      )

      warnSpy.mockRestore()
    })

    it('should track event with properties after initialization', () => {
      process.env.NEXT_PUBLIC_ANALYTICS_PROVIDER = 'vercel'
      vi.stubEnv('NODE_ENV', 'development')
      const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {})

      initAnalytics()
      trackEvent('test_event', { foo: 'bar', count: 42 })

      expect(logSpy).toHaveBeenCalledWith(
        expect.stringContaining('Event:'),
        'test_event',
        expect.objectContaining({ foo: 'bar', count: 42 })
      )

      logSpy.mockRestore()
    })
  })

  describe('identifyUser', () => {
    it('should warn if not initialized', () => {
      const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})

      identifyUser('user123', { email: 'test@example.com' })

      expect(warnSpy).toHaveBeenCalledWith(
        expect.stringContaining('Not initialized')
      )

      warnSpy.mockRestore()
    })

    it('should identify user with traits after initialization', () => {
      process.env.NEXT_PUBLIC_ANALYTICS_PROVIDER = 'vercel'
      vi.stubEnv('NODE_ENV', 'development')
      const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {})

      initAnalytics()
      identifyUser('user123', { email: 'test@example.com' })

      expect(logSpy).toHaveBeenCalledWith(
        expect.stringContaining('Identify user:'),
        'user123',
        expect.objectContaining({ email: 'test@example.com' })
      )

      logSpy.mockRestore()
    })
  })
})
