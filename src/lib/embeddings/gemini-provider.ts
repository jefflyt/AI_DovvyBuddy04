/**
 * Gemini Embedding Provider
 *
 * Implements embedding generation using Google's Gemini API (text-embedding-004)
 */

import { GoogleGenerativeAI } from '@google/generative-ai'
import type { EmbeddingProvider } from './types'

const GEMINI_EMBEDDING_MODEL = 'text-embedding-004'
const GEMINI_EMBEDDING_DIMENSION = 768 // text-embedding-004 produces 768-dimensional vectors
const MAX_RETRIES = 3
const INITIAL_RETRY_DELAY_MS = 1000

export class GeminiEmbeddingProvider implements EmbeddingProvider {
  private client: GoogleGenerativeAI
  private model: string

  constructor(apiKey: string, model: string = GEMINI_EMBEDDING_MODEL) {
    if (!apiKey) {
      throw new Error('Gemini API key is required')
    }

    this.client = new GoogleGenerativeAI(apiKey)
    this.model = model
  }

  async generateEmbedding(text: string): Promise<number[]> {
    if (!text || text.trim().length === 0) {
      throw new Error('Text cannot be empty')
    }

    let lastError: Error | null = null

    for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
      try {
        const model = this.client.getGenerativeModel({ model: this.model })
        const result = await model.embedContent(text)

        if (!result.embedding || !result.embedding.values) {
          throw new Error('Invalid embedding response from Gemini API')
        }

        const embedding = result.embedding.values

        // Validate dimension
        if (embedding.length !== GEMINI_EMBEDDING_DIMENSION) {
          throw new Error(
            `Expected embedding dimension ${GEMINI_EMBEDDING_DIMENSION}, got ${embedding.length}`
          )
        }

        return embedding
      } catch (error) {
        lastError = error as Error

        // Check if it's a rate limit error
        const isRateLimit =
          error instanceof Error &&
          (error.message.includes('429') ||
            error.message.includes('rate limit') ||
            error.message.includes('quota'))

        if (isRateLimit && attempt < MAX_RETRIES - 1) {
          // Exponential backoff
          const delay = INITIAL_RETRY_DELAY_MS * Math.pow(2, attempt)
          console.warn(
            `Rate limit hit, retrying in ${delay}ms (attempt ${attempt + 1}/${MAX_RETRIES})`
          )
          await new Promise((resolve) => setTimeout(resolve, delay))
          continue
        }

        // If not rate limit or last attempt, throw
        if (attempt === MAX_RETRIES - 1) {
          break
        }
      }
    }

    throw new Error(`Failed to generate embedding after ${MAX_RETRIES} attempts: ${lastError?.message}`)
  }

  async generateEmbeddings(texts: string[]): Promise<number[][]> {
    if (!texts || texts.length === 0) {
      throw new Error('Texts array cannot be empty')
    }

    // Process sequentially to avoid rate limits
    const embeddings: number[][] = []

    for (const text of texts) {
      const embedding = await this.generateEmbedding(text)
      embeddings.push(embedding)
    }

    return embeddings
  }

  getDimension(): number {
    return GEMINI_EMBEDDING_DIMENSION
  }

  getProviderName(): string {
    return `gemini:${this.model}`
  }
}
