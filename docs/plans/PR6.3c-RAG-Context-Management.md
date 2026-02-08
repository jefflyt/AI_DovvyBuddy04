# PR6.3c: Smart RAG Context Management

**Part of Epic:** PR6.3 Gemini API Cost Efficiency Optimization

**Status:** Implementation Complete

**Owner:** jefflyt

**Date:** 2026-02-08

---

## Goal

Reduce RAG context token usage by 30-40% through intelligent context budgeting, top_k reduction, and query-based filtering, while maintaining response quality.

---

## Scope

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

---

## Backend Changes

### Services/modules to modify

**1. `backend/app/core/config.py`**

Change `rag_top_k: int = 8` to `rag_top_k: int = 5`

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

### Auth, validation, error handling

- Complexity scoring failures default to "complex" (conservative)
- Empty RAG results handled gracefully (already exists)

---

## Frontend Changes

No changes.

---

## Data Changes

No migrations or schema changes.

---

## Infra / Config

**Environment variables:**
- `RAG_TOP_K` default changes from 8 to 5 (existing var, new default)

---

## Testing

### Unit tests

- `test_assess_query_complexity_skip()` - "Hi" → "skip"
- `test_assess_query_complexity_medium()` - "What is buoyancy?" → "medium"
- `test_assess_query_complexity_complex()` - "Where can I dive in Tioman?" → "complex"
- `test_dynamic_top_k_skip()` - Skip query returns empty context
- `test_dynamic_top_k_medium()` - Medium query uses top_k=3
- `test_dynamic_top_k_complex()` - Complex query uses top_k=5
- `test_complexity_scoring_edge_cases()` - Empty query, very long query, mixed signals

### Integration tests

- `test_rag_pipeline_skip_for_greeting()` - "Thanks" returns NO_DATA
- `test_rag_pipeline_medium_query()` - "What is a BCD?" retrieves 3 chunks
- `test_rag_pipeline_complex_query()` - "Where can I dive in Tioman?" retrieves 5 chunks
- `test_rag_token_counting()` - Verify rag_tokens logged correctly

### Manual checks

- Run 30 queries across complexity levels:
  - 5 greetings/simple (should skip RAG, 0 tokens)
  - 15 medium queries (should get 3 chunks, ~1200 tokens)
  - 10 complex queries (should get 5 chunks, ~2000 tokens)
- Measure average RAG tokens before/after optimization
- Verify response quality unchanged for each category
- Check for "I don't have information" responses increasing

---

## Verification

### Commands to run

- Install: `cd backend && .venv/bin/pip install -e .`
- Dev: `cd backend && .venv/bin/uvicorn app.main:app --reload`
- Test: `cd backend && .venv/bin/pytest tests/unit/services/test_rag_pipeline.py -v`
- Test: `cd backend && .venv/bin/pytest tests/integration/services/test_rag_integration.py -v`

### Manual verification checklist

1. Test skip: Send "Hello" → Check logs for "Skipping RAG" and 0 rag_tokens
2. Test medium: Send "What is nitrox?" → Check logs for top_k=3, ~1200 rag_tokens
3. Test complex: Send "Where can I dive in Tioman?" → Check logs for top_k=5, ~2000 rag_tokens
4. Verify response quality maintained across all complexity levels
5. Calculate token savings from PR6.3a baseline
6. Verify no increase in "I don't have information" responses

---

## Rollback Plan

**Feature flag / kill switch:** None (behavior change)

**Revert strategy:**
- Change `rag_top_k` back to 8 in config
- Remove or disable query complexity scoring (set all to "complex")
- Redeploy
- No data loss

---

## Dependencies

**PRs required before this one:**
- PR6.3a (Token Tracking) - To measure RAG token reduction

**External dependencies:** None

---

## Risks & Mitigations

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

## Success Metrics

- RAG context dynamically adjusted based on query complexity
- Token savings of 500-1000 tokens per query on average (RAG component)
- No increase in "I don't have information" responses (≤5% change)
- Response quality maintained across all complexity levels
- 70-80% of queries correctly classified by complexity scorer

---

## Implementation Status (2026-02-08)

**Completed:**
- Reduced `rag_top_k` default to 5
- Added query complexity scoring with skip/medium/complex
- Implemented dynamic `top_k` selection and skip behavior
- Added unit tests for complexity scoring and dynamic `top_k`
- Added integration test for greeting skip behavior

**Pending:**
* Manual 30-query validation and token savings check

**Done since last update:**
- Ran RAG pipeline unit tests
- Ran full backend integration suite (RAG integration and ingestion tests passing with gemini-embedding-001)

**Previous PR:** PR6.3b (Prompt Compression)  
**Next PR:** PR6.3d (Routing Optimization)
