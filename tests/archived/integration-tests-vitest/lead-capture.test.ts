import { describe, it, expect, beforeAll } from 'vitest'
import { apiClient } from '@/lib/api-client'

/**
 * Integration tests for lead capture functionality
 *
 * Prerequisites:
 * - Backend server running at http://localhost:8000
 * - Database configured and migrations applied
 * - RESEND_API_KEY and LEAD_EMAIL_TO environment variables set
 *
 * SKIPPED: These tests have AbortSignal issues in Node.js test environment.
 * Use E2E tests (Playwright) for integration testing instead.
 */

describe.skip('Lead Capture Integration Tests', () => {
  let sessionId: string

  beforeAll(async () => {
    // Create a test session by sending a chat message
    const chatResponse = await apiClient.chat({
      message: 'Tell me about PADI Open Water certification',
    })
    sessionId = chatResponse.sessionId
    expect(sessionId).toBeDefined()
  })

  describe('Training Lead Submission', () => {
    it('should successfully submit a training lead', async () => {
      const leadData = {
        type: 'training' as const,
        data: {
          email: 'test-training@example.com',
          name: 'John Doe',
          phone: '+1234567890',
          message: 'Agency: PADI, Level: Open Water, Location: Singapore',
        },
        session_id: sessionId,
      }

      const response = await apiClient.createLead(leadData)

      expect(response.success).toBe(true)
      expect(response.lead_id).toBeDefined()

      // Log for manual verification
      console.log('Training lead submitted:', response.lead_id)
    })

    it('should fail with validation error for invalid email', async () => {
      const leadData = {
        type: 'training' as const,
        data: {
          email: 'not-an-email',
          name: 'Test User',
          message: 'Agency: PADI',
        },
        session_id: sessionId,
      }

      await expect(apiClient.createLead(leadData)).rejects.toThrow()
    })

    it('should fail with validation error for missing email', async () => {
      const leadData = {
        type: 'training' as const,
        data: {
          email: '',
          name: 'Test User',
          message: 'Agency: PADI',
        },
        session_id: sessionId,
      }

      await expect(apiClient.createLead(leadData)).rejects.toThrow()
    })
  })

  describe('Trip Lead Submission', () => {
    it('should successfully submit a trip lead', async () => {
      const leadData = {
        type: 'trip' as const,
        data: {
          email: 'test-trip@example.com',
          name: 'Jane Smith',
          phone: '+9876543210',
          destination: 'Tioman',
          travel_dates: 'June 2026',
          message:
            'Certification: AOW, Dive Count: 25, Interests: Wrecks, Reefs',
        },
        session_id: sessionId,
      }

      const response = await apiClient.createLead(leadData)

      expect(response.success).toBe(true)
      expect(response.lead_id).toBeDefined()

      console.log('Trip lead submitted:', response.lead_id)
    })

    it('should handle optional fields correctly', async () => {
      const leadData = {
        type: 'trip' as const,
        data: {
          email: 'minimal@example.com',
          name: 'Minimal User',
          destination: 'Bali',
        },
        session_id: sessionId,
      }

      const response = await apiClient.createLead(leadData)

      expect(response.success).toBe(true)
      expect(response.lead_id).toBeDefined()
    })
  })

  describe('Multiple Submissions', () => {
    it('should allow multiple lead submissions in same session', async () => {
      // First submission
      const lead1 = await apiClient.createLead({
        type: 'training',
        data: {
          email: 'first@example.com',
          name: 'First User',
          message: 'First inquiry',
        },
        session_id: sessionId,
      })

      expect(lead1.success).toBe(true)

      // Second submission
      const lead2 = await apiClient.createLead({
        type: 'trip',
        data: {
          email: 'second@example.com',
          name: 'Second User',
          destination: 'Bali',
          message: 'Second inquiry',
        },
        session_id: sessionId,
      })

      expect(lead2.success).toBe(true)
      expect(lead1.lead_id).not.toBe(lead2.lead_id)
    })
  })

  describe('Error Handling', () => {
    it('should handle network errors gracefully', async () => {
      // This test requires manually stopping the backend server
      // Skip in CI/CD, use for manual testing
      if (process.env.CI) {
        return
      }

      // Test will be skipped unless backend is intentionally stopped
      console.log(
        'To test network errors, stop the backend and run this test manually'
      )
    })

    it('should handle session not found error', async () => {
      const invalidSessionId = '00000000-0000-0000-0000-000000000000'

      const leadData = {
        type: 'training' as const,
        data: {
          email: 'test@example.com',
          name: 'Test User',
          message: 'Test',
        },
        session_id: invalidSessionId,
      }

      // Backend should return 404 for non-existent session
      await expect(apiClient.createLead(leadData)).rejects.toThrow()
    })
  })
})

/**
 * Database Verification Tests
 *
 * Note: These tests require direct database access
 * They are commented out by default but can be enabled for manual verification
 */
describe.skip('Database Verification', () => {
  it('should verify lead exists in database', async () => {
    // This would require setting up a database client
    // For manual verification, use:
    // SELECT * FROM leads WHERE email='test-training@example.com';

    console.log(
      'Manual DB check: SELECT * FROM leads ORDER BY created_at DESC LIMIT 5;'
    )
  })

  it('should verify email notification was sent', async () => {
    // Manual verification:
    // Check LEAD_EMAIL_TO inbox for lead notification email

    console.log('Manual check: Verify email received at LEAD_EMAIL_TO address')
  })
})
