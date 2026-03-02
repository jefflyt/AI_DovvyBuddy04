# Backend Agent Guide

Scope: `src/backend/`

## Default Focus

- API routes and request/response contract:
  - `app/api/routes/`
- Conversation orchestration:
  - `app/orchestration/`
- Agent logic:
  - `app/agents/`
- RAG and retrieval:
  - `app/services/rag/`
- Data models and repositories:
  - `app/db/`

## Scan Discipline

- First pass:
  - 6 to 10 files max.
  - start with route -> orchestrator -> service chain.
- Do not read the whole backend tree up front.
- Expand to frontend only if request/response contract changed.

## Common Commands

- Backend tests (all):
  - `.venv/bin/python -m pytest src/backend/tests -q`
- Unit tests only:
  - `.venv/bin/python -m pytest src/backend/tests/unit -q`
- Integration tests:
  - `.venv/bin/python -m pytest src/backend/tests/integration -q`

## Change Rules

- Preserve API response compatibility unless task explicitly requires a contract change.
- If contract changes are required, update frontend client usage and `docs/context/CURRENT_STATE.md`.
- Keep safety and grounding behavior intact when editing orchestration/agent prompts.

