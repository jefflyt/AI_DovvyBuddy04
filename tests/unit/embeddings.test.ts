/**
 * Embedding Provider Tests
 *
 * Unit tests for embedding provider functionality
 */

import { describe, it, expect } from 'vitest'
import { GeminiEmbeddingProvider } from '../../src/lib/embeddings/gemini-provider'
import { createEmbeddingProvider } from '../../src/lib/embeddings'

describe('Gemini Embedding Provider', () => {
  describe('constructor', () => {
    it('should throw error if no API key provided', () => {
      expect(() => new GeminiEmbeddingProvider('')).toThrow('Gemini API key is required')
    })

    it('should create instance with valid API key', () => {
      const provider = new GeminiEmbeddingProvider('test-key')
      expect(provider).toBeDefined()
      expect(provider.getProviderName()).toContain('gemini')
    })
  })

  describe('getDimension', () => {
    it('should return correct dimension for text-embedding-004', () => {
      const provider = new GeminiEmbeddingProvider('test-key')
      expect(provider.getDimension()).toBe(768)
    })
  })

  describe('generateEmbedding', () => {
    it('should throw error for empty text', async () => {
      const provider = new GeminiEmbeddingProvider('test-key')
      await expect(provider.generateEmbedding('')).rejects.toThrow('Text cannot be empty')
    })

    // Note: Actual API calls require mocking GoogleGenerativeAI
    // In a real test environment, we would mock the API client
  })
})

describe('Embedding Provider Factory', () => {
  it('should create Gemini provider', () => {
    const provider = createEmbeddingProvider({
      provider: 'gemini',
      apiKey: 'test-key',
    })

    expect(provider).toBeInstanceOf(GeminiEmbeddingProvider)
  })

  it('should throw error for unsupported provider', () => {
    expect(() =>
      createEmbeddingProvider({
        provider: 'groq' as any,
        apiKey: 'test-key',
      })
    ).toThrow()
  })
})
