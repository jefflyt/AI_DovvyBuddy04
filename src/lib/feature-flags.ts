/**
 * Feature flag management for frontend features.
 *
 * Provides centralized access to feature flags controlled via environment variables.
 */

/**
 * Registry of all feature flags in the system.
 */
export enum FeatureFlag {
  CONVERSATION_FOLLOWUP = 'conversation_followup',
  // Add future feature flags here
  // Example:
  // SSE_STREAMING = 'sse_streaming',
  // ANALYTICS_TRACKING = 'analytics_tracking',
}

/**
 * Feature flag manager for checking enabled features.
 */
class FeatureFlagManager {
  private flags: Map<FeatureFlag, boolean>

  constructor() {
    this.flags = new Map()
    this.loadFlags()
  }

  /**
   * Load feature flags from environment variables.
   */
  private loadFlags(): void {
    for (const flag of Object.values(FeatureFlag)) {
      const envKey = `NEXT_PUBLIC_FEATURE_${flag.toUpperCase()}_ENABLED`
      const enabled = process.env[envKey] === 'true'
      this.flags.set(flag as FeatureFlag, enabled)

      if (process.env.NODE_ENV === 'development') {
        console.log(`[FeatureFlags] ${flag} = ${enabled}`)
      }
    }
  }

  /**
   * Check if a feature flag is enabled.
   *
   * @param flag - Feature flag to check
   * @returns True if enabled, false otherwise
   */
  isEnabled(flag: FeatureFlag): boolean {
    return this.flags.get(flag) ?? false
  }

  /**
   * Get all feature flags and their states.
   *
   * @returns Object mapping flag names to enabled state
   */
  getAllFlags(): Record<string, boolean> {
    const result: Record<string, boolean> = {}
    this.flags.forEach((enabled, flag) => {
      result[flag] = enabled
    })
    return result
  }
}

// Global instance
let flagManager: FeatureFlagManager | null = null

/**
 * Get the global feature flag manager instance.
 *
 * @returns FeatureFlagManager singleton instance
 */
export function getFeatureFlagManager(): FeatureFlagManager {
  if (!flagManager) {
    flagManager = new FeatureFlagManager()
  }
  return flagManager
}

/**
 * Convenience function to check if a feature is enabled.
 *
 * @param flag - Feature flag to check
 * @returns True if enabled, false otherwise
 */
export function isFeatureEnabled(flag: FeatureFlag): boolean {
  return getFeatureFlagManager().isEnabled(flag)
}
