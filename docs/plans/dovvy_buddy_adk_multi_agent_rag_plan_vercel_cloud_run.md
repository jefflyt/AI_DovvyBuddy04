# DovvyBuddy (Google ADK) — Multi-Agent RAG Implementation Plan (Vercel + Cloud Run)

> Target: **TypeScript/Next.js frontend on Vercel** + **Python (Google ADK) backend on Google Cloud Run**. The backend enforces grounding, type contracts, citations, and safety before the UI renders anything.  
> Source architecture baseline: Brain/Face/Bridge + RAF + ADK API Server/SSE. 【6†DovvyBuddy_ Python-Backend & TypeScript-Frontend Architecture Guide.pdf】

---

## 0) Assumptions
- Monorepo (`backend/`, `frontend/`) but deployed as **two independent surfaces**.
- Backend exposes **REST + SSE** (streaming) endpoints.
- RAG retrieval uses either **Vertex AI RAG Engine** or your own vector store (choose one and keep a single tool wrapper).

---

## 1) Target Architecture

### 1.1 Split-stack
- **Brain (Backend | Python + ADK)**: intent routing, multi-agent orchestration, RAG retrieval, safety checks.
- **Face (Frontend | Next.js + TS)**: chat UI, renders streamed events, citations, error states.
- **Bridge (API)**: FastAPI + ADK Router exposing standardized endpoints and SSE streams. 【6†DovvyBuddy_ Python-Backend & TypeScript-Frontend Architecture Guide.pdf】

### 1.2 RAF requirements (backend-enforced)
- Grounded retrieval + citations.
- Type-safe request/response contracts.
- Structured error responses (never “hallucinated” strings for failures). 【6†DovvyBuddy_ Python-Backend & TypeScript-Frontend Architecture Guide.pdf】

---

## 2) Repo Structure (recommended)

```
dovvybuddy/
  backend/
    agents/
      orchestrator.py
      retriever.py
      safety.py
    rag/
      tools.py
      schemas.py
      ingestion/
        ingest.py
        chunking.py
    api/
      server.py
      schemas.py
    core/
      config.py
      logging.py
      exceptions.py
    tests/
    Dockerfile
    pyproject.toml (or requirements.txt)

  frontend/
    src/
      app/
      components/
      hooks/
      types/
      lib/
    next.config.js
    package.json

  docs/
    DECISIONS.md
    ASSUMPTIONS.md
    SAFETY.md
    RAG_DESIGN.md

  README.md
```

---

## 3) Backend (Python + Google ADK) — Build Tasks

### 3.1 Dependencies
- Python 3.10+
- `google-adk`, `google-cloud-aiplatform`, `fastapi`, `uvicorn[standard]` (+ your RAG/vector deps) 【6†DovvyBuddy_ Python-Backend & TypeScript-Frontend Architecture Guide.pdf】

### 3.2 Multi-agent topology (minimum viable)
- **Root agent** (UI talks to this only): `dovvy_orchestrator`
- **Retriever specialist**: `dovvy_retriever` (retrieval-only; returns `NO_DATA` when empty)

Doc baseline indicates a hierarchical orchestrator pattern where the root agent manages sub-agents internally. 【6†DovvyBuddy_ Python-Backend & TypeScript-Frontend Architecture Guide.pdf】

### 3.3 RAG tool wrapper (single interface)
Implement a single tool abstraction used by `dovvy_retriever`:
- `rag_search(query: str, filters: dict) -> RagResult`
- `RagResult` must include:
  - `chunks[]: { doc_id, title, snippet, url?, score? }`
  - `citations[]: { doc_id, locator? }` (canonical ids)
- If no results: return `NO_DATA`

### 3.4 API Bridge (FastAPI + ADK Router)
- Run FastAPI and mount the ADK Router under `/api`.
- Provide streaming endpoint (SSE) consistent with ADK server pattern (example in doc):
  - `POST /api/apps/dovvy/sessions/{id}/run_sse` 【6†DovvyBuddy_ Python-Backend & TypeScript-Frontend Architecture Guide.pdf】

Backend endpoints (minimum):
- `GET /health` (version/build + dependency status)
- Streaming chat: `POST /api/apps/dovvy/sessions/{id}/run_sse`
- Optional non-stream chat: `POST /api/chat` (returns final JSON)

### 3.5 RAF enforcement rules (non-negotiable)
- If an answer contains factual claims:
  - must have at least one valid citation.
  - if missing citations, respond with uncertainty + ask for clarification.
- If retrieval returns `NO_DATA`:
  - respond: “Not found in sources” + suggest next question or ask user to provide doc.
- Dive safety:
  - append safety disclaimers for operational dive guidance.
  - refuse unsafe guidance and redirect to certified professional judgment.

---

## 4) Frontend (Next.js + TypeScript) — Build Tasks

### 4.1 Type-safe streaming DTOs
Define an event envelope for streamed responses:
- `type: 'text' | 'tool_call' | 'citation' | 'error'`
- `content: string`
- `metadata?: { confidence_score?: number; doc_id?: string }` 【6†DovvyBuddy_ Python-Backend & TypeScript-Frontend Architecture Guide.pdf】

### 4.2 SSE consumption
- Implement `useDovvyChat()` hook:
  - optimistic append user message
  - call backend SSE endpoint
  - parse SSE frames and append events

### 4.3 RAF-aware rendering
- Render citations as distinct UI blocks (e.g., “Source Verified”).
- Render `NO_DATA` and structured errors clearly.

---

## 5) Deployment Plan (Vercel + Cloud Run)

### 5.1 Deployment topology
- **Frontend**: Vercel (Next.js)
- **Backend**: Google Cloud Run (Python/ADK + FastAPI)
- **Communication**: Browser (or Vercel) calls Cloud Run endpoint over HTTPS.

### 5.2 Recommended integration pattern (simplest)
**Frontend calls backend directly** using `NEXT_PUBLIC_BACKEND_URL`.
- Pros: simplest, least moving parts, streaming SSE works directly.
- Cons: requires correct **CORS** configuration on Cloud Run.

**CORS on backend**
- Allow origins:
  - `https://<your-vercel-domain>` (preview and prod) and your custom domain if used.
- Allow methods/headers needed for SSE:
  - `POST`, `OPTIONS`
  - `Content-Type`, `Authorization` (if used)

### 5.3 Alternative pattern (if you want same-origin)
Use **Vercel rewrites** to proxy `/api/*` to Cloud Run.
- Pros: avoids CORS, cleaner client code (`/api/...`).
- Cons: must confirm streaming behavior through rewrites in your setup.

Example (conceptual) in `frontend/vercel.json`:
```json
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "https://<cloud-run-url>/api/:path*" }
  ]
}
```

### 5.4 Cloud Run backend build + deploy checklist
Backend must be containerized and deployed to Cloud Run.

**Dockerfile (backend)**
- Python 3.10 base
- install deps
- run `uvicorn api.server:app --host 0.0.0.0 --port 8080`

**Deploy (conceptual)**
- `gcloud run deploy dovvy-backend \
  --source backend \
  --region <region> \
  --allow-unauthenticated (or authenticated, see below) \
  --set-env-vars ...`

**Auth choice**
- MVP simplest: `--allow-unauthenticated` + server-side safety guardrails.
- More secure: require auth (Cloud Run IAM) and use a server-side proxy (Vercel API route) to attach identity.

**Cloud Run config**
- Set request timeout high enough for longer answers/streams.
- Set concurrency appropriately.
- Consider minimum instances = 1 if cold start is unacceptable.

### 5.5 Vercel frontend deploy checklist
- Connect `frontend/` directory to Vercel project.
- Set environment variables:
  - `NEXT_PUBLIC_BACKEND_URL=https://<cloud-run-url>` (or use rewrites)
- Ensure Node runtime compatible (Node 18+ recommended).

---

## 6) Environment Variables (minimum)

### Backend (Cloud Run)
- `GOOGLE_APPLICATION_CREDENTIALS` (prefer Workload Identity in Cloud Run)
- `VERTEX_PROJECT_ID`
- `VERTEX_LOCATION`
- `RAG_KB_NAME` or `RAG_INDEX_ID`
- `MODEL_ORCHESTRATOR` (e.g. gemini-1.5-pro)
- `MODEL_RETRIEVER` (e.g. gemini-1.5-flash)
- `CORS_ORIGINS` (vercel domains)
- `LOG_LEVEL`

### Frontend (Vercel)
- `NEXT_PUBLIC_BACKEND_URL` (Cloud Run base URL)
- `NEXT_PUBLIC_ENV` (`dev|staging|prod`)

---

## 7) Required Docs (ship these early)
- `docs/DECISIONS.md` (deployment choice: Vercel + Cloud Run)
- `docs/ASSUMPTIONS.md`
- `docs/SAFETY.md` (dive disclaimers + refusal rules)
- `docs/RAG_DESIGN.md` (sources + licensing + chunking + evaluation)

---

## 8) MVP “Done” Criteria

Backend:
- Root agent routes to retriever when grounding needed.
- Retriever returns citations or `NO_DATA`.
- Orchestrator blocks uncited factual claims.
- SSE endpoint works end-to-end.
- Safety disclaimers enforced.

Frontend:
- Chat UI supports streaming.
- Citations are visible and distinct.
- Error/NO_DATA states are clear.

Deployment:
- Frontend deployed on Vercel.
- Backend deployed on Cloud Run.
- CORS and env vars verified.

---

## 9) Next Actions (implement in this order)
1) Scaffold backend API server + ADK root agent + retriever tool wrapper.
2) Implement SSE endpoint via ADK router.
3) Implement frontend hook to consume SSE + RAF-aware rendering.
4) Local E2E test (frontend → backend SSE → retriever → response).
5) Deploy backend to Cloud Run; deploy frontend to Vercel.
6) Add minimal eval set + logging for missing citations/hallucinations.

