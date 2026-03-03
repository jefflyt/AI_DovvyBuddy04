# apps/web/src/shared/lib

Shared utilities and core logic for DovvyBuddy.

> Note: Current production backend runtime is Python in `apps/api`. This folder contains frontend/shared TypeScript modules and historical abstractions retained for compatibility.

## Contents

### ✅ Completed Modules (PR1-PR3.1)

- **agent/** — Google ADK multi-agent system (PR3.1)
  - `base-agent.ts` — Agent abstraction
  - `certification-agent.ts` — Certification specialist
  - `trip-agent.ts` — Trip planning specialist
  - `safety-agent.ts` — Safety validation agent
  - `retrieval-agent.ts` — Knowledge base retrieval
  - `agent-registry.ts` — Agent lookup and routing
  - `tools/` — Agent tools (vector-search, session-lookup, safety-check)
- **orchestration/** — Chat orchestration (PR3, PR3.1)
  - `chat-orchestrator.ts` — Main orchestrator with ADK routing
  - `chat-orchestrator-adk.ts` — Multi-agent coordination
- **model-provider/** — LLM provider interface (PR3)
  - Legacy abstraction retained for frontend compatibility
  - Primary runtime LLM orchestration now lives in `apps/api/app/domain/orchestration`
- **embeddings/** — Embedding generation (PR2)
  - Gemini text-embedding-004 provider
- **rag/** — Retrieval-Augmented Generation pipeline (PR2)
  - Chunking, embedding, vector search
- **session/** — Session management (PR3)
  - CRUD operations, history tracking
- **prompts/** — System prompts and templates (PR3)
  - Certification, trip, safety prompts

### 🚧 Future Modules

- **validation/** — Input validation and sanitization
- **utils/** — General-purpose helper functions

## Usage

Import from `@/shared/lib` using the TypeScript path alias:

```typescript
import { someUtil } from '@/shared/lib/utils'
```
