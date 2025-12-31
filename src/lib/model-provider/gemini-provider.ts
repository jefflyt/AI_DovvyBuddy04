/**
 * Gemini LLM Provider implementation
 * Uses Google Generative AI SDK for production-grade responses
 */

import { GoogleGenerativeAI, GenerativeModel, HarmCategory, HarmBlockThreshold } from '@google/generative-ai';
import pino from 'pino';
import { BaseModelProvider } from './base-provider';
import type { ModelConfig, ModelMessage, ModelResponse, ModelProviderOptions } from './types';

const logger = pino({ name: 'gemini-provider' });

export class GeminiProvider extends BaseModelProvider {
  private client: GoogleGenerativeAI;
  private model: GenerativeModel;
  private modelName: string;

  constructor(options: ModelProviderOptions) {
    // Default config for Gemini
    const defaultConfig: ModelConfig = {
      model: options.defaultConfig?.model || 'gemini-2.0-flash-exp',
      temperature: options.defaultConfig?.temperature ?? 0.7,
      maxTokens: options.defaultConfig?.maxTokens || 2048,
      topP: options.defaultConfig?.topP ?? 0.95,
    };

    super(defaultConfig);

    this.client = new GoogleGenerativeAI(options.apiKey);
    this.modelName = defaultConfig.model;

    // Initialize model with safety settings
    this.model = this.client.getGenerativeModel({
      model: this.modelName,
      safetySettings: [
        {
          category: HarmCategory.HARM_CATEGORY_HARASSMENT,
          threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        },
        {
          category: HarmCategory.HARM_CATEGORY_HATE_SPEECH,
          threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        },
        {
          category: HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
          threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        },
        {
          category: HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
          threshold: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        },
      ],
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
        msg: 'Calling Gemini API',
      });

      // Convert messages to Gemini format
      // Gemini uses a different message structure - we need to extract system prompt
      // and convert user/assistant messages to chat history
      const systemMessage = messages.find((m) => m.role === 'system');
      const chatMessages = messages.filter((m) => m.role !== 'system');

      // Build chat history for Gemini
      const history = chatMessages.slice(0, -1).map((msg) => ({
        role: msg.role === 'assistant' ? 'model' : 'user',
        parts: [{ text: msg.content }],
      }));

      // Last message should be the current user message
      const lastMessage = chatMessages[chatMessages.length - 1];
      if (!lastMessage || lastMessage.role !== 'user') {
        throw new Error('Last message must be from user');
      }

      // Start chat with history
      const chat = this.model.startChat({
        history,
        generationConfig: {
          temperature: finalConfig.temperature,
          maxOutputTokens: finalConfig.maxTokens,
          topP: finalConfig.topP,
        },
      });

      // Prepend system prompt to the user message if exists
      const userMessage = systemMessage
        ? `${systemMessage.content}\n\n${lastMessage.content}`
        : lastMessage.content;

      const result = await chat.sendMessage(userMessage);
      const response = result.response;

      const duration = Date.now() - startTime;

      // Check for safety blocks
      if (response.promptFeedback?.blockReason) {
        logger.warn({
          blockReason: response.promptFeedback.blockReason,
          msg: 'Gemini blocked response due to safety filters',
        });

        return {
          content:
            "I'm not able to discuss that topic as it may relate to medical or safety advice. Please consult a dive medical professional.",
          finishReason: 'SAFETY',
        };
      }

      const content = response.text();
      const finishReason = response.candidates?.[0]?.finishReason;

      const modelResponse: ModelResponse = {
        content,
        model: this.modelName,
        finishReason: finishReason || undefined,
        tokensUsed: response.usageMetadata?.totalTokenCount,
      };

      logger.info({
        model: modelResponse.model,
        tokensUsed: modelResponse.tokensUsed,
        finishReason: modelResponse.finishReason,
        durationMs: duration,
        msg: 'Gemini API call successful',
      });

      return modelResponse;
    } catch (error) {
      const duration = Date.now() - startTime;

      logger.error({
        error: error instanceof Error ? error.message : 'Unknown error',
        durationMs: duration,
        msg: 'Gemini API call failed',
      });

      if (error instanceof Error) {
        throw new Error(`Gemini API error: ${error.message}`);
      }
      throw new Error('Gemini API error: Unknown error occurred');
    }
  }
}
