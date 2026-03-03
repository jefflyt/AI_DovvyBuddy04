/**
 * Vitest setup file
 * Configures test environment before tests run
 */

import { beforeAll } from 'vitest'

// Mock localStorage for jsdom environment
beforeAll(() => {
  // jsdom doesn't implement localStorage properly in some versions
  // Create a mock implementation
  const localStorageMock = (() => {
    let store: Record<string, string> = {}
    return {
      getItem: (key: string) => store[key] || null,
      setItem: (key: string, value: string) => {
        store[key] = value.toString()
      },
      removeItem: (key: string) => {
        delete store[key]
      },
      clear: () => {
        store = {}
      },
      get length() {
        return Object.keys(store).length
      },
      key: (index: number) => {
        const keys = Object.keys(store)
        return keys[index] || null
      },
    }
  })()

  // Try to set localStorage, and if it fails (SecurityError), force it
  try {
    if (typeof window !== 'undefined') {
      // Test if localStorage is accessible
      window.localStorage.setItem('test', 'test')
      window.localStorage.removeItem('test')
    }
  } catch (e) {
    // localStorage not available or throws SecurityError
    // Override with mock
    if (typeof window !== 'undefined') {
      Object.defineProperty(window, 'localStorage', {
        value: localStorageMock,
        writable: true,
        configurable: true,
      })
    }
  }
})
