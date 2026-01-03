```markdown
# Technology Stack

This document summarizes the primary technologies and libraries used across the DovvyBuddy project. Use this as a quick reference when onboarding or when making changes that touch infra, APIs, or ML components.

## Frontend
- Framework: `Next.js` (React)
- Language: `TypeScript`
- Key files: `package.json`, `src/`, `next.config.js`
- UI libs: React 18

## Primary Backend (TypeScript)
- Runtime: Node.js (>=20)
- Framework: Next.js serverless API routes
- LLM integration: client code and model-provider in `src/lib/model-provider`
- RAG integration: `src/lib/rag`, retrieval helpers
- Key files: `package.json`, `pnpm-lock.yaml`, `drizzle.config.ts`, `src/lib/`

## Python Backend (Python-first services)
- Framework: FastAPI (async)
- ORM: SQLAlchemy 2.0 (async) with Alembic for migrations
- LLM & Embeddings services: custom `app/services/` implementations
- Packaging: `pyproject.toml` (setuptools), virtualenv recommended
- Key files: `backend/app/`, `backend/pyproject.toml`, `backend/openapi.yaml`

## Datastore / Search
- Primary DB: PostgreSQL (Neon / managed Postgres) with `pgvector` extension for vector search
- TypeScript ORM: Drizzle (Drizzle schema used as source-of-truth)
- Python ORM: SQLAlchemy models mirror Drizzle schema (see `backend/app/db/models`)
- Vector retrieval: `pgvector` + cosine/similarity queries

## LLM & Embeddings Providers
- Gemini (Google) for embeddings and LLMs — recommended model: `gemini-2.0-flash`
  - Embeddings model: `text-embedding-004` (768 dimensions)
- Groq used for development/testing (`llama-3.3-70b` family shown in Python config)
- ADK / Genkit integration lives under `src/lib/agent/` for multi-agent orchestration
- Key env vars: see `.env.example` and `backend/.env.example` (`GEMINI_API_KEY`, `GROQ_API_KEY`, `ENABLE_ADK`, `ADK_MODEL`, etc.)

## RAG Pipeline
- Chunking: markdown-aware chunker (`backend/app/services/rag/chunker.py`)
- Retriever: vector search with `pgvector` (`backend/app/services/rag/retriever.py`)
- Orchestration: TypeScript orchestrator (`src/lib/orchestration/*`) and Python RAG pipeline (`backend/app/services/rag/pipeline.py`)

## Tooling & Dev
- Package managers: `pnpm` (frontend/TS), Python virtualenv / pip + `pyproject.toml`
- Linters & formatters: `ruff` (Python), `prettier`/`eslint` (JS/TS)
- Testing: `vitest` (TS), `pytest` (Python)
- Type checking: `tsc` for TS, `mypy` (deferred) for Python

## CI / CD & Infra
- CI: standard `pnpm typecheck && pnpm lint && pnpm test && pnpm build` pipeline for JS; Python CI templates present in `backend/` docs
- Hosting: Vercel (Next.js) for frontend; Python services can be deployed separately (FastAPI on Uvicorn / container)
- Secrets: GCP service account JSON and API keys stored as env vars in deployment platform

## Observability & Logging
- Logging: `pino` (TS), Python uses standard `logging` (config in `backend/app/core`)
- Telemetry: optional Cloud Trace / ADK tracing (configured via env vars)

## Where to find more details
- Project-wide instructions and LLM model standards: `/.github/instructions/Global Instructions.instructions.md`
- Architecture and PR plans: `docs/plans/` (PR3, PR3.1, PR3.2*, etc.)
- Service-level docs: `backend/README_SERVICES.md` and `backend/VERIFICATION_SUMMARY_PR3.2b.md`

## Notes and Guidelines
- Follow the repository's instruction docs when adding or changing provider code (Gemini usage locked to `gemini-2.0-flash`).
- Keep Drizzle as the schema source-of-truth; mirror schema changes into Python SQLAlchemy models and Alembic as needed.
- Use the `.env.example` templates to add new environment variables and document them in `docs/` when they are required for new features.

---
_Generated: 2026-01-03 — summary of project technology stack._

```
