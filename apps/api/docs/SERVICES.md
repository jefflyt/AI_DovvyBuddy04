# DovvyBuddy Backend Services

This document describes the current Python backend service architecture, including ADK orchestration, RAG, and quota controls.

## Scope

Backend location: `apps/api/`

Primary capabilities:

- ADK-based multi-agent orchestration
- RAG retrieval with citations
- emergency and medical safety classification
- Gemini LLM and embedding providers
- free-tier-safe quota enforcement

## Service Architecture

### 1) Orchestration Layer

- `app/orchestration/orchestrator.py` (`ChatOrchestrator`)
  - Entrypoint for chat execution and SSE streaming.
  - Handles emergency pre-check first.
  - Manages DB-backed session continuity.
  - Adds structured metadata (`route_decision`, `safety_classification`, `policy_enforced`, `citations`, `quota_snapshot`).

- `app/adk/graph_orchestrator.py` (`ADKNativeGraphOrchestrator`)
  - Native ADK coordinator + specialist graph.
  - Enabled via `ENABLE_ADK_NATIVE_GRAPH=true`.

- `app/orchestration/gemini_orchestrator.py` (`GeminiOrchestrator`)
  - Legacy ADK function-call router for staged fallback.
  - Used when native graph is disabled or unavailable.

### 2) ADK Tool Contracts

`app/adk/tools.py` is the shared tool source of truth:

- `rag_search_tool(query, filters)` -> chunks/citations/has_data
- `session_context_tool(session_id)` -> history/state/profile
- `safety_classification_tool(message, history)` -> emergency/medical/non_medical
- `response_policy_tool(answer, citations, safety_flags)` -> policy enforcement verdict

### 3) LLM + Embedding Providers

- `app/services/llm/gemini.py`
  - Gemini text generation.
  - Token/cost capture in `LLMResponse` (`prompt_tokens`, `completion_tokens`, `tokens_used`, `cost_usd`).
  - Shared quota reservation before provider call.

- `app/services/embeddings/gemini.py`
  - Gemini embedding generation (`text-embedding-004`).
  - Matryoshka-compatible output dimensions.
  - Shared quota reservation before provider call.

### 4) Cost and Quota Controls

- `app/services/cost/token_cost.py`
  - token estimation/counting utilities
  - Gemini cost estimation helper

- `app/core/quota_manager.py`
  - Central process-level quota manager
  - Buckets: `text_generation`, `embedding`
  - Sliding-window RPM/TPM + rolling 24h RPD
  - Queue-and-wait for RPM/TPM pressure
  - Fail-fast on RPD exhaustion

## API Runtime Notes

### `POST /api/chat`

- Contract remains backward compatible.
- Additional metadata fields may be present:
  - `route_decision`
  - `safety_classification`
  - `policy_enforced`
  - `citations`
  - `quota_snapshot`

### `POST /api/chat/stream`

SSE event types:

- `route`
- `safety`
- `token`
- `citation`
- `final`
- `error`

## Setup

### 1. Install

```bash
cd apps/api
pip install -e .
```

### 2. Environment

Use root `.env.local`:

```bash
cp .env.example .env.local
# then set GEMINI_API_KEY and DATABASE_URL
```

### 3. Run Backend

From repository root:

```bash
export PYTHONPATH="$PWD/apps/api"
.venv/bin/uvicorn app.main:app --reload --app-dir apps/api --port 8000
```

## Configuration Reference

Defaults reflect Gemini free-tier-safe profile and can be overridden by environment variables.

### ADK / Orchestration

- `ENABLE_ADK=true`
- `ENABLE_AGENT_ROUTING=true`
- `ENABLE_ADK_NATIVE_GRAPH=false`
- `ADK_MODEL=gemini-2.5-flash-lite`

### LLM Quota Controls

- `QUOTA_ENFORCEMENT_ENABLED=true`
- `QUOTA_PROFILE_NAME=gemini_free_tier`
- `RATE_WINDOW_SECONDS=60`
- `LLM_RPM_LIMIT=15`
- `LLM_TPM_LIMIT=250000`
- `LLM_RPD_LIMIT=1000`

### Embedding Quota Controls

- `EMBEDDING_RPM_LIMIT=100`
- `EMBEDDING_TPM_LIMIT=30000`
- `EMBEDDING_RPD_LIMIT=1000`
- `EMBEDDING_MODEL=text-embedding-004`
- `EMBEDDING_DIMENSION=768`

### RAG

- `ENABLE_RAG=true`
- `RAG_TOP_K=8`
- `RAG_MIN_SIMILARITY=0.5`

## Testing

Run from repository root:

```bash
export PYTHONPATH="$PWD/apps/api"
.venv/bin/python -m pytest apps/api/tests -q
```

Notes:

- `pytest.ini` already sets `--import-mode=importlib`.
- Some service integration tests are skipped when `GEMINI_API_KEY` is missing.
- Ingestion integration tests run with in-memory test doubles (no external DB required).

## Key Paths

```
apps/api/app/
├── adk/                     # ADK-native graph, tools, typed contracts
├── orchestration/           # Chat orchestrator and legacy ADK router fallback
├── core/
│   ├── config.py            # Settings and defaults
│   └── quota_manager.py     # Shared quota enforcement
├── services/
│   ├── cost/                # Token/cost utilities
│   ├── embeddings/          # Gemini embeddings
│   ├── llm/                 # Gemini text generation
│   └── rag/                 # Retrieval pipeline
└── api/routes/chat.py       # /api/chat + /api/chat/stream
```
