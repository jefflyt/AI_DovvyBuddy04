# PR6.3e: Conversation History Optimization

**Part of Epic:** PR6.3 Gemini API Cost Efficiency Optimization

**Status:** Implementation Complete

**Owner:** jefflyt

**Date:** 2026-02-08

---

## Goal

Reduce conversation history token usage by 40-60% through sliding window reduction and token budget enforcement, while maintaining conversation continuity.

---

## Scope

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

---

## Backend Changes

### Services/modules to modify

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

### Auth, validation, error handling

- Empty history handled gracefully (already exists)
- Token budget failures default to empty history (conservative)

---

## Frontend Changes

No changes.

---

## Data Changes

**No migrations or schema changes.**

Full conversation history still stored in database. Only in-memory processing changes (what gets passed to LLM).

---

## Infra / Config

**Environment variables:**
- `MAX_HISTORY_TOKENS` - NEW, default 1500

---

## Testing

### Unit tests

- `test_truncate_history_by_tokens_empty()` - Handle empty history
- `test_truncate_history_by_tokens_under_budget()` - All messages fit
- `test_truncate_history_by_tokens_over_budget()` - Truncates oldest
- `test_truncate_history_preserves_order()` - Verify message order maintained
- `test_truncate_history_respects_budget()` - Verify total ≤ max_tokens
- `test_token_counting_for_messages()` - Verify token counting accurate

### Integration tests

- `test_conversation_with_short_history()` - 4 messages, all included
- `test_conversation_with_long_history()` - 15 messages, only 6 most recent
- `test_history_token_budget_enforced()` - Large messages, verify truncation
- `test_conversation_continuity_maintained()` - Response contextually relevant

### Manual checks

- Create long conversation (20 messages)
- Verify only 6 most recent messages passed to agent
- Verify token budget never exceeded (≤1500 tokens)
- Test conversation continuity:
  - 3-turn conversation about Tioman
  - Verify bot remembers context from previous turns
- Measure history token savings from PR6.3a baseline

---

## Verification

### Commands to run

- Install: `cd backend && .venv/bin/pip install -e .`
- Dev: `cd backend && .venv/bin/uvicorn app.main:app --reload`
- Test: `cd backend && .venv/bin/pytest tests/unit/orchestration/test_context_builder.py -v`
- Test: `cd backend && .venv/bin/pytest tests/integration/ -k conversation -v`

### Manual verification checklist

1. Start conversation, send 10 messages
2. Check logs: Verify "Conversation history: 6 messages" (not 10)
3. Verify token budget: Verify history_tokens ≤ 1500 in logs
4. Test continuity: Ask follow-up question, verify contextually relevant response
5. Test very long messages: Send messages with 500+ chars each, verify truncation
6. Calculate history token savings from PR6.3a baseline
7. Verify no degradation in follow-up question quality

---

## Rollback Plan

**Feature flag / kill switch:** None (behavior change)

**Revert strategy:**
- Change history slice back to `[-10:]` in agents
- Remove token budget enforcement in context_builder
- Redeploy
- No data loss (full history still in DB)

---

## Dependencies

**PRs required before this one:**
- PR6.3a (Token Tracking) - To measure history token reduction

**External dependencies:** None

---

## Risks & Mitigations

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

## Success Metrics

- Conversation history reduced to 6 messages with token budget
- History token savings: 500-800 tokens per query on average
- Token budget never exceeded (max 1500 tokens, 100% compliance)
- Conversation continuity maintained (context-aware responses in multi-turn tests)
- No degradation in follow-up question quality
- Zero user complaints about bot "forgetting" context

---

## Epic Completion

**With PR6.3e completed, the entire PR6.3 epic delivers:**
- Total token reduction of 40-50% vs baseline
- Cost reduced from ~$0.03 to ~$0.015 per query
- Response quality maintained across all test scenarios
- All diving info still references RAG database
- Comprehensive token tracking and cost visibility

---

**Previous PR:** PR6.3d (Routing Optimization)  
**Epic:** PR6.3 (Gemini API Cost Efficiency Optimization) - COMPLETE

---

## Implementation Status (2026-02-08)

**Completed:**
- Added `max_history_tokens` config
- Implemented token-budget truncation in context builder
- Reduced agent history window to 6 messages
- Added unit tests for token-based history truncation

**Pending:**
* Manual multi-turn validation and token savings check

**Done since last update:**
- Ran context builder unit tests
- Ran full backend integration suite (38 tests)
