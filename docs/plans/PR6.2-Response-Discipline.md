# PR6.2: User-Facing Response Discipline - Feature Plan

**Status:** 🟡 PLANNED  
**Created:** January 31, 2026  
**Based on:** docs/decisions/0008-FEATURE-User-facing-Response.md  
**Depends on:** PR6.1 (Conversation Continuity)

---

## 0) Assumptions

1. **PR6.1 is complete and tested**: Conversation Manager with follow-up generation is working and feature-flagged.
2. **Token counting is not enforced server-side initially**: We'll rely on prompt instructions and LLM behavior first; if needed, add post-generation token validation in future iteration.
3. **Emergency detection remains unchanged**: PR6.1's `EmergencyDetector` handles medical emergencies correctly and bypasses follow-ups.

---

## 1) Clarifying questions

None – requirements are explicit in the feature document.

---

## 2) Feature summary

### Goal

Enforce strict user-facing response discipline across all agent responses to optimize for token efficiency, readability, and clean UX by eliminating internal RAG mentions and enforcing concise output.

### User story

As a **DovvyBuddy user**, I want **clear, concise answers without technical jargon or system internals** so that **I get quick, actionable information without confusion**.

### Acceptance criteria

1. ✅ **Default response length**: 3-5 sentences OR ≤120 tokens (whichever comes first).
2. ✅ **Single primary idea**: Each response addresses one core concept only.
3. ✅ **No RAG/source mentions**: Never expose "provided context", "source", "filename", "document", "retrieval", "according to the context", or bracketed references like `[Source: ...]`.
4. ✅ **Citations as metadata only**: If citations exist, return them in `metadata.citations` field, not in visible message text.
5. ✅ **No generic closers**: Avoid "Let me know if you need anything else" or similar fluff.
6. ✅ **Safety notes concise**: Safety disclaimers limited to one sentence unless emergency override.
7. ✅ **Emergency override**: If emergency detected, provide urgent medical instructions without follow-up questions (existing behavior preserved).
8. ✅ **Style consistency**: Professional, direct, calm tone across all agents.
9. ✅ **Feature flag compatibility**: Works seamlessly with conversation continuity feature flag (on/off).
10. ✅ **Unit tests pass**: All existing agent tests updated to validate new response format.

### Non-goals (explicit)

- Token counting/enforcement at generation time (defer to future PR if needed).
- Response streaming or incremental display (out of scope).
- Multi-turn response splitting (responses must fit in one turn).
- Custom response length per agent type (all agents use same discipline).

---

## 3) Approach overview

### Proposed UX (high-level)

**Before (current):**
```
User: "What certifications do I need for wreck diving?"

DovvyBuddy: "Great question! Based on the provided context, wreck diving 
typically requires an Advanced Open Water certification at minimum. PADI 
offers a Wreck Diver specialty course that covers penetration diving, 
navigation, and safety protocols. According to our documentation, you 
should also have good buoyancy control and at least 20 logged dives. 
Different agencies like SSI also offer similar courses. Would you like to 
know more about specific prerequisites or training requirements? Let me 
know if you need anything else!"
```

**After (PR6.2):**
```
User: "What certifications do I need for wreck diving?"

DovvyBuddy: "Wreck diving typically requires Advanced Open Water 
certification as a baseline. PADI and SSI both offer Wreck Diver specialty 
courses that cover penetration techniques and safety. Most instructors 
recommend having 20+ logged dives and solid buoyancy control first.

Which certification agency are you training with?"
```

**Key differences:**
- No "provided context" or "according to documentation" mentions
- Concise (3 sentences + follow-up)
- Direct, professional tone
- One clear idea (cert requirements)
- Follow-up question (from PR6.1) preserved

### Proposed API (high-level)

**No API changes required.** Response structure remains identical:

```typescript
interface ChatResponse {
  message: string;           // Formatted response text (enforces discipline)
  session_id: string;
  agent_type: string;
  metadata?: {
    mode?: string;
    intent?: string;
    confidence?: number;
    citations?: Array<{     // NEW: extracted from response, not shown to user
      source: string;
      chunk_id?: string;
    }>;
    state_updates?: SessionState;
    follow_up?: string;
  };
}
```

### Proposed data changes (high-level)

**No database schema changes.** This is purely prompt/response formatting logic.

### AuthZ/authN rules (if any)

None – applies to all guest sessions uniformly.

---

## 4) PR plan

### PR Title

**PR6.2: Enforce User-Facing Response Discipline (Concise, No RAG Mentions)**

### Branch name

`feature/pr6.2-response-discipline`

### Scope (in)

1. **Update all agent system prompts** (`backend/app/agents/*.py`) with strict response discipline instructions.
2. **Update orchestrator/response formatter** to strip any leaked RAG references if agents fail to comply.
3. **Update RAG service integration** to ensure citations are extracted and moved to metadata, not response text.
4. **Update tests** to validate response format (no forbidden terms, concise length guidelines).
5. **Add response validation utility** (optional) to log warnings when responses violate discipline rules (for monitoring, not blocking).
6. **Update documentation** (backend README, SERVICES.md) to reflect new response standards.

### Out of scope (explicit)

- Token counting/enforcement middleware (future PR if needed).
- Response length limits enforced by LLM provider (rely on prompt instructions).
- Dynamic response length tuning per user preference (future feature).
- Conversation history summarization (defer to PR7+).
- Prompt testing framework (defer to PR11 "Post-Launch Iteration").

### Key changes by layer

#### Frontend

**No frontend changes required.** Response text is consumed as-is from API.

#### Backend

**1. Agent System Prompts** (`backend/app/agents/*.py`)

Update all agent classes:
- `CertificationAgent` (`certification.py`)
- `TripAgent` (`trip.py`)
- `SafetyAgent` (`safety.py`)
- `RetrievalAgent` (`retrieval.py`)

**Changes in each `_build_messages()` method:**

Add strict response discipline block to system prompt:

```python
RESPONSE DISCIPLINE (CRITICAL):
- Default length: 3-5 sentences OR ≤120 tokens (whichever comes first)
- Address ONE primary idea per response
- NEVER mention: "provided context", "source", "filename", "document", 
  "retrieval", "according to the context", bracketed references [Source: ...]
- If information is insufficient, ask a clarifying question instead
- Style: Professional, direct, calm. No fluff, no cheerleading, no repetition
- Avoid generic closers like "Let me know if you need anything else"
- Safety notes: ONE sentence max (unless emergency override)
```

**2. Response Formatter** (`backend/app/orchestration/response_formatter.py`)

Add post-processing method to strip any leaked RAG references:

```python
def sanitize_response(self, response: str) -> str:
    """
    Remove any leaked RAG/source references from response text.
    
    Strips common patterns:
    - "according to the context"
    - "based on the provided information"
    - "from the documentation"
    - "[Source: ...]" brackets
    
    Returns sanitized response.
    """
    ...
```

Call this method in orchestrator before returning `ChatResponse`.

**3. RAG Service** (`backend/app/services/rag_service.py`)

Update `retrieve()` method to return citations separately:

```python
@dataclass
class RAGResult:
    context: str              # Combined chunk text for LLM
    citations: List[Citation] # Extracted source metadata
    relevance_scores: List[float]

@dataclass
class Citation:
    source: str              # content/path/to/file.md
    chunk_id: Optional[str]
    similarity: float
```

Agents use `result.context` in prompts; orchestrator attaches `result.citations` to `metadata.citations`.

**4. Orchestrator** (`backend/app/orchestration/orchestrator.py`)

In `_build_agent_response()`:
1. Call agent with RAG context (text only).
2. Extract citations from RAG result.
3. Sanitize response text via `response_formatter.sanitize_response()`.
4. Attach citations to `metadata.citations`.
5. Return `ChatResponse` with clean message + metadata.

#### Data

**No schema changes.**

#### Infra/config

**No new environment variables.** This is behavior-only change.

#### Observability

**Add telemetry logging** in orchestrator:

```python
logger.info(
    "Response discipline check",
    extra={
        "session_id": str(session.id),
        "agent_type": agent_type,
        "response_length": len(response),
        "response_tokens": estimate_tokens(response),  # rough estimate
        "has_rag_mentions": contains_rag_mentions(response),
        "violations": get_discipline_violations(response),
    }
)
```

Use for post-launch monitoring to identify prompt drift.

### Edge cases to handle

1. **Emergency medical override**: Preserve existing behavior from PR6.1 – no follow-ups, urgent instructions only.
2. **RAG retrieval failure**: If no context found, response should ask clarifying question (existing behavior, ensure it's concise).
3. **Ambiguous queries**: Agent should provide brief best-effort answer + one clarifying follow-up (existing PR6.1 behavior).
4. **Multi-part questions**: Extract primary question, answer concisely, use follow-up for secondary parts.
5. **Conversation history context**: Agents can reference prior user statements naturally (e.g., "Based on your OW certification...") but NOT internal system context (e.g., "According to the retrieved document...").

### Migration/compatibility notes (if applicable)

**Backwards compatible:**
- Existing conversation histories remain valid.
- Feature flag `FEATURE_CONVERSATION_FOLLOWUP_ENABLED` continues to control follow-up generation.
- No API contract changes.

**Rollout strategy:**
- Deploy with feature flag ON (default in PR6.1).
- Monitor telemetry for discipline violations.
- If excessive violations, iterate on prompts without re-deploying (prompt hotfix).

---

## 5) Testing & verification

### Automated tests to add/update

#### Unit tests

**1. Response Formatter Tests** (`backend/tests/unit/orchestration/test_response_formatter.py`)

New test file for sanitization logic:

```python
def test_sanitize_response_removes_rag_mentions():
    """Test that RAG references are stripped from response."""
    formatter = ResponseFormatter()
    
    response = "According to the provided context, you need AOW certification."
    sanitized = formatter.sanitize_response(response)
    
    assert "according to" not in sanitized.lower()
    assert "provided context" not in sanitized.lower()
    assert "AOW certification" in sanitized  # Preserve actual content

def test_sanitize_response_removes_bracketed_sources():
    """Test that bracketed citations are removed."""
    formatter = ResponseFormatter()
    
    response = "Wreck diving requires AOW [Source: certifications/padi/aow.md]."
    sanitized = formatter.sanitize_response(response)
    
    assert "[Source:" not in sanitized
    assert "Wreck diving requires AOW" in sanitized

def test_sanitize_response_preserves_clean_text():
    """Test that clean responses pass through unchanged."""
    formatter = ResponseFormatter()
    
    response = "Wreck diving requires Advanced Open Water certification."
    sanitized = formatter.sanitize_response(response)
    
    assert sanitized == response
```

**2. Agent Tests** (`backend/tests/unit/agents/test_*.py`)

Update existing agent tests to validate response discipline:

```python
@pytest.mark.asyncio
async def test_certification_agent_response_is_concise(mock_llm, mock_rag):
    """Test that certification agent produces concise responses."""
    agent = CertificationAgent(llm=mock_llm, rag=mock_rag)
    
    # Mock LLM to return verbose response with RAG mention
    mock_llm.generate.return_value = LLMResponse(
        content="According to the provided context, you need AOW...",
        model="gemini-2.0-flash",
        tokens_used=85,
    )
    
    context = AgentContext(
        query="What cert for wrecks?",
        conversation_history=[],
    )
    
    response = await agent.execute(context)
    
    # Validate conciseness (rough check)
    assert len(response.split()) < 100  # ~120 tokens ≈ 90 words
    assert "provided context" not in response.lower()
    assert "according to" not in response.lower()
```

Apply similar tests to `TripAgent`, `SafetyAgent`, `RetrievalAgent`.

**3. RAG Service Tests** (`backend/tests/unit/services/test_rag.py`)

```python
def test_rag_retrieve_returns_citations_separately():
    """Test that RAG result includes citations as metadata."""
    rag = RAGService()
    
    result = await rag.retrieve("wreck diving certs")
    
    assert isinstance(result, RAGResult)
    assert result.context  # String for LLM
    assert isinstance(result.citations, list)
    assert all(isinstance(c, Citation) for c in result.citations)
    assert result.citations[0].source.startswith("content/")
```

#### Integration tests

**Orchestrator Integration** (`backend/tests/integration/test_orchestrator.py`)

```python
@pytest.mark.asyncio
async def test_chat_response_excludes_rag_mentions(db_session):
    """Test that orchestrator strips RAG mentions from final response."""
    orchestrator = ChatOrchestrator(db_session)
    
    request = ChatRequest(
        message="What cert do I need for wreck diving?",
        session_id=None,
    )
    
    response = await orchestrator.handle_chat(request)
    
    # Validate response discipline
    assert response.message
    assert "source" not in response.message.lower()
    assert "document" not in response.message.lower()
    assert "retrieval" not in response.message.lower()
    assert "provided context" not in response.message.lower()
    
    # Validate citations are in metadata
    if response.metadata and "citations" in response.metadata:
        assert isinstance(response.metadata["citations"], list)
```

#### E2E tests

**Not required for this PR** – unit and integration tests provide sufficient coverage.

### Manual verification checklist

1. **Test conversation flow with concise responses:**
   - [ ] Start new chat session
   - [ ] Ask certification question: "What cert do I need for wreck diving?"
   - [ ] Verify response is 3-5 sentences, no RAG mentions
   - [ ] Ask follow-up: "What about deep diving?"
   - [ ] Verify second response is also concise

2. **Test trip planning response:**
   - [ ] Ask: "Where can I dive in Tioman?"
   - [ ] Verify response mentions sites without RAG metadata
   - [ ] Check that citations (if any) are in metadata, not visible text

3. **Test safety/medical response:**
   - [ ] Ask: "Can I dive with asthma?"
   - [ ] Verify response is brief medical disclaimer + referral (one sentence)
   - [ ] Verify no RAG references like "according to safety docs"

4. **Test emergency detection:**
   - [ ] Ask: "I have chest pain after my last dive"
   - [ ] Verify emergency response is clear, urgent, no follow-up question
   - [ ] Verify no RAG mentions in emergency message

5. **Test feature flag toggle:**
   - [ ] Set `FEATURE_CONVERSATION_FOLLOWUP_ENABLED=false`
   - [ ] Restart backend
   - [ ] Verify responses are concise but NO follow-up questions
   - [ ] Verify RAG mentions still stripped (independent of follow-up feature)

### Commands to run

```bash
# Install dependencies
cd backend
source ../.venv/bin/activate
pip install -e .

# Run backend dev server
.venv/bin/uvicorn app.main:app --reload --app-dir backend

# Run tests
cd backend
pytest                                    # All tests
pytest tests/unit/orchestration/         # Response formatter tests
pytest tests/unit/agents/                # Agent tests
pytest tests/integration/                # Orchestrator integration

# Lint & format
cd backend
ruff check app/ tests/
ruff format app/ tests/

# Typecheck (optional - not currently enforced)
cd backend
mypy app/

# Build (no build step for backend)

# Frontend (no changes, but verify integration)
cd ..
pnpm install
pnpm dev                                 # Dev server
pnpm test                                # Vitest unit tests (no changes expected)
pnpm lint                                # ESLint (no changes)
pnpm typecheck                           # TypeScript check (no changes)
```

---

## 6) Rollback plan

**Rollback strategy:**

1. **Prompt revert**: If response quality degrades, revert agent system prompts via git without full deployment.
2. **Feature flag disable**: If critical issues arise with conversation continuity, disable via `FEATURE_CONVERSATION_FOLLOWUP_ENABLED=false` (responses remain concise but lose follow-ups).
3. **Full PR revert**: If fundamental issues, revert PR6.2 entirely via `git revert` and redeploy.

**Risk mitigation:**

- Response discipline is additive (stricter prompts) – low risk of breaking existing behavior.
- Sanitization is defensive (strips unwanted text) – worst case is no-op if agents already compliant.
- Citations moved to metadata are optional – frontend doesn't render them currently, safe to add.

**Monitoring signals:**

- **High discipline violation rate** (>20% of responses) → Prompt tuning needed.
- **User reports of incomplete answers** → Response length too strict, adjust prompts.
- **Increased conversation turns** → Users asking for more detail → Expected trade-off, monitor for frustration.

---

## 7) Follow-ups (optional)

1. **PR6.3: Token enforcement middleware** – Add post-generation token counting and automatic truncation if responses exceed 120 tokens consistently.
2. **PR6.4: Response quality monitoring** – Dashboard for tracking discipline violations, response lengths, and user satisfaction signals.
3. **PR7+: Prompt testing framework** – Automated regression tests for response formats (aligned with PR11 Post-Launch Iteration plan).
4. **Future: Dynamic response length tuning** – Allow users to request "detailed" vs "brief" answers via UI toggle (requires auth/profiles from PR9).
5. **Future: Citation rendering in UI** – Display `metadata.citations` as expandable "Sources" section below response (post-MVP polish).

---

## Implementation Notes

**Order of implementation:**

1. Update `RAGService` to return `RAGResult` with separate citations (bottom-up).
2. Update agent system prompts with response discipline block (parallel task).
3. Implement `ResponseFormatter.sanitize_response()` method.
4. Update orchestrator to call sanitization and attach citations to metadata.
5. Write unit tests for each component.
6. Write integration tests for full flow.
7. Manual testing with feature flag on/off.
8. Deploy to dev, monitor telemetry, iterate on prompts if needed.

**Testing strategy:**

- Focus on **unit tests for sanitization logic** (deterministic string matching).
- Use **integration tests for end-to-end flow** (mocked LLM responses).
- **Manual testing for subjective quality** (conciseness, tone, clarity).
- **Post-deployment monitoring** for discipline violations (telemetry logs).

**Success metrics (post-deploy):**

- Discipline violation rate <10% (logged warnings for non-compliant responses).
- Average response length ≤120 tokens (via telemetry).
- No increase in user drop-off rate (Vercel Analytics).
- No spike in "unclear answer" feedback (if feedback system exists).

---

**Owner:** jefflyt  
**Reviewers:** TBD  
**Target Completion:** 2-3 days (solo dev)
