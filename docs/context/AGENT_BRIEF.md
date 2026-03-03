# Agent Brief

Last updated: 2026-03-02

## Purpose

Use this file as the default pre-read before scanning code. It provides a compact map of DovvyBuddy so agents can stay within a small context window.

## System Snapshot

- Frontend: Next.js 14 (App Router), TypeScript (`apps/web/src/`)
- Backend: FastAPI + SQLAlchemy async (`apps/api/`)
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
  - `apps/api/app/domain/orchestration/`
  - `apps/api/app/api/routes/chat.py`
- Specialized agents:
  - `apps/api/app/domain/agents/`
- RAG and retrieval:
  - `apps/api/app/infrastructure/services/rag/`
- Frontend chat UX:
  - `apps/web/src/app/chat/`
  - `apps/web/src/features/chat/components/`
- Shared frontend API and hooks:
  - `apps/web/src/shared/lib/api-client/`
  - `apps/web/src/shared/hooks/`
- Knowledge content:
  - `content/source/`

## Source-Of-Truth Docs

- Technical runtime spec:
  - `docs/architecture/specification.md`
- Developer setup and command reference:
  - `README.DEV.md`
- Product vision and scope:
  - `docs/product/psd/DovvyBuddy-PSD-V6.2.md`
- Architecture decisions:
  - `docs/architecture/decisions/`

## Context Control Playbook

1. Read this file and `docs/context/CURRENT_STATE.md`.
2. Pick one primary domain (`apps/api`, `apps/web`, `content`, or `docs`).
3. Run a narrow `rg` search in that domain only.
4. Open only files directly tied to the task.
5. Expand to adjacent domains only when an interface requires it.

## Default Verification Commands

- Frontend unit tests:
  - `pnpm test`
- Frontend type/lint:
  - `pnpm typecheck && pnpm lint`
- Backend unit/integration tests:
  - `.venv/bin/python -m pytest apps/api/tests -q`
