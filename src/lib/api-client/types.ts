/**
 * API Client Types
 * Request/response types for API communication
 */

// ============================================================================
// Request Types
// ============================================================================

export interface ChatRequest {
  sessionId?: string
  message: string
  sessionState?: Record<string, unknown> // PR6.1: Session state from localStorage
}

export interface TrainingLeadData {
  name: string
  email: string
  phone?: string
  certification_level?: string
  interested_certification?: string
  preferred_location?: string
  message?: string
}

export interface TripLeadData {
  name: string
  email: string
  phone?: string
  destination?: string
  travel_dates?: string
  group_size?: number
  budget?: string
  message?: string
}

export type LeadRequest =
  | {
      type: 'training'
      data: TrainingLeadData
      session_id?: string
    }
  | {
      type: 'trip'
      data: TripLeadData
      session_id?: string
    }

export interface FastApiValidationDetail {
  loc: Array<string | number>
  msg: string
  type?: string
}

// ============================================================================
// Response Types
// ============================================================================

export interface ChatResponse {
  sessionId: string
  message: string
  agentType?: string
  metadata?: ChatMetadata
  followUpQuestion?: string // PR6.1: Follow-up question for conversation continuity
}

export interface ChatMetadata {
  tokensUsed?: number
  contextChunks?: number
  model?: string
  promptMode?: string
  agentsUsed?: string[]
  queryType?: string
  detectedIntent?: string // PR6.1: Detected conversation intent
  detected_intent?: string
  stateUpdates?: Record<string, unknown> // PR6.1: Session state updates from LLM
  state_updates?: Record<string, unknown>
  [key: string]: unknown
}

export interface SessionResponse {
  id: string
  conversation_history: Array<Record<string, string>>
  diver_profile?: Record<string, unknown> | null
  created_at?: string | null
  updated_at?: string | null
}

export interface LeadResponse {
  success: boolean
  lead_id: string
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
  | 'DB_ERROR'
  | 'CONFIG_ERROR'
  | 'SESSION_NOT_FOUND'
  | 'SESSION_EXPIRED'
  | 'TIMEOUT'
  | 'NETWORK_ERROR'
  | 'INTERNAL_ERROR'
  | 'UNKNOWN'
  | 'UNKNOWN_ERROR'

export interface ApiError {
  error?: string
  code?: ApiErrorCode | string
  details?: ValidationDetail[] | FastApiValidationDetail[] | string
  detail?: unknown
}

export interface ValidationDetail {
  field: string
  message: string
}

// ============================================================================
// Client Types
// ============================================================================

export interface RequestOptions {
  timeout?: number
  retryAttempts?: number
  retryDelay?: number
  signal?: AbortSignal
}
