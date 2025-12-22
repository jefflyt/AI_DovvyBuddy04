import { describe, it, expect } from 'vitest'

describe('Example test suite', () => {
  it('should pass a basic assertion', () => {
    expect(1 + 1).toBe(2)
  })

  it('should handle string operations', () => {
    const greeting = 'Hello, DovvyBuddy'
    expect(greeting).toContain('DovvyBuddy')
  })
})
