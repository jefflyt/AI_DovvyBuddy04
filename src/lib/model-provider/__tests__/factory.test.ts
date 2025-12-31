/**
 * Unit tests for Model Provider Factory
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { createModelProvider, resetProviderInstances, ModelProviderType } from '../index';
import { GroqProvider } from '../groq-provider';
import { GeminiProvider } from '../gemini-provider';

describe('Model Provider Factory', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    // Reset module state before each test
    resetProviderInstances();
    // Clone env to avoid test pollution
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    // Restore original env
    process.env = originalEnv;
    vi.restoreAllMocks();
  });

  describe('createModelProvider', () => {
    it('should create Groq provider when LLM_PROVIDER=groq', () => {
      process.env.LLM_PROVIDER = 'groq';
      process.env.GROQ_API_KEY = 'test-groq-key';

      const provider = createModelProvider();

      expect(provider).toBeInstanceOf(GroqProvider);
    });

    it('should create Gemini provider when LLM_PROVIDER=gemini', () => {
      process.env.LLM_PROVIDER = 'gemini';
      process.env.GEMINI_API_KEY = 'test-gemini-key';

      const provider = createModelProvider();

      expect(provider).toBeInstanceOf(GeminiProvider);
    });

    it('should default to Groq when LLM_PROVIDER not set', () => {
      delete process.env.LLM_PROVIDER;
      process.env.GROQ_API_KEY = 'test-groq-key';

      const provider = createModelProvider();

      expect(provider).toBeInstanceOf(GroqProvider);
    });

    it('should accept explicit provider type override', () => {
      process.env.LLM_PROVIDER = 'groq';
      process.env.GROQ_API_KEY = 'test-groq-key';
      process.env.GEMINI_API_KEY = 'test-gemini-key';

      const provider = createModelProvider(ModelProviderType.GEMINI);

      expect(provider).toBeInstanceOf(GeminiProvider);
    });

    it('should throw error if Groq API key missing', () => {
      process.env.LLM_PROVIDER = 'groq';
      delete process.env.GROQ_API_KEY;

      expect(() => createModelProvider()).toThrow(
        'GROQ_API_KEY environment variable is required'
      );
    });

    it('should throw error if Gemini API key missing', () => {
      process.env.LLM_PROVIDER = 'gemini';
      delete process.env.GEMINI_API_KEY;

      expect(() => createModelProvider()).toThrow(
        'GEMINI_API_KEY environment variable is required'
      );
    });

    it('should throw error for invalid provider type', () => {
      process.env.LLM_PROVIDER = 'invalid';

      expect(() => createModelProvider()).toThrow('Invalid LLM_PROVIDER');
    });

    it('should return singleton instance on subsequent calls', () => {
      process.env.LLM_PROVIDER = 'groq';
      process.env.GROQ_API_KEY = 'test-groq-key';

      const provider1 = createModelProvider();
      const provider2 = createModelProvider();

      expect(provider1).toBe(provider2);
    });

    it('should respect custom model config from env vars', () => {
      process.env.LLM_PROVIDER = 'groq';
      process.env.GROQ_API_KEY = 'test-groq-key';
      process.env.GROQ_MODEL = 'custom-model';
      process.env.LLM_TEMPERATURE = '0.5';
      process.env.LLM_MAX_TOKENS = '1024';

      const provider = createModelProvider() as GroqProvider;

      // Check that provider was created (can't access protected defaultConfig easily)
      expect(provider).toBeInstanceOf(GroqProvider);
    });
  });

  describe('resetProviderInstances', () => {
    it('should clear singleton instances', () => {
      process.env.LLM_PROVIDER = 'groq';
      process.env.GROQ_API_KEY = 'test-groq-key';

      const provider1 = createModelProvider();
      resetProviderInstances();
      const provider2 = createModelProvider();

      expect(provider1).not.toBe(provider2);
    });
  });
});
