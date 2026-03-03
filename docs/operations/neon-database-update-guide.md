# Neon Database Update Guide

**Last Updated:** 2026-03-03  
**Applies To:** Neon PostgreSQL operations for DovvyBuddy

## Overview

This guide covers safe database updates in the current monorepo setup.

- Schema and runtime code: `apps/api`
- Markdown ingestion source: `content/source`
- Embedding refresh commands: root `pnpm content:*`

## Before You Change Data

1. Confirm `.env.local` contains the correct `DATABASE_URL`.
2. Ensure root virtualenv is active and API package is installed.
3. Check current migration state:

```bash
cd apps/api && ../../.venv/bin/alembic current
```

## Migration Workflow (Schema Changes)

### Create migration

```bash
cd apps/api && ../../.venv/bin/alembic revision --autogenerate -m "describe schema change"
```

### Apply migration

```bash
cd apps/api && ../../.venv/bin/alembic upgrade head
```

### Roll back one step (if needed)

```bash
cd apps/api && ../../.venv/bin/alembic downgrade -1
```

## Structured Data Updates

When updating relational tables like `destinations` and `dive_sites`, use SQL or API/repository paths directly.

### Inspect current records

```bash
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM destinations;"
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM dive_sites;"
```

### Apply controlled SQL updates

```bash
# Example pattern only: use explicit IDs/filters in your change script
psql "$DATABASE_URL" -c "BEGIN; /* update statements */ COMMIT;"
```

### Verify after update

```bash
psql "$DATABASE_URL" -c "SELECT id, name, country FROM destinations ORDER BY created_at DESC LIMIT 20;"
psql "$DATABASE_URL" -c "SELECT dive_site_id, name, destination_id FROM dive_sites ORDER BY created_at DESC LIMIT 20;"
```

## Content Embedding Updates

Changes under `content/source` are not reflected in RAG until you ingest.

```bash
# Validate source markdown
pnpm content:validate

# Incremental ingestion
pnpm content:ingest

# Full rebuild when chunking/model settings changed
pnpm content:ingest -- --full
```

## Backup and Safety

### Quick backup of embeddings table

```bash
psql "$DATABASE_URL" -c "CREATE TABLE IF NOT EXISTS content_embeddings_backup_$(date +%Y%m%d_%H%M%S) AS SELECT * FROM content_embeddings;"
```

### Check recent writes

```bash
psql "$DATABASE_URL" -c "SELECT content_path, created_at FROM content_embeddings ORDER BY created_at DESC LIMIT 20;"
```

## Troubleshooting

### `pnpm content:ingest` fails due Python mismatch

Rebuild the root `.venv` with Python 3.11 and reinstall:

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e apps/api/
```

### Data appears stale in retrieval

Rebuild embeddings:

```bash
pnpm content:clear -- --force
pnpm content:ingest -- --full
```

### Migration conflict

Check head/current mismatch:

```bash
cd apps/api && ../../.venv/bin/alembic heads
cd apps/api && ../../.venv/bin/alembic current
```

## Related Docs

- [Content Ingestion Guide](./content-ingestion-guide.md)
- [Developer Workflow Guide](./developer-workflow.md)
- [Architecture Specification](../architecture/specification.md)
