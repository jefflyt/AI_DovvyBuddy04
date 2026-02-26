# Technical Debt

**Last Updated:** February 26, 2026

---

## Current Runtime Snapshot

- Backend runtime: Python FastAPI (`src/backend`)
- Orchestration: strict Google ADK (`ENABLE_ADK=true`)
- LLM model: `gemini-2.5-flash-lite`
- Embeddings: `text-embedding-004` at 768 dimensions
- Test status baseline: backend unit + integration suites passing

---

## Active Technical Debt

### 1. Deprecation Warnings in Runtime and Tests

**Scope:** Pydantic `Config` class usage and FastAPI `on_event` startup hooks  
**Impact:** No runtime failure, but adds warning noise and future upgrade risk  
**Priority:** Medium  
**Recommended Fix:**

- Migrate Pydantic models to `ConfigDict`
- Migrate FastAPI startup/shutdown handling to lifespan events

### 2. Documentation Drift in Historical Records

**Scope:** Legacy planning/project-management records still describe older provider and migration phases  
**Impact:** Possible confusion for new contributors if historical docs are treated as runtime source of truth  
**Priority:** Low  
**Recommended Fix:**

- Keep historical docs unchanged as records
- Maintain current-state docs in `README*.md`, `docs/technical/`, and `src/backend/docs/`
- Add clear “historical record” labels where needed

### 3. Uvicorn Local Run Instability (Environment-Specific)

**Scope:** Local `uvicorn` exits observed in certain terminal sessions (exit 137/1)  
**Impact:** Intermittent local startup friction  
**Priority:** Medium  
**Recommended Fix:**

- Capture stable repro steps and shell env details
- Add a dedicated troubleshooting subsection in backend runtime docs

---

## Recently Resolved Debt

- Circular import risk in orchestration package initialization
- Stale backend unit tests after async API/signature changes
- Integration drift for RAG/ingestion/session contracts
- Repository field mismatch (`chunk_text` vs legacy `content`) and vector SQL binding issues

---

## Tracking

Track new debt items as GitHub issues with label `technical-debt` and link to impacted docs/code paths.
