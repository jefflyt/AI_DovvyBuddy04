import { pgTable, uuid, jsonb, timestamp } from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';

export const sessions = pgTable('sessions', {
  id: uuid('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  diverProfile: jsonb('diver_profile'), // { agency, level, dive_count, etc. }
  conversationHistory: jsonb('conversation_history').notNull().default(sql`'[]'::jsonb`), // Array of { role, content, timestamp }
  createdAt: timestamp('created_at', { withTimezone: true })
    .notNull()
    .default(sql`now()`),
  expiresAt: timestamp('expires_at', { withTimezone: true })
    .notNull()
    .default(sql`now() + interval '24 hours'`),
});

export type Session = typeof sessions.$inferSelect;
export type NewSession = typeof sessions.$inferInsert;
