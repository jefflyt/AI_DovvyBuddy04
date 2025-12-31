/**
 * RAG Types
 *
 * Type definitions for RAG pipeline (chunking, retrieval, etc.)
 */

export interface ContentChunk {
  text: string
  metadata: {
    contentPath: string
    chunkIndex: number
    sectionHeader?: string
    [key: string]: any // Allow additional metadata from frontmatter
  }
}

export interface RetrievalResult {
  chunkId: string
  text: string
  similarity: number
  metadata: {
    contentPath: string
    chunkIndex: number
    [key: string]: any
  }
}

export interface ChunkingOptions {
  targetTokens?: number // Target chunk size in tokens (default: 650)
  maxTokens?: number // Maximum chunk size (default: 800)
  minTokens?: number // Minimum chunk size (default: 100)
  overlapTokens?: number // Overlap between chunks (default: 50)
}
