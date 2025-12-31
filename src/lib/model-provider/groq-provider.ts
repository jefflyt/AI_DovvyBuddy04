/**
 * Groq LLM Provider implementation
 * Uses Groq SDK for fast inference with Llama models
 */

import Groq from 'groq-sdk';
import pino from 'pino';
import { BaseModelProvider } from './base-provider';
import type { ModelConfig, ModelMessage, ModelResponse, ModelProviderOptions } from './types';

const logger = pino({ name: 'groq-provider' });

export class GroqProvider extends BaseModelProvider {
  private client: Groq;
  private apiKey: string;

  constructor(options: ModelProviderOptions) {
    // Default config for Groq
    const defaultConfig: ModelConfig = {
      model: options.defaultConfig?.model || 'llama-3.1-70b-versatile',
      temperature: options.defaultConfig?.temperature ?? 0.7,
      maxTokens: options.defaultConfig?.maxTokens || 2048,
      topP: options.defaultConfig?.topP ?? 1,
    };

    super(defaultConfig);

    this.apiKey = options.apiKey;
    this.client = new Groq({
      apiKey: this.apiKey,
    });
  }

  async generateResponse(
    messages: ModelMessage[],
    config?: Partial<ModelConfig>
  ): Promise<ModelResponse> {
    this.validateMessages(messages);
    const finalConfig = this.mergeConfig(config);

    const startTime = Date.now();

    try {
      logger.info({
        model: finalConfig.model,
        messageCount: messages.length,
        msg: 'Calling Groq API',
      });

      const completion = await this.client.chat.completions.create({
        model: finalConfig.model,
        messages: messages as Groq.Chat.Completions.ChatCompletionMessageParam[],
        temperature: finalConfig.temperature,
        max_tokens: finalConfig.maxTokens,
        top_p: finalConfig.topP,
      });

      const duration = Date.now() - startTime;

      const response: ModelResponse = {
        content: completion.choices[0]?.message?.content || '',
        tokensUsed: completion.usage?.total_tokens,
        model: completion.model,
        finishReason: completion.choices[0]?.finish_reason || undefined,
      };

      logger.info({
        model: response.model,
        tokensUsed: response.tokensUsed,
        finishReason: response.finishReason,
        durationMs: duration,
        msg: 'Groq API call successful',
      });

      return response;
    } catch (error) {
      const duration = Date.now() - startTime;

      logger.error({
        error: error instanceof Error ? error.message : 'Unknown error',
        durationMs: duration,
        msg: 'Groq API call failed',
      });

      if (error instanceof Error) {
        throw new Error(`Groq API error: ${error.message}`);
      }
      throw new Error('Groq API error: Unknown error occurred');
    }
  }
}
