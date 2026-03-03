# Content Ingestion Guide

**Last Updated:** 2026-03-03  
**Applies To:** `content/source` + `apps/api/scripts/ingest_content.py`

## Scope

This guide covers markdown ingestion for RAG embeddings only.

- Source files: `content/source/**/*.md`
- Target table: `content_embeddings`
- Entry commands: `pnpm content:validate`, `pnpm content:ingest`, `pnpm content:clear`

For structured destination/site table changes, see [Neon Database Update Guide](./neon-database-update-guide.md).

## Prerequisites

- Root virtualenv created with Python 3.11: `.venv`
- API package installed: `.venv/bin/pip install -e apps/api/`
- `.env.local` configured (`DATABASE_URL`, `GEMINI_API_KEY`)
- pgvector enabled in the database

## Content Layout

```text
content/
├── source/
│   ├── certifications/
│   ├── destinations/
│   └── safety/
├── generated/
└── templates/
```

Use `content/source` as the authoring source of truth.

## Standard Workflow

### 1. Validate markdown

```bash
pnpm content:validate
```

### 2. Run incremental ingestion (default)

```bash
pnpm content:ingest
```

### 3. Verify database update

```bash
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM content_embeddings;"
psql "$DATABASE_URL" -c "SELECT content_path, created_at FROM content_embeddings ORDER BY created_at DESC LIMIT 10;"
```

## Common Operations

### Full re-ingestion

```bash
pnpm content:ingest -- --full
```

### Ingest one content domain

```bash
pnpm content:ingest -- --content-dir ../../content/source/destinations
```

### Ingest with dry-run

```bash
pnpm content:ingest -- --dry-run
```

### Clear all embeddings

```bash
pnpm content:clear
```

### Clear only a subset

```bash
pnpm content:clear -- --pattern "destinations/*"
```

## Direct Python Commands (Optional)

Use these when you need explicit CLI control from `apps/api`:

```bash
cd apps/api
../../.venv/bin/python -m scripts.validate_content --content-dir ../../content/source
../../.venv/bin/python -m scripts.ingest_content --content-dir ../../content/source --full
../../.venv/bin/python -m scripts.clear_embeddings --pattern "certifications/*"
```

## Verification and Tests

```bash
# API-side ingestion tests
.venv/bin/python -m pytest apps/api/tests/unit/scripts -q
.venv/bin/python -m pytest apps/api/tests/integration/scripts -q

# RAG service integration tests
.venv/bin/python -m pytest apps/api/tests/integration/services/test_rag_integration.py -q
```

## Troubleshooting

### Command uses wrong Python version

Symptom: type-hint errors like `int | None` unsupported.

Fix:

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e apps/api/
```

### No new embeddings after content changes

- Confirm files were updated under `content/source`, not `content/generated`.
- Re-run full ingestion:

```bash
pnpm content:ingest -- --full
```

### Validation fails on missing frontmatter

Inspect file and add required fields (`title`, `description`) in frontmatter.
