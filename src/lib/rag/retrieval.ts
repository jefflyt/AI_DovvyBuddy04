/**
 * RAG Retrieval
 *
 * Vector similarity search for retrieving relevant content chunks using native pgvector
 */

import { db } from '../../db/client'
import { contentEmbeddings } from '../../db/schema'
import { createEmbeddingProviderFromEnv } from '../embeddings'
import type { RetrievalResult } from './types'
import { sql } from 'drizzle-orm'

export interface RetrievalOptions {
  topK?: number // Number of results to return (default: 5)
  minSimilarity?: number // Minimum cosine similarity threshold (default: 0.0)
  filters?: {
    docType?: string | string[] // Filter by doc_type
    tags?: string[] // Filter by tags (any match)
    destination?: string // Filter by destination
  }
}

/**
 * Retrieve relevant content chunks based on query using native pgvector operations
 */
export async function retrieveRelevantChunks(
  query: string,
  options: RetrievalOptions = {}
): Promise<RetrievalResult[]> {
  const {
    topK = 5,
    minSimilarity = 0.0,
    filters = {},
  } = options

  if (!query || query.trim().length === 0) {
    throw new Error('Query cannot be empty')
  }

  // Generate embedding for query
  const embeddingProvider = createEmbeddingProviderFromEnv()
  const queryEmbedding = await embeddingProvider.generateEmbedding(query)

  // Convert embedding array to pgvector format string
  const embeddingVector = `[${queryEmbedding.join(',')}]`

  // Build filter conditions
  const conditions: any[] = []

  if (filters.docType) {
    if (Array.isArray(filters.docType)) {
      conditions.push(sql`metadata->>'doc_type' IN (${sql.join(filters.docType.map(t => sql`${t}`), sql`, `)})`)
    } else {
      conditions.push(sql`metadata->>'doc_type' = ${filters.docType}`)
    }
  }

  if (filters.destination) {
    conditions.push(sql`metadata->>'destination' = ${filters.destination}`)
  }

  if (filters.tags && filters.tags.length > 0) {
    // Check if any of the specified tags exist in the metadata->tags array
    const tagConditions = filters.tags.map(tag => 
      sql`metadata->'tags' @> ${JSON.stringify([tag])}`
    )
    conditions.push(sql`(${sql.join(tagConditions, sql` OR `)})`)
  }

  // Build WHERE clause
  const whereClause = conditions.length > 0 
    ? sql`WHERE ${sql.join(conditions, sql` AND `)}`
    : sql``

  // Query database using pgvector cosine distance operator (<=>)
  // Note: cosine distance = 1 - cosine similarity
  // We convert back to similarity for consistency with the interface
  const sqlQuery = sql`
    SELECT 
      id::text,
      content_path,
      chunk_text,
      metadata,
      1 - (embedding <=> ${embeddingVector}::vector) as similarity
    FROM ${contentEmbeddings}
    ${whereClause}
    ORDER BY embedding <=> ${embeddingVector}::vector
    LIMIT ${topK}
  `

  const results = await db.execute(sqlQuery)

  // Map results to RetrievalResult format
  const mapped: RetrievalResult[] = (results as any[]).map((row: any) => ({
    chunkId: row.id,
    text: row.chunk_text,
    similarity: row.similarity,
    metadata: row.metadata,
  }))

  // Filter by minimum similarity threshold
  const filtered = mapped.filter((result: RetrievalResult) => result.similarity >= minSimilarity)

  return filtered
}

/**
 * Retrieve relevant chunks with context (includes surrounding chunks)
 * Useful for maintaining context across chunk boundaries
 */
export async function retrieveRelevantChunksWithContext(
  query: string,
  options: RetrievalOptions = {}
): Promise<RetrievalResult[]> {
  // Get initial relevant chunks
  const results = await retrieveRelevantChunks(query, options)

  // For each result, fetch adjacent chunks from same document
  // (Future enhancement - not implementing in V1)

  return results
}

/**
 * Hybrid search: combine keyword and vector search
 * (Future enhancement - not implementing in V1)
 */
export async function hybridSearch(
  query: string,
  options: RetrievalOptions = {}
): Promise<RetrievalResult[]> {
  // Future: combine BM25/keyword search with vector search
  // For now, just use vector search
  return retrieveRelevantChunks(query, options)
}
