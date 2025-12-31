/**
 * Embedding Provider Types
 *
 * Defines the interface for embedding generation providers (Gemini, OpenAI, etc.)
 */

export interface EmbeddingProvider {
  /**
   * Generate an embedding vector for the given text
   * @param text - The text to embed
   * @returns A promise that resolves to the embedding vector (number array)
   */
  generateEmbedding(text: string): Promise<number[]>

  /**
   * Generate embeddings for multiple texts in a single batch
   * @param texts - Array of texts to embed
   * @returns A promise that resolves to an array of embedding vectors
   */
  generateEmbeddings(texts: string[]): Promise<number[][]>

  /**
   * Get the dimension of embeddings produced by this provider
   */
  getDimension(): number

  /**
   * Get the name of the provider
   */
  getProviderName(): string
}

export interface EmbeddingResult {
  embedding: number[]
  dimension: number
  model: string
}

export interface BatchEmbeddingResult {
  embeddings: number[][]
  dimension: number
  model: string
}
