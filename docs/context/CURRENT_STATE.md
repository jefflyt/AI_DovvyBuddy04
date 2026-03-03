# Current State

Last updated: 2026-03-02

## Project Phase

- Stage: Active development toward production launch.
- Platform shape:
  - Web frontend in `apps/web/`
  - Python backend in `apps/api/`
  - Curated content corpus in `content/source/`

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
  - `apps/api/app/api/routes/chat.py`
  - `apps/api/app/domain/orchestration/orchestrator.py`
- Frontend chat behavior:
  - `apps/web/src/app/chat/page.tsx`
  - `apps/web/src/features/chat/components/`
- Content quality/retrieval issues:
  - `content/source/`
  - `apps/api/app/infrastructure/services/rag/`

## Fast Validation Set

- Frontend:
  - `pnpm typecheck`
  - `pnpm test`
- Backend:
  - `.venv/bin/python -m pytest apps/api/tests/unit -q`
- Content:
  - `pnpm content:validate`

## Update Policy

When cross-domain contracts change (API payloads, session shape, lead fields, retrieval metadata), update this file in the same change set.
