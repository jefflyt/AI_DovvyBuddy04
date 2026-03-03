# Frontend Agent Guide

Scope: `apps/web/src/`

## Default Focus

- Routes/pages:
  - `apps/web/src/app/`
- Chat experience:
  - `apps/web/src/app/chat/`
  - `src/features/chat/components/`
- Landing UI:
  - `src/features/landing/components/`
- API client and hooks:
  - `src/shared/lib/api-client/`
  - `src/shared/hooks/`

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
- If API contract assumptions change, coordinate with `apps/api/` and update `docs/context/CURRENT_STATE.md`.
- For chat behavior changes, validate session persistence and lead capture flows.
