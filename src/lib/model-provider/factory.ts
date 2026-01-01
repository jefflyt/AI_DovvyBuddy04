/**
 * Factory for creating LLM provider instances
 * Supports environment-based provider selection (Groq for dev, Gemini for prod)
 */

import pino from 'pino';
import { GroqProvider } from './groq-provider';
import { GeminiProvider } from './gemini-provider';
import { ModelProviderType } from './types';
import type { BaseModelProvider } from './base-provider';

const logger = pino({ name: 'model-provider-factory' });

// Singleton instances for serverless optimization
let groqInstance: GroqProvider | null = null;
let geminiInstance: GeminiProvider | null = null;

/**
 * Create or retrieve a model provider based on environment configuration
 * Uses singleton pattern for serverless function reuse
 *
 * @param providerType - Optional override for provider type (defaults to LLM_PROVIDER env var)
 * @returns BaseModelProvider instance (Groq or Gemini)
 * @throws Error if provider type is invalid or API key is missing
 */
export function createModelProvider(providerType?: ModelProviderType): BaseModelProvider {
  // Determine provider type from param or env
  const provider =
    providerType ||
    (process.env.LLM_PROVIDER?.toLowerCase() as ModelProviderType) ||
    ModelProviderType.GROQ;

  logger.info({ provider, msg: 'Creating model provider' });

  switch (provider) {
    case ModelProviderType.GROQ: {
      if (!process.env.GROQ_API_KEY) {
        throw new Error(
          'GROQ_API_KEY environment variable is required when LLM_PROVIDER=groq'
        );
      }

      // Return singleton instance if exists
      if (groqInstance) {
        logger.debug({ msg: 'Reusing existing Groq provider instance' });
        return groqInstance;
      }

      logger.info({ msg: 'Initializing new Groq provider instance' });
      groqInstance = new GroqProvider({
        apiKey: process.env.GROQ_API_KEY,
        defaultConfig: {
          model: process.env.GROQ_MODEL || 'llama-3.3-70b-versatile',
          temperature: process.env.LLM_TEMPERATURE
            ? parseFloat(process.env.LLM_TEMPERATURE)
            : 0.7,
          maxTokens: process.env.LLM_MAX_TOKENS
            ? parseInt(process.env.LLM_MAX_TOKENS, 10)
            : 2048,
        },
      });

      return groqInstance;
    }

    case ModelProviderType.GEMINI: {
      if (!process.env.GEMINI_API_KEY) {
        throw new Error(
          'GEMINI_API_KEY environment variable is required when LLM_PROVIDER=gemini'
        );
      }

      // Return singleton instance if exists
      if (geminiInstance) {
        logger.debug({ msg: 'Reusing existing Gemini provider instance' });
        return geminiInstance;
      }

      logger.info({ msg: 'Initializing new Gemini provider instance' });
      geminiInstance = new GeminiProvider({
        apiKey: process.env.GEMINI_API_KEY,
        defaultConfig: {
          model: process.env.GEMINI_MODEL || 'gemini-2.0-flash-exp',
          temperature: process.env.LLM_TEMPERATURE
            ? parseFloat(process.env.LLM_TEMPERATURE)
            : 0.7,
          maxTokens: process.env.LLM_MAX_TOKENS
            ? parseInt(process.env.LLM_MAX_TOKENS, 10)
            : 2048,
        },
      });

      return geminiInstance;
    }

    default:
      throw new Error(
        `Invalid LLM_PROVIDER: ${provider}. Must be 'groq' or 'gemini'`
      );
  }
}

/**
 * Reset singleton instances (useful for testing)
 */
export function resetProviderInstances(): void {
  groqInstance = null;
  geminiInstance = null;
  logger.info({ msg: 'Provider instances reset' });
}
