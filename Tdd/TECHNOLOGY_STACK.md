# Technology Stack

This document summarizes the primary technologies and libraries used across the DovvyBuddy project. Use this as a quick reference when onboarding or when making changes that touch infra, APIs, or ML components.

## Frontend
- Framework: `Next.js` (React)
- Language: `TypeScript`
- Key files: `package.json`, `src/`, `next.config.js`
- UI libs: React 18

## Primary Backend (TypeScript)
- Runtime: Node.js (>=20)
- Framework: Next.js serverless API routes
- LLM integration: client code and model-provider in `src/lib/model-provider`
- RAG integration: `src/lib/rag`, retrieval helpers
- Key files: `package.json`, `pnpm-lock.yaml`, `drizzle.config.ts`, `src/lib/`

## Python Backend (Python-first services)
# TECHNICAL NOTE: file moved

This file has been moved to `docs/tdd/TECHNOLOGY_STACK.md` to consolidate project documentation under `docs/`.

Please update any references to point to the new location.
