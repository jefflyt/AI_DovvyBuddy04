# src/db

Database schema, migrations, and query functions for DovvyBuddy.

## Database: Postgres with pgvector

We use **Postgres** (Neon or Supabase) with the **pgvector** extension for:

- Structured data (destinations, dive sites, leads, sessions)
- Vector embeddings for RAG retrieval

## Contents (to be added in PR1)

- **schema.sql** — Initial database schema (destinations, dive_sites, leads, sessions, pgvector setup)
- **migrations/** — Migration scripts (future)
- **queries/** — Typed query functions using a Postgres client
- **seed.ts** — Seed script for initial data

## Schema Overview (planned)

### Tables

- `destinations` — Dive destinations (V1: 1 destination)
- `dive_sites` — Dive sites with certification requirements and difficulty
- `leads` — Captured leads for partner shops/schools
- `sessions` — Guest session storage (24h lifetime)
- `content_embeddings` — Vector embeddings for RAG (optional, if using pgvector for retrieval)

## Setup (for future PRs)

1. Provision a Postgres database with pgvector extension
2. Set `DATABASE_URL` in `.env.local`
3. Run migrations: `pnpm db:migrate`
4. Seed data: `pnpm db:seed`
