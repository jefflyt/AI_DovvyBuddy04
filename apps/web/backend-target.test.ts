import { describe, expect, it } from 'vitest'

const {
  DEFAULT_LOCAL_BACKEND_URL,
  resolveBackendUrl,
} = require('./backend-target')

describe('resolveBackendUrl', () => {
  it('returns the configured backend URL without a trailing slash', () => {
    expect(
      resolveBackendUrl({
        backendUrl: 'https://api.dovvybuddy.com/',
        nodeEnv: 'production',
      })
    ).toBe('https://api.dovvybuddy.com')
  })

  it('falls back to the local backend in development', () => {
    expect(
      resolveBackendUrl({
        backendUrl: '',
        nodeEnv: 'development',
      })
    ).toBe(DEFAULT_LOCAL_BACKEND_URL)
  })

  it('throws in production when the backend URL is missing', () => {
    expect(() =>
      resolveBackendUrl({
        backendUrl: '',
        nodeEnv: 'production',
      })
    ).toThrow(/BACKEND_URL is required/i)
  })
})
