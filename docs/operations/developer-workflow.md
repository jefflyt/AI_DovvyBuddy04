# Developer Workflow Guide

**Last Updated:** 2026-03-03  
**Status:** Active

## Overview

This guide documents the day-to-day workflow for the current monorepo layout:

- Web app: `apps/web`
- API app: `apps/api`
- Content source: `content/source`
- Shared tooling: `tooling`

## One-Time Setup

```bash
# 1) Install Node dependencies at repo root
pnpm install

# 2) Create Python 3.11 virtualenv at repo root
python3.11 -m venv .venv

# 3) Install API package into the root virtualenv
.venv/bin/pip install -e apps/api/

# 4) Configure environment
cp .env.example .env.local
# Edit .env.local with DATABASE_URL, GEMINI_API_KEY, and related settings
```

## Local Development

### Start API

```bash
.venv/bin/uvicorn app.main:app --reload --app-dir apps/api --port 8000
```

### Start Web

```bash
pnpm dev
```

## Content Workflow

### Validate Content

```bash
pnpm content:validate
```

### Ingest Content

```bash
# Incremental (default)
pnpm content:ingest

# Full re-ingestion
pnpm content:ingest -- --full

# Ingest only one domain folder
pnpm content:ingest -- --content-dir ../../content/source/destinations
```

### Clear Embeddings

```bash
pnpm content:clear

# Non-interactive
pnpm content:clear -- --force
```

## Testing and Quality

### Web Checks

```bash
pnpm typecheck
pnpm lint
pnpm test
pnpm build
```

### API Checks

```bash
.venv/bin/python -m pytest apps/api/tests/unit -q
.venv/bin/python -m pytest apps/api/tests/integration -q
```

### Cross-App E2E

```bash
pnpm test:e2e
```

## Database Migrations (Alembic)

```bash
# Apply migrations
cd apps/api && ../../.venv/bin/alembic upgrade head

# Create migration
cd apps/api && ../../.venv/bin/alembic revision --autogenerate -m "describe change"

# Roll back one migration
cd apps/api && ../../.venv/bin/alembic downgrade -1
```

## Agent Scan Workflow

```bash
# 1) preflight for task scope
pnpm agent:preflight -- docs --ack I_READ_CONTEXT

# 2) scoped search through wrapper
pnpm agent:scan -- -n "orchestrator" apps/api/app
```

Supported scopes: `backend`, `frontend`, `content`, `docs`.

## Troubleshooting

### `pnpm content:*` fails with Python typing errors

Use Python 3.11 in the root `.venv`, then reinstall:

```bash
python3.11 -m venv .venv
.venv/bin/pip install -e apps/api/
```

### API import errors in tests

Run tests with the root virtualenv:

```bash
.venv/bin/python -m pytest apps/api/tests/unit -q
```

### Validate current structure

```bash
find apps content docs tooling -maxdepth 2 -type d | sort
```
