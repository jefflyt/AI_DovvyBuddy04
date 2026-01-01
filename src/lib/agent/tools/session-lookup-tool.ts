/**
 * Session Lookup Tool
 * Retrieves recent conversation history from session
 */

import type { Tool } from '../types';

export const sessionLookupTool: Tool = {
  name: 'get_conversation_history',
  description: 'Retrieve recent conversation history',
  parameters: {
    sessionId: { type: 'string' },
    last_n: { type: 'number', default: 10 },
  },
  async execute(params: { sessionId: string; last_n?: number }) {
    try {
      // Dynamic import to avoid circular dependencies
      const { getSession } = await import('@/lib/session/session-service');

      const session = await getSession(params.sessionId);
      if (!session) {
        return { history: [] };
      }

      const lastN = params.last_n || 10;
      const history = session.conversationHistory.slice(-lastN);

      return {
        history: history.map((m) => ({
          role: m.role,
          content: m.content,
          timestamp: m.timestamp,
        })),
      };
    } catch (error) {
      console.error('Session lookup failed:', error);
      return { history: [], error: 'Session unavailable' };
    }
  },
};

