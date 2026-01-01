# PR3.2c: Agent System & Orchestration

**Status:** Draft  
**Parent Epic:** PR3.2 (Python-First Backend Migration)  
**Date:** January 1, 2026  
**Duration:** 3-4 weeks

---

## Goal

Migrate multi-agent system (certification, trip, safety, retrieval agents) and chat orchestration logic from TypeScript to Python. Backend can handle complete chat conversations with intelligent agent routing, session management, and response generation.

---

## Scope

### In Scope

- Base agent abstraction (interface and common functionality)
- Specialized agents:
  - CertificationAgent (PADI/SSI certification guidance)
  - TripAgent (destination and dive site recommendations)
  - SafetyAgent (safety disclaimers and redirects)
  - RetrievalAgent (RAG-based information retrieval)
- Agent registry and factory pattern
- Chat orchestrator (main conversation controller)
- Session manager (CRUD operations with conversation history)
- Mode detection (certification vs trip vs general vs safety)
- Prompt templates and system prompts
- Message history management
- Complete `/api/chat` endpoint implementation (replace placeholder)
- `/api/session/{id}` endpoint implementation
- Comparison tests: TypeScript vs Python orchestration (50+ conversations)

### Out of Scope

- Content ingestion scripts (PR3.2d)
- Frontend integration (PR3.2e)
- Production deployment (PR3.2f)
- Advanced agent frameworks (LangGraph, CrewAI) — custom implementation for V1
- Multi-agent parallel execution — sequential for simplicity

---

## Backend Changes

### New Modules

**Agent & Orchestration Structure:**
```
backend/app/agents/
├── __init__.py
├── base.py                        # Base agent interface
├── certification.py               # CertificationAgent
├── trip.py                        # TripAgent
├── safety.py                      # SafetyAgent
├── retrieval.py                   # RetrievalAgent
├── registry.py                    # Agent registry
├── config.py                      # Agent configuration
└── types.py                       # Agent-specific types

backend/app/orchestration/
├── __init__.py
├── orchestrator.py                # Chat orchestrator (main controller)
├── session_manager.py             # Session CRUD with history management
├── mode_detector.py               # Detect conversation mode
├── context_builder.py             # Build context from history + RAG
└── types.py                       # Orchestration types

backend/app/prompts/
├── __init__.py
├── system.py                      # Base system prompts
├── certification.py               # Certification prompt templates
├── trip.py                        # Trip prompt templates
├── safety.py                      # Safety disclaimers and templates
└── templates.py                   # Jinja2 template utilities

backend/tests/
├── unit/agents/
│   ├── test_base_agent.py
│   ├── test_certification_agent.py
│   ├── test_trip_agent.py
│   ├── test_safety_agent.py
│   ├── test_retrieval_agent.py
│   └── test_agent_registry.py
├── unit/orchestration/
│   ├── test_orchestrator.py
│   ├── test_session_manager.py
│   ├── test_mode_detector.py
│   └── test_context_builder.py
├── integration/
│   └── test_chat_flow.py
└── comparison/orchestration/
    ├── test_agent_routing.py
    └── test_conversation_quality.py
```

**Key Implementation Files:**

1. **Base Agent** (`agents/base.py`)
   - Abstract base class with `execute()` method
   - Common functionality: logging, error handling
   - Agent metadata (name, description, capabilities)

2. **Specialized Agents**
   - **CertificationAgent**: Handles certification queries (PADI, SSI pathways)
   - **TripAgent**: Handles destination/site recommendations
   - **SafetyAgent**: Provides safety disclaimers, redirects medical/emergency
   - **RetrievalAgent**: Uses RAG pipeline for information retrieval

3. **Chat Orchestrator** (`orchestration/orchestrator.py`)
   - Main entry point for chat requests
   - Session creation and retrieval
   - Mode detection → agent selection
   - Context building (history + RAG)
   - Prompt assembly
   - LLM call coordination
   - Response formatting

4. **Session Manager** (`orchestration/session_manager.py`)
   - Create new sessions
   - Retrieve session by ID
   - Append messages to conversation history
   - Manage session expiry

5. **Prompt Templates** (`prompts/`)
   - Base system prompt with diving bot personality
   - Mode-specific prompts (certification, trip, safety)
   - Jinja2 templates for dynamic prompt generation

### Modified Modules

- `backend/app/api/routes/chat.py` — **Replace placeholder with full orchestration**
  - Handle POST /api/chat
  - Validate request (sessionId optional, message required)
  - Call orchestrator
  - Return response with metadata

- `backend/app/api/routes/session.py` — **Implement GET /api/session/{id}**
  - Retrieve session by ID
  - Return session data with conversation history
  - Handle not found errors

- `backend/app/core/config.py` — Add orchestration configuration:
  - `MAX_MESSAGE_LENGTH`: 2000
  - `SESSION_EXPIRY_HOURS`: 24
  - `ENABLE_AGENT_ROUTING`: true/false (feature flag)
  - `MAX_CONVERSATION_HISTORY`: 20 messages

- `backend/pyproject.toml` — Add dependencies:
  - `jinja2>=3.1.3` (template rendering)

---

## Frontend Changes

None (backend-only PR, frontend connects in PR3.2e)

---

## Data Changes

None (uses existing `sessions` table from PR3.2a)

**Session table reminder:**
- `id`: UUID
- `diver_profile`: JSONB (nullable)
- `conversation_history`: JSONB (array of messages)
- `created_at`: timestamp
- `expires_at`: timestamp

---

## Infra / Config

### Environment Variables (Additions)

```bash
# Orchestration Configuration
MAX_MESSAGE_LENGTH=2000            # Maximum user message length
SESSION_EXPIRY_HOURS=24            # Session expiry time
MAX_CONVERSATION_HISTORY=20        # Max messages to keep in history

# Agent Configuration
ENABLE_AGENT_ROUTING=true          # Enable intelligent agent routing
DEFAULT_AGENT=retrieval            # Default agent if mode unclear

# Prompt Configuration
SYSTEM_PROMPT_VERSION=v1           # System prompt version (for A/B testing)
INCLUDE_SAFETY_DISCLAIMER=true     # Always include safety disclaimer
```

### Feature Flags

- `ENABLE_AGENT_ROUTING`: Toggle agent system on/off (fallback to simple retrieval)
- `INCLUDE_SAFETY_DISCLAIMER`: Add safety disclaimer to all responses

---

## Testing

### Unit Tests

**Coverage Target:** ≥80%

**Agent Tests:**

1. **test_base_agent.py**
   - Abstract base class interface
   - Common functionality (logging, error handling)
   - Agent metadata

2. **test_certification_agent.py**
   - Handles certification queries correctly
   - PADI vs SSI pathways
   - Prerequisites and requirements
   - Course structure explanations
   - Responds appropriately to out-of-scope queries

3. **test_trip_agent.py**
   - Handles destination queries
   - Dive site recommendations
   - Seasonal considerations
   - Certification level matching
   - Budget and duration considerations

4. **test_safety_agent.py**
   - Recognizes medical queries
   - Provides appropriate disclaimers
   - Redirects to professionals
   - Emergency guidance without instructing

5. **test_retrieval_agent.py**
   - Uses RAG pipeline (mocked)
   - Formats retrieved context
   - Handles no-results gracefully

6. **test_agent_registry.py**
   - Register and retrieve agents
   - Factory instantiation
   - Agent lookup by name

**Orchestration Tests:**

1. **test_orchestrator.py**
   - Session creation and retrieval (mocked)
   - Mode detection integration
   - Agent selection logic
   - Context building
   - Prompt assembly
   - LLM call coordination (mocked)
   - Response formatting
   - Error handling (invalid session, LLM failure, etc.)

2. **test_session_manager.py**
   - Create new session
   - Retrieve existing session
   - Append message to history
   - Session expiry handling
   - Conversation history trimming (keep last N messages)

3. **test_mode_detector.py**
   - Classify certification queries
   - Classify trip queries
   - Classify safety/medical queries
   - Classify general queries
   - Handle ambiguous queries

4. **test_context_builder.py**
   - Build context from history
   - Include RAG results
   - Format for prompt template
   - Handle empty history
   - Handle no RAG results

### Integration Tests

**Test Files:**

1. **test_chat_flow.py**
   - Full chat flow: create session → send message → receive response
   - Multi-turn conversation (3-5 messages)
   - Session history persistence
   - Agent routing (verify correct agent used)
   - Error handling:
     - Invalid session ID
     - Empty message
     - Message too long
     - LLM API failure (mocked)
     - Database failure (mocked)

**Test Scenarios:**
- Certification query: "What is PADI Open Water?"
- Trip query: "Best dive sites in Tioman?"
- Safety query: "What if I have a cold?"
- General query: "Tell me about diving"
- Multi-turn: Certification → follow-up → trip planning

### Comparison Tests (Critical)

**Test Files:**

1. **test_agent_routing.py**
   - 100 labeled test queries (domain known)
   - Run through both TS and Python orchestrators
   - Compare agent selection
   - Acceptance: ≥90% same agent selected

2. **test_conversation_quality.py**
   - 50 multi-turn conversations
   - Run through both implementations
   - Manual review of responses
   - Automated checks:
     - Response length reasonable (50-500 words)
     - Safety disclaimer present when needed
     - No hallucinations (factual accuracy)
     - Appropriate tone and style

**Test Data:**
- Use conversation_test_cases.json with labeled queries
- Cover all domains (cert, trip, safety, general)
- Include edge cases (ambiguous, out-of-scope, follow-ups)

### Manual Checks

```bash
# 1. Test certification query
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is PADI Open Water certification?"}'

# 2. Test trip query (with session)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "SESSION_ID_FROM_STEP1", "message": "Best dive sites in Tioman?"}'

# 3. Test safety query
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Can I dive with a cold?"}'

# 4. Retrieve session
curl http://localhost:8000/api/session/SESSION_ID

# 5. Compare with TypeScript
# Run same queries through TypeScript backend
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is PADI Open Water certification?"}'
```

---

## Verification

### Commands

```bash
# Unit tests
pytest tests/unit/agents
pytest tests/unit/orchestration

# Integration tests
pytest tests/integration

# Comparison tests
pytest tests/comparison/orchestration -v

# All tests
pytest

# Coverage
pytest --cov=app/agents --cov=app/orchestration --cov-report=html
```

### Manual Verification Checklist

**Agent System:**
- [ ] CertificationAgent handles PADI/SSI queries appropriately
- [ ] TripAgent provides relevant destination recommendations
- [ ] SafetyAgent redirects medical queries appropriately
- [ ] RetrievalAgent uses RAG pipeline correctly
- [ ] Agent registry returns correct agent instances
- [ ] Agent selection logged correctly (check logs)

**Orchestration:**
- [ ] POST `/api/chat` returns coherent responses for all query types
- [ ] Session created automatically if no sessionId provided
- [ ] Session ID returned in response
- [ ] Conversation history persists across messages
- [ ] GET `/api/session/{id}` returns complete session data
- [ ] Session expiry works (24 hours)
- [ ] Mode detection selects appropriate agent (check logs)
- [ ] Error handling graceful (invalid inputs, API failures)

**Comparison:**
- [ ] Agent routing matches TypeScript ≥90% (labeled queries)
- [ ] Response quality acceptable (manual review of 20+ responses)
- [ ] No obvious quality regressions
- [ ] Safety disclaimers present when appropriate
- [ ] Tone and style consistent with TypeScript bot

**Code Quality:**
- [ ] All unit tests pass (≥80% coverage)
- [ ] All integration tests pass
- [ ] All comparison tests pass
- [ ] Linting passes (`ruff check .`)
- [ ] Formatting passes (`ruff format --check .`)
- [ ] Type checking passes (`mypy app`)

---

## Rollback Plan

### Feature Flag

`ENABLE_AGENT_ROUTING=false` to disable agent system (fall back to simple retrieval-only orchestration)

### Revert Strategy

1. **Revert chat endpoint to placeholder** (from PR3.2a)
2. **No impact:** Python backend still not connected to frontend
3. **Session data preserved:** Schema unchanged, existing sessions remain
4. **Execution time:** <5 minutes (git revert)

---

## Dependencies

### PRs that must be merged

- ✅ **PR3.2a** (Backend Foundation) — Database and repositories required
- ✅ **PR3.2b** (Core Services) — RAG pipeline and LLM providers required

### External Dependencies

- LLM API keys (Gemini, Groq) — already configured
- Existing embeddings in database — for RAG retrieval
- Python 3.11+ with all dependencies installed

---

## Risks & Mitigations

### Risk 1: Agent routing behavior differs from TypeScript

**Likelihood:** Medium  
**Impact:** High (wrong agent → incorrect responses)

**Mitigation:**
- Comparison tests with 100+ labeled queries
- Manual review of agent selection logs
- Threshold: ≥90% match required
- Document intentional differences (if any improvements made)

**Acceptance Criteria:**
- ≥90% same agent selected for labeled queries
- Manual review confirms routing makes sense
- No critical misrouting (e.g., medical query → trip agent)

### Risk 2: Response quality degrades

**Likelihood:** Medium  
**Impact:** High (user experience degradation)

**Mitigation:**
- Comparison tests with 50+ conversations
- Manual review of 20+ responses per agent
- Check for hallucinations, tone issues, missing disclaimers
- Side-by-side comparison with TypeScript responses

**Acceptance Criteria:**
- No obvious quality regressions in manual review
- Safety disclaimers present when needed (100%)
- Response length appropriate (50-500 words)
- Factual accuracy maintained

### Risk 3: Session management bugs

**Likelihood:** Low-Medium  
**Impact:** High (lost conversation context, data corruption)

**Mitigation:**
- Integration tests for session lifecycle
- Test concurrent sessions (multiple users)
- Test conversation history trimming
- Test session expiry behavior
- Load testing with concurrent requests

**Acceptance Criteria:**
- Sessions persist correctly across multiple messages
- Conversation history maintained (up to MAX_CONVERSATION_HISTORY)
- No race conditions with concurrent sessions
- Expiry works correctly (sessions deleted after 24h)

### Risk 4: Orchestration complexity leads to bugs

**Likelihood:** Medium  
**Impact:** Medium (crashes, incorrect routing)

**Mitigation:**
- Comprehensive error handling at each orchestration step
- Extensive unit tests (≥80% coverage)
- Integration tests covering happy path + error scenarios
- Structured logging for debugging

**Acceptance Criteria:**
- Error handling graceful (no crashes)
- Errors logged with context (request ID, session ID, error details)
- Fallback behavior works (default agent if routing fails)

### Risk 5: Prompt templates have syntax errors

**Likelihood:** Low  
**Impact:** Medium (Jinja2 errors, incorrect prompts)

**Mitigation:**
- Unit tests for template rendering
- Test with various input combinations
- Validate template syntax at startup
- Document template variables clearly

**Acceptance Criteria:**
- All templates render without errors
- Variables substituted correctly
- No missing variables in production use

---

## Trade-offs

### Trade-off 1: Custom Orchestration vs LangGraph

**Chosen:** Custom orchestration for V1

**Rationale:**
- Simpler implementation (no learning curve)
- More control over agent routing logic
- Easier to debug and optimize
- Proven pattern from TypeScript implementation

**Trade-off:**
- More code to maintain
- Missing LangGraph features (parallel agents, advanced routing)

**Decision:** Accept trade-off. Custom sufficient for V1, can migrate to LangGraph post-V1 if needed.

### Trade-off 2: Sequential vs Parallel Agent Execution

**Chosen:** Sequential execution

**Rationale:**
- Simpler implementation
- Easier to reason about and debug
- Current workload doesn't require parallelism
- One agent per query is sufficient

**Trade-off:**
- Can't combine multiple agent responses
- Potential latency if multiple agents needed (future)

**Decision:** Accept trade-off. Sequential sufficient for current use cases.

### Trade-off 3: Agent Routing Threshold (90% vs 95%)

**Chosen:** 90% match threshold for comparison tests

**Rationale:**
- Allows for minor routing differences (improvements)
- Focus on "no critical misrouting" vs "exact match"
- Some queries may be ambiguous (acceptable to differ)

**Trade-off:**
- May miss subtle routing issues
- Requires manual review of 10% differences

**Decision:** Accept 90% threshold, manually review all failures.

### Trade-off 4: Conversation History Limit (20 messages)

**Chosen:** Keep last 20 messages in history

**Rationale:**
- Balances context preservation vs token usage
- Most conversations are <20 messages
- Prevents unbounded history growth

**Trade-off:**
- Loses early context in very long conversations
- May need to re-explain if user refers back

**Decision:** Accept 20 message limit. Monitor if users hit this limit.

---

## Open Questions

### Q1: Should we implement agent confidence scoring?

**Context:** Agents could return confidence scores to enable fallback routing

**Options:**
- A) No confidence scoring (single agent per query)
- B) Confidence scoring with threshold-based fallback
- C) Confidence scoring with multi-agent consultation

**Recommendation:** Option A for V1 (simpler), revisit in future if needed

**Decision:** Option A ✅

### Q2: How should we handle ambiguous queries?

**Context:** Some queries could match multiple agents (e.g., "Tell me about diving in Tioman")

**Options:**
- A) Choose agent with highest mode detection score
- B) Default to RetrievalAgent for ambiguous queries
- C) Combine multiple agents (complex)

**Recommendation:** Option A (highest score wins)

**Decision:** Option A ✅

### Q3: Should we persist agent metadata in session?

**Context:** Track which agents were used for each message

**Options:**
- A) Store agent name in conversation_history metadata
- B) Store in separate table (agent_usage log)
- C) Don't persist (only log)

**Recommendation:** Option A (simple, useful for debugging)

**Decision:** Option A ✅

### Q4: Should we replicate ADK multi-agent system from PR3.1?

**Context:** PR3.1 introduced Google ADK for multi-agent orchestration

**Options:**
- A) Replicate ADK architecture with custom Python implementation
- B) Use Google ADK Python SDK (if available)
- C) Use LangGraph for similar functionality

**Recommendation:** Option A (proven from TS, no new dependencies)

**Decision:** Option A ✅

---

## Success Criteria

### Technical Success

- [ ] All 4 specialized agents implemented and tested
- [ ] Agent registry and factory work correctly
- [ ] Chat orchestrator handles full conversation flow
- [ ] Session manager persists conversation history
- [ ] Mode detection classifies queries accurately
- [ ] POST `/api/chat` returns appropriate responses for all query types
- [ ] GET `/api/session/{id}` retrieves session data correctly
- [ ] All unit tests pass (≥80% coverage)
- [ ] All integration tests pass
- [ ] All comparison tests pass:
  - [ ] Agent routing ≥90% match
  - [ ] Response quality acceptable (manual review)

### Quality Success

- [ ] Code review complete
- [ ] Linting, formatting, type checking pass
- [ ] Documentation complete (docstrings, README)
- [ ] Structured logging for all orchestration steps
- [ ] Error handling comprehensive

### Comparison Success

- [ ] 100+ labeled queries tested
- [ ] Agent routing match ≥90%
- [ ] 50+ conversations reviewed
- [ ] No critical quality regressions
- [ ] Safety disclaimers present when appropriate

---

## Next Steps

After PR3.2c is merged:

1. **Document learnings:** Note any orchestration patterns that work better in Python
2. **PR3.2d:** Implement content processing scripts using these services
3. **Monitor:** Watch session data for any unexpected patterns

---

## Related Documentation

- **Parent Epic:** `/docs/plans/PR3.2-Python-Backend-Migration.md`
- **Previous PRs:**
  - `/docs/plans/PR3.2a-Backend-Foundation.md`
  - `/docs/plans/PR3.2b-Core-Services.md`
- **TypeScript Orchestration:** `/docs/plans/PR3-Model-Provider-Session.md`
- **TypeScript ADK:** `/docs/plans/PR3.1-ADK-Multi-Agent-RAG.md`
- **Product Spec:** `/docs/psd/DovvyBuddy-PSD-V6.2.md`

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-01 | AI Assistant | Initial draft |

---

**Status:** 🟡 Draft — Ready after PR3.2a and PR3.2b complete

**Estimated Duration:** 3-4 weeks  
**Complexity:** Very High (most complex step)  
**Risk Level:** Medium-High
