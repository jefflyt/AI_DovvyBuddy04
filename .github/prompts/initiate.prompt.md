---
name: initiate
description: Greenfield bootstrap from PSD (PR0 scaffold + commands + copilot-project.md + minimal CI)
agent: agent
argument-hint: "Paste PSD. Optional: preferred stack/hosting. If none, use the default preset."
---

You are bootstrapping a brand-new repo from a PSD. There is NO existing codebase, NO scripts, NO CI.
Your output MUST define PR0: Project Bootstrap so the repo becomes runnable and future prompts have “truth”.

## Hard rules
- Do NOT write feature implementation code.
- Do NOT output fenced code blocks.
- Do NOT invent commands after the fact: all commands you define must be consistent and form a runnable toolchain.
- If PSD doesn’t specify stack, use the default preset below and mark it DECIDED.

## Default preset (unless PSD forces otherwise)
- Next.js (TypeScript) + pnpm + ESLint + Prettier + Vitest
- Optional: Playwright only if PSD requires e2e early

## Output (MUST follow)
## 0) Assumptions (max 3)
- ...

## 1) PSD extraction (only what affects scaffolding)
- App type:
- Key pages/flows (names only):
- Data needs (none/SQLite/Postgres):
- Auth need (none/basic/OAuth):

## 2) Tech decisions (DECIDED)
- Stack preset:
- Package manager:
- Test runner:
- Lint/format:
- Typecheck:
- Environment strategy (.env.*):
- Minimal CI checks:

## 3) Repo structure (DECIDED)
- Top-level folders:
- Where UI lives:
- Where API lives (if any):
- Where shared code lives:
- Where DB/migrations live (if any):

## 4) PR0 — Project Bootstrap
- Goal:
- Scope:
- Files to create (explicit):
  - README.md (setup + commands)
  - .github/copilot-project.md
  - .github/workflows/ci.yml (or equivalent)
  - config files (lint/format/typecheck/test)
- Commands to establish (explicit list):
  - install:
  - dev:
  - build:
  - test:
  - lint:
  - format:
  - typecheck:
- Verification checklist (what to run locally):
- Risks / gotchas:

## 5) Next step
- After PR0 exists, run `plan.prompt.md` on the same PSD to generate PR1..n.