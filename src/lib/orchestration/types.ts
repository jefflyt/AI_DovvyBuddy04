/**
 * Type definitions for Chat Orchestration
 * Defines request/response shapes and RAG integration types
 */

export interface ChatRequest {
  sessionId?: string;
  message: string;
}

export interface ChatResponse {
  sessionId: string;
  response: string;
  metadata?: {
    tokensUsed?: number;
    contextChunks?: number;
    model?: string;
    promptMode?: string;
  };
}

export interface RetrievalResult {
  chunks: Array<{
    text: string;
    metadata?: {
      source?: string;
      title?: string;
      [key: string]: unknown;
    };
  }>;
}
