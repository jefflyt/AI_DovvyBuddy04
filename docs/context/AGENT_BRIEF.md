# Agent Brief

Last updated: 2026-03-02

## Purpose

Use this file as the default pre-read before scanning code. It provides a compact map of DovvyBuddy so agents can stay within a small context window.

## System Snapshot

- Frontend: Next.js 14 (App Router), TypeScript (`src/`)
- Backend: FastAPI + SQLAlchemy async (`src/backend/`)
- Data: PostgreSQL + pgvector (Neon)
- LLM stack: Gemini (`gemini-2.5-flash-lite`) + `text-embedding-004`
- Core domains: diving certification guidance, trip planning, safety guidance, lead capture

## Guardrails

- Safety boundary: information support only, not medical/training instruction replacement.
- Keep responses grounded in curated content and explicit uncertainty when data is missing.
- Preserve session continuity rules (24-hour session model in current runtime docs).
- Do not assume a clean git state; avoid reverting unrelated local changes.

## Where To Look First

- Chat orchestration and routing:
  - `src/backend/app/orchestration/`
  - `src/backend/app/api/routes/chat.py`
- Specialized agents:
  - `src/backend/app/agents/`
- RAG and retrieval:
  - `src/backend/app/services/rag/`
- Frontend chat UX:
  - `src/app/chat/`
  - `src/components/chat/`
- Shared frontend API and hooks:
  - `src/lib/api-client/`
  - `src/lib/hooks/`
- Knowledge content:
  - `content/`

## Source-Of-Truth Docs

- Technical runtime spec:
  - `docs/technical/specification.md`
- Developer setup and command reference:
  - `README.DEV.md`
- Product vision and scope:
  - `docs/psd/DovvyBuddy-PSD-V6.2.md`
- Architecture decisions:
  - `docs/decisions/`

## Context Control Playbook

1. Read this file and `docs/context/CURRENT_STATE.md`.
2. Pick one primary domain (`src/backend`, `src/app`, `content`, or `docs`).
3. Run a narrow `rg` search in that domain only.
4. Open only files directly tied to the task.
5. Expand to adjacent domains only when an interface requires it.

## Default Verification Commands

- Frontend unit tests:
  - `pnpm test`
- Frontend type/lint:
  - `pnpm typecheck && pnpm lint`
- Backend unit/integration tests:
  - `.venv/bin/python -m pytest src/backend/tests -q`

