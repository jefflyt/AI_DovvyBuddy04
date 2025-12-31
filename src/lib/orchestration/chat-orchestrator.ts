/**
 * Chat Orchestrator
 * Main conversation flow: session management → RAG retrieval → prompt building → LLM call
 */

import pino from 'pino';
import { createModelProvider } from '@/lib/model-provider';
import type { ModelMessage } from '@/lib/model-provider';
import {
  createSession,
  getSession,
  updateSessionHistory,
  type SessionData,
  type SessionMessage,
} from '@/lib/session';
import {
  buildCertificationPrompt,
  buildTripPrompt,
  detectPromptMode,
  BASE_SYSTEM_PROMPT,
} from '@/lib/prompts';
import type { ChatRequest, ChatResponse, RetrievalResult } from './types';

const logger = pino({ name: 'chat-orchestrator' });

/**
 * Mock RAG retrieval function
 * TODO: Replace with real RAG integration when PR2 is complete
 * @param query - User's message to retrieve context for
 * @returns Mock retrieval result
 */
async function mockRetrieveContext(query: string): Promise<RetrievalResult> {
  // Simulate async retrieval
  await new Promise((resolve) => setTimeout(resolve, 10));

  logger.debug({ query, msg: 'Using mock RAG retrieval (PR2 not yet integrated)' });

  return {
    chunks: [],
  };
}

/**
 * Validate user message
 * @param message - User's input message
 * @throws Error if message is invalid
 */
function validateMessage(message: string): void {
  if (!message || typeof message !== 'string') {
    throw new Error('Message must be a non-empty string');
  }

  const trimmedMessage = message.trim();
  if (trimmedMessage.length === 0) {
    throw new Error('Message cannot be empty');
  }

  const maxLength = process.env.MAX_MESSAGE_LENGTH
    ? parseInt(process.env.MAX_MESSAGE_LENGTH, 10)
    : 2000;

  if (trimmedMessage.length > maxLength) {
    throw new Error(`Message exceeds maximum length of ${maxLength} characters`);
  }
}

/**
 * Build context string from retrieval results
 * @param retrieval - RAG retrieval results
 * @returns Formatted context string
 */
function buildContextString(retrieval: RetrievalResult): string | undefined {
  if (!retrieval.chunks || retrieval.chunks.length === 0) {
    return undefined;
  }

  const contextParts = retrieval.chunks.map((chunk, index) => {
    const source = chunk.metadata?.source || `Source ${index + 1}`;
    return `[${source}]\n${chunk.text}`;
  });

  return contextParts.join('\n\n---\n\n');
}

/**
 * Convert session messages to model messages format
 * @param sessionHistory - Conversation history from session
 * @returns Array of model messages
 */
function convertToModelMessages(sessionHistory: SessionMessage[]): ModelMessage[] {
  return sessionHistory.map((msg) => ({
    role: msg.role,
    content: msg.content,
  }));
}

/**
 * Main chat orchestration function
 * Handles the complete flow: session → retrieval → prompt → LLM → history update
 *
 * @param request - Chat request with optional session ID and user message
 * @returns Chat response with session ID and assistant message
 */
export async function orchestrateChat(request: ChatRequest): Promise<ChatResponse> {
  const startTime = Date.now();

  try {
    // Step 1: Validate input
    validateMessage(request.message);

    logger.info({
      sessionId: request.sessionId,
      messageLength: request.message.length,
      msg: 'Starting chat orchestration',
    });

    // Step 2: Get or create session
    let session: SessionData;

    if (request.sessionId) {
      const existingSession = await getSession(request.sessionId);

      if (existingSession) {
        session = existingSession;
        logger.debug({
          sessionId: session.id,
          messageCount: session.conversationHistory.length,
          msg: 'Using existing session',
        });
      } else {
        // Session expired or not found, create new one
        session = await createSession();
        logger.info({
          sessionId: session.id,
          msg: 'Previous session not found, created new session',
        });
      }
    } else {
      // No session ID provided, create new session
      session = await createSession();
      logger.info({
        sessionId: session.id,
        msg: 'Created new session',
      });
    }

    // Step 3: Retrieve relevant context (RAG)
    const retrievalResult = await mockRetrieveContext(request.message);
    const contextString = buildContextString(retrievalResult);

    logger.debug({
      sessionId: session.id,
      contextChunks: retrievalResult.chunks.length,
      msg: 'Retrieved context',
    });

    // Step 4: Determine prompt mode and build system prompt
    const conversationHistory = convertToModelMessages(session.conversationHistory);
    const promptMode = detectPromptMode(request.message, conversationHistory);

    let systemPrompt: string;
    switch (promptMode) {
      case 'certification':
        systemPrompt = buildCertificationPrompt(contextString);
        break;
      case 'trip':
        systemPrompt = buildTripPrompt(contextString);
        break;
      default:
        systemPrompt = contextString
          ? `${BASE_SYSTEM_PROMPT}\n\n## Reference Information\n\n${contextString}`
          : BASE_SYSTEM_PROMPT;
    }

    logger.debug({
      sessionId: session.id,
      promptMode,
      hasContext: !!contextString,
      msg: 'Built system prompt',
    });

    // Step 5: Build messages array for LLM
    const messages: ModelMessage[] = [
      { role: 'system', content: systemPrompt },
      ...conversationHistory,
      { role: 'user', content: request.message },
    ];

    // Step 6: Call LLM provider
    const provider = createModelProvider();
    const llmResponse = await provider.generateResponse(messages);

    logger.info({
      sessionId: session.id,
      tokensUsed: llmResponse.tokensUsed,
      model: llmResponse.model,
      msg: 'LLM response received',
    });

    // Step 7: Update session history
    await updateSessionHistory(session.id, {
      userMessage: request.message,
      assistantMessage: llmResponse.content,
    });

    logger.debug({
      sessionId: session.id,
      msg: 'Session history updated',
    });

    // Step 8: Build and return response
    const duration = Date.now() - startTime;

    logger.info({
      sessionId: session.id,
      durationMs: duration,
      msg: 'Chat orchestration complete',
    });

    return {
      sessionId: session.id,
      response: llmResponse.content,
      metadata: {
        tokensUsed: llmResponse.tokensUsed,
        contextChunks: retrievalResult.chunks.length,
        model: llmResponse.model,
        promptMode,
      },
    };
  } catch (error) {
    const duration = Date.now() - startTime;

    logger.error({
      sessionId: request.sessionId,
      error: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined,
      durationMs: duration,
      msg: 'Chat orchestration failed',
    });

    throw error;
  }
}
