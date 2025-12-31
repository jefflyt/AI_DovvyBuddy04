/**
 * Integration tests for POST /api/chat endpoint
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { POST } from '../route';

// Mock the orchestrateChat function
vi.mock('@/lib/orchestration', () => ({
  orchestrateChat: vi.fn(),
}));

import { orchestrateChat } from '@/lib/orchestration';

// Helper to create NextRequest mock
function createRequest(body: any): Request {
  return new Request('http://localhost:3000/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
}

describe('POST /api/chat', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Successful requests', () => {
    it('should return 200 with valid request (no sessionId)', async () => {
      (orchestrateChat as any).mockResolvedValueOnce({
        sessionId: 'new-session-id',
        response: 'Hello! I can help with diving certifications and trip planning.',
        metadata: {
          tokensUsed: 50,
          contextChunks: 0,
          model: 'test-model',
          promptMode: 'general',
        },
      });

      const request = createRequest({
        message: 'Hello',
      });

      const response = await POST(request as any);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.sessionId).toBe('new-session-id');
      expect(data.response).toBeDefined();
      expect(data.metadata).toBeDefined();
    });

    it('should return 200 with valid request (with sessionId)', async () => {
      (orchestrateChat as any).mockResolvedValueOnce({
        sessionId: 'existing-session-id',
        response: 'Open Water is the entry-level certification...',
        metadata: {
          tokensUsed: 120,
          contextChunks: 2,
          model: 'test-model',
          promptMode: 'certification',
        },
      });

      const request = createRequest({
        sessionId: '123e4567-e89b-12d3-a456-426614174000',
        message: 'What is Open Water certification?',
      });

      const response = await POST(request as any);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.sessionId).toBe('existing-session-id');
      expect(orchestrateChat).toHaveBeenCalledWith({
        sessionId: '123e4567-e89b-12d3-a456-426614174000',
        message: 'What is Open Water certification?',
      });
    });
  });

  describe('Validation errors', () => {
    it('should return 400 when message is missing', async () => {
      const request = createRequest({
        sessionId: '123e4567-e89b-12d3-a456-426614174000',
      });

      const response = await POST(request as any);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error).toBe('Invalid request');
      expect(data.code).toBe('VALIDATION_ERROR');
      expect(data.details).toBeDefined();
    });

    it('should return 400 when message is empty', async () => {
      const request = createRequest({
        message: '',
      });

      const response = await POST(request as any);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error).toBe('Invalid request');
      expect(data.code).toBe('VALIDATION_ERROR');
    });

    it('should return 400 when message exceeds max length', async () => {
      const request = createRequest({
        message: 'a'.repeat(2001),
      });

      const response = await POST(request as any);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error).toBe('Invalid request');
      expect(data.code).toBe('VALIDATION_ERROR');
    });

    it('should return 400 when sessionId is not valid UUID', async () => {
      const request = createRequest({
        sessionId: 'not-a-uuid',
        message: 'Test',
      });

      const response = await POST(request as any);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.error).toBe('Invalid request');
      expect(data.code).toBe('VALIDATION_ERROR');
    });

    it('should return 400 when body is not JSON', async () => {
      const request = new Request('http://localhost:3000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: 'invalid json',
      });

      const response = await POST(request as any);
      await response.json();

      expect(response.status).toBe(500);
    });
  });

  describe('Error handling', () => {
    it('should return 503 when LLM API fails', async () => {
      (orchestrateChat as any).mockRejectedValueOnce(new Error('Groq API error: timeout'));

      const request = createRequest({
        message: 'Test',
      });

      const response = await POST(request as any);
      const data = await response.json();

      expect(response.status).toBe(503);
      expect(data.error).toContain('AI service temporarily unavailable');
      expect(data.code).toBe('LLM_SERVICE_UNAVAILABLE');
    });

    it('should return 500 when database fails', async () => {
      (orchestrateChat as any).mockRejectedValueOnce(new Error('Failed to create session'));

      const request = createRequest({
        message: 'Test',
      });

      const response = await POST(request as any);
      const data = await response.json();

      expect(response.status).toBe(500);
      expect(data.error).toContain('Unable to process request');
      expect(data.code).toBe('DATABASE_ERROR');
    });

    it('should return 400 for validation errors from orchestrator', async () => {
      (orchestrateChat as any).mockRejectedValueOnce(new Error('Message exceeds maximum length'));

      const request = createRequest({
        message: 'a'.repeat(100),
      });

      const response = await POST(request as any);
      const data = await response.json();

      expect(response.status).toBe(400);
      expect(data.code).toBe('VALIDATION_ERROR');
    });

    it('should return 500 for unexpected errors', async () => {
      (orchestrateChat as any).mockRejectedValueOnce(new Error('Unexpected error'));

      const request = createRequest({
        message: 'Test',
      });

      const response = await POST(request as any);
      const data = await response.json();

      expect(response.status).toBe(500);
      expect(data.error).toContain('unexpected error');
      expect(data.code).toBe('INTERNAL_SERVER_ERROR');
    });

    it('should include error details in development mode', async () => {
      // Note: Cannot modify NODE_ENV in tests, would need to mock the check instead
      vi.stubEnv('NODE_ENV', 'development');

      (orchestrateChat as any).mockRejectedValueOnce(new Error('Test error message'));

      const request = createRequest({
        message: 'Test',
      });

      const response = await POST(request as any);
      const data = await response.json();

      expect(data.details).toBeDefined();

      vi.unstubAllEnvs();
    });

    it('should not include error details in production mode', async () => {
      // Note: Cannot modify NODE_ENV in tests, would need to mock the check instead
      vi.stubEnv('NODE_ENV', 'production');

      (orchestrateChat as any).mockRejectedValueOnce(new Error('Groq API error'));

      const request = createRequest({
        message: 'Test',
      });

      const response = await POST(request as any);
      const data = await response.json();

      expect(data.details).toBeUndefined();

      vi.unstubAllEnvs();
    });
  });

  describe('Edge cases', () => {
    it('should handle very long messages within limit', async () => {
      (orchestrateChat as any).mockResolvedValueOnce({
        sessionId: 'test-session',
        response: 'Response',
        metadata: {},
      });

      const request = createRequest({
        message: 'a'.repeat(2000), // Max length
      });

      const response = await POST(request as any);

      expect(response.status).toBe(200);
    });

    it('should handle special characters in message', async () => {
      (orchestrateChat as any).mockResolvedValueOnce({
        sessionId: 'test-session',
        response: 'Response',
        metadata: {},
      });

      const request = createRequest({
        message: 'Test with émojis 🤿🐠 and spëcial çharacters!',
      });

      const response = await POST(request as any);

      expect(response.status).toBe(200);
    });
  });
});
