# PR6.3a: Token Tracking & Cost Logging

**Part of Epic:** PR6.3 Gemini API Cost Efficiency Optimization

**Status:** Implementation Complete

**Owner:** jefflyt

**Date:** 2026-02-08

---

## Goal

Implement detailed token tracking and cost calculation at every Gemini API call point to establish baseline metrics and identify cost leaks. This PR provides visibility without changing behavior.

---

## Scope

**In scope:**
- Extend `LLMResponse` dataclass with token breakdown fields
- Extract and log `usage_metadata` from Gemini API responses
- Calculate cost in USD based on Gemini 2.5 Flash Lite pricing
- Add structured logging at LLM, orchestrator, and agent levels
- Create token counting utility for RAG context
- Log token breakdown: prompt_tokens, completion_tokens, total_tokens, cost_usd

**Out of scope:**
- Token usage aggregation dashboard (future)
- Real-time cost alerts (future)
- Any optimization or behavior changes
- Historical token analysis tools

---

## Backend Changes

### APIs to modify

None (logging only, no API contract changes)

### Services/modules to add/modify

**1. `backend/app/services/llm/types.py`**

Extend `LLMResponse` dataclass:
- Add `prompt_tokens: Optional[int]`
- Add `completion_tokens: Optional[int]`
- Add `cost_usd: Optional[float]`
- Keep `tokens_used` as backward-compatible total

**2. `backend/app/services/llm/gemini.py`**

In `generate()` method:
- Extract from `response.usage_metadata`:
  - `prompt_token_count`
  - `candidates_token_count`
  - `total_token_count`
- Calculate cost using Gemini 2.5 Flash Lite pricing:
  - Input: $0.15 per 1M tokens
  - Output: $0.60 per 1M tokens
  - Formula: `(prompt_tokens * 0.15 + completion_tokens * 0.60) / 1_000_000`
- Add structured log after successful generation
- Add fallback if `usage_metadata` is None

**3. `backend/app/services/rag/token_utils.py` (NEW)**

Create new module with:
- Function `count_tokens(text: str) -> int`
  - Uses `tiktoken.encoding_for_model("gpt-3.5-turbo")` (existing pattern)
  - Returns token count
- Function `calculate_gemini_cost(prompt_tokens: int, completion_tokens: int) -> float`
  - Calculates cost in USD
  - Returns formatted float (4 decimal places)

**4. `backend/app/orchestration/gemini_orchestrator.py`**

In `route_request()`, after LLM call:
- Extract routing token usage from response
- Calculate routing cost
- Log routing decision with tokens and cost

**5. `backend/app/orchestration/context_builder.py`**

Before passing RAG context to agent:
- Count tokens using `count_tokens(rag_context)`
- Log RAG context preparation with token count

**6. `backend/app/agents/base.py`**

In `execute()` method, after LLM generation:
- Log agent execution complete with token breakdown
- Include: agent_type, total_tokens, cost_usd, rag_tokens, history_messages

### Auth, validation, error handling

- Add fallback if `usage_metadata` is None (log warning, continue without token data)
- Token tracking failures should not break requests
- Cost calculation errors should not propagate (default to None)

---

## Frontend Changes

No changes.

---

## Data Changes

No migrations or schema changes.

---

## Infra / Config

No new environment variables.

---

## Testing

### Unit tests

- `test_llm_response_extended_fields()` - Verify new fields in LLMResponse
- `test_cost_calculation()` - Verify formula: `(100k*0.15 + 50k*0.60)/1M = $0.045`
- `test_cost_calculation_edge_cases()` - Zero tokens, None tokens, large numbers
- `test_token_counting_utility()` - Verify count_tokens() matches tiktoken
- `test_fallback_missing_usage_metadata()` - Verify graceful handling

### Integration tests

- `test_llm_generate_logs_tokens()` - Verify log output contains all token fields
- `test_orchestrator_logs_routing_tokens()` - Verify routing logs tokens
- `test_agent_logs_execution_tokens()` - Verify agent logs include token breakdown
- `test_rag_token_counting()` - Verify RAG context tokens logged

### Manual checks

- Run 10 chat queries with varying complexity
- Inspect logs for structured token data
- Verify all LLM calls have token logs
- Calculate total cost for 10 queries
- Identify highest token consumers (routing vs agent vs RAG)

---

## Verification

### Commands to run

- Install: `cd backend && .venv/bin/pip install -e .`
- Dev: `cd backend && .venv/bin/uvicorn app.main:app --reload`
- Test: `cd backend && .venv/bin/pytest tests/unit/services/test_llm.py -v`
- Test: `cd backend && .venv/bin/pytest tests/integration/services/test_llm_integration.py -v`
- Lint: `cd backend && .venv/bin/ruff check app/`
- Typecheck: `cd backend && .venv/bin/mypy app/`

### Manual verification checklist

1. Start backend server
2. Send chat request: POST /api/chat with message "Where can I dive in Tioman?"
3. Check logs for "LLM generation complete" with prompt_tokens, completion_tokens, cost_usd
4. Check logs for "Routing decision" with routing_tokens, routing_cost_usd
5. Check logs for "Agent execution complete" with total_tokens, cost_usd
6. Verify no errors if usage_metadata missing (test by mocking)
7. Calculate total cost from logs, verify reasonable (<$0.05 per query)

---

## Rollback Plan

**Feature flag / kill switch:** None needed (logging only, no behavior change)

**Revert strategy:**
- Revert PR6.3a if logging causes performance issues
- No data loss risk (logging only)
- No user-facing impact

---

## Dependencies

**PRs required before this one:** None (foundational)

**External dependencies:**
- Gemini API must return usage_metadata (assumed available)

---

## Risks & Mitigations

**Risk 1: Gemini API may not always return usage_metadata**
- **Mitigation:** Add fallback to None, log warning, continue without token data
- **Impact:** Some requests won't have token data, but won't break

**Risk 2: Logging overhead could slow requests**
- **Mitigation:** Structured logging is fast (<5ms overhead)
- **Mitigation:** Async logging in Python logging module
- **Impact:** Negligible (<10ms expected)

**Risk 3: Token counting with tiktoken inaccurate for Gemini**
- **Mitigation:** Tiktoken (GPT-3.5) is close approximation; exact counts from API
- **Impact:** RAG token estimates may be off by 5-10%, but API provides exact totals

---

## Success Metrics

- All Gemini API calls log token usage and cost
- Baseline metrics established (avg tokens per query, cost per query)
- Token breakdown available for all components (routing, RAG, history, LLM)
- No performance degradation from logging overhead (<10ms)
- Zero requests fail due to token tracking issues

---

## Implementation Status (2026-02-08)

**Completed:**
- Extended `LLMResponse` with `prompt_tokens`, `completion_tokens`, `cost_usd`
- Added Gemini token/cost extraction + logging in LLM provider
- Added routing token/cost logging in orchestrator
- Added RAG token counting + logging in context builder
- Added agent-level token/cost logging and metadata propagation
- Added unit tests for token utils and LLMResponse extended fields

**Pending:**
* Run manual log verification (10 query baseline) and capture results

**Done since last update:**
- Full backend integration suite passed (38 tests)
- Gemini embedding model verified via gemini-embedding-001 for integration coverage

**Next PR:** PR6.3b (Prompt Compression)
