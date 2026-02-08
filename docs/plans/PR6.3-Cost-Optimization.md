# PR6.3: Gemini API Cost Efficiency Optimization

**Epic Goal:** Reduce Gemini API token consumption and costs by 40-50% through comprehensive token tracking, prompt optimization, intelligent RAG context management, and conversation history optimization.

**Target Model:** Gemini 2.5 Flash Lite (maintain consistency across all LLM operations)

**Status:** Implementation Complete

**Owner:** jefflyt

**Date:** 2026-02-08

---

## Table of Contents

1. [Overview](#overview)
2. [Feature/Epic Summary](#featureepic-summary)
3. [Complexity & Fit](#complexity--fit)
4. [Full-Stack Impact](#full-stack-impact)
5. [PR Roadmap](#pr-roadmap)
   - [PR6.3a: Token Tracking & Cost Logging](#pr63a-token-tracking--cost-logging)
   - [PR6.3b: Prompt Compression](#pr63b-prompt-compression)
   - [PR6.3c: Smart RAG Context Management](#pr63c-smart-rag-context-management)
   - [PR6.3d: Routing Optimization](#pr63d-routing-optimization)
   - [PR6.3e: Conversation History Optimization](#pr63e-conversation-history-optimization)
6. [Milestones & Sequence](#milestones--sequence)
7. [Risks, Trade-offs, and Open Questions](#risks-trade-offs-and-open-questions)

---

## Overview

This epic addresses Gemini API cost efficiency through systematic optimization of token usage across all components of the chat system. The work is divided into 5 incremental PRs that build upon each other to achieve 40-50% total cost reduction while maintaining response quality and ensuring all diving-related information continues to reference the RAG database.

**Expected Results:**
- Overall token reduction: 40-50%
- Cost reduction: ~$0.03 → ~$0.015 per query
- Response quality maintained
- No user-facing changes
- All diving info still references RAG database

**Timeline Estimate:** 7-10 days (solo dev)

---

## Recent Updates (2026-02-08)

- Switched embedding model to `gemini-embedding-001` for integration coverage
- Standardized embeddings on pgvector `Vector(768)` storage and query casting
- Stabilized async DB test execution with session-scoped event loop
- Full backend integration suite passed (38 tests)

---

## Feature/Epic Summary

### Objective

Reduce Gemini API token consumption and costs by 40-50% through comprehensive token tracking, prompt optimization, intelligent RAG context management, and conversation history optimization, while maintaining response quality and ensuring all diving-related information references the RAG database.

### User Impact

**Direct Impact:**
- No visible changes to users (backend optimization)
- Response quality maintained or improved
- Slight response time improvement from reduced token processing (<50ms)

**Indirect Impact:**
- Sustainable costs enable longer-term service availability
- Better monitoring enables quality improvements
- Foundation for future cost-aware features

### Dependencies

**Existing Systems:**
- RAG pipeline (PR2, PR3.2b) - retrieval and context formatting
- Multi-agent orchestration (PR3.2c) - routing and agent execution  
- LLM provider abstraction (PR3.2b) - Gemini integration
- Conversation management (PR6.1, PR6.2) - session history and state

**External Dependencies:**
- Google Gemini API (gemini-2.5-flash-lite model)
- Gemini API usage_metadata availability for token tracking

### Assumptions

1. Gemini API consistently returns `usage_metadata` with token counts
2. Current prompt verbosity can be reduced without quality loss
3. 5 RAG chunks (vs current 8) still provide adequate context
4. 6 messages of conversation history (vs current 10) sufficient for continuity
5. Routing can use heuristics for 70-80% of queries without LLM call
6. Token counting overhead (<50ms) acceptable for cost visibility

---

## Complexity & Fit

### Classification: Multi-PR

### Rationale

- **Multiple optimization areas:** Token tracking, prompt compression, RAG tuning, routing optimization, history management (5 distinct areas)
- **Independent testability required:** Each optimization needs isolated validation to measure impact
- **Risk management:** Incremental deployment reduces risk of quality degradation
- **Measurement dependencies:** Token tracking must be implemented first to measure subsequent optimizations
- **Rollback flexibility:** Each PR independently reversible if quality issues detected
- **Solo dev efficiency:** Smaller PRs easier to implement, test, and validate in focused work sessions

### Recommended Number of PRs: 5 PRs

---

## Full-Stack Impact

### Frontend

**No changes planned.**

Cost optimization is entirely backend-focused. Token usage and costs are not exposed to frontend.

### Backend

**APIs to modify:**
- `POST /api/chat` - Add token logging, pass reduced context to agents (no contract changes)

**Services/modules impacted:**
- `backend/app/services/llm/gemini.py` - Extract and log token usage from API responses
- `backend/app/services/llm/types.py` - Extend LLMResponse with token breakdown
- `backend/app/orchestration/gemini_orchestrator.py` - Add routing token logging, compress routing prompt
- `backend/app/orchestration/context_builder.py` - Add RAG token counting, history truncation
- `backend/app/services/rag/pipeline.py` - Implement query complexity scoring, dynamic top_k
- `backend/app/services/rag/token_utils.py` - NEW: Token counting utilities
- `backend/app/prompts/rag.py` - Compress RAG system prompt
- `backend/app/prompts/system.py` - Compress base system prompt
- `backend/app/agents/retrieval.py`, `trip.py` - Reduce history window, log tokens

**Validation/auth/error-handling concerns:**
- No auth changes
- Error handling: token tracking failures should not break requests
- Add fallback for missing usage_metadata
- Token counting errors should not propagate

### Data

**No schema changes.**

- Session history still stored fully in database
- RAG embeddings unchanged
- Only in-memory processing changes (what gets passed to LLM)

### Infra / Config

**Environment variables:**
- `RAG_TOP_K` - Change default from 8 to 5
- `MAX_HISTORY_TOKENS` - NEW: Add with default 1500

**Feature flags:**
- No new feature flags needed (all optimizations always-on once deployed)

**CI/CD considerations:**
- Add token usage regression tests
- Monitor for quality degradation in staging
- Consider canary deployment for prompt changes

---

## PR Roadmap

### PR6.3a: Token Tracking & Cost Logging

**Goal**

Implement detailed token tracking and cost calculation at every Gemini API call point to establish baseline metrics and identify cost leaks. This PR provides visibility without changing behavior.

**Scope**

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

#### Backend Changes

**APIs to modify:**
- None (logging only, no API contract changes)

**Services/modules to add/modify:**

**1. `backend/app/services/llm/types.py`**
- Extend `LLMResponse` dataclass:
  - Add `prompt_tokens: Optional[int]`
  - Add `completion_tokens: Optional[int]`
  - Add `cost_usd: Optional[float]`
  - Keep `tokens_used` as backward-compatible total

**2. `backend/app/services/llm/gemini.py`**
- In `generate()` method, extract from `response.usage_metadata`:
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
- Function `count_tokens(text: str) -> int`
  - Uses `tiktoken.encoding_for_model("gpt-3.5-turbo")` (existing pattern)
  - Returns token count
- Function `calculate_gemini_cost(prompt_tokens: int, completion_tokens: int) -> float`
  - Calculates cost in USD
  - Returns formatted float (4 decimal places)

**4. `backend/app/orchestration/gemini_orchestrator.py`**
- In `route_request()`, after LLM call:
  - Extract routing token usage from response
  - Calculate routing cost
  - Log routing decision with tokens and cost

**5. `backend/app/orchestration/context_builder.py`**
- Before passing RAG context to agent:
  - Count tokens using `count_tokens(rag_context)`
  - Log RAG context preparation with token count

**6. `backend/app/agents/base.py`**
- In `execute()` method, after LLM generation:
  - Log agent execution complete with token breakdown
  - Include: agent_type, total_tokens, cost_usd, rag_tokens, history_messages

**Auth, validation, error handling:**
- Add fallback if `usage_metadata` is None (log warning, continue without token data)
- Token tracking failures should not break requests
- Cost calculation errors should not propagate (default to None)

#### Frontend Changes

No changes.

#### Data Changes

No migrations or schema changes.

#### Infra / Config

No new environment variables.

#### Testing

**Unit tests:**
- `test_llm_response_extended_fields()` - Verify new fields in LLMResponse
- `test_cost_calculation()` - Verify formula: `(100k*0.15 + 50k*0.60)/1M = $0.045`
- `test_cost_calculation_edge_cases()` - Zero tokens, None tokens, large numbers
- `test_token_counting_utility()` - Verify count_tokens() matches tiktoken
- `test_fallback_missing_usage_metadata()` - Verify graceful handling

**Integration tests:**
- `test_llm_generate_logs_tokens()` - Verify log output contains all token fields
- `test_orchestrator_logs_routing_tokens()` - Verify routing logs tokens
- `test_agent_logs_execution_tokens()` - Verify agent logs include token breakdown
- `test_rag_token_counting()` - Verify RAG context tokens logged

**Manual checks:**
- Run 10 chat queries with varying complexity
- Inspect logs for structured token data
- Verify all LLM calls have token logs
- Calculate total cost for 10 queries
- Identify highest token consumers (routing vs agent vs RAG)

#### Verification

**Commands to run:**
- Install: `cd backend && .venv/bin/pip install -e .`
- Dev: `cd backend && .venv/bin/uvicorn app.main:app --reload`
- Test: `cd backend && .venv/bin/pytest tests/unit/services/test_llm.py -v`
- Test: `cd backend && .venv/bin/pytest tests/integration/services/test_llm_integration.py -v`
- Lint: `cd backend && .venv/bin/ruff check app/`
- Typecheck: `cd backend && .venv/bin/mypy app/`

**Manual verification checklist:**
1. Start backend server
2. Send chat request: POST /api/chat with message "Where can I dive in Tioman?"
3. Check logs for "LLM generation complete" with prompt_tokens, completion_tokens, cost_usd
4. Check logs for "Routing decision" with routing_tokens, routing_cost_usd
5. Check logs for "Agent execution complete" with total_tokens, cost_usd
6. Verify no errors if usage_metadata missing (test by mocking)
7. Calculate total cost from logs, verify reasonable (<$0.05 per query)

#### Rollback Plan

**Feature flag / kill switch:** None needed (logging only, no behavior change)

**Revert strategy:**
- Revert PR6.3a if logging causes performance issues
- No data loss risk (logging only)
- No user-facing impact

#### Dependencies

**PRs required before this one:** None (foundational)

**External dependencies:**
- Gemini API must return usage_metadata (assumed available)

#### Risks & Mitigations

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

### PR6.3b: Prompt Compression

**Goal**

Reduce system prompt and RAG prompt token count by 40-60% while preserving essential instructions, safety guardrails, and RAG adherence rules.

**Scope**

**In scope:**
- Compress `RAG_SYSTEM_PROMPT` in `backend/app/prompts/rag.py` (500+ → 200-250 tokens)
- Compress `NO_RAG_PROMPT` (80 → 40 tokens)
- Compress `BASE_SYSTEM_PROMPT` in `backend/app/prompts/system.py` (350+ → 150-180 tokens)
- Compress `GENERAL_SYSTEM_PROMPT` (60 → 30 tokens)
- Remove verbose examples, redundant phrasing, formatting repetition
- Keep all safety disclaimers and critical RAG adherence rules

**Out of scope:**
- Changing prompt logic or behavior
- Removing safety guidelines
- Modifying agent-specific prompts (certification, trip, safety) - defer to future
- Changing RAG context format

#### Backend Changes

**Services/modules to modify:**

**1. `backend/app/prompts/rag.py`**

Compress `RAG_SYSTEM_PROMPT` from ~500 tokens to ~200-250 tokens:
- Remove verbose "CONTEXT HANDLING RULES" explanations
- Remove "FORBIDDEN PHRASES" section (200+ tokens, covered by general rule)
- Remove example responses (150+ tokens, not needed by model)
- Consolidate formatting rules into 3 bullets
- Use direct imperative language
- Remove redundant emphasis (emojis, ALL CAPS sections)
- Keep core rules: "Use only verified information", safety disclaimers

Compressed structure:
- Identity + role (1 line)
- VERIFIED INFORMATION: {context}
- Core rules (4 bullets)
- Formatting (3 bullets)
- Safety (2 bullets)
- Tone (1 line)

Compress `NO_RAG_PROMPT` from ~80 tokens to ~40 tokens:
- Essential message only: no info available, ask for rephrasing

**2. `backend/app/prompts/system.py`**

Compress `BASE_SYSTEM_PROMPT` from ~350 tokens to ~150-180 tokens:
- Consolidate "YOUR ROLE" and "PERSONALITY" sections
- Shorten security section (keep core rules, remove repetition)
- Use bullet format instead of numbered paragraphs
- Keep all safety guidelines verbatim

Compress `GENERAL_SYSTEM_PROMPT` from ~60 tokens to ~30 tokens:
- Already concise, minor trim only

**Auth, validation, error handling:**
- No changes

#### Frontend Changes

No changes.

#### Data Changes

No migrations or schema changes.

#### Infra / Config

No environment variable changes.

#### Testing

**Unit tests:**
- `test_rag_prompt_token_count()` - Verify compressed ≤ 250 tokens
- `test_base_prompt_token_count()` - Verify compressed ≤ 180 tokens
- `test_no_rag_prompt_token_count()` - Verify compressed ≤ 40 tokens
- `test_prompts_contain_safety_disclaimers()` - Verify critical rules preserved
- `test_prompts_contain_rag_adherence_rules()` - Verify "use only verified info" present

**Integration tests:**
- `test_chat_with_compressed_prompts()` - Full chat flow works
- `test_rag_adherence_maintained()` - "Where can I dive in Tioman?" returns specific sites
- `test_safety_disclaimers_maintained()` - "Can I dive with a cold?" advises medical professional
- `test_response_formatting()` - Multiple sites use bullet formatting

**Regression tests:**
- Rerun PR6.2 Response Discipline tests (5 scenarios)
- Verify all pass with compressed prompts

**Manual checks:**
- Run 20 diverse queries:
  - 10 with RAG context (destinations, certifications, safety)
  - 5 without RAG (general diving knowledge)
  - 5 edge cases (medical, equipment, marine life)
- Compare response quality to baseline (PR6.3a logs)
- Check for hallucinations (generic site descriptions where specifics expected)
- Verify formatting maintained (bullet lists, blank lines)
- Verify safety disclaimers present

#### Verification

**Commands to run:**
- Install: `cd backend && .venv/bin/pip install -e .`
- Dev: `cd backend && .venv/bin/uvicorn app.main:app --reload`
- Test: `cd backend && .venv/bin/pytest tests/unit/prompts/ -v`
- Test: `cd backend && .venv/bin/pytest tests/integration/ -k chat -v`

**Manual verification checklist:**
1. Start backend with compressed prompts
2. Test RAG adherence: "Best dive sites in Tioman?" → Should list specific sites (Tiger Reef, Renggis)
3. Test safety: "Is it safe to fly after diving?" → Should reference 18-24hr rule from RAG
4. Test medical: "Can I dive with diabetes?" → Should recommend consulting doctor
5. Test formatting: Multiple sites should use bullets with blank lines
6. Compare token usage in logs: verify 200-300 tokens saved per request
7. Verify no generic answers where specifics expected

#### Rollback Plan

**Feature flag / kill switch:** None (prompt changes only)

**Revert strategy:**
- Revert `backend/app/prompts/rag.py` and `system.py`
- Instant rollback, no dependencies
- No data impact

#### Dependencies

**PRs required before this one:**
- PR6.3a (Token Tracking) - To measure token savings

**External dependencies:** None

#### Risks & Mitigations

**Risk 1: Removing examples might reduce model adherence**
- **Mitigation:** Gemini 2.5 Flash Lite quality sufficient for concise instructions
- **Mitigation:** Keep core rules verbatim, only remove explanations
- **Mitigation:** Extensive testing with RAG adherence cases

**Risk 2: Over-compression could hurt response quality**
- **Mitigation:** Conservative compression (40-60%, not 80%)
- **Mitigation:** 20-query manual validation before deployment
- **Mitigation:** Easy rollback if issues detected

**Risk 3: Safety disclaimers might be weakened**
- **Mitigation:** Preserve safety-critical instructions verbatim
- **Mitigation:** Regression test for safety responses
- **Impact:** Zero tolerance - any safety degradation triggers rollback

---

### PR6.3c: Smart RAG Context Management

**Goal**

Reduce RAG context token usage by 30-40% through intelligent context budgeting, top_k reduction, and query-based filtering, while maintaining response quality.

**Scope**

**In scope:**
- Reduce `rag_top_k` default from 8 to 5
- Implement query complexity scoring (skip/medium/complex)
- Adjust top_k dynamically: skip RAG for greetings, 3 chunks for medium, 5 for complex
- Add token counting for RAG context before passing to agent
- Log RAG token usage per query

**Out of scope:**
- Changing RAG retrieval algorithm (hybrid search unchanged)
- Modifying chunk size (stays 400 tokens)
- Changing min_similarity threshold (stays 0.5)
- Chunk deduplication (future optimization)

#### Backend Changes

**Services/modules to modify:**

**1. `backend/app/core/config.py`**
- Change `rag_top_k: int = 8` to `rag_top_k: int = 5`

**2. `backend/app/services/rag/pipeline.py`**

Add method `_assess_query_complexity(query: str) -> str`:
- Returns: "skip" | "medium" | "complex"
- Skip patterns: greetings ("hi", "hello", "thanks"), yes/no, clarifications
- Complex indicators: 
  - Location mentions
  - Keywords: "where can i", "best sites in", "recommend", "plan trip"
  - Long queries (> 100 chars)
- Medium: most "what/how/why" questions
- Default: medium

Modify `retrieve_context()`:
- Call `_assess_query_complexity()` at start
- If "skip", return empty RAGContext with NO_DATA
- If complexity provided, use dynamic top_k:
  - medium: 3 chunks (~1200 tokens)
  - complex: 5 chunks (~2000 tokens)
- Log: "Query complexity: {complexity}, using top_k={top_k}"

**3. `backend/app/orchestration/context_builder.py`**

Add token counting for RAG context:
- Count tokens before passing to agent
- Log: "RAG context prepared" with chunks count and rag_tokens

**Auth, validation, error handling:**
- Complexity scoring failures default to "complex" (conservative)
- Empty RAG results handled gracefully (already exists)

#### Frontend Changes

No changes.

#### Data Changes

No migrations or schema changes.

#### Infra / Config

**Environment variables:**
- `RAG_TOP_K` default changes from 8 to 5 (existing var, new default)

#### Testing

**Unit tests:**
- `test_assess_query_complexity_skip()` - "Hi" → "skip"
- `test_assess_query_complexity_medium()` - "What is buoyancy?" → "medium"
- `test_assess_query_complexity_complex()` - "Where can I dive in Tioman?" → "complex"
- `test_dynamic_top_k_skip()` - Skip query returns empty context
- `test_dynamic_top_k_medium()` - Medium query uses top_k=3
- `test_dynamic_top_k_complex()` - Complex query uses top_k=5
- `test_complexity_scoring_edge_cases()` - Empty query, very long query, mixed signals

**Integration tests:**
- `test_rag_pipeline_skip_for_greeting()` - "Thanks" returns NO_DATA
- `test_rag_pipeline_medium_query()` - "What is a BCD?" retrieves 3 chunks
- `test_rag_pipeline_complex_query()` - "Where can I dive in Tioman?" retrieves 5 chunks
- `test_rag_token_counting()` - Verify rag_tokens logged correctly

**Manual checks:**
- Run 30 queries across complexity levels:
  - 5 greetings/simple (should skip RAG, 0 tokens)
  - 15 medium queries (should get 3 chunks, ~1200 tokens)
  - 10 complex queries (should get 5 chunks, ~2000 tokens)
- Measure average RAG tokens before/after optimization
- Verify response quality unchanged for each category
- Check for "I don't have information" responses increasing

#### Verification

**Commands to run:**
- Install: `cd backend && .venv/bin/pip install -e .`
- Dev: `cd backend && .venv/bin/uvicorn app.main:app --reload`
- Test: `cd backend && .venv/bin/pytest tests/unit/services/test_rag_pipeline.py -v`
- Test: `cd backend && .venv/bin/pytest tests/integration/services/test_rag_integration.py -v`

**Manual verification checklist:**
1. Test skip: Send "Hello" → Check logs for "Skipping RAG" and 0 rag_tokens
2. Test medium: Send "What is nitrox?" → Check logs for top_k=3, ~1200 rag_tokens
3. Test complex: Send "Where can I dive in Tioman?" → Check logs for top_k=5, ~2000 rag_tokens
4. Verify response quality maintained across all complexity levels
5. Calculate token savings from PR6.3a baseline
6. Verify no increase in "I don't have information" responses

#### Rollback Plan

**Feature flag / kill switch:** None (behavior change)

**Revert strategy:**
- Change `rag_top_k` back to 8 in config
- Remove or disable query complexity scoring (set all to "complex")
- Redeploy
- No data loss

#### Dependencies

**PRs required before this one:**
- PR6.3a (Token Tracking) - To measure RAG token reduction

**External dependencies:** None

#### Risks & Mitigations

**Risk 1: Reducing top_k might miss relevant context**
- **Mitigation:** Conservative top_k values (3 and 5 still generous)
- **Mitigation:** Monitor for "I don't have information" responses
- **Mitigation:** Can adjust thresholds based on feedback

**Risk 2: Complexity scoring might misclassify queries**
- **Mitigation:** Use multiple heuristics (keywords, length, patterns)
- **Mitigation:** Default to "complex" on uncertainty
- **Mitigation:** Log all classification decisions for analysis

**Risk 3: Users might notice less comprehensive answers**
- **Mitigation:** 5 chunks (2000 tokens) still substantial context
- **Mitigation:** Quality testing before deployment
- **Impact:** Easy to increase back to 6-7 if needed

---

### PR6.3d: Routing Optimization

**Goal**

Reduce routing overhead by compressing routing prompt and implementing lightweight heuristic pre-filtering for obvious routing cases.

**Scope**

**In scope:**
- Compress routing system instruction in `GeminiOrchestrator` (150+ → 60-70 tokens)
- Implement heuristic pre-filter for obvious cases (trip vs knowledge_base)
- Add routing token/cost logging
- Document routing efficiency metrics

**Out of scope:**
- Removing routing entirely (multi-agent system requires it)
- Changing routing logic (function calling unchanged)
- Adding new agents
- Routing decision caching (future optimization)

#### Backend Changes

**Services/modules to modify:**

**1. `backend/app/orchestration/gemini_orchestrator.py`**

Compress `system_instruction` in `route_request()`:
- Current: ~150 tokens with verbose rules and examples
- Target: ~60-70 tokens with concise rules
- Remove repetitive examples
- Use imperative bullet format

Compressed routing instruction:
```
Route user queries to specialist agents.

RULES:
- Location/destination/sites/trip → trip_planner
- Safety/certification/equipment/marine life → knowledge_base

You MUST call a tool. Use exact query in args.
```

Add method `_quick_route_heuristic(message: str) -> Optional[str]`:
- Fast keyword-based routing for obvious cases
- Trip keywords: "where can i dive", "best sites in", "destinations", "plan trip"
- Info keywords: "certification", "padi", "ssi", "equipment", "safety", "what is"
- Returns agent name if confident, None if needs LLM

Modify `route_request()`:
- Try heuristic first
- If heuristic returns agent, use it (0 routing tokens)
- Otherwise, call LLM routing
- Log routing method and tokens

**Auth, validation, error handling:**
- Heuristic failures default to LLM routing (conservative)
- LLM routing failures handled by existing error handling

#### Frontend Changes

No changes.

#### Data Changes

No migrations or schema changes.

#### Infra / Config

No environment variable changes.

#### Testing

**Unit tests:**
- `test_compressed_routing_prompt_token_count()` - Verify ≤ 70 tokens
- `test_heuristic_routing_trip()` - "Where can I dive in Bali?" → "trip_planner" (heuristic)
- `test_heuristic_routing_info()` - "What is a BCD?" → "knowledge_base" (heuristic)
- `test_heuristic_routing_ambiguous()` - "Tell me about diving" → None (needs LLM)
- `test_heuristic_edge_cases()` - Empty query, multi-intent queries

**Integration tests:**
- `test_routing_with_heuristic()` - Verify heuristic routes correctly, 0 tokens
- `test_routing_with_llm_fallback()` - Verify LLM routing when heuristic returns None
- `test_routing_token_logging()` - Verify routing_method and routing_tokens logged
- `test_routing_accuracy()` - 20 queries, verify correct agent selected

**Manual checks:**
- Run 20 queries across routing scenarios:
  - 10 obvious trip queries (should use heuristic)
  - 5 obvious info queries (should use heuristic)
  - 5 ambiguous queries (should use LLM)
- Measure routing token savings
- Verify routing accuracy (no misroutes)
- Calculate % queries using heuristic (target: 70-80%)

#### Verification

**Commands to run:**
- Install: `cd backend && .venv/bin/pip install -e .`
- Dev: `cd backend && .venv/bin/uvicorn app.main:app --reload`
- Test: `cd backend && .venv/bin/pytest tests/unit/orchestration/test_gemini_orchestrator.py -v`

**Manual verification checklist:**
1. Test trip heuristic: "Where can I dive in Tioman?" → Check logs for routing_method=heuristic, agent=trip_planner
2. Test info heuristic: "What is nitrox?" → Check logs for routing_method=heuristic, agent=knowledge_base
3. Test LLM fallback: "Tell me about diving" → Check logs for routing_method=llm
4. Verify routing accuracy: No misroutes detected in 20-query test
5. Calculate routing token savings from PR6.3a baseline
6. Verify routing_tokens=0 for heuristic routes

#### Rollback Plan

**Feature flag / kill switch:** None (behavior change)

**Revert strategy:**
- Revert routing prompt to original
- Disable heuristic routing (always call LLM)
- Redeploy
- No data loss

#### Dependencies

**PRs required before this one:**
- PR6.3a (Token Tracking) - To measure routing token savings

**External dependencies:** None

#### Risks & Mitigations

**Risk 1: Heuristic might misroute some queries**
- **Mitigation:** Conservative keyword matching (only obvious cases)
- **Mitigation:** LLM fallback for ambiguous queries
- **Mitigation:** Monitor for user complaints or wrong responses
- **Impact:** Misroute would result in suboptimal but not broken response

**Risk 2: Over-compressed routing prompt might confuse model**
- **Mitigation:** Test routing accuracy thoroughly (20+ queries)
- **Mitigation:** Gemini 2.5 Flash Lite handles concise instructions well
- **Mitigation:** Easy rollback if accuracy drops

**Risk 3: Heuristic keywords might overlap or conflict**
- **Mitigation:** Prioritize trip keywords (more specific)
- **Mitigation:** Test multi-intent queries
- **Mitigation:** Default to LLM on uncertainty

---

### PR6.3e: Conversation History Optimization

**Goal**

Reduce conversation history token usage by 40-60% through sliding window reduction and token budget enforcement, while maintaining conversation continuity.

**Scope**

**In scope:**
- Reduce history window from 10 messages to 6 most recent in agent message building
- Add token budget enforcement (max 1500 tokens for history)
- Implement history token counting and truncation by token budget
- Log history token usage per query
- Full history still persisted in database

**Out of scope:**
- Changing session persistence (history still stored fully in DB)
- Implementing conversation summarization (future enhancement)
- Changing message structure
- History compression techniques

#### Backend Changes

**Services/modules to modify:**

**1. `backend/app/core/config.py`**
- Add `max_history_tokens: int = 1500`
- Keep `max_conversation_history: int = 20` (DB storage unchanged)

**2. `backend/app/orchestration/context_builder.py`**

Add method `_truncate_history_by_tokens(history: List[dict], max_tokens: int) -> List[dict]`:
- Iterates from most recent to oldest
- Counts tokens per message: `f"{role}: {content}"`
- Stops when budget exceeded
- Returns truncated list (preserves message order)
- Logs: "History truncated: {kept}/{total} messages, {tokens} tokens"

Modify `build_context()`:
- Get recent history: `[-6:]` instead of all
- Apply token budget with `_truncate_history_by_tokens()`
- Count final history tokens
- Log: "Conversation history: {len} messages, {tokens} tokens"
- Pass budgeted history to `AgentContext`

**3. `backend/app/agents/retrieval.py`, `trip.py`**
- Change history slice from `[-10:]` to `[-6:]`
- (Context builder handles token budget, but agents also have direct slice)

**Auth, validation, error handling:**
- Empty history handled gracefully (already exists)
- Token budget failures default to empty history (conservative)

#### Frontend Changes

No changes.

#### Data Changes

**No migrations or schema changes.**

Full conversation history still stored in database. Only in-memory processing changes (what gets passed to LLM).

#### Infra / Config

**Environment variables:**
- `MAX_HISTORY_TOKENS` - NEW, default 1500

#### Testing

**Unit tests:**
- `test_truncate_history_by_tokens_empty()` - Handle empty history
- `test_truncate_history_by_tokens_under_budget()` - All messages fit
- `test_truncate_history_by_tokens_over_budget()` - Truncates oldest
- `test_truncate_history_preserves_order()` - Verify message order maintained
- `test_truncate_history_respects_budget()` - Verify total ≤ max_tokens
- `test_token_counting_for_messages()` - Verify token counting accurate

**Integration tests:**
- `test_conversation_with_short_history()` - 4 messages, all included
- `test_conversation_with_long_history()` - 15 messages, only 6 most recent
- `test_history_token_budget_enforced()` - Large messages, verify truncation
- `test_conversation_continuity_maintained()` - Response contextually relevant

**Manual checks:**
- Create long conversation (20 messages)
- Verify only 6 most recent messages passed to agent
- Verify token budget never exceeded (≤1500 tokens)
- Test conversation continuity:
  - 3-turn conversation about Tioman
  - Verify bot remembers context from previous turns
- Measure history token savings from PR6.3a baseline

#### Verification

**Commands to run:**
- Install: `cd backend && .venv/bin/pip install -e .`
- Dev: `cd backend && .venv/bin/uvicorn app.main:app --reload`
- Test: `cd backend && .venv/bin/pytest tests/unit/orchestration/test_context_builder.py -v`
- Test: `cd backend && .venv/bin/pytest tests/integration/ -k conversation -v`

**Manual verification checklist:**
1. Start conversation, send 10 messages
2. Check logs: Verify "Conversation history: 6 messages" (not 10)
3. Verify token budget: Verify history_tokens ≤ 1500 in logs
4. Test continuity: Ask follow-up question, verify contextually relevant response
5. Test very long messages: Send messages with 500+ chars each, verify truncation
6. Calculate history token savings from PR6.3a baseline
7. Verify no degradation in follow-up question quality

#### Rollback Plan

**Feature flag / kill switch:** None (behavior change)

**Revert strategy:**
- Change history slice back to `[-10:]` in agents
- Remove token budget enforcement in context_builder
- Redeploy
- No data loss (full history still in DB)

#### Dependencies

**PRs required before this one:**
- PR6.3a (Token Tracking) - To measure history token reduction

**External dependencies:** None

#### Risks & Mitigations

**Risk 1: Reducing history might break context for complex conversations**
- **Mitigation:** 6 messages = 3 conversation turns (sufficient for most cases)
- **Mitigation:** Token budget is generous (1500 tokens)
- **Mitigation:** Test multi-turn conversations extensively
- **Impact:** Monitor for "forgetting" complaints in user feedback

**Risk 2: Token budget truncation might cut critical context**
- **Mitigation:** Budget set high enough for 6-8 normal messages
- **Mitigation:** Keeps most recent messages (most relevant)
- **Mitigation:** Full history still in DB for debugging

**Risk 3: Users might notice bot "forgetting" earlier topics**
- **Mitigation:** Most conversations don't span >6 messages
- **Mitigation:** Can increase to 7-8 messages if feedback indicates issues
- **Impact:** Easy to adjust window size based on production data

---

## Milestones & Sequence

### Milestone 1: Visibility & Baseline (PR6.3a)

**User value:** Establishes cost visibility and identifies optimization opportunities

**PRs included:**
- PR6.3a: Comprehensive Token Tracking & Cost Logging

**"Done" means:**
- All Gemini API calls log token usage and cost
- Baseline metrics established (avg tokens per query, cost per query)
- Token breakdown available for all components (routing, RAG, history, LLM)
- No performance degradation from logging overhead

### Milestone 2: Core Optimizations (PR6.3b, PR6.3c)

**User value:** Achieves 30-40% token reduction through prompt and RAG optimizations

**PRs included:**
- PR6.3b: Prompt Compression
- PR6.3c: Smart RAG Context Management

**"Done" means:**
- Prompts compressed by 40-60% with quality maintained
- RAG context dynamically adjusted based on query complexity
- Token savings of 500-1000 tokens per query on average
- No quality degradation in 20-query validation test
- Response formatting and safety disclaimers preserved

### Milestone 3: Advanced Optimizations (PR6.3d, PR6.3e)

**User value:** Achieves additional 15-25% token reduction through routing and history optimization

**PRs included:**
- PR6.3d: Routing Optimization
- PR6.3e: Conversation History Optimization

**"Done" means:**
- 70-80% of routing decisions use heuristics (0 tokens)
- Conversation history reduced to 6 messages with token budget
- Total token reduction of 40-50% vs baseline
- Cost reduced from ~$0.03 to ~$0.015 per query
- Conversation continuity maintained
- No routing accuracy degradation

---

## Risks, Trade-offs, and Open Questions

### Major Risks

**Risk 1: Response Quality Degradation from Prompt Compression**
- **Likelihood:** Medium
- **Impact:** High (user-facing quality issues)
- **Mitigation:**
  - PR6.3b includes extensive testing (20 queries, PR6.2 regression tests)
  - Conservative compression (40-60%, not 80%)
  - Easy rollback (revert prompt file)
  - Can adjust compression level if issues detected
- **Detection:** Monitor for hallucinations, generic responses, safety disclaimer omissions

**Risk 2: Context Loss from RAG Reduction**
- **Likelihood:** Low-Medium
- **Impact:** Medium (less comprehensive answers)
- **Mitigation:**
  - Dynamic top_k based on query complexity (not blanket reduction)
  - Conservative values (3-5 chunks still substantial)
  - Monitor for "I don't have information" responses increasing
  - Easy to adjust top_k thresholds
- **Detection:** User complaints about incomplete answers, increased "no data" responses

**Risk 3: Conversation Context Loss from History Reduction**
- **Likelihood:** Low
- **Impact:** Medium (users notice "forgetting")
- **Mitigation:**
  - 6 messages = 3 turns (sufficient for most conversations)
  - Token budget (1500 tokens) is generous
  - Full history still in DB for debugging
  - Easy to increase window to 7-8 if needed
- **Detection:** User complaints about bot forgetting earlier topics, follow-up question quality degradation

**Risk 4: Routing Misroutes from Heuristic**
- **Likelihood:** Low
- **Impact:** Low-Medium (suboptimal response, not broken)
- **Mitigation:**
  - Conservative heuristic (only obvious cases)
  - LLM fallback for ambiguous queries
  - Extensive routing accuracy testing (20+ queries)
  - Easy to disable heuristic if accuracy drops
- **Detection:** Wrong agent selected (trip agent for certification question), monitor logs

**Risk 5: Token Counting Overhead Degrades Performance**
- **Likelihood:** Very Low
- **Impact:** Low (<50ms latency increase)
- **Mitigation:**
  - Structured logging is fast (<5-10ms)
  - Token counting with tiktoken is fast (<5ms)
  - Can cache token counts for repeated strings
- **Detection:** Latency monitoring, response time increase >100ms

### Trade-offs

**Trade-off 1: RAG Context Richness vs Cost**
- **Decision:** Reduce top_k from 8 to 5 (dynamic 3-5)
- **Rationale:** 8 chunks often excessive; 5 provides comprehensive context at lower cost
- **Alternative Considered:** Keep 8 but implement chunk deduplication (more complex)
- **Why Chosen:** Simpler implementation, safer, still provides rich context
- **Impact:** Slight reduction in context breadth, but dynamic adjustment mitigates risk

**Trade-off 2: Prompt Clarity vs Token Count**
- **Decision:** Compress prompts by removing examples and verbose explanations (40-60% reduction)
- **Rationale:** Gemini 2.5 Flash Lite quality sufficient for concise instructions
- **Alternative Considered:** Keep prompts verbose, optimize only RAG/history
- **Why Chosen:** Prompts are largest token consumer (500+ tokens per request), biggest ROI
- **Impact:** Risk of reduced model adherence, mitigated by extensive testing

**Trade-off 3: Routing Accuracy vs Cost**
- **Decision:** Use heuristics for obvious cases, LLM for ambiguous
- **Rationale:** 70-80% of queries are obviously trip or info, save 130 tokens per route
- **Alternative Considered:** Always use LLM routing (most accurate but expensive)
- **Why Chosen:** Heuristic is fast, cheap, and accurate for obvious cases
- **Impact:** Potential for misroutes on edge cases, mitigated by LLM fallback

**Trade-off 4: Conversation History Depth vs Cost**
- **Decision:** Reduce from 10 to 6 messages with 1500 token budget
- **Rationale:** Most conversations don't need full 10-message context
- **Alternative Considered:** Implement full conversation summarization (complex)
- **Why Chosen:** Simpler, faster, 6 messages adequate for continuity
- **Impact:** Potential context loss in long conversations, mitigated by generous token budget

### Open Questions

**Q1: Should we implement prompt caching for frequently used system prompts?**
- **Context:** Google Gemini supports prompt caching, which could reduce costs for repeated prompts
- **Impact on plan:** Would require separate PR for caching implementation, monitoring cache hit rates
- **Decision needed by:** After PR6.3b deployed, analyze prompt repetition patterns
- **If yes:** Add PR6.3f for prompt caching (estimated 10-20% additional savings on cached prompts)
- **If no:** Defer to Phase 2 based on cost analysis

**Q2: Should we add token usage to session metadata for per-user tracking?**
- **Context:** Currently no user accounts (all guest sessions), but future may have auth
- **Impact on plan:** Would require schema changes (session_tokens field), aggregation logic
- **Decision needed by:** Before PR9 (auth implementation)
- **If yes:** Add session-level token tracking in PR9
- **If no:** Continue with aggregate logging only

**Q3: Should we implement automatic prompt version testing (A/B testing)?**
- **Context:** Could test compressed vs original prompts in production for data-driven decisions
- **Impact on plan:** Would require feature flag infrastructure, experiment tracking, statistical analysis
- **Decision needed by:** After PR6.3b deployed, if quality concerns arise
- **If yes:** Add PR6.3f for prompt experimentation framework
- **If no:** Rely on manual testing and user feedback

**Q4: What is the acceptable threshold for "I don't have information" response increase?**
- **Context:** RAG reduction (PR6.3c) might increase empty context cases
- **Impact on plan:** May need to adjust top_k thresholds if threshold exceeded
- **Decision needed by:** During PR6.3c validation
- **If 5% increase:** Acceptable (some queries genuinely lack content)
- **If >10% increase:** Adjust top_k back to 6 or add fallback logic

**Q5: Should we optimize agent-specific prompts (certification, trip, safety)?**
- **Context:** PR6.3b only optimizes base prompts; agent prompts also verbose
- **Impact on plan:** Would add PR6.3f for agent prompt optimization (additional 100-200 tokens savings)
- **Decision needed by:** After PR6.3e completed and total savings measured
- **If total savings <40%:** Add PR6.3f for agent prompts
- **If total savings ≥40%:** Defer to future optimization cycle

---

**End of PR6.3 Plan**

**Document Status:** Ready for Implementation  
**Next Steps:** Begin PR6.3a implementation  
**Review Date:** After each PR completion

