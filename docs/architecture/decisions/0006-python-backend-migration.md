# ADR-0006: Python-First Backend Migration Strategy

**Status:** ✅ Implemented  
**Date:** January 1, 2026  
**Implementation Completed:** January 5, 2026  
**Deciders:** Solo Founder

---

## Context

DovvyBuddy was initially built as a **TypeScript full-stack monolith** using Next.js:

- Frontend: Next.js App Router (React + TypeScript)
- Backend: Next.js API routes (serverless functions)
- Database ORM: Drizzle ORM (TypeScript)
- All business logic in TypeScript (`apps/web/src/shared/lib/`)

This architecture delivered:

- ✅ Fast initial development (single language, single deployment)
- ✅ Type safety across full stack
- ✅ Vercel deployment simplicity
- ✅ Good developer experience with hot reload

However, as the product evolved, **limitations emerged**:

**AI/ML Ecosystem Constraints:**

- TypeScript has limited AI/ML libraries (no LangChain, LlamaIndex, sentence-transformers)
- RAG operations in TypeScript less mature (chunking, embeddings, vector ops)
- Cannot leverage Python data science tools (pandas, numpy, spaCy)
- ADK (Agent Development Kit) while functional, has better Python support

**Multi-Channel Architecture:**

- PR8b plans Telegram bot integration
- Telegram bot libraries are primarily Python-based (python-telegram-bot)
- Sharing business logic between web and Telegram requires extraction
- Next.js API routes not ideal for non-HTTP interfaces

**Operational Limitations:**

- Content ingestion scripts could benefit from Python data processing (pandas, better markdown parsing)
- Analytics and benchmarking easier with Python (matplotlib, jupyter notebooks)
- TypeScript mocking and testing for AI/ML flows more brittle (Drizzle ORM mocking issues)

**Scaling Considerations:**

- Serverless functions have cold start and execution time limits
- Complex agent orchestration approaching Vercel timeout limits
- Database connection pooling challenging in serverless context

The application now requires:

- Better AI/ML tooling for advanced RAG and agent features
- Multi-channel support (web + Telegram + future WhatsApp)
- More robust analytics and content processing
- Independent scaling of backend from frontend
- Easier integration with Python-native AI services

---

## Decision

Migrate to a **Python-first backend architecture** with **TypeScript frontend**:

**New Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (TypeScript)                    │
│  Next.js (Vercel) - SSR + Static Pages + Client Components  │
└─────────────────┬───────────────────────────────────────────┘
                  │ REST API (OpenAPI)
┌─────────────────▼───────────────────────────────────────────┐
│                   Backend (Python)                           │
│  FastAPI (Cloud Run) - Async + Pydantic + SQLAlchemy       │
│  ├─ domain/agents + domain/orchestration                    │
│  ├─ infrastructure/services (embeddings, llm, rag)          │
│  ├─ infrastructure/db (SQLAlchemy models + repositories)    │
│  └─ scripts/ (content processing)                           │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              PostgreSQL + pgvector (Neon)                    │
│         (Schema unchanged, accessed by Python)               │
└─────────────────────────────────────────────────────────────┘
```

**Key Implementation Decisions:**

1. **Backend Stack:**
   - FastAPI for REST API (async, OpenAPI auto-generation, Pydantic validation)
   - SQLAlchemy for ORM (async with asyncpg)
   - Alembic for migrations (replaces Drizzle Kit)
   - Python 3.11+ for performance

2. **Frontend Stack:**
   - Keep Next.js + TypeScript (no changes to React components)
   - Generate TypeScript API client from OpenAPI spec
   - Update to call Python backend via HTTP

3. **Data Layer:**
   - **No schema changes** — existing Postgres schema preserved
   - SQLAlchemy models mirror current Drizzle schema
   - Data remains intact during migration

4. **Deployment:**
   - Python backend: Google Cloud Run (containerized, auto-scaling)
   - Next.js frontend: Vercel (existing setup)
   - DNS: `api.dovvybuddy.com` → Cloud Run, `dovvybuddy.com` → Vercel

5. **Migration Strategy:**
   - **8-step incremental approach** (6-9 weeks, 3 sprints)
   - Behavior-preserving refactor (API contract unchanged)
   - Extensive comparison testing (TS vs Python outputs)
   - Staged rollout with rollback capability

**Migration Steps:**

1. Define API contract & scaffold Python project (3-4 days)
2. Migrate database access layer (5-7 days)
3. Migrate embedding & model providers (4-5 days)
4. Migrate RAG pipeline (5-6 days)
5. Migrate agents & orchestration (7-10 days)
6. Migrate content scripts (3-4 days)
7. Connect frontend to Python backend (3-4 days)
8. Production deployment (5-7 days)

---

## Consequences

### Positive

- ✅ **Rich AI/ML ecosystem** — Access to LangChain, LlamaIndex, sentence-transformers, spaCy, etc.
- ✅ **Better RAG performance** — Python-native vector operations, batching, caching
- ✅ **Multi-channel enablement** — Python backend can serve web + Telegram + future channels
- ✅ **Data science tooling** — pandas, matplotlib, jupyter for analytics and content processing
- ✅ **Async/await native** — FastAPI built for async from ground up
- ✅ **Independent scaling** — Backend can scale separately from frontend
- ✅ **Better testing** — Python mocking and fixtures more mature for AI workflows
- ✅ **Deployment flexibility** — Cloud Run, Railway, Render all viable (not locked to Vercel)
- ✅ **Cost optimization** — Can optimize backend compute independently

### Negative

- ⚠️ **Dual language maintenance** — Team must maintain TypeScript (frontend) + Python (backend)
- ⚠️ **Deployment complexity** — Two services vs one (separate CI/CD, monitoring, debugging)
- ⚠️ **API drift risk** — OpenAPI contract must be maintained to prevent frontend/backend misalignment
- ⚠️ **Migration effort** — 6-9 weeks to complete, delays other features (PR4-PR6)
- ⚠️ **Learning curve** — Solo founder must be proficient in both ecosystems
- ⚠️ **CORS complexity** — Cross-origin requests require careful configuration
- ⚠️ **Increased operational overhead** — More infrastructure to monitor, debug, and maintain
- ⚠️ **Cold start potential** — Cloud Run containers have cold start latency (though minimal with min instances)

### Neutral

- 🔄 **Different deployment model** — From monolith to microservices
- 🔄 **New tooling** — pytest, mypy, ruff, alembic vs vitest, eslint, drizzle-kit
- 🔄 **API-first development** — Must define OpenAPI contract before implementation

---

## Alternatives Considered

### Alternative 1: Keep TypeScript Full-Stack Monolith

**Description:** Continue with Next.js for both frontend and backend

**Pros:**

- No migration effort (continue building features)
- Single language, simpler mental model
- Existing team expertise
- Vercel deployment simplicity

**Cons:**

- Limited AI/ML ecosystem (major constraint)
- Multi-channel architecture difficult (Telegram bot would require separate service anyway)
- Serverless limitations (cold starts, timeouts, connection pooling)
- Content processing and analytics remain limited

**Why rejected:** AI/ML ecosystem limitation is a blocker for planned features (advanced RAG, better agents, data analysis). Telegram bot (PR8b) would require backend extraction anyway.

### Alternative 2: Hybrid TypeScript/Python (Gradual Extraction)

**Description:** Keep Next.js monolith, add Python microservices for specific features

**Pros:**

- Incremental migration (lower risk)
- Can prioritize which features to extract first
- Frontend unchanged during transition
- Each microservice can be Python or TypeScript

**Cons:**

- Complex architecture (multiple services, mixed languages)
- Harder to share code between services
- Operational complexity even higher than clean split
- Eventually results in same end state (Python backend) but with more interim complexity

**Why rejected:** Clean split is simpler long-term. Hybrid state would be painful to maintain. Migration plan already incremental (8 steps) with rollback points.

### Alternative 3: Move Entire Stack to Python (Django/FastAPI + React)

**Description:** Migrate frontend to React (no Next.js) and backend to Python

**Pros:**

- Single language for full stack
- Mature Python ecosystem for everything
- Lots of Django/React examples and libraries

**Cons:**

- Lose Next.js SSR, App Router, and Vercel deployment benefits
- Frontend migration effort on top of backend migration (much more work)
- React without Next.js requires more boilerplate (routing, SSR setup, build config)
- TypeScript frontend has been working well (no need to change)

**Why rejected:** Frontend works well, no reason to migrate it. Keeping Next.js/TypeScript frontend preserves investment and allows focus on backend migration.

### Alternative 4: Use Deno for Backend (TypeScript on Server)

**Description:** Migrate backend to Deno Deploy (TypeScript server runtime)

**Pros:**

- Keep TypeScript for full stack
- Deno has better serverless performance than Node
- Modern runtime with native TypeScript support
- Good DX and deployment

**Cons:**

- AI/ML ecosystem still limited (Python libraries don't work on Deno)
- Smaller community and fewer libraries than Python
- Telegram bot libraries limited or non-existent
- Data science tools (pandas equivalent) immature or missing

**Why rejected:** Doesn't solve core problem (AI/ML ecosystem). Would still be fighting limited libraries for agent features, RAG improvements, and data processing.

### Alternative 5: Python Backend with Separate TypeScript Agent Service

**Description:** Python for API/business logic, TypeScript for agent orchestration only

**Pros:**

- Keeps existing TypeScript agent code
- Python for everything except agents
- Gradual migration of agents to Python later

**Cons:**

- Defeats purpose (agents are where Python ecosystem helps most)
- Two backend services (Python + TypeScript) to maintain
- Agents would still lack Python AI/ML tooling
- Complex inter-service communication

**Why rejected:** Agents are precisely where Python ecosystem provides most value (LangChain, LangGraph, tool libraries). Keeping them in TypeScript defeats the purpose.

---

## References

- **PR3.2 Plan:** [../../archive/plans/PR3.2-Python-Backend-Migration.md](../../archive/plans/PR3.2-Python-Backend-Migration.md)
- **Related ADRs:**
  - [0004-google-adk-multi-agent.md](./0004-google-adk-multi-agent.md) — Multi-agent architecture to migrate
  - [0002-postgres-pgvector.md](./0002-postgres-pgvector.md) — Database schema to preserve
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **SQLAlchemy Docs:** https://www.sqlalchemy.org/

---

## Notes

**Implementation Status:** ✅ Complete (January 5, 2026)

**What Was Completed:**

- ✅ Python FastAPI backend fully implemented and functional
- ✅ All TypeScript backend code removed (orchestration, agents, RAG, session, model-provider, embeddings, prompts)
- ✅ Drizzle ORM and TypeScript scripts removed
- ✅ Python scripts (ingest, validate, benchmark) now primary
- ✅ Next.js config simplified to always proxy to Python backend
- ✅ Frontend API client updated to use Python backend only
- ✅ Package.json cleaned of backend dependencies
- ✅ README updated to reflect Python-first architecture
- ✅ Database schema preserved (no data migration needed)

**Timeline:**

- PR3.2 Implementation: ~3 weeks (December 2025)
- TypeScript Backend Cleanup: January 5, 2026
- **Total:** ~4 weeks

**Migration Results:**

- TypeScript backend completely removed from codebase
- Python backend is now the sole backend implementation
- Frontend unchanged (only HTTP client configuration updated)
- All content scripts migrated to Python
- Database accessed exclusively via SQLAlchemy
- Feature flag `USE_PYTHON_BACKEND` removed (Python is now mandatory)

**Risk Mitigation (Applied):**

- ✅ Python backend tested and validated before removing TypeScript
- ✅ Git branch created for safe rollback (`feat/remove-typescript-backend`)
- ✅ All Python scripts verified functional before removing TypeScript versions
- ✅ Feature parity confirmed between TypeScript and Python implementations

**Success Criteria (Achieved):**

- ✅ TypeScript backend code completely removed
- ✅ API contract preserved (frontend unchanged except HTTP client)
- ✅ Database schema unchanged (existing data intact)
- ✅ Python scripts functional for all content operations
- ✅ Next.js proxies all API requests to Python backend
- ✅ Documentation updated to reflect new architecture

**Future Considerations:**

- Consider LangChain/LangGraph for agent orchestration enhancements
- Evaluate agent performance metrics to optimize routing and tool use
- Monitor Python backend performance and optimize hot paths
- Explore additional Python AI/ML libraries for RAG improvements

**Blockers/Dependencies:**

- ✅ PR1, PR2, PR3, PR3.1 complete
- ✅ Python backend implementation complete
- ✅ TypeScript backend removal complete
- ✅ Documentation updated

**Team Impact:**

- Solo founder responsible for both TypeScript frontend and Python backend
- Must context-switch between languages regularly
- Documentation critical to remember implementation details across services

---

**Last Updated:** January 5, 2026  
**Migration Completed:** January 5, 2026
