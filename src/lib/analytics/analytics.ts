/**
 * Analytics abstraction layer
 * Supports multiple analytics providers with a unified API
 */

type AnalyticsProvider = 'vercel' | 'posthog' | 'ga4' | 'none'

interface AnalyticsConfig {
  provider: AnalyticsProvider
  debug?: boolean
}

interface EventProperties {
  [key: string]: string | number | boolean | undefined
}

class Analytics {
  private provider: AnalyticsProvider
  private debug: boolean
  private initialized: boolean = false

  constructor(config: AnalyticsConfig) {
    this.provider = config.provider
    this.debug = config.debug || false
  }

  /**
   * Initialize analytics provider
   * Call this once in the root layout on mount
   */
  init(): void {
    if (this.initialized) return

    if (this.debug) {
      console.log('[Analytics] Initializing provider:', this.provider)
    }

    switch (this.provider) {
      case 'vercel':
        // Vercel Analytics is auto-initialized via @vercel/analytics package
        // No manual initialization needed
        break

      case 'posthog':
        this.initPosthog()
        break

      case 'ga4':
        this.initGA4()
        break

      case 'none':
        if (this.debug) {
          console.log('[Analytics] Analytics disabled')
        }
        break
    }

    this.initialized = true
  }

  /**
   * Track a page view
   */
  trackPageView(page: string): void {
    if (!this.initialized) {
      console.warn('[Analytics] Not initialized, skipping page view')
      return
    }

    if (this.debug) {
      console.log('[Analytics] Page view:', page)
    }

    switch (this.provider) {
      case 'vercel':
        // Vercel Analytics auto-tracks page views
        // Manual tracking not needed
        break

      case 'posthog':
        if (typeof window !== 'undefined' && (window as any).posthog) {
          ;(window as any).posthog.capture('$pageview', { page })
        }
        break

      case 'ga4':
        if (typeof window !== 'undefined' && (window as any).gtag) {
          ;(window as any).gtag('event', 'page_view', { page_path: page })
        }
        break
    }
  }

  /**
   * Track a custom event
   */
  trackEvent(event: string, properties?: EventProperties): void {
    if (!this.initialized) {
      console.warn('[Analytics] Not initialized, skipping event')
      return
    }

    if (this.debug) {
      console.log('[Analytics] Event:', event, properties)
    }

    switch (this.provider) {
      case 'vercel':
        // Vercel Analytics supports custom events via track() from @vercel/analytics
        if (typeof window !== 'undefined') {
          try {
            // Dynamic import to avoid SSR issues
            import('@vercel/analytics').then(({ track }) => {
              track(event, properties)
            })
          } catch (error) {
            console.error('[Analytics] Vercel track error:', error)
          }
        }
        break

      case 'posthog':
        if (typeof window !== 'undefined' && (window as any).posthog) {
          ;(window as any).posthog.capture(event, properties)
        }
        break

      case 'ga4':
        if (typeof window !== 'undefined' && (window as any).gtag) {
          ;(window as any).gtag('event', event, properties)
        }
        break
    }
  }

  /**
   * Identify a user (for authenticated sessions)
   * Not used in V1 (guest sessions only)
   */
  identifyUser(userId: string, traits?: EventProperties): void {
    if (!this.initialized) return

    if (this.debug) {
      console.log('[Analytics] Identify user:', userId, traits)
    }

    switch (this.provider) {
      case 'posthog':
        if (typeof window !== 'undefined' && (window as any).posthog) {
          ;(window as any).posthog.identify(userId, traits)
        }
        break

      case 'ga4':
        if (typeof window !== 'undefined' && (window as any).gtag) {
          ;(window as any).gtag('set', { user_id: userId })
          if (traits) {
            ;(window as any).gtag('set', 'user_properties', traits)
          }
        }
        break
    }
  }

  private initPosthog(): void {
    const posthogKey = process.env.NEXT_PUBLIC_POSTHOG_KEY
    const posthogHost =
      process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com'

    if (!posthogKey) {
      console.warn('[Analytics] Posthog key not found, skipping initialization')
      return
    }

    // Load Posthog script
    if (typeof window !== 'undefined' && !(window as any).posthog) {
      const script = document.createElement('script')
      script.innerHTML = `
        !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.async=!0,p.src=s.api_host+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="capture identify alias people.set people.set_once set_config register register_once unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset isFeatureEnabled onFeatureFlags getFeatureFlag getFeatureFlagPayload reloadFeatureFlags group updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures getActiveMatchingSurveys getSurveys".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
        posthog.init('${posthogKey}', {api_host: '${posthogHost}'})
      `
      document.head.appendChild(script)
    }
  }

  private initGA4(): void {
    const gaId = process.env.NEXT_PUBLIC_GA_ID

    if (!gaId) {
      console.warn('[Analytics] GA4 ID not found, skipping initialization')
      return
    }

    // Load GA4 script
    if (typeof window !== 'undefined' && !(window as any).gtag) {
      const script1 = document.createElement('script')
      script1.async = true
      script1.src = `https://www.googletagmanager.com/gtag/js?id=${gaId}`
      document.head.appendChild(script1)

      const script2 = document.createElement('script')
      script2.innerHTML = `
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', '${gaId}');
      `
      document.head.appendChild(script2)
    }
  }
}

// Singleton instance
let analyticsInstance: Analytics | null = null

/**
 * Reset analytics instance (for testing only)
 * @internal
 */
export function __resetAnalyticsForTesting(): void {
  analyticsInstance = null
}

/**
 * Initialize analytics
 * Call this once in the root layout
 */
export function initAnalytics(): void {
  if (analyticsInstance) return

  const provider =
    (process.env.NEXT_PUBLIC_ANALYTICS_PROVIDER as AnalyticsProvider) ||
    'vercel'
  const debug = process.env.NODE_ENV === 'development'

  analyticsInstance = new Analytics({ provider, debug })
  analyticsInstance.init()
}

/**
 * Track a page view
 */
export function trackPageView(page: string): void {
  if (!analyticsInstance) {
    console.warn('[Analytics] Not initialized, call initAnalytics() first')
    return
  }
  analyticsInstance.trackPageView(page)
}

/**
 * Track a custom event
 */
export function trackEvent(event: string, properties?: EventProperties): void {
  if (!analyticsInstance) {
    console.warn('[Analytics] Not initialized, call initAnalytics() first')
    return
  }
  analyticsInstance.trackEvent(event, properties)
}

/**
 * Identify a user
 */
export function identifyUser(
  userId: string,
  traits?: EventProperties
): void {
  if (!analyticsInstance) {
    console.warn('[Analytics] Not initialized, call initAnalytics() first')
    return
  }
  analyticsInstance.identifyUser(userId, traits)
}
