# Backend Integration Update (2026-03-02)

## Scope

This update captures the latest backend changes merged into `main` and validated in the current codespace.

## Implemented Changes

1. ADK orchestration runtime hardening
- Added ADK-native graph module at `src/backend/app/adk/`.
- `ChatOrchestrator` now supports:
  - native ADK graph path (`ENABLE_ADK_NATIVE_GRAPH=true`)
  - legacy ADK router fallback path (`ENABLE_ADK_NATIVE_GRAPH=false`)
- Route failure fallback now defaults to `general_retrieval_specialist` instead of hard failure.

2. Shared free-tier quota enforcement
- Added process-level quota manager: `src/backend/app/core/quota_manager.py`.
- Enforced buckets:
  - `text_generation` (LLM + ADK controller/router calls)
  - `embedding`
- Added queue-and-wait backpressure for RPM/TPM and fail-fast behavior for RPD exhaustion.

3. Cost and token accounting
- Added `src/backend/app/services/cost/token_cost.py`.
- Gemini LLM responses now include:
  - `prompt_tokens`
  - `completion_tokens`
  - `tokens_used`
  - `cost_usd`

4. Streaming endpoint upgrade
- `POST /api/chat/stream` now returns structured SSE event payloads aligned with orchestration flow:
  - `route`
  - `safety`
  - `token`
  - `citation`
  - `final`
  - `error`

5. Integration/test reliability improvements
- Added `--import-mode=importlib` in `src/backend/pytest.ini` to avoid duplicate module import collisions.
- Updated ingestion integration tests to use in-memory test doubles (no external DB/network requirement).
- Added unit coverage for quota manager behavior and integration coverage for chat stream events.

## Config Defaults (Gemini Free Tier Profile)

- `LLM_RPM_LIMIT=15`
- `LLM_TPM_LIMIT=250000`
- `LLM_RPD_LIMIT=1000`
- `EMBEDDING_RPM_LIMIT=100`
- `EMBEDDING_TPM_LIMIT=30000`
- `EMBEDDING_RPD_LIMIT=1000`
- `RATE_WINDOW_SECONDS=60`
- `QUOTA_PROFILE_NAME=gemini_free_tier`
- `QUOTA_ENFORCEMENT_ENABLED=true`

## Verification Status

Validated in this codespace on 2026-03-02:

- Full backend suite: `243 passed, 10 skipped`
- Integration suite: `27 passed, 10 skipped`

Warnings were non-blocking upstream SDK deprecation warnings from `google.genai`.
