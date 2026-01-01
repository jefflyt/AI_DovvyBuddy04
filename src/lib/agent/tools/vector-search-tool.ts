/**
 * Vector Search Tool
 * Searches the diving knowledge base for relevant information
 */

import type { Tool } from '../types';

export const vectorSearchTool: Tool = {
  name: 'search_knowledge_base',
  description: 'Search the diving knowledge base for relevant information',
  parameters: {
    query: { type: 'string', description: 'Search query' },
    top_k: { type: 'number', description: 'Number of results', default: 5 },
  },
  async execute(params: { query: string; top_k?: number }) {
    try {
      // Check if RAG is enabled
      if (process.env.ENABLE_RAG !== 'true') {
        console.log('RAG disabled, returning empty chunks');
        return { chunks: [] };
      }

      // Dynamic import to avoid circular dependencies
      const { retrieveRelevantChunks } = await import('@/lib/rag/retrieval');

      const results = await retrieveRelevantChunks(params.query, {
        topK: params.top_k || 5,
        minSimilarity: 0.5,
      });

      return {
        chunks: results.map((r) => ({
          text: r.text,
          metadata: {
            source: r.metadata?.contentPath,
            similarity: r.similarity,
          },
        })),
      };
    } catch (error) {
      console.error('Vector search failed:', error);
      return { chunks: [], error: 'Search unavailable' };
    }
  },
};

