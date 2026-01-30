# PR6.2: Conversation Continuity via Intent + State + Follow-up - Feature Plan

**Status:** 📝 Draft
**Created:** January 30, 2026
**Based on:** docs/decisions/0007-FEATURE-Conversation.md, MASTER_PLAN.md

---

## 0) Assumptions

1. **Hybrid LLM-based conversation management:** Single lightweight LLM call per turn handles intent classification, session state extraction, and contextual follow-up generation. Emergency detection remains keyword-based for safety.
2. **localStorage for session state:** Minimal session state (cert_level, context_mode, location_known, conditions_known, last_intent) stored in localStorage. LLM extracts and updates state naturally from conversation.
3. **Feature flag rollout:** Next-Turn Obligation ships behind a feature flag (FEATURE_CONVERSATION_FOLLOWUP_ENABLED) for gradual rollout and easy rollback.

---

## 1) Clarifying questions

None - plan is actionable with stated assumptions. LLM-based approach provides natural conversation handling while maintaining safety-first principles.

---

## 2) Feature summary

### Goal

Transform DovvyBuddy from a one-shot Q&A assistant into a more conversational dive buddy by ensuring every non-emergency response includes exactly one specific follow-up question that advances planning or fills critical missing session state.

### User story

**As a diver using the chat,**  
**I want** the assistant to naturally continue the conversation with relevant follow-up questions,  
**So that** I feel guided through my diving journey without having to guess what to ask next.

### Acceptance criteria

1. Every non-emergency assistant response ends with **exactly one** specific, actionable follow-up question.
2. Follow-up question must be relevant to the user's intent (not generic "Anything else?").
3. Follow-up question must not introduce new factual claims (safety-first principle).
4. `EMERGENCY_MEDICAL` intent bypasses follow-ups entirely and returns safety-first guidance with referral language.
5. Intent classifier uses LLM to route messages to one of 8 intent types with natural language understanding.
6. Session state tracks: `cert_level`, `context_mode`, `location_known`, `conditions_known`, `last_intent`. LLM extracts state updates from user messages naturally.
7. Unit tests verify: intent routing (with LLM mocking), follow-up enforcement, emergency bypass (keyword-based).
8. Telemetry counters track: % turns with follow-up, average turns per session, LLM call latency.
9. Feature flag allows instant disable/rollback in production.
10. No regression in existing safety refusal behavior.

### Non-goals (explicit)

- No "personality agent" that invents banter or adds ungrounded facts (structured LLM output only).
- No multi-agent orchestration changes (reuses existing agent system from PR3.2c).
- No custom ML model training (uses existing Gemini/Groq providers with structured output).
- No full telemetry dashboard UI (counters only, dashboard in future PR).
- No new frontend navigation flows (inline follow-up text within existing chat UI).
- No cross-device session state sync (localStorage only).

---

## 3) Approach overview

### Proposed UX (high-level)

**Before (current):**
- User: "What is a DSMB?"
- Assistant: "A DSMB is a surface marker buoy used to signal your position to the dive boat."

**After (PR6.2):**
- User: "What is a DSMB?"
- Assistant: "A DSMB is a surface marker buoy used to signal your position to the dive boat. **Are you learning about this for training, planning a dive, or just curious?**"

**Visual change:** Same chat interface. Assistant message bubble now includes a follow-up question in **bold** or as a new line. No new UI components needed.

**Emergency bypass:**
- User: "I have chest pain after diving"
- Assistant: "⚠️ Seek immediate medical attention. Contact DAN or local emergency services. Do not delay." (No follow-up question)

### Proposed API (high-level)

**New backend components:**

1. **Conversation Manager** (`app/orchestration/conversation_manager.py`):
   - Single lightweight LLM call with structured JSON output
   - Input: user message + conversation history (last 3-5 turns) + current session state
   - Output: `{ intent, state_updates, follow_up, bypass_followup }`
   - Uses existing Gemini Flash or Groq provider (fast, cheap)
   - Handles intent classification, state extraction, and follow-up generation in one call

2. **Emergency Detector** (`app/orchestration/emergency_detector.py`):
   - Keyword-based safety check (runs BEFORE LLM call)
   - Input: user message
   - Output: boolean (is_emergency)
   - Bypasses LLM and follow-up logic if emergency detected
   - Keywords: ["chest pain", "can't breathe", "decompression sickness", "injury", "bleeding", "unconscious"]

3. **Response Post-Processor** (integrated into `ChatOrchestrator`):
   - Appends LLM-generated follow-up to assistant response
   - Skips append if emergency detected or bypass_followup=true

**Modified backend flow:**
```
User Message → Emergency Detector → [if emergency: bypass] → Conversation Manager (LLM) → Agent Selection → RAG Retrieval → Main LLM Response → Append Follow-up → Final Response
```

**Frontend changes:**

1. **Session State Hook** (`src/lib/hooks/useSessionState.ts`):
   - Reads/writes minimal session state from localStorage
   - Schema: { cert_level, context_mode, location_known, conditions_known, last_intent }

2. **State Extraction Logic** (backend LLM-driven):
   - Conversation Manager LLM extracts state updates from user messages naturally
   - Frontend receives state_updates in API response and syncs to localStorage
   - No manual keyword parsing needed

3. **Feature Flag Check** (`src/app/chat/page.tsx`):
   - Read NEXT_PUBLIC_FEATURE_CONVERSATION_FOLLOWUP from env
   - If disabled, skip sending session state to backend and skip follow-up rendering

### Proposed data changes (high-level)

**No database schema changes** for V1. Session state stored in localStorage only.

**localStorage schema:**
```json
{
  "dovvybuddy-session-state": {
    "cert_level": "unknown" | "OW" | "AOW" | "DM" | "Instructor",
    "context_mode": "learning" | "planning" | "briefing" | "curiosity",
    "location_known": boolean,
    "conditions_known": boolean,
    "last_intent": "INFO_LOOKUP" | "DIVE_PLANNING" | ... | null
  }
}
```

**Optional V2:** Add `session_state` JSONB column to `sessions` table for server-side persistence.

### AuthZ/authN rules (if any)

None - V1 is guest-only. Auth handled in PR8 separately.

---

## 4) PR plan

### PR Title

feat(conversation): Add intent-driven follow-up questions for continuity

### Branch name

pr6.2-conversation-continuity

### Scope (in)

**Backend:**
- Implement Conversation Manager with structured LLM call (intent + state extraction + follow-up generation).
- Implement Emergency Detector with keyword-based safety check (runs before LLM).
- Integrate conversation management into `ChatOrchestrator`.
- Add feature flag: `FEATURE_CONVERSATION_FOLLOWUP_ENABLED` (default: false).

**Frontend:**
- Add `useSessionState` hook to read/write session state from localStorage.
- Update chat page to send session state with each message (optional payload).
- Receive and apply state updates from backend API response (LLM-extracted).
- Read feature flag from env and conditionally enable/disable feature.

**Testing:**
- Unit tests for Conversation Manager (with LLM mocking via fixtures).
- Unit tests for Emergency Detector (keyword matching, no LLM).
- Unit tests for state extraction (mock LLM responses with state_updates).
- Integration test for full flow: user message → conversation manager → response with follow-up.

**Observability:**
- Add telemetry counters: `conversation.turns_with_followup`, `conversation.total_turns`, `conversation.sessions_started`, `conversation.llm_call_latency_ms`.
- Log intent distribution, LLM call duration, and emergency bypasses to backend logs.

**Documentation:**
- Update README with feature flag instructions.
- Add comments explaining intent rules and follow-up templates.

### Out of scope (explicit)

- Custom ML model training (reuse existing LLM providers).
- Full telemetry dashboard (add counters only, build dashboard in V2).
- Session state server-side persistence (localStorage only for V1).
- Cross-device sync for session state.
- New UI components or navigation (inline follow-up text only).
- Major refactor of existing agent system (reuse PR3.2c agents).

### Key changes by layer

#### Frontend

**File: `src/lib/hooks/useSessionState.ts` (new file)**
- Export `useSessionState()` hook.
- Reads/writes `dovvybuddy-session-state` from localStorage.
- Provides `{ sessionState, updateSessionState, clearSessionState }`.
- Schema: `{ cert_level, context_mode, location_known, conditions_known, last_intent }`.
- Graceful degradation if localStorage unavailable (SecurityError, private browsing).

**File: `src/app/chat/page.tsx` (modifications)**
- Import `useSessionState` hook.
- Send `sessionState` in API request payload (optional field).
- Receive `state_updates` from API response (LLM-extracted).
- Apply state updates to localStorage: merge `response.metadata.state_updates` into current sessionState.
- Read `NEXT_PUBLIC_FEATURE_CONVERSATION_FOLLOWUP` env var. If false, skip sending sessionState.

**File: `src/lib/api-client.ts` (modifications)**
- Update `chat()` method signature to accept optional `sessionState` parameter.
- Include in POST body if provided.

**File: `.env.example` (modifications)**
- Add `NEXT_PUBLIC_FEATURE_CONVERSATION_FOLLOWUP_ENABLED=false` with comment.

#### Backend

**File: `src/backend/app/orchestration/emergency_detector.py` (new file)**
- Define **symptom-based** emergency patterns (first-person, present-tense):
  - Symptom keywords: ["chest pain", "can't breathe", "difficulty breathing", "dizzy", "numb", "paralyzed", "bleeding", "unconscious", "confused", "tingling"]
  - Context filters (must include one of): ["I", "I'm", "I am", "my", "me", "after dive", "after diving", "during dive"]
- Implement `EmergencyDetector` class with `is_emergency(message: str) → bool`.
- Logic:
  1. Check if message contains symptom keyword.
  2. If yes, check if message also contains first-person context.
  3. Return True only if both conditions met.
- Examples:
  - "I have chest pain after diving" → True (symptom + first-person)
  - "What is decompression sickness?" → False (no first-person context)
  - "Can you explain DCS symptoms?" → False (educational query)
  - "My buddy is dizzy after the dive" → True (symptom + possessive first-person)
- Case-insensitive matching (fast, deterministic, safety-critical).
- No LLM call for safety-critical detection.
- Log all emergency detections for monitoring false positive/negative rates.

**File: `src/backend/app/orchestration/conversation_manager.py` (new file)**
- Define `IntentType` enum: INFO_LOOKUP, DIVE_PLANNING, CONDITIONS, SKILL_EXPLANATION, MARINE_LIFE, GEAR, AGENCY_CERT, EMERGENCY_MEDICAL.
- Define `SessionState` dataclass: cert_level, context_mode, location_known, conditions_known, last_intent.
- Define `ConversationAnalysis` dataclass: intent, state_updates, follow_up, bypass_followup, confidence.
- Implement `ConversationManager` class with `analyze(message: str, history: List[Dict], state: SessionState) → ConversationAnalysis`.
- Single LLM call with structured JSON output:
  - System prompt instructs LLM to return: `{ "intent": "...", "state_updates": {...}, "follow_up": "...", "confidence": 0.0-1.0 }`.
  - Rules embedded in prompt:
    - Detect intent from user message and conversation context.
    - Extract state updates naturally (e.g., "I'm Open Water certified" → cert_level: "OW").
    - Generate exactly one contextual follow-up question (max 100 chars, must end with ?).
    - No numbers, no site/depth/condition specifics, no advice in follow-ups.
    - Prioritize state-gap questions if critical fields unknown.
    - Return confidence score (0.0-1.0) for intent classification.
  - Use lightweight model: Gemini Flash or Groq llama-3.1-70b (fast inference).
  - Parse JSON response, validate schema with **field-level fallbacks**:
    - `intent`: If missing/invalid → INFO_LOOKUP (always safe fallback).
    - `state_updates`: If missing/invalid → {} (skip state updates, no harm).
    - `follow_up`: If missing/invalid/fails validation → use intent-based template fallback.
    - `confidence`: If missing → 0.5 (neutral default).
  - **Confidence-based behavior:**
    - confidence < 0.4: Force intent=INFO_LOOKUP, use clarifying follow-up, skip state updates.
    - confidence ≥ 0.4: Use extracted intent and state normally.
- Follow-up validation (post-LLM):
  - Must be exactly one question (no multiple ? marks).
  - Must end with ? character.
  - Must be ≤ 100 characters.
  - Must not contain numbers (no "dive to 30m", no "site #3").
  - Must not contain site names, depth references, or condition specifics.
  - If validation fails: fall back to intent-based template (e.g., "What certification level are you?").
- Error handling: if LLM call fails entirely, return fallback (intent=INFO_LOOKUP, no state updates, template follow-up).

**File: `src/backend/app/orchestration/types.py` (modifications)**
- Add `session_state: Optional[Dict[str, Any]]` to `ChatRequest` dataclass.
- Add `follow_up_question: Optional[str]` to `ChatResponse` dataclass.
- Add `state_updates: Optional[Dict[str, Any]]` to `ChatResponse` metadata (for syncing to frontend).

**File: `src/backend/app/orchestration/orchestrator.py` (modifications)**
- Import `ConversationManager` and `EmergencyDetector`.
- Instantiate in `__init__`.
- **Before mode detection:** Check for emergency: `emergency_detector.is_emergency(request.message)`.
  - If emergency: skip conversation manager, set bypass_followup=True, return safety response immediately.
- **Otherwise:** Call `conversation_manager.analyze(request.message, history, session_state)` → returns ConversationAnalysis.
- Store detected intent and state_updates in metadata.
- Use detected intent for agent selection (existing flow).
- After agent execution, append follow-up to `response.message` if not bypassed.
- Update session state with LLM-extracted state_updates.
- Add logging: "Intent: {intent}, State updates: {state_updates}, Follow-up: {yes/no}, LLM latency: {ms}".

**File: `src/backend/app/api/routes/chat.py` (modifications)**
- Update `ChatRequestPayload` to include optional `session_state: Optional[dict]` field.
- Pass `session_state` to `ChatRequest` when calling orchestrator.
- Return `follow_up_question` and `state_updates` in `ChatResponsePayload` metadata.

**File: `src/backend/app/core/config.py` (modifications)**
- Add `feature_conversation_followup_enabled: bool = Field(default=False)` setting.
- Load from `FEATURE_CONVERSATION_FOLLOWUP_ENABLED` env var.

**File: `src/backend/pyproject.toml` (dependencies)**
- No new dependencies required (uses existing LLM provider from PR3.2c).

#### Data

No database migrations for V1. Session state stored in localStorage only.

Optional V2 migration:
```sql
ALTER TABLE sessions ADD COLUMN session_state JSONB DEFAULT '{}'::jsonb;
```

#### Infra/config

**Environment Variables:**

- **Backend:** `FEATURE_CONVERSATION_FOLLOWUP_ENABLED=false` (default: false for gradual rollout).
- **Frontend:** `NEXT_PUBLIC_FEATURE_CONVERSATION_FOLLOWUP_ENABLED=false` (must match backend).

**Deployment:**
- Deploy backend first with feature flag OFF.
- Verify no regressions in production.
- Enable feature flag via env var (no code deploy needed).
- Monitor telemetry for 24 hours.
- If issues detected, disable flag immediately.

#### Observability

**Backend Logging (structured):**
- Log detected intent for each message: `logger.info(f"Intent: {intent}, confidence: {confidence:.2f}")`.
- Log follow-up generation: `logger.info(f"Follow-up: {follow_up}, validation: {passed/failed}, fallback: {yes/no}")`.
- Log emergency detection: `logger.warning(f"Emergency detected: symptom={symptom}, context={first_person}, bypassing conversation manager")`.
- Log low confidence: `logger.info(f"Low confidence ({confidence:.2f}), forcing INFO_LOOKUP, skipping state updates")`.
- Log field-level fallbacks: `logger.warning(f"LLM field missing/invalid: {field_name}, using fallback")`.

**Telemetry Counters (Sentry/custom):**
- `conversation.turns_with_followup`: Increment when follow-up is appended.
- `conversation.followup_validation_failures`: Increment when LLM follow-up fails validation.
- `conversation.followup_template_fallbacks`: Increment when falling back to template.
- `conversation.low_confidence_intents`: Increment when confidence < 0.4.
- `conversation.emergency_detections`: Increment on emergency keyword detection.
- `conversation.total_turns`: Increment on every chat turn.
- `conversation.sessions_started`: Increment on new session creation (existing counter).
- Derived metrics:
  - `% turns with follow-up = turns_with_followup / total_turns`
  - `% follow-up validation failures = followup_validation_failures / total_turns`
  - `% low confidence = low_confidence_intents / total_turns`

**Analytics Events (Vercel/PostHog/GA4):**
- `conversation_intent_detected` with properties: `{ intent, confidence }`.
- `conversation_followup_shown` with properties: `{ intent, state_known_fields }`.

### Edge cases to handle

1. **Ambiguous intent:**
   - LLM uses conversation context to disambiguate naturally.
   - Emergency detection remains keyword-based (no ambiguity, safety-first).

2. **User ignores follow-up and changes topic:**
   - Intent classifier handles topic shift naturally.
   - Session state persists but doesn't block new intents.

3. **User message is too short ("ok", "yes", "no"):**
   - LLM uses conversation history (last 3-5 turns) to understand context.
   - Follow-up continues previous conversation thread naturally.

4. **localStorage unavailable (private browsing):**
   - Frontend catches SecurityError, continues without session state.
   - Backend still generates follow-ups based on conversation history alone.

5. **Feature flag OFF:**
   - Backend skips intent classification and follow-up generation.
   - Frontend skips session state tracking and parsing.
   - Zero performance impact when disabled.

6. **Emergency misdetection:**
   - Keyword-based emergency detection (NOT LLM-based) to ensure deterministic safety behavior.
   - Conservative keyword list to minimize false negatives.
   - If emergency keywords detected, bypass LLM conversation manager entirely.

7. **Follow-up question too long:**
   - LLM prompt instructs max 100 characters for follow-up.
   - Backend validates and truncates if needed.
   - Test rendering on mobile devices.

8. **LLM call timeout or failure:**
   - Set 2-second timeout for conversation manager LLM call.
   - If timeout or error: field-level fallbacks (intent=INFO_LOOKUP, state_updates={}, template follow-up).
   - Log error to Sentry, continue processing without blocking user.

9. **LLM returns invalid JSON:**
   - Validate JSON schema with Pydantic.
   - Use field-level fallbacks for missing/invalid fields.
   - Log error for monitoring.

10. **LLM generates unsafe follow-up:**
   - Validation catches: contains numbers, site names, depth references, or multiple questions.
   - Falls back to intent-based template.
   - Log validation failure for prompt tuning.

11. **Low confidence classification:**
   - If confidence < 0.4: force intent to INFO_LOOKUP, skip state updates, use clarifying follow-up.
   - Prevents incorrect state pollution from ambiguous messages.

### Migration/compatibility notes (if applicable)

**No breaking changes.** All changes are additive:
- Backend: New optional `session_state` field in request (backward compatible).
- Frontend: New localStorage key (doesn't affect existing sessions).
- Feature flag defaults to OFF (existing behavior unchanged).

**Rollout strategy:**
1. Deploy backend + frontend with flag OFF.
2. Test in staging with flag ON.
3. Enable flag for 10% of production traffic (A/B test group).
4. Monitor telemetry for 24 hours.
5. Gradually increase to 50% → 100% over 1 week.
6. Make flag default to ON after 2 weeks of stable production.

---

## 5) Testing & verification

### Automated tests to add/update

#### Unit Tests

**File: `src/backend/tests/unit/orchestration/test_emergency_detector.py` (new)**
- Test symptom + context detection (keyword-based, no LLM):
  - **True (emergency):**
    - "I have chest pain after diving" → True (symptom + first-person)
    - "I can't breathe" → True (symptom + first-person)
    - "My buddy is dizzy after the dive" → True (symptom + possessive first-person)
    - "I feel numb in my hands" → True (symptom + first-person)
  - **False (educational/informational):**
    - "What is decompression sickness?" → False (no first-person)
    - "Can you explain DCS symptoms?" → False (no first-person)
    - "Tell me about chest pain in diving" → False (no first-person)
    - "Where should I dive?" → False (no symptom)
- Test case-insensitive matching.
- Test partial matches (e.g., "chest pain" in longer sentence with first-person context).
- Test edge cases:
  - "I want to learn about DCS" → False (informational intent)
  - "I think my friend has chest pain" → False (third-person, not first-person emergency)

**File: `src/backend/tests/unit/orchestration/test_conversation_manager.py` (new)**
- Mock LLM provider to return fixed JSON responses.
- Test intent classification with mocked responses:
  - DIVE_PLANNING: mock LLM returns `{"intent": "DIVE_PLANNING", ...}`
  - INFO_LOOKUP: mock LLM returns `{"intent": "INFO_LOOKUP", ...}`
- Test state extraction:
  - User says "I'm Open Water certified" → mock LLM returns `{"state_updates": {"cert_level": "OW"}}`
  - User says "planning a trip to Tioman" → mock LLM returns `{"state_updates": {"location_known": true, "context_mode": "planning"}}`
- Test follow-up generation:
  - Verify mock LLM returns exactly one follow-up question (single ?).
  - Verify follow-up ends with ? character.
  - Verify follow-up is ≤ 100 characters.
  - Verify follow-up contains no numbers.
  - Verify follow-up contains no site names or depth references.
- Test follow-up validation and fallback:
  - Mock LLM returns invalid follow-up (no ?, or >100 chars, or contains numbers) → verify falls back to template.
  - Mock LLM returns empty follow-up → verify falls back to template.
  - Verify template fallback is intent-specific (DIVE_PLANNING → "Which destination?", INFO_LOOKUP → "Is this for learning or planning?").
- Test LLM timeout/error handling:
  - Mock LLM to raise timeout → verify fallback behavior.
  - Mock LLM to return invalid JSON → verify fallback behavior.
- Test confidence-based behavior:
  - Mock LLM returns confidence < 0.4 → verify intent forced to INFO_LOOKUP, state updates skipped.
  - Mock LLM returns confidence ≥ 0.4 → verify intent and state updates used normally.
  - Mock LLM returns missing confidence field → verify defaults to 0.5.
- Test field-level fallbacks:
  - Mock LLM returns missing intent → verify defaults to INFO_LOOKUP.
  - Mock LLM returns invalid state_updates → verify skipped (empty dict).
  - Mock LLM returns missing follow_up → verify uses template fallback.

**File: `src/backend/tests/unit/orchestration/test_orchestrator.py` (update existing)**
- Test emergency detector called before conversation manager.
- Test emergency bypass (no conversation manager call, no follow-up).
- Test conversation manager called when no emergency.
- Test intent from conversation manager used for agent selection.
- Test state_updates applied to session.
- Test follow-up appended to response.
- Test feature flag disables conversation manager.

**File: `src/app/chat/__tests__/useSessionState.test.tsx` (new)**
- Test `useSessionState` hook reads/writes localStorage.
- Test graceful degradation when localStorage unavailable.
- Test `clearSessionState` removes localStorage key.
- Test state update merging from API response:
  - API returns `state_updates: {"cert_level": "OW"}` → merged into localStorage.
  - Partial updates don't overwrite entire state.

#### Integration Tests

**File: `src/backend/tests/integration/test_chat_with_followup.py` (new)**
- Test full chat flow with follow-up:
  - Send user message → verify response includes follow-up.
  - Send follow-up answer → verify next response has new follow-up.
  - Send emergency message → verify no follow-up.
- Test session state updates via API.
- Test feature flag ON/OFF behavior.

#### E2E Tests (optional, can defer to manual)

**File: `tests/e2e/conversation-continuity.spec.ts` (optional)**
- Navigate to chat page.
- Send message: "What is Open Water certification?"
- Assert assistant response ends with follow-up question.
- Type follow-up answer.
- Assert next response also has follow-up.

### Manual verification checklist

**Pre-requisites:**
- Backend running: `cd src/backend && uvicorn app.main:app --reload`
- Frontend running: `pnpm dev`
- Feature flag ON: `FEATURE_CONVERSATION_FOLLOWUP_ENABLED=true` in backend and `NEXT_PUBLIC_FEATURE_CONVERSATION_FOLLOWUP_ENABLED=true` in frontend.

**Test cases:**

1. **Basic follow-up generation:**
   - [ ] Clear localStorage.
   - [ ] Navigate to http://localhost:3000/chat.
   - [ ] Send: "What is a DSMB?"
   - [ ] Verify response includes follow-up question (e.g., "Is this for learning, planning, or just curious?").
   - [ ] Verify follow-up is **bold** or on new line.

2. **State-driven follow-up prioritization:**
   - [ ] Clear localStorage.
   - [ ] Send: "Where should I dive in Malaysia?"
   - [ ] Verify response asks about certification level (LLM detects missing state).
   - [ ] Send: "I'm Open Water certified."
   - [ ] Verify localStorage updated: `cert_level = "OW"` (LLM extracted).
   - [ ] Verify console log shows state_updates from backend.
   - [ ] Send: "Where should I dive in Malaysia?" again.
   - [ ] Verify response now asks different question (LLM sees cert_level now known).

3. **Emergency detection accuracy:**
   - [ ] Send: "I have chest pain after diving."
   - [ ] Verify response contains safety warning.
   - [ ] Verify NO follow-up question appended.
   - [ ] Verify console log: "Emergency detected: symptom + first-person context".
   - [ ] Send: "What is decompression sickness?" (educational)
   - [ ] Verify response includes follow-up (NOT treated as emergency).
   - [ ] Verify console log: "No emergency detected (educational query, no first-person context)".

4. **Follow-up validation:**
   - [ ] Observe multiple responses.
   - [ ] Verify all follow-ups end with ? character.
   - [ ] Verify all follow-ups are ≤ 100 characters.
   - [ ] Verify no follow-ups contain numbers (e.g., "dive to 30m").
   - [ ] Verify no follow-ups name specific sites or conditions.
   - [ ] If LLM generates invalid follow-up, verify fallback to template in console log.

5. **Feature flag OFF:**
   - [ ] Stop backend, set `FEATURE_CONVERSATION_FOLLOWUP_ENABLED=false`.
   - [ ] Restart backend.
   - [ ] Send message.
   - [ ] Verify response has NO follow-up question (existing behavior).

6. **localStorage unavailable (private browsing):**
   - [ ] Open chat in private/incognito window.
   - [ ] Send message.
   - [ ] Verify response still includes follow-up (backend uses history only).
   - [ ] Verify console warning: "localStorage unavailable, session state will not persist".

7. **Cross-turn continuity:**
   - [ ] Clear localStorage.
   - [ ] Send 5 messages in a conversation.
   - [ ] Verify each response (except emergency) includes follow-up.
   - [ ] Verify follow-ups are contextually relevant (not repetitive).

### Commands to run

**Install dependencies:**
```bash
pnpm install
cd src/backend && pip install -e .
```

**Run frontend dev server:**
```bash
pnpm dev
```

**Run backend dev server:**
```bash
cd src/backend
uvicorn app.main:app --reload
```

**Run unit tests:**
```bash
# Frontend
pnpm test

# Backend
cd src/backend
pytest tests/unit/orchestration/
```

**Run integration tests:**
```bash
cd src/backend
pytest tests/integration/test_chat_with_followup.py
```

**Run E2E tests (optional):**
```bash
pnpm test:e2e
```

**Lint:**
```bash
pnpm lint
```

**Typecheck:**
```bash
pnpm typecheck
```

**Build:**
```bash
pnpm build
```

---

## 6) Rollback plan

### Immediate rollback (zero-downtime)

1. **Disable feature flag in production env:**
   - Set `FEATURE_CONVERSATION_FOLLOWUP_ENABLED=false` in backend.
   - Set `NEXT_PUBLIC_FEATURE_CONVERSATION_FOLLOWUP_ENABLED=false` in frontend.
   - Restart services (or use hot-reload if supported).
   - Feature disabled instantly without code revert.

2. **Monitor telemetry:**
   - Verify `conversation.turns_with_followup` counter drops to 0.
   - Verify no errors in Sentry or logs.

### Full rollback (if flag toggle insufficient)

1. **Revert PR branch:**
   - `git revert <commit-hash>` or merge revert PR.
   - Deploy reverted code to production.

2. **Clear localStorage (client-side):**
   - No action needed - localStorage key `dovvybuddy-session-state` is harmless if unused.
   - Future PR can add cleanup logic if needed.

### Risks and mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Intent misclassification causes irrelevant follow-ups | Low | LLM uses conversation context. Fallback to INFO_LOOKUP on errors. Monitor user feedback. |
| Follow-ups feel interrogative/annoying | Medium | Limit to one question per turn. LLM prompt instructs friendly/conversational tone. A/B test sentiment. |
| localStorage quota exceeded | Low | Session state is tiny (~200 bytes). Catch QuotaExceededError, log warning, continue. |
| Emergency intent bypass fails (safety risk) | High | Keyword-based detection (NOT LLM). Multiple emergency keywords. Unit tests enforce bypass. Logging alerts on emergency detection. |
| LLM latency increases response time | Medium | Use lightweight model (Gemini Flash ~100ms). Set 2s timeout. Fallback on timeout. |
| LLM costs increase per message | Low | Gemini Flash: ~$0.0001/message. Budget impact: $1 per 10k messages. |
| LLM returns invalid/unsafe follow-ups | Low | Multi-layer validation: ends with ?, ≤100 chars, no numbers/sites/advice. Template fallback if validation fails. |
| Emergency false positives (educational queries) | Medium | Symptom + first-person context required. "What is DCS?" will NOT trigger emergency. Log all detections for monitoring. |
| Low confidence causes incorrect state updates | Low | Confidence < 0.4 forces INFO_LOOKUP, skips state updates. Prevents pollution from ambiguous messages. |

### Monitoring for success

**Metrics to watch (first 48 hours):**
- `conversation.turns_with_followup / conversation.total_turns` → target: >80%.
- `conversation.followup_validation_failures / conversation.total_turns` → target: <5% (LLM prompt quality indicator).
- `conversation.low_confidence_intents / conversation.total_turns` → target: <10%.
- Average turns per session → target: ≥3 turns (up from current ~1.5).
- Session drop-off after 1st answer → target: <50% (down from current ~70%).
- Conversation manager LLM call latency (p50, p95) → target: p50 <150ms, p95 <500ms.
- Conversation manager error rate → target: <1% (with graceful fallback).
- Emergency detection false positive rate → target: <1% (monitor educational queries).
- Emergency detection false negative rate → target: 0% (safety-critical).

**User feedback:**
- Monitor support channels for complaints about "too many questions".
- Track lead conversion rate (should remain stable or improve).

---

## 7) Follow-ups (optional)

1. **PR6.3: Fine-tune conversation manager on production data (V2)**
   - Collect production conversation logs (intent, state, follow-up quality).
   - Fine-tune small model on DovvyBuddy-specific patterns.
   - Improve intent accuracy and follow-up relevance.

2. **PR6.4: Session state server-side persistence**
   - Add `session_state` JSONB column to `sessions` table.
   - Sync localStorage state to backend on each turn.
   - Enable cross-device continuity (requires auth from PR8).

3. **PR6.5: A/B test follow-up vs no-follow-up**
   - Split production traffic 50/50.
   - Measure: average turns/session, lead conversion rate, user sentiment.
   - Decide on permanent rollout or iteration.

4. **PR6.6: Telemetry dashboard for conversation metrics**
   - Build Grafana/Metabase dashboard with:
     - Intent distribution over time.
     - Average session length trend.
     - Follow-up engagement rate (users who answer follow-up vs ignore).

5. **PR6.7: Multi-turn context-aware follow-ups**
   - Improve follow-up relevance by analyzing multi-turn patterns.
   - Avoid repetitive questions when state already inferred.
   - Use LLM to generate dynamic follow-ups (fallback when templates insufficient).

---

**End of PR6.2 Plan**
