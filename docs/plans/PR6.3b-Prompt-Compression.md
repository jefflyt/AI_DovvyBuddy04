# PR6.3b: Prompt Compression

**Part of Epic:** PR6.3 Gemini API Cost Efficiency Optimization

**Status:** Implementation Complete

**Owner:** jefflyt

**Date:** 2026-02-08

---

## Goal

Reduce system prompt and RAG prompt token count by 40-60% while preserving essential instructions, safety guardrails, and RAG adherence rules.

---

## Scope

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

---

## Backend Changes

### Services/modules to modify

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

### Auth, validation, error handling

No changes

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

- `test_rag_prompt_token_count()` - Verify compressed ≤ 250 tokens
- `test_base_prompt_token_count()` - Verify compressed ≤ 180 tokens
- `test_no_rag_prompt_token_count()` - Verify compressed ≤ 40 tokens
- `test_prompts_contain_safety_disclaimers()` - Verify critical rules preserved
- `test_prompts_contain_rag_adherence_rules()` - Verify "use only verified info" present

### Integration tests

- `test_chat_with_compressed_prompts()` - Full chat flow works
- `test_rag_adherence_maintained()` - "Where can I dive in Tioman?" returns specific sites
- `test_safety_disclaimers_maintained()` - "Can I dive with a cold?" advises medical professional
- `test_response_formatting()` - Multiple sites use bullet formatting

### Regression tests

- Rerun PR6.2 Response Discipline tests (5 scenarios)
- Verify all pass with compressed prompts

### Manual checks

- Run 20 diverse queries:
  - 10 with RAG context (destinations, certifications, safety)
  - 5 without RAG (general diving knowledge)
  - 5 edge cases (medical, equipment, marine life)
- Compare response quality to baseline (PR6.3a logs)
- Check for hallucinations (generic site descriptions where specifics expected)
- Verify formatting maintained (bullet lists, blank lines)
- Verify safety disclaimers present

---

## Verification

### Commands to run

- Install: `cd backend && .venv/bin/pip install -e .`
- Dev: `cd backend && .venv/bin/uvicorn app.main:app --reload`
- Test: `cd backend && .venv/bin/pytest tests/unit/prompts/ -v`
- Test: `cd backend && .venv/bin/pytest tests/integration/ -k chat -v`

### Manual verification checklist

1. Start backend with compressed prompts
2. Test RAG adherence: "Best dive sites in Tioman?" → Should list specific sites (Tiger Reef, Renggis)
3. Test safety: "Is it safe to fly after diving?" → Should reference 18-24hr rule from RAG
4. Test medical: "Can I dive with diabetes?" → Should recommend consulting doctor
5. Test formatting: Multiple sites should use bullets with blank lines
6. Compare token usage in logs: verify 200-300 tokens saved per request
7. Verify no generic answers where specifics expected

---

## Rollback Plan

**Feature flag / kill switch:** None (prompt changes only)

**Revert strategy:**
- Revert `backend/app/prompts/rag.py` and `system.py`
- Instant rollback, no dependencies
- No data impact

---

## Dependencies

**PRs required before this one:**
- PR6.3a (Token Tracking) - To measure token savings

**External dependencies:** None

---

## Risks & Mitigations

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

## Success Metrics

- Prompts compressed by 40-60% with quality maintained
- Token savings of 200-300 tokens per request
- No quality degradation in 20-query validation test
- Response formatting preserved (bullets, blank lines)
- Safety disclaimers maintained (100% pass rate on safety tests)
- RAG adherence maintained (no hallucinations in manual tests)

---

## Implementation Status (2026-02-08)

**Completed:**
- Compressed `RAG_SYSTEM_PROMPT` and `NO_RAG_PROMPT`
- Compressed `BASE_SYSTEM_PROMPT` and `GENERAL_SYSTEM_PROMPT`
- Added unit tests for token counts and required safety/RAG rules
- Prompt unit tests passed
- Integration chat tests passed (selected with -k chat)

**Pending:**
* Manual 20-query quality check vs PR6.3a baseline

**Verification Notes:**
- Unit tests executed: tests/unit/prompts
- Integration tests executed: tests/integration (full backend suite)

**Previous PR:** PR6.3a (Token Tracking)  
**Next PR:** PR6.3c (Smart RAG Context Management)
