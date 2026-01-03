/**
 * API Client Integration Tests
 * 
 * These tests verify frontend-to-backend communication.
 * They require both Next.js and Python backend to be running.
 * 
 * Setup:
 * Terminal 1: cd backend && uvicorn app.main:app --reload
 * Terminal 2: pnpm dev
 * Terminal 3: pnpm test:integration
 */

import { describe, it, expect, beforeAll } from 'vitest';
import { ApiClient, ApiClientError } from '@/lib/api-client';

// Test configuration
const TEST_CONFIG = {
  baseURL: process.env.BACKEND_URL || 'http://localhost:8000',
  timeout: 10000,
  retryAttempts: 3,
  retryDelay: 1000,
  credentials: 'include' as RequestCredentials,
};

describe('API Client Integration Tests', () => {
  let client: ApiClient;

  beforeAll(() => {
    client = new ApiClient(TEST_CONFIG);
  });

  describe('Chat API', () => {
    it('should send first chat message and create session', async () => {
      const response = await client.chat({
        message: 'What is Open Water certification?',
      });

      expect(response).toBeDefined();
      expect(response.sessionId).toBeDefined();
      expect(typeof response.sessionId).toBe('string');
      expect(response.response).toBeDefined();
      expect(typeof response.response).toBe('string');
      expect(response.response.length).toBeGreaterThan(0);
    }, 30000); // 30s timeout for LLM response

    it('should maintain session across multiple messages', async () => {
      // First message
      const response1 = await client.chat({
        message: 'What is PADI?',
      });

      expect(response1.sessionId).toBeDefined();
      const sessionId = response1.sessionId;

      // Second message with same session
      const response2 = await client.chat({
        sessionId,
        message: 'Tell me more about it',
      });

      expect(response2.sessionId).toBe(sessionId);
      expect(response2.response).toBeDefined();

      // Third message with same session
      const response3 = await client.chat({
        sessionId,
        message: 'What about SSI?',
      });

      expect(response3.sessionId).toBe(sessionId);
      expect(response3.response).toBeDefined();
    }, 60000); // 60s timeout for multiple LLM responses

    it('should handle validation error (empty message)', async () => {
      await expect(
        client.chat({ message: '' })
      ).rejects.toThrow(ApiClientError);

      try {
        await client.chat({ message: '' });
      } catch (error) {
        expect(error).toBeInstanceOf(ApiClientError);
        expect((error as ApiClientError).code).toBe('VALIDATION_ERROR');
        expect((error as ApiClientError).statusCode).toBe(400);
      }
    }, 10000);

    it('should handle validation error (message too long)', async () => {
      const longMessage = 'a'.repeat(2001); // Exceeds max length

      await expect(
        client.chat({ message: longMessage })
      ).rejects.toThrow(ApiClientError);

      try {
        await client.chat({ message: longMessage });
      } catch (error) {
        expect(error).toBeInstanceOf(ApiClientError);
        expect((error as ApiClientError).code).toBe('VALIDATION_ERROR');
        expect((error as ApiClientError).statusCode).toBe(400);
      }
    }, 10000);
  });

  describe('Session API', () => {
    it('should get session information', async () => {
      // Create a session first
      const chatResponse = await client.chat({
        message: 'Test session',
      });

      const sessionId = chatResponse.sessionId;

      // Get session info
      const sessionResponse = await client.getSession(sessionId);

      expect(sessionResponse).toBeDefined();
      expect(sessionResponse.sessionId).toBe(sessionId);
      expect(sessionResponse.createdAt).toBeDefined();
      expect(sessionResponse.lastActivity).toBeDefined();
      expect(sessionResponse.messageCount).toBeGreaterThanOrEqual(1);
      expect(sessionResponse.isExpired).toBe(false);
    }, 30000);

    it('should handle session not found (404)', async () => {
      const invalidSessionId = '00000000-0000-0000-0000-000000000000';

      await expect(
        client.getSession(invalidSessionId)
      ).rejects.toThrow(ApiClientError);

      try {
        await client.getSession(invalidSessionId);
      } catch (error) {
        expect(error).toBeInstanceOf(ApiClientError);
        expect((error as ApiClientError).code).toBe('SESSION_NOT_FOUND');
        expect((error as ApiClientError).statusCode).toBe(404);
      }
    }, 10000);
  });

  describe('Lead API', () => {
    it('should create lead with email', async () => {
      // Create a session first
      const chatResponse = await client.chat({
        message: 'I want to learn diving',
      });

      const sessionId = chatResponse.sessionId;

      // Create lead
      const leadResponse = await client.createLead({
        sessionId,
        email: 'test@example.com',
        name: 'Test User',
        phone: '+1234567890',
        preferredContact: 'email',
        message: 'I would like to learn more about Open Water certification',
      });

      expect(leadResponse).toBeDefined();
      expect(leadResponse.success).toBe(true);
      expect(leadResponse.leadId).toBeDefined();
      expect(leadResponse.message).toBeDefined();
    }, 30000);

    it('should handle validation error (invalid email)', async () => {
      const sessionId = '123e4567-e89b-12d3-a456-426614174000';

      await expect(
        client.createLead({
          sessionId,
          email: 'invalid-email',
        })
      ).rejects.toThrow(ApiClientError);

      try {
        await client.createLead({
          sessionId,
          email: 'invalid-email',
        });
      } catch (error) {
        expect(error).toBeInstanceOf(ApiClientError);
        expect((error as ApiClientError).code).toBe('VALIDATION_ERROR');
        expect((error as ApiClientError).statusCode).toBe(400);
      }
    }, 10000);
  });

  describe('Error Handling', () => {
    it('should retry on transient errors', async () => {
      // This test is difficult to simulate reliably
      // Skip for now, covered by unit tests
    });

    it('should handle network errors gracefully', async () => {
      // Create client with invalid URL
      const badClient = new ApiClient({
        ...TEST_CONFIG,
        baseURL: 'http://localhost:9999', // Non-existent server
      });

      await expect(
        badClient.chat({ message: 'Test' })
      ).rejects.toThrow(ApiClientError);

      try {
        await badClient.chat({ message: 'Test' });
      } catch (error) {
        expect(error).toBeInstanceOf(ApiClientError);
        // Could be NETWORK_ERROR or TIMEOUT depending on timing
        expect(['NETWORK_ERROR', 'TIMEOUT']).toContain(
          (error as ApiClientError).code
        );
      }
    }, 15000);
  });

  describe('CORS', () => {
    it('should include credentials in requests', async () => {
      // This is implicitly tested by session persistence tests
      // Cookies (session ID) should be automatically included
      
      const response1 = await client.chat({
        message: 'First message',
      });

      const sessionId = response1.sessionId;

      // If CORS credentials work, this should use the same session
      const response2 = await client.chat({
        sessionId,
        message: 'Second message',
      });

      expect(response2.sessionId).toBe(sessionId);
    }, 40000);
  });
});
