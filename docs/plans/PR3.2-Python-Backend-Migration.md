# PR3.2: Python-First Backend Migration

**Status:** Draft  
**Based on:** PR3 (Model Provider & Session Logic) and PR2 (RAG Pipeline)  
**Date:** January 1, 2026

---

## 1. Feature/Epic Summary

### Objective

Migrate DovvyBuddy from a TypeScript full-stack monolith (Next.js API routes) to a Python-first backend architecture with TypeScript web frontend, enabling better ML/AI ecosystem integration, improved RAG performance, and multi-channel support (web + future Telegram).

### User Impact

- **Maintained experience**: API contract unchanged; migration is transparent to users
- **Improved performance**: Better RAG retrieval with Python-native vector operations and batching
- **Future capabilities**: Python backend enables Telegram bot (PR8b), advanced NLP, and data science workflows
- **No UI disruption**: Frontend remains Next.js with TypeScript, preserving modern React developer experience

### Dependencies

- **Requires:** ✅ PR1 (Database Schema) — Postgres schema stable
- **Requires:** ✅ PR2 (RAG Pipeline) — TypeScript RAG implementation complete
- **Requires:** ✅ PR3 (Model Provider & Session Logic) — Baseline orchestration complete
- **Requires:** ✅ PR3.1 (ADK Multi-Agent RAG) — Multi-agent system complete
- **Integrates with:** PR5 (Chat Interface) — Frontend will consume new Python API
- **Enables:** PR8b (Telegram Bot Adapter) — Shared Python backend for multi-channel
- **Enables:** Advanced ML features — Python ecosystem (LangChain, LlamaIndex, sentence-transformers)

### Assumptions

- **Assumption:** Current Postgres schema remains unchanged during migration
- **Assumption:** Python FastAPI can match or exceed Next.js API route performance
- **Assumption:** OpenAPI contract prevents API drift between backend and frontend
- **Assumption:** Cloud Run (or Railway/Render) deployment is viable for production scale
- **Assumption:** Solo founder can manage dual TypeScript + Python codebases

---

## 2. Complexity & Fit

### Classification: `Multi-Phase` (8 implementation steps across 3 sprints)

### Rationale

- **Architecture refactor**: Fundamental change from monolith to microservices
- **Cross-language migration**: TypeScript → Python requires rewriting entire backend
- **Deployment complexity**: Two services (Next.js on Vercel + Python on Cloud Run) vs one
- **Risk management**: Behavior-preserving refactor requires extensive testing and staged rollout
- **Timeline**: 6-9 weeks for solo founder (2-3 weeks per sprint, 3 sprints total)

This is a substantial refactor that touches every layer of the stack (database access, business logic, API, deployment). The 8-step incremental approach with clear checkpoints is necessary to manage risk and allow continuous validation.

**Recommended approach:** Complete in 3 sprints:
- **Sprint 1** (Steps 1-4): Foundation — API contract, database, embeddings, RAG
- **Sprint 2** (Steps 5-6): Business logic — Agents, orchestration, content scripts
- **Sprint 3** (Steps 7-8): Integration — Frontend connection, deployment

---

## 3. Full-Stack Impact

### Frontend

**Moderate changes:**

- **Modified modules:**
  - `src/lib/api-client/` — New TypeScript API client (generated from OpenAPI)
    - `client.ts` — Configured HTTP client for Python backend
    - `error-handler.ts` — API error mapping
  - `src/app/api/chat/route.ts` — Updated to proxy to Python backend (or removed)
  - `next.config.js` — Backend URL configuration for rewrites
  - `.env.local` — Add `BACKEND_URL` or `NEXT_PUBLIC_API_URL`

- **New dependencies:**
  - `openapi-typescript-codegen` or `orval` — TypeScript client generation

- **Deleted modules:** None (TypeScript frontend code preserved)

**Impact:** Low. API contract preserved, only HTTP client changes.

### Backend

**Complete rewrite in Python:**

- **New Python service:** `src/backend/` directory (separate from Next.js)
  - `src/backend/app/` — FastAPI application
    - `main.py` — FastAPI app initialization, CORS, middleware
    - `api/routes/` — Route handlers (chat, session, lead)
    - `services/` — Business logic
      - `embeddings/` — Gemini embedding provider
      - `llm/` — LLM provider abstraction (Groq/Gemini)
      - `rag/` — RAG pipeline (chunking, retrieval)
    - `agents/` — Multi-agent system (certification, trip, safety)
    - `orchestration/` — Chat orchestrator
    - `db/` — SQLAlchemy models and repositories
      - `models/` — ORM models (sessions, embeddings, leads, etc.)
      - `repositories/` — Data access layer
      - `session.py` — Async DB session management
    - `prompts/` — System prompts and templates
    - `core/` — Configuration, logging, dependencies
  - `src/backend/scripts/` — Content processing
    - `ingest_content.py` — Content ingestion
    - `validate_content.py` — Content validation
    - `benchmark_rag.py` — RAG benchmarking
  - `src/backend/tests/` — Pytest test suite
  - `src/backend/alembic/` — Database migrations (replaces Drizzle)
  - `src/backend/pyproject.toml` or `requirements.txt` — Python dependencies
  - `src/backend/Dockerfile` — Container image
  - `src/backend/openapi.yaml` — API specification

- **Deleted TypeScript modules:**
  - `src/lib/orchestration/` — Replaced by Python orchestrator
  - `src/lib/agent/` — Replaced by Python agents (ADK multi-agent system in PR3.1)
  - `src/lib/model-provider/` — Replaced by Python LLM providers (currently retained as fallback)
  - `src/lib/embeddings/` — Replaced by Python embedding service
  - `src/lib/rag/` — Replaced by Python RAG pipeline
  - `src/lib/session/` — Replaced by Python session management
  - `src/lib/prompts/` — Replaced by Python prompt templates
  - `scripts/ingest-content.ts` — Replaced by Python script
  - `scripts/validate-content.ts` — Replaced by Python script
  - `scripts/benchmark-rag.ts` — Replaced by Python script

**Note:** PR3.1 introduced Google ADK multi-agent system. The Python migration will replicate this architecture or use LangChain/LangGraph alternatives.

- **Preserved TypeScript modules:**
  - `src/app/` — Next.js pages and layouts (frontend)
  - `src/types/` — Shared TypeScript types (some may be regenerated from OpenAPI)

**Impact:** High. Entire backend rewritten in Python.

### Data

**Schema unchanged, ORM replaced:**

- **No schema changes**: Postgres tables, columns, types remain identical
- **Drizzle ORM → SQLAlchemy**: Python ORM replaces TypeScript ORM
- **Drizzle Kit → Alembic**: Python migration tool replaces TypeScript migration tool
- **Migrations strategy**:
  - Existing Drizzle migrations already applied to production
  - Alembic initialized with current schema (no-op initial migration)
  - Future migrations use Alembic only
  - Drizzle migrations frozen (not deleted for historical reference)

**Impact:** Medium. ORM layer completely replaced, but schema and data untouched.

### Infrastructure

**Significant changes:**

- **Deployment architecture**:
  - **Current:** Single Next.js app on Vercel (API routes + frontend)
  - **New:** Two services
    - Python backend on Cloud Run (or Railway/Render)
    - Next.js frontend on Vercel (SSR + static pages)

- **CI/CD**:
  - Update `.github/workflows/` to build and test both Python and TypeScript
  - Separate deployment workflows for backend and frontend
  - Python linting (ruff, mypy, black) and testing (pytest)
  - TypeScript linting and testing (existing)

- **Environment variables**:
  - Python backend: `DATABASE_URL`, `GEMINI_API_KEY`, `GROQ_API_KEY`, etc.
  - Next.js frontend: `BACKEND_URL` or `NEXT_PUBLIC_API_URL`

- **DNS**:
  - `api.dovvybuddy.com` → Cloud Run (Python backend)
  - `dovvybuddy.com` → Vercel (Next.js frontend)

- **Monitoring**:
  - Sentry SDK added to both Python backend and TypeScript frontend
  - Cloud Run metrics (request count, latency, error rate)
  - Structured logging (JSON logs to stdout)

**Impact:** High. Deployment complexity increases with two services.

---

## 4. User-Facing Changes

### User Experience

**No changes.** Migration is transparent to users. Chat interface, response quality, and behavior remain identical.

### API Contract

**Preserved.** All API endpoints maintain exact request/response formats:

- `POST /api/chat` — Chat endpoint (request/response unchanged)
- `POST /session` — Create new session (if exposed as separate endpoint)
- `GET /session/{id}` — Retrieve session (if exposed)
- `POST /lead` — Lead capture (unchanged)

**OpenAPI specification ensures contract stability.**

### Performance

**Target: No degradation, potential improvements:**

- **Chat response latency:** <5 seconds (P95) — maintained or improved
- **RAG retrieval:** <500ms (P95) — likely improved with Python vector operations
- **Embedding generation:** Potential improvement with batching and caching

### Error Handling

**Preserved.** Error messages, status codes, and safety disclaimers remain consistent.

---

## 5. Database Changes

### Schema Changes

**None.** Existing Postgres schema unchanged:

- `sessions` table — unchanged
- `content_embeddings` table — unchanged (vector dimension 768 maintained)
- `leads` table — unchanged
- `destinations` table — unchanged
- `dive_sites` table — unchanged

### Migration Strategy

**ORM migration, not schema migration:**

1. **Drizzle ORM (TypeScript) → SQLAlchemy (Python)**
   - Create SQLAlchemy models mirroring Drizzle schema
   - Test query equivalence (same inputs → same outputs)

2. **Drizzle Kit → Alembic**
   - Initialize Alembic in `src/backend/alembic/`
   - Generate initial migration reflecting current schema (no-op)
   - Future migrations use Alembic exclusively

3. **Data preservation**
   - No data migration needed (schema unchanged)
   - Existing sessions, embeddings, leads remain intact
   - Verify data integrity after Python backend deployment

### Rollback Plan

**No database rollback needed** (schema unchanged). If Python backend fails, revert to TypeScript backend without data loss.

---

## 6. Testing Strategy

### Unit Tests

**Python (backend):**
- Pytest for all modules (services, agents, orchestration, repositories)
- Mock external dependencies (LLM API, embedding API, database)
- Test coverage target: ≥80%
- Fast execution: <30 seconds for full suite

**TypeScript (frontend):**
- Vitest for API client and utilities (existing tests maintained)
- Mock Python backend API responses

### Integration Tests

**Backend → Database:**
- Test SQLAlchemy repositories with Docker Postgres (test database)
- Verify vector search returns correct results
- Test session CRUD operations

**Backend → External APIs:**
- Test embedding generation with real Gemini API (limited runs)
- Test LLM calls with real Groq/Gemini API (limited runs)
- Use VCR-style mocking (record/replay) for CI

**Frontend → Backend:**
- Test API client can call Python backend endpoints
- Verify request/response serialization
- Test error handling and retries

### Comparison Tests

**Critical for behavior preservation:**

- **RAG retrieval:** Run 50+ test queries through both TS and Python RAG, compare top-5 results
- **Embeddings:** Generate embeddings for sample texts, verify cosine similarity ≈ 1.0
- **Chunking:** Compare chunk boundaries and IDs for sample content
- **Orchestration:** Run 50+ test conversations through TS and Python backends, compare response quality
- **Agent routing:** Compare agent selection decisions for labeled test queries

### E2E Tests

**Staged rollout validation:**
- Deploy to staging environment (both services)
- Run full E2E test suite (chat flow, lead capture, session persistence)
- Manual testing: 10+ real user scenarios
- Load testing: Verify performance under concurrent requests

### Performance Tests

**Benchmarking:**
- RAG retrieval latency: Compare TS vs Python
- Embedding generation: Compare TS vs Python (batch vs single)
- Chat response latency: End-to-end timing

**Load testing:**
- Use `locust` or `k6` to simulate 50+ concurrent users
- Verify Cloud Run auto-scaling works correctly
- Monitor database connection pool usage

---

## 7. Security Considerations

### API Security

**CORS configuration:**
- Python backend allows only frontend origin (Vercel domain)
- No wildcard `*` origins in production
- Credentials (cookies) allowed for session management

**Rate limiting:**
- Implement rate limiting on Python backend (per IP or session)
- Prevent abuse of LLM API (costly)
- Use `slowapi` or similar library

**Input validation:**
- Pydantic models validate all request payloads
- Prevent injection attacks (SQL, NoSQL, prompt injection)
- Sanitize user messages before logging

### Secrets Management

**Environment variables:**
- Use Cloud Secret Manager (GCP) or Vercel encrypted env vars
- Never commit `.env` files to Git
- Rotate API keys regularly

**Database credentials:**
- Use IAM authentication for Cloud SQL (if applicable)
- Connection strings stored in secret manager
- No credentials in logs or error messages

### Session Security

**Guest sessions (V1):**
- Session ID in HTTP-only cookie (prevents XSS)
- `SameSite=Lax` or `SameSite=None` with `Secure` flag
- 24-hour expiry enforced server-side

**Future auth (PR8):**
- Python backend must support JWT or session-based auth
- Follow OWASP best practices

---

## 8. Rollout Plan

### Pre-Rollout

**Week -2: Development & Testing**
- Complete Steps 1-6 (foundation, business logic, scripts)
- Run full test suite (unit, integration, comparison)
- Deploy to local dev environment
- Code review and documentation

**Week -1: Staging Deployment**
- Deploy Python backend to staging Cloud Run
- Deploy Next.js frontend to Vercel preview
- Run E2E tests on staging
- Load testing on staging
- Fix bugs and optimize performance

### Rollout Phases

**Phase 1: Canary Deployment (Day 1)**
- Deploy Python backend to production Cloud Run
- Configure traffic splitting: 10% → Python, 90% → TypeScript (if dual deployment possible)
- Monitor metrics for 24 hours:
  - Error rate (target: <1%)
  - Latency P95 (target: <5s)
  - Response quality (manual spot checks)
- **Rollback trigger:** Error rate >5% or latency >10s

**Phase 2: Gradual Rollout (Day 2-3)**
- Increase Python traffic: 25% → 50% → 75%
- Continue monitoring
- Collect user feedback (if available)
- **Rollback trigger:** Same as Phase 1

**Phase 3: Full Rollout (Day 4)**
- Route 100% traffic to Python backend
- Deprecate TypeScript backend (keep code for rollback)
- Update documentation
- Announce migration complete

**Phase 4: Cleanup (Week 2)**
- Remove TypeScript backend code (after 1 week stability)
- Archive Drizzle migrations (historical reference)
- Update CI/CD to remove TypeScript backend jobs
- Celebrate! 🎉

### Monitoring During Rollout

**Real-time dashboards:**
- Cloud Run metrics (requests/sec, latency, errors)
- Sentry error tracking (both backend and frontend)
- Database connection pool usage
- API response times (chat endpoint)

**Alerts:**
- Error rate >5% → page on-call (solo founder = you!)
- Latency P95 >10s → investigate immediately
- Database connection exhaustion → scale up or optimize

**Manual checks:**
- Test 10+ user scenarios every 4 hours during rollout
- Check Sentry for new error types
- Monitor user feedback channels (email, Discord, etc.)

---

## 9. Rollback Strategy

### Automatic Rollback

**Cloud Run revision rollback:**
```bash
gcloud run services update-traffic dovvybuddy-backend \
  --to-revisions=PREVIOUS_REVISION=100
```
- Execution time: <1 minute
- Restores previous Python backend version
- No data loss (database unchanged)

**Vercel deployment rollback:**
- Revert to previous deployment in Vercel dashboard
- Or redeploy from Git commit
- Execution time: ~2 minutes

### Manual Rollback

**Revert to TypeScript backend:**
1. Update frontend `BACKEND_URL` to point to Next.js API routes (internal)
2. Redeploy frontend with old API client
3. Stop Python backend (or set traffic to 0%)
4. Execution time: ~10 minutes

**Database rollback:**
- **Not needed** — schema unchanged, data compatible with both backends

### Rollback Testing

**Pre-rollout:**
- Practice rollback procedure in staging
- Document exact commands and steps
- Time each rollback scenario
- Verify data integrity after rollback

**During rollout:**
- Keep rollback commands ready (tmux/screen session)
- Monitor error dashboards continuously
- Set conservative rollback thresholds (err on side of caution)

---

## 10. Implementation Steps

### Step 1: Define API Contract & Project Structure

**Duration:** 3-4 days

**Goal:** Establish OpenAPI specification and scaffold Python FastAPI project.

**Tasks:**
1. Design OpenAPI 3.0 spec for all backend endpoints (chat, session, lead)
2. Create `src/backend/` directory with FastAPI project structure
3. Setup Python tooling (poetry, pytest, mypy, ruff, black)
4. Create placeholder route handlers returning mock data
5. Generate TypeScript API client from OpenAPI spec
6. Test: Python backend returns valid mock responses, TS client compiles

**Deliverables:**
- `src/backend/openapi.yaml` — API specification
- `src/backend/app/main.py` — FastAPI app with placeholder routes
- `src/lib/api-client/` — Generated TypeScript client
- `src/backend/pyproject.toml` — Python dependencies

**Checkpoint:** Backend returns mock responses matching OpenAPI spec, frontend client generates successfully, all tests pass.

---

### Step 2: Migrate Database Access Layer to Python

**Duration:** 5-7 days

**Goal:** Replace Drizzle ORM with SQLAlchemy, preserve all database operations.

**Tasks:**
1. Create SQLAlchemy ORM models matching Drizzle schema (sessions, embeddings, leads, etc.)
2. Setup async database session management (asyncpg)
3. Implement repository pattern for data access (session_repo, embedding_repo, lead_repo)
4. Setup Alembic for migrations (initial no-op migration)
5. Implement vector search in Python using pgvector
6. Test: All database operations work in Python, vector search matches TS results

**Deliverables:**
- `src/backend/app/db/models/` — SQLAlchemy models
- `src/backend/app/db/repositories/` — Repository classes
- `src/backend/app/db/session.py` — Async session factory
- `src/backend/alembic/` — Alembic configuration and migrations
- Integration tests with Docker Postgres

**Checkpoint:** Database queries return same results as TypeScript implementation, test coverage ≥80%, vector search validated.

---

### Step 3: Migrate Embedding and Model Provider Services

**Duration:** 4-5 days

**Goal:** Move embedding generation and LLM provider abstractions to Python.

**Tasks:**
1. Implement embedding provider abstraction (base class + Gemini provider)
2. Add batching and caching for embeddings
3. Implement LLM provider abstraction (base class + Groq/Gemini providers)
4. Add retry logic and error handling (tenacity library)
5. Preserve behavior from TypeScript implementations (temperature, safety filters)
6. Test: Embeddings match TS output (cosine similarity ≈ 1.0), LLM responses equivalent

**Deliverables:**
- `src/backend/app/services/embeddings/` — Embedding providers
- `src/backend/app/services/llm/` — LLM providers
- Unit tests with mocked APIs
- Integration tests with real APIs (limited runs)

**Checkpoint:** Embeddings and LLM calls work reliably, response quality matches current system, error handling robust.

---

### Step 4: Migrate RAG Pipeline and Chunking Logic

**Duration:** 5-6 days

**Goal:** Move content chunking and retrieval logic to Python, leveraging LangChain or similar libraries.

**Tasks:**
1. Implement text chunking in Python (translate `chunkText` from TS)
2. Maintain markdown-aware splitting and token counting (tiktoken)
3. Implement vector retrieval service (translate `retrieveRelevantChunks`)
4. Create RAG pipeline orchestration (query → embedding → retrieval → formatting)
5. Behavior preservation validation (compare TS vs Python RAG results)
6. Test: RAG pipeline returns equivalent results, chunk boundaries consistent

**Deliverables:**
- `src/backend/app/services/rag/` — RAG pipeline (chunker, retriever, pipeline)
- Comparison tests with 50+ test queries
- Benchmark results (latency, accuracy)

**Checkpoint:** RAG pipeline returns equivalent results to TypeScript, performance equal or better, chunk boundaries consistent.

---

### Step 5: Migrate Agent Logic and Orchestration

**Duration:** 7-10 days (most complex step)

**Goal:** Move multi-agent orchestration and specialized agents to Python.

**Tasks:**
1. Migrate agent abstractions (base agent, certification, trip, safety, retrieval agents)
2. Migrate orchestration logic (chat orchestrator, session manager)
3. Migrate prompt management (system prompts, mode detection, prompt builders)
4. Decide on orchestration framework (custom vs LangChain vs LangGraph) — recommend custom for V1
5. Implement chat API handler (`POST /chat` route)
6. Test: All agents respond appropriately, orchestration flow matches TS, session history preserved

**Deliverables:**
- `src/backend/app/agents/` — Agent implementations
- `src/backend/app/orchestration/` — Chat orchestrator
- `src/backend/app/prompts/` — System prompts
- `src/backend/app/api/routes/chat.py` — Chat endpoint handler
- Comparison tests with 50+ test conversations

**Checkpoint:** Agents respond appropriately, orchestration matches TypeScript behavior, no response quality regressions.

---

### Step 6: Migrate Content Ingestion and Validation Scripts

**Duration:** 3-4 days

**Goal:** Migrate offline content processing scripts from TypeScript to Python.

**Tasks:**
1. Migrate content validation script (markdown parsing, frontmatter validation)
2. Migrate content ingestion script (chunking, embedding, database insert)
3. Add incremental ingestion (skip unchanged files)
4. Migrate RAG benchmark script
5. Update CI/CD to run Python scripts
6. Test: Scripts run successfully, embeddings generated correctly, validation catches errors

**Deliverables:**
- `src/backend/scripts/` — Python scripts (ingest, validate, benchmark)
- Updated `package.json` scripts to call Python equivalents
- CI/CD workflows updated

**Checkpoint:** Scripts run successfully, embeddings identical to TypeScript version, CI/CD pipeline passes.

---

### Step 7: Update Frontend to Use Python Backend API

**Duration:** 3-4 days

**Goal:** Connect TypeScript frontend to Python backend, remove Next.js API route proxies.

**Tasks:**
1. Configure API client wrapper (generated TypeScript client)
2. Update Next.js API routes to proxy to Python backend (or remove if direct calls)
3. Implement CORS in Python backend (allow frontend origin)
4. Handle session management (cookies or headers)
5. Test: Frontend calls Python backend successfully, session persistence works, errors handled gracefully

**Deliverables:**
- `src/lib/api-client/client.ts` — Configured API client
- `src/app/api/chat/route.ts` — Updated to proxy (or removed)
- CORS middleware in `src/backend/app/main.py`
- Integration tests (frontend → backend)

**Checkpoint:** Frontend successfully calls Python backend, session persistence works, no CORS issues, errors handled gracefully.

---

### Step 8: Deployment and Infrastructure Setup

**Duration:** 5-7 days

**Goal:** Deploy Python backend and TypeScript frontend to production with monitoring and rollback capability.

**Tasks:**
1. Containerize Python backend (Dockerfile)
2. Deploy Python backend to Cloud Run (staging first)
3. Configure DNS and CORS (api.dovvybuddy.com → Cloud Run)
4. Deploy Next.js frontend to Vercel (staging first)
5. Setup monitoring (Sentry, Cloud Run metrics, structured logging)
6. Document deployment process and rollback procedures
7. Execute staged rollout (10% → 25% → 50% → 100%)
8. Test: Production deployment successful, monitoring active, rollback tested

**Deliverables:**
- `src/backend/Dockerfile` — Container image
- `.github/workflows/deploy-backend.yml` — CI/CD for backend
- `docs/deployment.md` — Deployment documentation
- Production deployment completed
- Monitoring dashboards configured

**Checkpoint:** Production deployment successful, frontend and backend communicate, monitoring active, rollback tested, no critical errors.

---

## 11. Success Criteria

### Technical Success

✅ **All 8 implementation steps completed** with checkpoints met  
✅ **Test coverage ≥80%** for Python backend  
✅ **API contract preserved** — frontend unchanged except HTTP client  
✅ **Database schema unchanged** — existing data intact  
✅ **Performance maintained or improved** — latency ≤5s (P95), RAG retrieval ≤500ms  
✅ **Comparison tests pass** — RAG results, embeddings, orchestration equivalent to TS  
✅ **Production deployment stable** — error rate <1%, no critical bugs  
✅ **Rollback tested** — can revert to TS backend in <10 minutes  

### User Success

✅ **Zero user-facing disruptions** during migration  
✅ **Response quality maintained or improved** (manual spot checks)  
✅ **Chat latency within acceptable range** (<5s for 95% of requests)  
✅ **No data loss** — all sessions and leads preserved  

### Business Success

✅ **Python backend enables Telegram bot** (PR8b can proceed)  
✅ **Foundation for advanced ML features** (LangChain, custom models, etc.)  
✅ **Operational complexity manageable** — monitoring, CI/CD, deployment documented  
✅ **Technical debt reduced** — cleaner separation of concerns, better testability  

---

## 12. Open Questions & Decisions

### Q1: Orchestration Framework Choice

**Question:** Use custom orchestration, LangChain, or LangGraph for agent coordination?

**Options:**
- **A) Custom orchestration** — Simple, explicit, no external dependencies
- **B) LangChain agents/chains** — Mature ecosystem, built-in tools, memory
- **C) LangGraph** — Advanced multi-agent workflows, better observability

**Recommendation:** **Option A (custom)** for V1. Migrate to LangGraph post-PR7 if complexity increases.

**Decision:** TBD (to be finalized in Step 5)

---

### Q2: Deployment Platform for Python Backend

**Question:** Deploy Python backend to Cloud Run, Railway, or Render?

**Options:**
- **A) Cloud Run** — Google-native, auto-scales, serverless, but has cold starts
- **B) Railway** — Simpler setup, fixed pricing, always-on, but less scalable
- **C) Render** — Similar to Railway, good DX, free tier for testing

**Recommendation:** **Cloud Run for production** (better scaling), **Railway for staging** (easier setup).

**Decision:** TBD (to be finalized in Step 8)

---

### Q3: Frontend API Call Strategy

**Question:** Should frontend call Python backend directly (client-side) or proxy through Next.js API routes?

**Options:**
- **A) Direct calls** — Lower latency, simpler, but exposes backend URL
- **B) Next.js proxy** — Enables SSR, hides backend, but adds hop

**Recommendation:** **Option B (Next.js proxy)** for V1 (Step 7), migrate to **Option A** post-PR5 when chat UI is built.

**Decision:** TBD (to be finalized in Step 7)

---

### Q4: Chunking Strategy Changes

**Question:** If chunking parameters need tuning, should we re-ingest all content?

**Options:**
- **A) Keep current chunking** — No re-ingestion, faster migration
- **B) Optimize chunking** — Better RAG quality, but requires full re-ingestion

**Recommendation:** **Option A** for migration (Step 4). Defer chunking optimization to post-migration iteration (PR10 or later).

**Decision:** TBD (to be validated in Step 4 comparison tests)

---

### Q5: Migration Timeline and Resource Allocation

**Question:** Can solo founder complete this in 6-9 weeks while maintaining other PRs (PR5 Chat UI, PR4 Lead Capture)?

**Risk:** Migration workload may delay other features. Alternatively, pausing other PRs may slow product development.

**Recommendation:**
- **Sprint 1 (Steps 1-4):** Focus 80% time on migration, 20% on PR5 frontend planning
- **Sprint 2 (Steps 5-6):** 100% focus on migration (most complex steps)
- **Sprint 3 (Steps 7-8):** 60% migration, 40% PR5 frontend work (can parallelize)

**Decision:** TBD (to be confirmed based on current workload and priorities)

---

## 13. Related Documentation

### Technical References

- **PSD V6.2:** `/docs/psd/DovvyBuddy-PSD-V6.2.md` — Product requirements and constraints
- **MASTER PLAN:** `/docs/plans/MASTER_PLAN.md` — Overall architecture and technology stack
- **PR1:** `/docs/plans/PR1-Database-Schema.md` — Database schema foundation
- **PR2:** `/docs/plans/PR2-RAG-Pipeline.md` — Current TypeScript RAG implementation
- **PR3:** `/docs/plans/PR3-Model-Provider-Session.md` — Current orchestration architecture
- **PR8b:** `/docs/plans/PR8b-Telegram-Bot-Adapter.md` — Future Telegram integration (enabled by this migration)

### External Documentation

- **FastAPI:** https://fastapi.tiangolo.com/ — Python web framework
- **SQLAlchemy:** https://www.sqlalchemy.org/ — Python ORM
- **Alembic:** https://alembic.sqlalchemy.org/ — Database migrations
- **pgvector Python:** https://github.com/pgvector/pgvector-python — Vector search
- **OpenAPI Generator:** https://openapi-generator.tech/ — TypeScript client generation
- **Cloud Run:** https://cloud.google.com/run/docs — Deployment platform
- **Pydantic:** https://docs.pydantic.dev/ — Request/response validation

---

## 14. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-01 | AI Assistant | Initial draft based on refactor plan |

---

## 15. Approval & Sign-off

**Technical Reviewer:** _TBD_  
**Product Owner:** _TBD_  
**Solo Founder Approval:** _TBD_

**Status:** 🟡 Draft — Pending review and decision on open questions

---

**End of PR3.2 Plan**
