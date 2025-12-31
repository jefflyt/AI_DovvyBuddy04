# Database Module

This module provides database access for DovvyBuddy using **Drizzle ORM** with **PostgreSQL** (Neon) and **pgvector** extension.

## Architecture

- **ORM:** Drizzle ORM (lightweight, TypeScript-first)
- **Database:** PostgreSQL 17 with pgvector extension (hosted on Neon)
- **Migrations:** Drizzle Kit
- **Connection:** Connection pooling via `postgres` driver

## Tables

### 1. `destinations`
Stores dive destinations (countries/regions).

**Columns:**
- `id` (uuid, PK) — Unique identifier
- `name` (text) — Destination name (e.g., "Cozumel")
- `country` (text) — Country name (e.g., "Mexico")
- `is_active` (boolean) — Whether destination is active (default: true)
- `created_at` (timestamptz) — Creation timestamp

### 2. `dive_sites`
Stores individual dive sites within destinations.

**Columns:**
- `id` (uuid, PK) — Unique identifier
- `destination_id` (uuid, FK → destinations.id) — Parent destination
- `name` (text) — Dive site name (e.g., "Palancar Reef")
- `description` (text, nullable) — Site description
- `min_certification_level` (text, nullable) — Minimum certification (e.g., "OW", "AOW")
- `min_logged_dives` (integer, nullable) — Minimum dive count required
- `difficulty_band` (text, nullable) — Difficulty (e.g., "beginner", "intermediate", "advanced")
- `access_type` (text, nullable) — Access method (e.g., "boat", "shore")
- `data_quality` (text, nullable) — Data quality indicator ("verified", "compiled", "anecdotal")
- `is_active` (boolean) — Whether site is active (default: true)
- `created_at` (timestamptz) — Creation timestamp

**Foreign Keys:**
- `destination_id` CASCADE on delete

### 3. `leads`
Stores lead capture submissions from chat interactions.

**Columns:**
- `id` (uuid, PK) — Unique identifier
- `type` (text) — Lead type (e.g., "trip", "certification", "general")
- `diver_profile` (jsonb) — Diver information (certification level, experience, etc.)
- `request_details` (jsonb) — Lead-specific details (destination, dates, etc.)
- `created_at` (timestamptz) — Creation timestamp

### 4. `sessions`
Stores chat session state for guest users.

**Columns:**
- `id` (uuid, PK) — Session identifier (also used as session ID in API)
- `diver_profile` (jsonb, nullable) — Collected diver profile information
- `conversation_history` (jsonb) — Array of conversation messages (default: `[]`)
- `created_at` (timestamptz) — Session creation time
- `expires_at` (timestamptz) — Session expiry time (default: 24 hours from creation)

**Notes:**
- Sessions expire after 24 hours (configurable via `SESSION_LIFETIME_HOURS`)
- Conversation history format: `[{ role: 'user' | 'assistant', content: string, timestamp: string }]`

### 5. `content_embeddings`
Stores RAG (Retrieval-Augmented Generation) content chunks with vector embeddings.

**Columns:**
- `id` (uuid, PK) — Unique identifier
- `content_path` (text) — Path to source file (e.g., `content/certifications/padi/open-water.md`)
- `chunk_text` (text) — Text content of the chunk
- `embedding` (vector(1536)) — Vector embedding (1536 dimensions for Gemini `text-embedding-004`)
- `metadata` (jsonb) — Chunk metadata (doc_type, title, tags, chunk_index, etc., default: `{}`)
- `created_at` (timestamptz) — Creation timestamp

**Indexes:**
- HNSW index on `embedding` for fast vector similarity search (created by PR2)

## Usage

### Importing the Database Client

```typescript
import { db } from '@/db/client'
import { destinations, diveSites, leads, sessions, contentEmbeddings } from '@/db/schema'
```

### Querying Data

```typescript
// Select all active destinations
const activeDestinations = await db
  .select()
  .from(destinations)
  .where(eq(destinations.isActive, true))

// Get dive sites for a destination
const cozumelSites = await db
  .select()
  .from(diveSites)
  .where(eq(diveSites.destinationId, destinationId))
```

### Inserting Data

```typescript
// Insert a new lead
const [lead] = await db
  .insert(leads)
  .values({
    type: 'trip',
    diverProfile: { certificationLevel: 'OW', loggedDives: 15 },
    requestDetails: { destination: 'Cozumel', dates: '2025-03-01 to 2025-03-07' },
  })
  .returning()
```

### Updating Data

```typescript
// Update session with new conversation message
await db
  .update(sessions)
  .set({
    conversationHistory: sql`conversation_history || ${JSON.stringify(newMessage)}::jsonb`,
  })
  .where(eq(sessions.id, sessionId))
```

## Database Scripts

All scripts are defined in `package.json` and can be run with `pnpm <script-name>`.

### Available Scripts

| Script | Command | Description |
|--------|---------|-------------|
| `db:generate` | `drizzle-kit generate` | Generate migration SQL from schema changes |
| `db:migrate` | `drizzle-kit migrate` | Apply migrations to database |
| `db:push` | `drizzle-kit push` | Push schema directly to database (bypass migrations) |
| `db:studio` | `drizzle-kit studio` | Launch Drizzle Studio (visual database browser) |
| `db:seed` | `tsx --env-file=.env.local src/db/seed.ts` | Seed database with initial data |

### Workflow

**1. Schema Changes:**
- Modify schema files in `src/db/schema/`
- Run `pnpm db:generate` to create migration SQL
- Review generated migration in `src/db/migrations/`
- Run `pnpm db:migrate` to apply migration

**2. Quick Prototyping (Development Only):**
- Modify schema files
- Run `pnpm db:push` to push changes directly (skips migrations)
- **Warning:** Use only in development; production requires proper migrations

**3. Seeding Data:**
- Run `pnpm db:seed` to populate initial data (1 destination, 8 dive sites)
- Script is idempotent (safe to run multiple times)

**4. Visual Database Browser:**
- Run `pnpm db:studio` to launch Drizzle Studio
- Browse tables, run queries, and inspect data visually
- Access at `https://local.drizzle.studio` (opens automatically)

## Environment Variables

Required environment variables (set in `.env.local`):

```env
# Database connection string (Neon Postgres)
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
```

**Note:** `.env.local` is gitignored. Use `.env.example` as a template.

## Connection Pooling

The `db` client uses connection pooling via the `postgres` driver:

- **Max connections:** Managed by Neon (varies by tier)
- **Idle timeout:** Default (driver manages)
- **SSL:** Required (`sslmode=require` in connection string)

For production, consider using Neon's connection pooler endpoint (already included in connection string).

## Migrations

Migrations are stored in `src/db/migrations/` and managed by Drizzle Kit.

**Migration Files:**
- `meta/_journal.json` — Migration history
- `0000_<description>.sql` — Initial schema
- `0001_<description>.sql` — Next migration (when schema changes)

**Best Practices:**
- Always review generated SQL before applying
- Test migrations on staging/development before production
- Never edit migration files manually after generation
- Use `db:generate` + `db:migrate` for production (not `db:push`)

## Type Safety

Drizzle ORM provides full TypeScript type inference:

```typescript
// TypeScript knows the shape of the result
const [destination] = await db
  .select()
  .from(destinations)
  .where(eq(destinations.name, 'Tioman Island'))
  .limit(1)

// destination.id is typed as string (uuid)
// destination.name is typed as string
// destination.isActive is typed as boolean
```

Schema types are automatically exported from `src/db/schema/index.ts`.

## Troubleshooting

### Issue: `DATABASE_URL environment variable is required`

**Cause:** `.env.local` missing or DATABASE_URL not set.

**Solution:**
1. Copy `.env.example` to `.env.local`
2. Set `DATABASE_URL` to your Neon connection string
3. Verify `.env.local` is in `.gitignore`

### Issue: `relation "destinations" does not exist`

**Cause:** Migrations not applied or schema not pushed.

**Solution:**
- Run `pnpm db:push` (development) or `pnpm db:migrate` (production)

### Issue: `type "vector" does not exist`

**Cause:** pgvector extension not enabled.

**Solution:**
- Connect to database via `psql` or Neon SQL Editor
- Run: `CREATE EXTENSION IF NOT EXISTS vector;`

### Issue: Seed script fails with duplicate key errors

**Cause:** Data already seeded (script is idempotent but may have changed).

**Solution:**
- Check seed script logic (should skip existing data)
- Or manually delete data: `DELETE FROM dive_sites; DELETE FROM destinations;`
- Then re-run `pnpm db:seed`

### Issue: Connection timeouts or SSL errors

**Cause:** Network issues or incorrect connection string.

**Solution:**
- Verify connection string includes `?sslmode=require`
- Check Neon project status (may be suspended on free tier)
- Test connection via `psql` directly

## Resources

- **Drizzle ORM Docs:** https://orm.drizzle.team/docs/overview
- **Drizzle Kit (Migrations):** https://orm.drizzle.team/kit-docs/overview
- **Neon Documentation:** https://neon.tech/docs
- **pgvector:** https://github.com/pgvector/pgvector
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

## Next Steps

After PR1 completion:

- **PR2:** Ingest content into `content_embeddings` table (RAG pipeline)
- **PR3:** Use `sessions` table for chat state management
- **PR4:** Implement lead capture logic using `leads` table
- **PR5:** Connect chat UI to backend APIs

---

**End of Database README**
