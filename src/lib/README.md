# src/lib

Shared utilities and core logic for DovvyBuddy.

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
  - Groq and Gemini implementations
  - Retained as fallback during Python migration
  
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

Import from `@/lib` using the TypeScript path alias:

```typescript
import { someUtil } from '@/lib/utils'
```
