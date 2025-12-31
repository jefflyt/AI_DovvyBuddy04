import { pgTable, uuid, text, jsonb, timestamp, vector } from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';

export const contentEmbeddings = pgTable('content_embeddings', {
  id: uuid('id')
    .primaryKey()
    .default(sql`gen_random_uuid()`),
  contentPath: text('content_path').notNull(), // e.g., "certifications/padi/open-water.md"
  chunkText: text('chunk_text').notNull(),
  embedding: vector('embedding', { dimensions: 768 }).notNull(), // Gemini text-embedding-004 uses 768 dimensions
  metadata: jsonb('metadata').notNull().default(sql`'{}'::jsonb`), // { section, tags, source, etc. }
  createdAt: timestamp('created_at', { withTimezone: true })
    .notNull()
    .default(sql`now()`),
});

export type ContentEmbedding = typeof contentEmbeddings.$inferSelect;
export type NewContentEmbedding = typeof contentEmbeddings.$inferInsert;
