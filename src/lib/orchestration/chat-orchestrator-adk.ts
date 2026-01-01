/**
 * Multi-Agent Chat Orchestrator (ADK-based)
 * Coordinates specialized agents for improved response quality
 */

import pino from 'pino';
import { getAgent } from '@/lib/agent/agent-registry';
import {
  createSession,
  getSession,
  updateSessionHistory,
  type SessionData,
} from '@/lib/session';
import type { ChatRequest, ChatResponse } from './types';

const logger = pino({ name: 'chat-orchestrator-adk' });

const MAX_MESSAGE_LENGTH = process.env.MAX_MESSAGE_LENGTH
  ? parseInt(process.env.MAX_MESSAGE_LENGTH, 10)
  : 2000;

/**
 * Query routing logic
 * Determines which specialist agent to use based on message content
 */
function detectQueryType(
  message: string,
  history: Array<{ role: string; content: string }>
): 'certification' | 'trip' | 'general' {
  const m = message.toLowerCase();

  // Certification keywords
  if (
    m.match(
      /certif|padi|ssi|open water|advanced|rescue|divemaster|course|training|instructor/
    )
  ) {
    return 'certification';
  }

  // Trip keywords
  if (
    m.match(
      /trip|destination|where to dive|dive site|travel|vacation|recommend|visit|location/
    )
  ) {
    return 'trip';
  }

  // Check history for context
  const recentMessages = history
    .slice(-4)
    .map((h) => h.content.toLowerCase())
    .join(' ');
  if (recentMessages.includes('certif') || recentMessages.includes('course')) {
    return 'certification';
  }
  if (recentMessages.includes('trip') || recentMessages.includes('destination')) {
    return 'trip';
  }

  return 'general';
}

/**
 * Validate user message
 */
function validateMessage(message: string): void {
  if (!message || typeof message !== 'string') {
    throw new Error('Message must be a non-empty string');
  }

  const trimmedMessage = message.trim();
  if (trimmedMessage.length === 0) {
    throw new Error('Message cannot be empty');
  }

  if (trimmedMessage.length > MAX_MESSAGE_LENGTH) {
    throw new Error(`Message exceeds maximum length of ${MAX_MESSAGE_LENGTH} characters`);
  }
}

/**
 * Main chat orchestration function with multi-agent coordination
 */
export async function orchestrateChat(request: ChatRequest): Promise<ChatResponse> {
  const startTime = Date.now();
  const agentsUsed: string[] = [];
  const toolCalls: any[] = [];

  try {
    // Step 1: Validate input
    validateMessage(request.message);

    logger.info({
      sessionId: request.sessionId,
      messageLength: request.message.length,
      msg: 'Starting multi-agent orchestration',
    });

    // Step 2: Get or create session
    let session: SessionData;
    let sessionId = request.sessionId;

    if (sessionId) {
      const existingSession = await getSession(sessionId);
      if (existingSession) {
        session = existingSession;
      } else {
        session = await createSession();
        sessionId = session.id;
      }
    } else {
      session = await createSession();
      sessionId = session.id;
    }

    // Build message context
    const messages = [
      ...session.conversationHistory.map((m) => ({ role: m.role, content: m.content })),
      { role: 'user', content: request.message },
    ];

    // Step 3: Query routing
    const queryType = detectQueryType(request.message, session.conversationHistory);
    logger.info({ sessionId, queryType, msg: 'Query routed' });

    // Step 4: Retrieval (parallel with routing)
    const retrievalAgent = getAgent('retrieval');
    let context = '';

    try {
      const retrievalResult = await Promise.race([
        retrievalAgent.generate({ messages, sessionId }),
        new Promise<never>((_, reject) =>
          setTimeout(() => reject(new Error('Retrieval timeout')), 2000)
        ),
      ]);

      if (retrievalResult && retrievalResult.toolCalls) {
        const searchResults = retrievalResult.toolCalls.find(
          (tc) => tc.tool === 'search_knowledge_base'
        );
        if (searchResults?.result?.chunks) {
          context = searchResults.result.chunks.map((c: any) => c.text).join('\n\n');
        }
      }
      agentsUsed.push('retrieval');
    } catch (error) {
      logger.warn({ sessionId, error, msg: 'Retrieval failed, proceeding without context' });
    }

    // Step 5: Specialist response
    const specialistName =
      queryType === 'certification' ? 'certification' : queryType === 'trip' ? 'trip' : 'certification';
    const specialist = getAgent(specialistName);

    let response: string;
    try {
      const specialistResult = await Promise.race([
        specialist.generate({ messages, context, sessionId }),
        new Promise<never>((_, reject) =>
          setTimeout(() => reject(new Error('Specialist timeout')), 5000)
        ),
      ]);

      response = specialistResult.content;
      agentsUsed.push(specialistName);

      if (specialistResult.toolCalls) {
        toolCalls.push(
          ...specialistResult.toolCalls.map((tc) => ({
            agent: specialistName,
            tool: tc.tool,
            duration: 0,
          }))
        );
      }
    } catch (error) {
      logger.error({ sessionId, error, msg: 'Specialist failed' });
      response =
        "I'm having trouble processing that request. Please try rephrasing or ask something simpler.";
    }

    // Step 6: Safety validation
    const safetyAgent = getAgent('safety');
    try {
      const safetyResult = await safetyAgent.generate({
        messages: [
          { role: 'user', content: request.message },
          { role: 'assistant', content: response },
        ],
      });

      if (safetyResult.toolCalls) {
        const safetyCheck = safetyResult.toolCalls.find((tc) => tc.tool === 'validate_safety');
        if (safetyCheck?.result?.warnings?.length > 0) {
          const suggestions = safetyCheck?.result?.suggestions || [];
          if (suggestions.length > 0) {
            response += '\n\n' + suggestions.join(' ');
          }
        }
      }
      agentsUsed.push('safety');
    } catch (error) {
      logger.warn({ sessionId, error, msg: 'Safety validation failed' });
    }

    // Step 7: Update session history
    await updateSessionHistory(sessionId, {
      userMessage: request.message,
      assistantMessage: response,
    });

    const totalDuration = Date.now() - startTime;

    logger.info({
      sessionId,
      agentsUsed,
      queryType,
      totalDuration,
      msg: 'Multi-agent orchestration complete',
    });

    return {
      sessionId,
      response,
      metadata: {
        agentsUsed,
        toolCalls,
        queryType,
        totalDuration,
        contextChunks: context ? context.split('\n\n').length : 0,
      },
    };
  } catch (error) {
    const duration = Date.now() - startTime;

    logger.error({
      sessionId: request.sessionId,
      error: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined,
      durationMs: duration,
      msg: 'Multi-agent orchestration failed',
    });

    throw error;
  }
}
