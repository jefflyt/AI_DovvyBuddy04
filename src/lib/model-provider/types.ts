/**
 * Type definitions for Model Provider abstraction layer
 * Supports Groq and Gemini LLM providers
 */

export enum ModelProviderType {
  GROQ = 'groq',
  GEMINI = 'gemini',
}

export interface ModelConfig {
  model: string;
  temperature: number;
  maxTokens: number;
  topP?: number;
}

export type ModelMessageRole = 'user' | 'assistant' | 'system';

export interface ModelMessage {
  role: ModelMessageRole;
  content: string;
}

export interface ModelResponse {
  content: string;
  tokensUsed?: number;
  model?: string;
  finishReason?: string;
}

export interface ModelProviderOptions {
  apiKey: string;
  defaultConfig?: Partial<ModelConfig>;
}
