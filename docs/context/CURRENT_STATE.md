# Current State

Last updated: 2026-03-02

## Project Phase

- Stage: Active development toward production launch.
- Platform shape:
  - Web frontend in `src/`
  - Python backend in `src/backend/`
  - Curated content corpus in `content/`

## Current Priorities

- Stabilize chat behavior and session continuity.
- Complete production-hardening across API, monitoring, and testing paths.
- Maintain grounded RAG quality as content evolves.
- Keep lead capture flow reliable across frontend and backend boundaries.

## Operational Constraints

- Orchestration/runtime defaults are Gemini-first in current docs.
- Session behavior and safety posture are product-critical and should not regress.
- Content integrity matters for response quality; validate content changes before ingestion.
- Repository can contain in-progress local edits; preserve unrelated changes.

## Suggested Task Entry Points

- Backend behavior bugs:
  - `src/backend/app/api/routes/chat.py`
  - `src/backend/app/orchestration/orchestrator.py`
- Frontend chat behavior:
  - `src/app/chat/page.tsx`
  - `src/components/chat/`
- Content quality/retrieval issues:
  - `content/`
  - `src/backend/app/services/rag/`

## Fast Validation Set

- Frontend:
  - `pnpm typecheck`
  - `pnpm test`
- Backend:
  - `.venv/bin/python -m pytest src/backend/tests/unit -q`
- Content:
  - `pnpm content:validate`

## Update Policy

When cross-domain contracts change (API payloads, session shape, lead fields, retrieval metadata), update this file in the same change set.

