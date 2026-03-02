# Frontend Agent Guide

Scope: `src/app/`, `src/components/`, `src/lib/`

## Default Focus

- Routes/pages:
  - `src/app/`
- Chat experience:
  - `src/app/chat/`
  - `src/components/chat/`
- Landing UI:
  - `src/components/landing/`
- API client and hooks:
  - `src/lib/api-client/`
  - `src/lib/hooks/`

## Scan Discipline

- Start with the page + directly imported components + related hook/client files.
- First pass budget: 6 to 10 files.
- Avoid scanning backend unless payload shape or endpoint behavior is relevant.

## Common Commands

- Type checks:
  - `pnpm typecheck`
- Lint:
  - `pnpm lint`
- Unit tests:
  - `pnpm test`
- E2E smoke:
  - `pnpm test:e2e`

## Change Rules

- Keep UI changes consistent with existing design tokens and component patterns.
- If API contract assumptions change, coordinate with `src/backend/` and update `docs/context/CURRENT_STATE.md`.
- For chat behavior changes, validate session persistence and lead capture flows.

