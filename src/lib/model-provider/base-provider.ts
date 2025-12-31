/**
 * Base abstract class for LLM providers
 * Provides common validation and structure for Groq and Gemini implementations
 */

import type { ModelConfig, ModelMessage, ModelResponse } from './types';

export abstract class BaseModelProvider {
  protected defaultConfig: ModelConfig;

  constructor(defaultConfig: ModelConfig) {
    this.defaultConfig = defaultConfig;
  }

  /**
   * Generate a response from the LLM
   * @param messages - Conversation history with system, user, and assistant messages
   * @param config - Optional config override for this specific request
   */
  abstract generateResponse(
    messages: ModelMessage[],
    config?: Partial<ModelConfig>
  ): Promise<ModelResponse>;

  /**
   * Validate that messages array is well-formed
   * @throws Error if messages are invalid
   */
  protected validateMessages(messages: ModelMessage[]): void {
    if (!Array.isArray(messages) || messages.length === 0) {
      throw new Error('Messages array must be non-empty');
    }

    for (const msg of messages) {
      if (!msg.role || !msg.content) {
        throw new Error('Each message must have role and content');
      }

      if (!['user', 'assistant', 'system'].includes(msg.role)) {
        throw new Error(`Invalid role: ${msg.role}`);
      }

      if (typeof msg.content !== 'string' || msg.content.trim().length === 0) {
        throw new Error('Message content must be a non-empty string');
      }
    }
  }

  /**
   * Merge default config with request-specific overrides
   */
  protected mergeConfig(override?: Partial<ModelConfig>): ModelConfig {
    return {
      ...this.defaultConfig,
      ...override,
    };
  }
}
