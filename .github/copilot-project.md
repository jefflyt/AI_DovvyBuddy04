# DovvyBuddy Project Context

**Last Updated:** 2026-03-03

## Project Summary

DovvyBuddy is an AI diving assistant with:

- `apps/web`: Next.js 14 frontend
- `apps/api`: FastAPI backend
- `content/source`: markdown source content for RAG
- `tooling`: shared scripts/config for scans and tests

## Monorepo Layout

```text
AI_DovvyBuddy04/
├── apps/
│   ├── web/
│   └── api/
├── content/
│   ├── source/
│   ├── generated/
│   └── templates/
├── docs/
│   ├── context/
│   ├── architecture/
│   ├── operations/
│   ├── product/
│   └── archive/
├── tooling/
│   ├── config/
│   └── scripts/
└── tests/
```

## Core Commands

```bash
# web
pnpm dev
pnpm build
pnpm test
pnpm lint
pnpm typecheck

# content pipeline
pnpm content:validate
pnpm content:ingest
pnpm content:ingest -- --full
pnpm content:clear

# backend tests
.venv/bin/python -m pytest apps/api/tests/unit -q
.venv/bin/python -m pytest apps/api/tests/integration -q

# e2e
pnpm test:e2e
```

## Agent Workflow Rules

1. Read context docs first:
   - `docs/context/AGENT_BRIEF.md`
   - `docs/context/CURRENT_STATE.md`
2. Run preflight before scans:
   - `pnpm agent:preflight -- <backend|frontend|content|docs> --ack I_READ_CONTEXT`
3. Use gated scan wrapper:
   - `pnpm agent:scan -- <rg args>`

## Source-of-Truth Docs

- Project setup and commands: `README.DEV.md`
- Runtime architecture: `docs/architecture/specification.md`
- Active operations runbooks: `docs/operations/`
- Historical plans and reports: `docs/archive/`

## Content Notes

- Author/edit only in `content/source`.
- Treat `content/generated` as derivative output.
- Run validation before ingestion.

## Safety Constraints

- Do not commit credentials.
- Keep secrets in root `.env.local` only.
- `.env.example` contains placeholders only.
