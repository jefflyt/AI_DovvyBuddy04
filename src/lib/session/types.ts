/**
 * Type definitions for Session management
 * Supports conversation history and diver profile tracking
 */

export interface SessionMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface DiverProfile {
  certificationLevel?: string;
  diveCount?: number;
  interests?: string[];
  fears?: string[];
}

export interface SessionData {
  id: string;
  conversationHistory: SessionMessage[];
  diverProfile: DiverProfile;
  createdAt: Date;
  expiresAt: Date;
}

export interface CreateSessionInput {
  diverProfile?: DiverProfile;
}

export interface UpdateSessionInput {
  userMessage: string;
  assistantMessage: string;
}
