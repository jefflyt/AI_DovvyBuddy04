-- Add HNSW index for optimized vector similarity search
-- This significantly improves query performance for large embedding tables

-- Create HNSW index on the embedding column using cosine distance operator
-- HNSW (Hierarchical Navigable Small World) is the most efficient index type for pgvector
CREATE INDEX IF NOT EXISTS content_embeddings_vector_idx 
ON content_embeddings 
USING hnsw (embedding vector_cosine_ops);

-- Index parameters explanation:
-- - vector_cosine_ops: Uses cosine distance (1 - cosine_similarity), matching our query operator (<=>)
-- - HNSW default m=16, ef_construction=64 provides good balance of speed vs accuracy
-- - For tuning: ALTER INDEX content_embeddings_vector_idx SET (m = 16, ef_construction = 64);

-- Expected improvements:
-- - P95 retrieval time: 1568ms → 200-400ms
-- - Average retrieval time: 376ms → 100-200ms
-- - Query consistency: Reduced variance in response times
