/**
 * API Client Types
 * Request/response types for API communication
 */

// ============================================================================
// Request Types
// ============================================================================

export interface ChatRequest {
  sessionId?: string;
  message: string;
}

export interface LeadRequest {
  sessionId: string;
  email: string;
  name?: string;
  phone?: string;
  preferredContact?: 'email' | 'phone' | 'whatsapp';
  message?: string;
}

// ============================================================================
// Response Types
// ============================================================================

export interface ChatResponse {
  sessionId: string;
  response: string;
  metadata?: ChatMetadata;
}

export interface ChatMetadata {
  tokensUsed?: number;
  contextChunks?: number;
  model?: string;
  promptMode?: string;
  agentsUsed?: string[];
  queryType?: string;
}

export interface SessionResponse {
  sessionId: string;
  createdAt: string;
  lastActivity: string;
  messageCount: number;
  isExpired: boolean;
}

export interface LeadResponse {
  success: boolean;
  leadId: string;
  message: string;
}

// ============================================================================
// Error Types
// ============================================================================

export type ApiErrorCode =
  | 'VALIDATION_ERROR'
  | 'LLM_API_ERROR'
  | 'LLM_SERVICE_UNAVAILABLE'
  | 'ADK_UNAVAILABLE'
  | 'DATABASE_ERROR'
  | 'SESSION_NOT_FOUND'
  | 'SESSION_EXPIRED'
  | 'TIMEOUT'
  | 'NETWORK_ERROR'
  | 'INTERNAL_ERROR'
  | 'UNKNOWN_ERROR';

export interface ApiError {
  error: string;
  code: ApiErrorCode;
  details?: ValidationDetail[] | string;
}

export interface ValidationDetail {
  field: string;
  message: string;
}

// ============================================================================
// Client Types
// ============================================================================

export interface RequestOptions {
  timeout?: number;
  retryAttempts?: number;
  retryDelay?: number;
  signal?: AbortSignal;
}
