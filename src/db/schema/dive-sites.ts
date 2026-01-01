import {
  pgTable,
  uuid,
  text,
  integer,
  boolean,
  timestamp,
  real,
  json,
} from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';
import { destinations } from './destinations';

export const diveSites = pgTable('dive_sites', {
  id: uuid('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  diveSiteId: text('dive_site_id').notNull().unique(), // e.g., "tioman_renggis_island"
  destinationId: uuid('destination_id')
    .notNull()
    .references(() => destinations.id, { onDelete: 'cascade' }),
  name: text('name').notNull(),
  description: text('description'),
  minCertificationLevel: text('min_certification_level'), // e.g., "OW", "AOW", "Rescue"
  minLoggedDives: integer('min_logged_dives'),
  difficultyRating: integer('difficulty_rating'), // 1-5 scale
  difficultyBand: text('difficulty_band'), // e.g., "beginner", "intermediate", "advanced"
  depthMin: real('depth_min_m'), // minimum depth in meters
  depthMax: real('depth_max_m'), // maximum depth in meters
  accessType: text('access_type'), // e.g., "shore", "boat"
  dataQuality: text('data_quality'), // e.g., "verified", "compiled", "anecdotal"
  tags: json('tags').$type<string[]>(), // array of tags
  isActive: boolean('is_active').notNull().default(true),
  lastUpdated: timestamp('last_updated', { withTimezone: true }), // content last updated date
  createdAt: timestamp('created_at', { withTimezone: true })
    .notNull()
    .default(sql`now()`),
  updatedAt: timestamp('updated_at', { withTimezone: true })
    .notNull()
    .default(sql`now()`),
});

export type DiveSite = typeof diveSites.$inferSelect;
export type NewDiveSite = typeof diveSites.$inferInsert;
