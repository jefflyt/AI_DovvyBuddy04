# PR6.3d: Routing Optimization

**Part of Epic:** PR6.3 Gemini API Cost Efficiency Optimization

**Status:** Implementation Complete

**Owner:** jefflyt

**Date:** 2026-02-08

---

## Goal

Reduce routing overhead by compressing routing prompt and implementing lightweight heuristic pre-filtering for obvious routing cases.

---

## Scope

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

---

## Backend Changes

### Services/modules to modify

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

### Auth, validation, error handling

- Heuristic failures default to LLM routing (conservative)
- LLM routing failures handled by existing error handling

---

## Frontend Changes

No changes.

---

## Data Changes

No migrations or schema changes.

---

## Infra / Config

No environment variable changes.

---

## Testing

### Unit tests

- `test_compressed_routing_prompt_token_count()` - Verify ≤ 70 tokens
- `test_heuristic_routing_trip()` - "Where can I dive in Bali?" → "trip_planner" (heuristic)
- `test_heuristic_routing_info()` - "What is a BCD?" → "knowledge_base" (heuristic)
- `test_heuristic_routing_ambiguous()` - "Tell me about diving" → None (needs LLM)
- `test_heuristic_edge_cases()` - Empty query, multi-intent queries

### Integration tests

- `test_routing_with_heuristic()` - Verify heuristic routes correctly, 0 tokens
- `test_routing_with_llm_fallback()` - Verify LLM routing when heuristic returns None
- `test_routing_token_logging()` - Verify routing_method and routing_tokens logged
- `test_routing_accuracy()` - 20 queries, verify correct agent selected

### Manual checks

- Run 20 queries across routing scenarios:
  - 10 obvious trip queries (should use heuristic)
  - 5 obvious info queries (should use heuristic)
  - 5 ambiguous queries (should use LLM)
- Measure routing token savings
- Verify routing accuracy (no misroutes)
- Calculate % queries using heuristic (target: 70-80%)

---

## Verification

### Commands to run

- Install: `cd backend && .venv/bin/pip install -e .`
- Dev: `cd backend && .venv/bin/uvicorn app.main:app --reload`
- Test: `cd backend && .venv/bin/pytest tests/unit/orchestration/test_gemini_orchestrator.py -v`

### Manual verification checklist

1. Test trip heuristic: "Where can I dive in Tioman?" → Check logs for routing_method=heuristic, agent=trip_planner
2. Test info heuristic: "What is nitrox?" → Check logs for routing_method=heuristic, agent=knowledge_base
3. Test LLM fallback: "Tell me about diving" → Check logs for routing_method=llm
4. Verify routing accuracy: No misroutes detected in 20-query test
5. Calculate routing token savings from PR6.3a baseline
6. Verify routing_tokens=0 for heuristic routes

---

## Rollback Plan

**Feature flag / kill switch:** None (behavior change)

**Revert strategy:**
- Revert routing prompt to original
- Disable heuristic routing (always call LLM)
- Redeploy
- No data loss

---

## Dependencies

**PRs required before this one:**
- PR6.3a (Token Tracking) - To measure routing token savings

**External dependencies:** None

---

## Risks & Mitigations

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

## Success Metrics

- 70-80% of routing decisions use heuristics (0 tokens)
- Routing prompt compressed by 50% (150 → 70 tokens)
- Routing token savings: 100-130 tokens per query on average
- Routing accuracy maintained (no misroutes detected in 20-query test)
- Zero user complaints about wrong agent selection

---

## Implementation Status (2026-02-08)

**Completed:**
- Compressed routing system instruction
- Added heuristic routing for obvious trip/info cases
- Added unit tests for routing prompt size and heuristics

**Pending:**
* Manual 20-query routing validation and token savings check

**Done since last update:**
- Ran routing unit tests
- Full backend integration suite passed (38 tests)

**Previous PR:** PR6.3c (Smart RAG Context Management)  
**Next PR:** PR6.3e (Conversation History Optimization)
