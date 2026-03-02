# DovvyBuddy Agent Router

This repository is a monorepo. Keep task context small by default.

## Required Pre-Read (In Order)

1. `docs/context/AGENT_BRIEF.md`
2. `docs/context/CURRENT_STATE.md`
3. The nearest scoped `AGENTS.md` for your task area:
   - `src/backend/AGENTS.md`
   - `src/app/AGENTS.md`
   - `content/AGENTS.md`

## Start-Of-Task Convention

- Run preflight before any code scan:
  - `pnpm agent:preflight -- <backend|frontend|content|docs>`
- Run repository scans through the gated wrapper:
  - `pnpm agent:scan -- <rg args>`
- If preflight is missing or stale, `agent:scan` will stop and require a fresh preflight.

## Scan Budget Rules

- Start with a bounded scan using `rg` in the target directory only.
- First pass budget: open at most 12 files and about 1,500 lines total.
- Do not scan `docs/plans/` or archived docs unless the task is planning/history.
- Expand scope only when blocked by missing dependencies or interfaces.

## Task Routing

- Backend API, orchestration, RAG, ingestion, Python tests:
  - Start in `src/backend/`
- Frontend UI, chat page, client behavior, Next.js routes:
  - Start in `src/app/` and `src/components/`
- Knowledge base updates and content quality:
  - Start in `content/`
- Architecture, decisions, implementation history:
  - Start in `docs/`

## Monorepo Working Norms

- Assume the worktree may be dirty; do not revert unrelated edits.
- Prefer targeted tests over full-suite runs during iteration.
- Keep changes scoped to one domain unless an interface change requires cross-domain edits.
- If changing cross-domain contracts, update docs in `docs/context/CURRENT_STATE.md`.
