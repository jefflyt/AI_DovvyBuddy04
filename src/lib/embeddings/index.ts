/**
 * Embedding Provider Factory
 *
 * Creates embedding provider instances based on configuration
 */

import { GeminiEmbeddingProvider } from './gemini-provider'
import type { EmbeddingProvider } from './types'

export type EmbeddingProviderType = 'gemini' | 'groq'

export interface EmbeddingConfig {
  provider: EmbeddingProviderType
  apiKey: string
  model?: string
}

/**
 * Create an embedding provider based on configuration
 */
export function createEmbeddingProvider(config: EmbeddingConfig): EmbeddingProvider {
  switch (config.provider) {
    case 'gemini':
      return new GeminiEmbeddingProvider(config.apiKey, config.model)

    case 'groq':
      throw new Error('Groq embedding provider not yet implemented (Groq may not have embedding endpoint)')

    default:
      throw new Error(`Unknown embedding provider: ${config.provider}`)
  }
}

/**
 * Create embedding provider from environment variables
 */
export function createEmbeddingProviderFromEnv(): EmbeddingProvider {
  const provider = (process.env.EMBEDDING_PROVIDER || 'gemini') as EmbeddingProviderType

  switch (provider) {
    case 'gemini': {
      const apiKey = process.env.GEMINI_API_KEY
      if (!apiKey) {
        throw new Error('GEMINI_API_KEY environment variable is required when using Gemini embeddings')
      }
      return new GeminiEmbeddingProvider(apiKey)
    }

    case 'groq':
      throw new Error('Groq embedding provider not yet implemented')

    default:
      throw new Error(`Unknown embedding provider: ${provider}`)
  }
}

// Re-export types
export type { EmbeddingProvider, EmbeddingResult, BatchEmbeddingResult } from './types'
