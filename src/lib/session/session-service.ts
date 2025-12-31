/**
 * Session Service
 * Handles CRUD operations for user sessions with conversation history
 */

import { eq } from 'drizzle-orm';
import { v4 as uuidv4 } from 'uuid';
import pino from 'pino';
import { db } from '@/db/client';
import { sessions } from '@/db/schema/sessions';
import type {
  SessionData,
  CreateSessionInput,
  UpdateSessionInput,
  SessionMessage,
  DiverProfile,
} from './types';

const logger = pino({ name: 'session-service' });

/**
 * Get session duration in hours from environment or default to 24
 */
function getSessionDurationHours(): number {
  const hours = process.env.MAX_SESSION_DURATION_HOURS;
  return hours ? parseInt(hours, 10) : 24;
}

/**
 * Create a new session
 * @param input - Optional diver profile data
 * @returns SessionData with new session ID and empty conversation history
 */
export async function createSession(input?: CreateSessionInput): Promise<SessionData> {
  const sessionId = uuidv4();
  const now = new Date();
  const durationHours = getSessionDurationHours();
  const expiresAt = new Date(now.getTime() + durationHours * 60 * 60 * 1000);

  logger.info({
    sessionId,
    durationHours,
    msg: 'Creating new session',
  });

  try {
    const [session] = await db
      .insert(sessions)
      .values({
        id: sessionId,
        diverProfile: input?.diverProfile || {},
        conversationHistory: [],
        expiresAt,
      })
      .returning();

    const sessionData: SessionData = {
      id: session.id,
      conversationHistory: (session.conversationHistory as SessionMessage[]) || [],
      diverProfile: (session.diverProfile as DiverProfile) || {},
      createdAt: session.createdAt,
      expiresAt: session.expiresAt,
    };

    logger.info({
      sessionId: sessionData.id,
      expiresAt: sessionData.expiresAt,
      msg: 'Session created successfully',
    });

    return sessionData;
  } catch (error) {
    logger.error({
      sessionId,
      error: error instanceof Error ? error.message : 'Unknown error',
      msg: 'Failed to create session',
    });
    throw new Error('Failed to create session');
  }
}

/**
 * Retrieve an existing session by ID
 * @param sessionId - UUID of the session
 * @returns SessionData if found and not expired, null otherwise
 */
export async function getSession(sessionId: string): Promise<SessionData | null> {
  // Validate UUID format
  const uuidRegex =
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  if (!uuidRegex.test(sessionId)) {
    logger.warn({ sessionId, msg: 'Invalid session ID format' });
    return null;
  }

  try {
    const [session] = await db
      .select()
      .from(sessions)
      .where(eq(sessions.id, sessionId))
      .limit(1);

    if (!session) {
      logger.debug({ sessionId, msg: 'Session not found' });
      return null;
    }

    // Check if session is expired
    if (session.expiresAt < new Date()) {
      logger.info({ sessionId, expiresAt: session.expiresAt, msg: 'Session expired' });
      return null;
    }

    const sessionData: SessionData = {
      id: session.id,
      conversationHistory: (session.conversationHistory as SessionMessage[]) || [],
      diverProfile: (session.diverProfile as DiverProfile) || {},
      createdAt: session.createdAt,
      expiresAt: session.expiresAt,
    };

    logger.debug({
      sessionId: sessionData.id,
      messageCount: sessionData.conversationHistory.length,
      msg: 'Session retrieved',
    });

    return sessionData;
  } catch (error) {
    logger.error({
      sessionId,
      error: error instanceof Error ? error.message : 'Unknown error',
      msg: 'Failed to retrieve session',
    });
    throw new Error('Failed to retrieve session');
  }
}

/**
 * Update session conversation history with new user and assistant messages
 * @param sessionId - UUID of the session
 * @param input - User message and assistant response to append
 */
export async function updateSessionHistory(
  sessionId: string,
  input: UpdateSessionInput
): Promise<void> {
  const timestamp = new Date().toISOString();

  try {
    // Get current session to append to history
    const session = await getSession(sessionId);
    if (!session) {
      throw new Error('Session not found or expired');
    }

    // Append new messages to history
    const newHistory: SessionMessage[] = [
      ...session.conversationHistory,
      {
        role: 'user',
        content: input.userMessage,
        timestamp,
      },
      {
        role: 'assistant',
        content: input.assistantMessage,
        timestamp,
      },
    ];

    // Implement history trimming to prevent JSONB bloat
    // Keep last 100 messages (50 exchanges)
    const maxMessages = 100;
    const trimmedHistory =
      newHistory.length > maxMessages
        ? newHistory.slice(newHistory.length - maxMessages)
        : newHistory;

    await db
      .update(sessions)
      .set({
        conversationHistory: trimmedHistory,
      })
      .where(eq(sessions.id, sessionId));

    logger.info({
      sessionId,
      newMessageCount: 2,
      totalMessages: trimmedHistory.length,
      msg: 'Session history updated',
    });
  } catch (error) {
    logger.error({
      sessionId,
      error: error instanceof Error ? error.message : 'Unknown error',
      msg: 'Failed to update session history',
    });
    throw new Error('Failed to update session history');
  }
}

/**
 * Expire a session immediately
 * Useful for explicit session termination (e.g., "New Chat" button)
 * @param sessionId - UUID of the session
 */
export async function expireSession(sessionId: string): Promise<void> {
  try {
    await db
      .update(sessions)
      .set({
        expiresAt: new Date(),
      })
      .where(eq(sessions.id, sessionId));

    logger.info({ sessionId, msg: 'Session expired' });
  } catch (error) {
    logger.error({
      sessionId,
      error: error instanceof Error ? error.message : 'Unknown error',
      msg: 'Failed to expire session',
    });
    throw new Error('Failed to expire session');
  }
}

/**
 * Check if a session is expired
 * @param session - SessionData to check
 * @returns true if expired, false otherwise
 */
export function isSessionExpired(session: SessionData): boolean {
  return session.expiresAt < new Date();
}

/**
 * Update diver profile for a session
 * @param sessionId - UUID of the session
 * @param profile - Updated diver profile data
 */
export async function updateDiverProfile(
  sessionId: string,
  profile: Partial<DiverProfile>
): Promise<void> {
  try {
    const session = await getSession(sessionId);
    if (!session) {
      throw new Error('Session not found or expired');
    }

    const updatedProfile = {
      ...session.diverProfile,
      ...profile,
    };

    await db
      .update(sessions)
      .set({
        diverProfile: updatedProfile,
      })
      .where(eq(sessions.id, sessionId));

    logger.info({
      sessionId,
      msg: 'Diver profile updated',
    });
  } catch (error) {
    logger.error({
      sessionId,
      error: error instanceof Error ? error.message : 'Unknown error',
      msg: 'Failed to update diver profile',
    });
    throw new Error('Failed to update diver profile');
  }
}
