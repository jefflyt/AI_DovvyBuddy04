import {
  pgTable,
  uuid,
  text,
  integer,
  boolean,
  timestamp,
} from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';
import { destinations } from './destinations';

export const diveSites = pgTable('dive_sites', {
  id: uuid('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  destinationId: uuid('destination_id')
    .notNull()
    .references(() => destinations.id, { onDelete: 'cascade' }),
  name: text('name').notNull(),
  description: text('description'),
  minCertificationLevel: text('min_certification_level'), // e.g., "OW", "AOW", "Rescue"
  minLoggedDives: integer('min_logged_dives'),
  difficultyBand: text('difficulty_band'), // e.g., "beginner", "intermediate", "advanced"
  accessType: text('access_type'), // e.g., "shore", "boat"
  dataQuality: text('data_quality'), // e.g., "verified", "compiled", "anecdotal"
  isActive: boolean('is_active').notNull().default(true),
  createdAt: timestamp('created_at', { withTimezone: true })
    .notNull()
    .default(sql`now()`),
});

export type DiveSite = typeof diveSites.$inferSelect;
export type NewDiveSite = typeof diveSites.$inferInsert;
