---
name: project-context
description: DovvyBuddy project overview, tech stack, architecture, and current development status.
type: project
---

# DovvyBuddy Project Context

## What it is
AI-powered diving assistant for scuba certification guidance and trip planning.

## Architecture
- **Monorepo** (pnpm workspace)
- **apps/web** — Next.js 14 frontend (React 18, TypeScript, Tailwind CSS)
- **apps/api** — Python backend (FastAPI, RAG system, Supabase)
- **tooling/** — Shared config, scripts, test configs
- **tests/** — E2E tests (Playwright)
- **content/** — Diving course content and knowledge base

## Tech Stack
- Frontend: Next.js 14, React 18, TypeScript, Tailwind CSS, shadcn/ui, Zod
- Backend: Python, FastAPI, Supabase (PostgreSQL), RAG embeddings
- Testing: Vitest (unit), pytest (integration), Playwright (E2E)
- CI/CD: GitHub Actions
- Deployment: Vercel

## Key Scripts
- `pnpm dev` — Start dev server
- `pnpm test` — Run unit tests
- `pnpm test:integration` — Run integration tests
- `pnpm test:e2e` — Run E2E tests
- `pnpm lint` / `pnpm lint:fix` — Lint frontend
- `pnpm build` — Build production bundle
- `pnpm agent:preflight` — Run preflight checks

## Constraints
- Files under 500 lines
- Strict TypeScript mode
- No hardcoded credentials
- Supabase RLS on all tables

---
**Why:** Provides essential context for any new conversation about DovvyBuddy.
**How to apply:** Read at session start to understand project before making suggestions.
