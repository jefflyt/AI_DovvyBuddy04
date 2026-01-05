# DovvyBuddy — Technology & TDD — V1.0

**Document Version:** V1.0  
**Last Updated:** January 3, 2026  
**Status:** Reference

---

## 1. Overview

This document is the Technology & Technical Design Decisions (TDD) reference for DovvyBuddy. It summarizes the primary technologies, integration points, and operational guidance used across the project. Use this when onboarding, planning infra changes, or updating model/provider code.

## 2. Frontend

- **Framework:** `Next.js` (React)
- **Language:** `TypeScript`
- **Key files:** `package.json`, `src/`, `next.config.js`
- **UI:** React 18

## 3. Primary Backend (TypeScript)

- **Runtime:** Node.js (>=20)
- **Pattern:** Next.js serverless API routes (server and edge handlers where applicable)
- **LLM integration:** `src/lib/model-provider` implements a `ModelProvider` switch (`LLM_PROVIDER=groq|gemini`)
- **RAG helpers:** `src/lib/rag` contains retrieval client helpers and orchestration bindings
- **Key files:** `package.json`, `pnpm-lock.yaml`, `drizzle.config.ts`, `src/lib/`

## 4. Python Backend (FastAPI services)

- **Framework:** FastAPI (async)
- **ORM / Migrations:** SQLAlchemy 2.0 (async) + Alembic
- **Services:** embeddings, LLM wrappers, RAG pipeline components under `src/backend/app/services/`
- **Packaging:** `pyproject.toml` (setuptools); prefer virtualenv or poetry for local dev
- **Key files:** `src/backend/app/`, `src/backend/pyproject.toml`, `src/backend/openapi.yaml`

## 5. Datastore & Vector Search

- **Primary DB:** PostgreSQL (Neon / managed Postgres) with `pgvector` extension for vector search
- **TypeScript schema:** Drizzle is the source-of-truth for TS-side schema
- **Python models:** SQLAlchemy models mirror Drizzle schema; migrations via Alembic
- **Vector retrieval:** `pgvector` + similarity queries (cosine/dot) for nearest-neighbor lookup

## 6. LLM & Embeddings Providers

- **Production target:** Google Gemini — model: `gemini-2.0-flash` (generation + preferred embeddings provider)
- **Embeddings model:** `text-embedding-004` (768 dims)
- **Development/testing:** Groq used for fast dev iterations; agent switch keeps interfaces consistent
- **Orchestration:** ADK / Genkit integration code lives under `src/lib/agent/` for multi-agent flows
- **Env vars (examples):** `GEMINI_API_KEY`, `GROQ_API_KEY`, `ENABLE_ADK`, `ADK_MODEL`

## 7. RAG Pipeline

- **Chunking:** markdown-aware chunker in Python RAG services (`src/backend/app/services/rag/chunker.py`)
- **Retriever:** vector search using `pgvector` (`src/backend/app/services/rag/retriever.py`)
- **Indexing:** ingest → chunk → embed → store vectors in Postgres (or object-storage-backed index if chosen)
- **Orchestration:** TypeScript orchestrator (`src/lib/orchestration/*`) coordinates retrieval + safety + model calls

## 8. Tooling & Developer Experience

- **Package managers:** `pnpm` (JS/TS), Python virtualenv / pip (or poetry)
- **Linters/formatters:** `prettier` + `eslint` (TS/JS), `ruff` (Python)
- **Testing:** `vitest` (TS), `pytest` (Python)
- **Type checking:** `tsc` (TS), `mypy` (Python — optional)

## 9. CI / CD & Hosting

- **CI checks (recommended):** `pnpm typecheck && pnpm lint && pnpm test && pnpm build` for JS; Python CI runs include lint & tests
- **Hosting:** Vercel for Next.js frontend; FastAPI services deployed to Cloud Run or container platform
- **Secrets:** Store service account JSON and API keys securely in deployment platform env vars

## 10. Observability & Logging

- **TS logging:** `pino`
- **Python logging:** stdlib `logging` configured in `src/backend/app/core`
- **Telemetry:** optional Cloud Trace / ADK tracing (enabled via env)

## 11. Where to Find More Details

- **Project instructions & LLM standards:** `/.github/instructions/Global Instructions.instructions.md`
- **Architecture & PR plans:** `docs/plans/` (see PR3, PR3.1, PR3.2*)
- **Service docs & verification:** `src/backend/README_SERVICES.md`, `src/backend/VERIFICATION_SUMMARY_PR3.2b.md`

## 12. Notes & Guidelines

- Keep Drizzle as the canonical DB schema source-of-truth; mirror schema updates into Python SQLAlchemy models and Alembic migrations.
- All model calls should use the `ModelProvider` abstraction so providers can be swapped via env vars.
- Prefer `gemini-2.0-flash` for production LLM usage and `text-embedding-004` for embeddings to ensure retrieval/generation alignment.
- When adding provider env vars, update `.env.example` and document new variables in `docs/`.

## 13. Changelog

- **V1.0 (2026-01-03):** Created TDD/Technology reference document; consolidated previous tech-stack notes into PSD-style format.

---

_Generated: 2026-01-03 — DovvyBuddy Technology & TDD V1.0_
