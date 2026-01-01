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
    agentsUsed?: string[];
    toolCalls?: Array<{ agent: string; tool: string; duration: number }>;
    queryType?: string;
    totalDuration?: number;
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

export interface AgentGraphResult {
  response: string;
  agentsUsed: string[];
  toolCalls: Array<{ agent: string; tool: string; duration: number }>;
  metadata: {
    totalDuration: number;
    tokensUsed: number;
    queryType: string;
  };
}
