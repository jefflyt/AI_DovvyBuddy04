import { pgTable, uuid, text, jsonb, timestamp } from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';

export const leads = pgTable('leads', {
  id: uuid('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  type: text('type').notNull(), // "training" | "trip"
  diverProfile: jsonb('diver_profile').notNull(), // { agency, level, dive_count, etc. }
  requestDetails: jsonb('request_details').notNull(), // { location, dates, interests, etc. }
  createdAt: timestamp('created_at', { withTimezone: true })
    .notNull()
    .default(sql`now()`),
});

export type Lead = typeof leads.$inferSelect;
export type NewLead = typeof leads.$inferInsert;
