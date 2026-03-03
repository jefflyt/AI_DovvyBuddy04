# Backend Agent Guide

Scope: `apps/api/`

## Default Focus

- API routes and request/response contract:
  - `app/api/routes/`
- Conversation orchestration:
  - `app/domain/orchestration/`
- Agent logic:
  - `app/domain/agents/`
- RAG and retrieval:
  - `app/infrastructure/services/rag/`
- Data models and repositories:
  - `app/infrastructure/db/`

## Scan Discipline

- First pass:
  - 6 to 10 files max.
  - start with route -> orchestrator -> service chain.
- Do not read the whole backend tree up front.
- Expand to frontend only if request/response contract changed.

## Common Commands

- Backend tests (all):
  - `.venv/bin/python -m pytest apps/api/tests -q`
- Unit tests only:
  - `.venv/bin/python -m pytest apps/api/tests/unit -q`
- Integration tests:
  - `.venv/bin/python -m pytest apps/api/tests/integration -q`

## Change Rules

- Preserve API response compatibility unless task explicitly requires a contract change.
- If contract changes are required, update frontend client usage and `docs/context/CURRENT_STATE.md`.
- Keep safety and grounding behavior intact when editing orchestration/agent prompts.
