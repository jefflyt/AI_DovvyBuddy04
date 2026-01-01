/**
 * Unit tests for Chat Orchestrator
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { orchestrateChat } from '../chat-orchestrator';

// Mock all dependencies
vi.mock('@/lib/model-provider', () => ({
  createModelProvider: vi.fn(() => ({
    generateResponse: vi.fn().mockResolvedValue({
      content: 'Mock response from LLM',
      tokensUsed: 100,
      model: 'test-model',
      finishReason: 'stop',
    }),
  })),
}));

vi.mock('@/lib/session', () => ({
  createSession: vi.fn().mockResolvedValue({
    id: 'test-session-id',
    conversationHistory: [],
    diverProfile: {},
    createdAt: new Date(),
    expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),
  }),
  getSession: vi.fn().mockResolvedValue(null),
  updateSessionHistory: vi.fn().mockResolvedValue(undefined),
}));

vi.mock('@/lib/prompts', () => ({
  buildCertificationPrompt: vi.fn((context) => `Certification prompt with context: ${context}`),
  buildTripPrompt: vi.fn((context) => `Trip prompt with context: ${context}`),
  detectPromptMode: vi.fn(() => 'certification'),
  BASE_SYSTEM_PROMPT: 'Base system prompt',
}));

vi.mock('@/lib/rag', () => ({
  retrieveRelevantChunks: vi.fn().mockResolvedValue([]),
}));

import { createModelProvider } from '@/lib/model-provider';
import { createSession, getSession, updateSessionHistory } from '@/lib/session';
import { detectPromptMode } from '@/lib/prompts';

describe('Chat Orchestrator', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('orchestrateChat', () => {
    it('should create new session when no sessionId provided', async () => {
      const result = await orchestrateChat({
        message: 'What is Open Water certification?',
      });

      expect(createSession).toHaveBeenCalled();
      expect(result.sessionId).toBe('test-session-id');
      expect(result.response).toBe('Mock response from LLM');
    });

    it('should create new session when existing session not found', async () => {
      (getSession as any).mockResolvedValueOnce(null);

      const result = await orchestrateChat({
        sessionId: 'non-existent-session',
        message: 'Hello',
      });

      expect(getSession).toHaveBeenCalledWith('non-existent-session');
      expect(createSession).toHaveBeenCalled();
      expect(result.sessionId).toBe('test-session-id');
    });

    it('should use existing session when found', async () => {
      const existingSession = {
        id: 'existing-session-id',
        conversationHistory: [
          { role: 'user', content: 'Previous message', timestamp: new Date().toISOString() },
        ],
        diverProfile: {},
        createdAt: new Date(),
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000),
      };

      (getSession as any).mockResolvedValueOnce(existingSession);

      const result = await orchestrateChat({
        sessionId: 'existing-session-id',
        message: 'Follow-up question',
      });

      expect(getSession).toHaveBeenCalledWith('existing-session-id');
      expect(createSession).not.toHaveBeenCalled();
      expect(result.sessionId).toBe('existing-session-id');
    });

    it('should update session history after LLM response', async () => {
      await orchestrateChat({
        message: 'Test message',
      });

      expect(updateSessionHistory).toHaveBeenCalledWith('test-session-id', {
        userMessage: 'Test message',
        assistantMessage: 'Mock response from LLM',
      });
    });

    it('should detect prompt mode and use appropriate system prompt', async () => {
      await orchestrateChat({
        message: 'Where should I dive?',
      });

      expect(detectPromptMode).toHaveBeenCalled();
    });

    it('should call LLM provider with correct message structure', async () => {
      const mockProvider = {
        generateResponse: vi.fn().mockResolvedValue({
          content: 'Response',
          tokensUsed: 50,
        }),
      };

      (createModelProvider as any).mockReturnValueOnce(mockProvider);

      await orchestrateChat({
        message: 'Test message',
      });

      expect(mockProvider.generateResponse).toHaveBeenCalledWith(
        expect.arrayContaining([
          expect.objectContaining({ role: 'system' }),
          expect.objectContaining({ role: 'user', content: 'Test message' }),
        ])
      );
    });

    it('should include metadata in response', async () => {
      const result = await orchestrateChat({
        message: 'Test',
      });

      expect(result.metadata).toBeDefined();
      expect(result.metadata?.tokensUsed).toBe(100);
      expect(result.metadata?.model).toBe('test-model');
      expect(result.metadata?.contextChunks).toBeDefined();
    });

    it('should validate message is non-empty', async () => {
      await expect(
        orchestrateChat({
          message: '',
        })
      ).rejects.toThrow();

      await expect(
        orchestrateChat({
          message: '   ',
        })
      ).rejects.toThrow();
    });

    it('should validate message length', async () => {
      const longMessage = 'a'.repeat(3000);

      await expect(
        orchestrateChat({
          message: longMessage,
        })
      ).rejects.toThrow();
    });

    it('should handle LLM provider errors', async () => {
      const mockProvider = {
        generateResponse: vi.fn().mockRejectedValue(new Error('LLM API error')),
      };

      (createModelProvider as any).mockReturnValueOnce(mockProvider);

      await expect(
        orchestrateChat({
          message: 'Test',
        })
      ).rejects.toThrow();
    });

    it('should handle session update errors', async () => {
      (updateSessionHistory as any).mockRejectedValueOnce(new Error('Database error'));

      await expect(
        orchestrateChat({
          message: 'Test',
        })
      ).rejects.toThrow();
    });
  });
});
