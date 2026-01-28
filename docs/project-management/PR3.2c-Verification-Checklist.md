# PR3.2c: Agent System & Orchestration - Verification Checklist

**Status:** 🟡 Ready for Verification  
**Date:** January 3, 2026  
**PR:** PR3.2c (Agent Orchestration)

---

## Pre-Verification Setup

### 1. Environment Setup

```bash
cd src/backend
source .venv/bin/activate
```

**Check Python version:**
```bash
python --version
# Expected: Python 3.9.6 or higher
```

**Verify .env configuration:**
```bash
cat .env | grep -E "(AGENT|SESSION|PROMPT|MESSAGE)"
```

Expected variables:
- [ ] `MAX_MESSAGE_LENGTH=2000`
- [ ] `SESSION_EXPIRY_HOURS=24`
- [ ] `MAX_CONVERSATION_HISTORY=20`
- [ ] `ENABLE_AGENT_ROUTING=true`
- [ ] `DEFAULT_AGENT=retrieval`
- [ ] `SYSTEM_PROMPT_VERSION=v1`
- [ ] `INCLUDE_SAFETY_DISCLAIMER=true`

### 2. Install Dependencies

```bash
pip install -e .
```

**Verify jinja2 installed:**
```bash
pip list | grep -i jinja
# Expected: jinja2>=3.1.3
```

---

## Automated Testing

### Unit Tests

#### Agent Tests
```bash
pytest tests/unit/agents/ -v
```

**Expected Results:**
- [ ] `test_base_agent.py` - All tests pass
- [ ] `test_agent_registry.py` - All tests pass

**Key Tests:**
- [ ] Agent execution works
- [ ] Agent metadata retrieval
- [ ] Agent error handling
- [ ] Registry initialization (4 agents)
- [ ] Get agent by type
- [ ] Get agent by name
- [ ] List all agents
- [ ] Singleton pattern works

#### Orchestration Tests
```bash
pytest tests/unit/orchestration/ -v
```

**Expected Results:**
- [ ] `test_mode_detector.py` - All tests pass
- [ ] `test_context_builder.py` - All tests pass

**Key Tests:**
- [ ] Certification mode detection
- [ ] Trip mode detection
- [ ] Safety mode detection (priority)
- [ ] General mode detection
- [ ] Context-based detection
- [ ] Follow-up question detection
- [ ] Context building with/without RAG
- [ ] History trimming

### Integration Tests
```bash
pytest tests/integration/test_chat_flow.py -v
```

**Expected Results:**
- [ ] New session creation works
- [ ] Existing session retrieval works
- [ ] Certification query routing
- [ ] Trip query routing
- [ ] Safety query routing with disclaimer
- [ ] Empty message validation
- [ ] Message length validation
- [ ] Session retrieval by ID

### Comparison Tests
```bash
pytest tests/comparison/orchestration/test_agent_routing.py -v
```

**Expected Results:**
- [ ] Overall accuracy ≥90% (36/40 queries)
- [ ] Certification queries routed correctly
- [ ] Trip queries routed correctly
- [ ] Safety queries routed correctly (priority)
- [ ] General queries routed correctly
- [ ] Mode-to-agent mapping correct
- [ ] Context-based routing works

### Test Coverage
```bash
pytest --cov=app/agents --cov=app/orchestration --cov-report=term-missing
```

**Expected Coverage:**
- [ ] `app/agents/` ≥80% coverage
- [ ] `app/orchestration/` ≥80% coverage

---

## Code Quality

### Linting
```bash
ruff check app/agents app/orchestration app/prompts app/api/routes
```

**Expected:**
- [ ] All checks passed (0 errors)

**Auto-fix if needed:**
```bash
ruff check app/agents app/orchestration app/prompts --fix
```

### Formatting
```bash
ruff format --check app/agents app/orchestration app/prompts
```

**Expected:**
- [ ] All files formatted correctly

**Format if needed:**
```bash
ruff format app/agents app/orchestration app/prompts
```

### Type Checking (Optional)
```bash
mypy app/agents app/orchestration app/prompts
```

**Note:** May require additional type stubs. Not blocking.

---

## Manual Functional Testing

### Start Backend Server
```bash
uvicorn app.main:app --reload --port 8000
```

**Verify server starts:**
- [ ] No import errors
- [ ] Server running on http://localhost:8000
- [ ] OpenAPI docs accessible at http://localhost:8000/docs

---

### Test 1: Certification Query (New Session)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is PADI Open Water certification?"}'
```

**Verify Response:**
- [ ] Status: 200 OK
- [ ] Response has `message` field
- [ ] Response has `sessionId` field (UUID format)
- [ ] Response has `agentType: "certification"`
- [ ] Response has `metadata` object
- [ ] Message content mentions PADI/certification
- [ ] Response length: 50-500 words

**Save session ID for next tests:**
```bash
SESSION_ID="<paste-session-id-here>"
```

---

### Test 2: Trip Query (Existing Session)

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"sessionId\": \"$SESSION_ID\", \"message\": \"Best dive sites in Tioman Malaysia?\"}"
```

**Verify Response:**
- [ ] Status: 200 OK
- [ ] Same `sessionId` returned
- [ ] `agentType: "trip"`
- [ ] Message mentions Tioman/Malaysia/dive sites
- [ ] Response is contextual and helpful

---

### Test 3: Safety Query

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Can I dive with a cold?"}'
```

**Verify Response:**
- [ ] Status: 200 OK
- [ ] `agentType: "safety"`
- [ ] Response includes safety disclaimer
- [ ] Mentions consulting medical professionals
- [ ] Mentions DAN (Divers Alert Network)
- [ ] Does NOT provide specific medical advice
- [ ] New session ID (different from previous)

---

### Test 4: General Query

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about scuba diving equipment"}'
```

**Verify Response:**
- [ ] Status: 200 OK
- [ ] `agentType: "retrieval"`
- [ ] Response provides general diving information
- [ ] Response is coherent and helpful

---

### Test 5: Follow-up Question

```bash
# Use session ID from Test 1
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"sessionId\": \"$SESSION_ID\", \"message\": \"What about Advanced Open Water?\"}"
```

**Verify Response:**
- [ ] Status: 200 OK
- [ ] Same session ID
- [ ] Agent routing considers context (likely certification)
- [ ] Response builds on previous conversation

---

### Test 6: Retrieve Session

```bash
curl http://localhost:8000/api/sessions/$SESSION_ID
```

**Verify Response:**
- [ ] Status: 200 OK
- [ ] Response has `id` field
- [ ] Response has `conversation_history` array
- [ ] History contains user messages
- [ ] History contains assistant messages
- [ ] History shows conversation flow
- [ ] Optional: `created_at`, `updated_at` timestamps

---

### Test 7: Error Handling - Empty Message

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": ""}'
```

**Verify Response:**
- [ ] Status: 400 Bad Request
- [ ] Error message indicates empty message

---

### Test 8: Error Handling - Invalid Session

```bash
curl http://localhost:8000/api/sessions/invalid-uuid-12345
```

**Verify Response:**
- [ ] Status: 404 Not Found
- [ ] Error message indicates session not found

---

### Test 9: Error Handling - Message Too Long

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "'$(python -c 'print("x" * 2001)')'"}' 
```

**Verify Response:**
- [ ] Status: 400 Bad Request
- [ ] Error message indicates message too long

---

## Database Verification

### Check Session Persistence

```bash
# Connect to database (adjust connection string)
psql $DATABASE_URL
```

**SQL Queries:**
```sql
-- Check sessions table
SELECT id, created_at, 
       jsonb_array_length(conversation_history) as message_count 
FROM sessions 
ORDER BY created_at DESC 
LIMIT 5;

-- Check specific session
SELECT id, conversation_history, diver_profile 
FROM sessions 
WHERE id = '<session-id>';

-- Verify session expiry
SELECT id, created_at, expires_at 
FROM sessions 
WHERE expires_at > NOW();
```

**Verify:**
- [ ] Sessions created successfully
- [ ] Conversation history stored as JSONB
- [ ] History contains correct role/content structure
- [ ] Session expiry set correctly (created_at + 24 hours)
- [ ] Multiple messages appended correctly

---

## Agent System Verification

### Verify Agent Registry

```python
# Python interactive shell
python
```

```python
from app.agents.registry import get_agent_registry

registry = get_agent_registry()
agents = registry.list_agents()

print(f"Total agents: {len(agents)}")
for agent in agents:
    print(f"- {agent['name']} ({agent['type']})")
```

**Expected Output:**
```
Total agents: 4
- Certification Agent (certification)
- Trip Agent (trip)
- Safety Agent (safety)
- Retrieval Agent (retrieval)
```

**Verify:**
- [ ] All 4 agents registered
- [ ] Each agent has correct metadata
- [ ] Registry is singleton

---

### Verify Mode Detection

```python
from app.orchestration.mode_detector import ModeDetector

detector = ModeDetector()

queries = [
    "What is PADI certification?",
    "Best dive sites in Thailand",
    "Can I dive with asthma?",
    "What is scuba diving?"
]

for query in queries:
    mode = detector.detect_mode(query)
    print(f"{query[:30]:30} -> {mode.value}")
```

**Expected Output:**
```
What is PADI certification?    -> certification
Best dive sites in Thailand    -> trip
Can I dive with asthma?        -> safety
What is scuba diving?          -> general
```

**Verify:**
- [ ] Mode detection works correctly
- [ ] Safety queries prioritized

---

## Performance Verification

### Response Time Testing

**Test average response time:**
```bash
time curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is PADI Open Water?"}'
```

**Expected:**
- [ ] Response time < 5 seconds (with RAG)
- [ ] Response time < 3 seconds (without RAG)

**Test multiple concurrent requests:**
```bash
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "Test query '$i'"}' &
done
wait
```

**Verify:**
- [ ] All requests complete successfully
- [ ] No race conditions
- [ ] Sessions created correctly

---

## Integration with Previous PRs

### Verify RAG Integration

**Check that RAG pipeline is used:**
```bash
# Enable debug logging
export DEBUG=true

# Make request and check logs
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about diving in Tioman"}'
```

**Verify Logs:**
- [ ] RAG retrieval attempted
- [ ] Chunks retrieved (if content exists)
- [ ] Context passed to agent
- [ ] Response uses retrieved context

### Verify LLM Provider Integration

**Check both providers work:**

**Groq:**
```bash
# .env should have DEFAULT_LLM_PROVIDER=groq
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Quick test"}'
```

**Gemini:**
```bash
# Temporarily change .env: DEFAULT_LLM_PROVIDER=gemini
# Restart server
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Quick test"}'
```

**Verify:**
- [ ] Both providers generate responses
- [ ] Model names logged correctly
- [ ] Token usage tracked (metadata)

---

## Documentation Verification

### Check Documentation Files

- [ ] `/docs/plans/PR3.2c-Agent-Orchestration.md` - Plan exists
- [ ] `/docs/project-management/PR3.2c-Implementation-Summary.md` - Summary exists
- [ ] `src/backend/README_SERVICES.md` - Updated with agent info
- [ ] Code comments complete
- [ ] Docstrings present

### Verify OpenAPI Documentation

**Access:** http://localhost:8000/docs

**Check endpoints:**
- [ ] POST `/api/chat` documented
- [ ] GET `/api/sessions/{id}` documented
- [ ] Request/response schemas correct
- [ ] Examples provided

---

## Known Issues & Limitations

### Document Any Issues Found

**Issue Template:**
```
Issue #: 
Severity: [Critical/High/Medium/Low]
Component: [Agent/Orchestration/API]
Description: 
Reproduction Steps:
Expected Behavior:
Actual Behavior:
Workaround:
```

### Expected Limitations (Documented)

- [ ] Sequential agent execution only (no parallel)
- [ ] Keyword-based mode detection (not ML)
- [ ] No agent confidence scoring
- [ ] Comparison tests incomplete (need TS backend)
- [ ] Session cleanup not automated (24h expiry set but no cron)

---

## Sign-Off Checklist

### Code Quality
- [ ] All unit tests pass (≥80% coverage)
- [ ] All integration tests pass
- [ ] Comparison tests ≥90% accuracy
- [ ] Linting passes (ruff)
- [ ] Formatting consistent (ruff format)

### Functionality
- [ ] All 4 agents working
- [ ] Agent routing correct
- [ ] Session management works
- [ ] API endpoints functional
- [ ] Error handling graceful
- [ ] RAG integration working
- [ ] LLM providers working

### Performance
- [ ] Response times acceptable
- [ ] Concurrent requests handled
- [ ] Database queries efficient
- [ ] No memory leaks

### Documentation
- [ ] Plan document complete
- [ ] Implementation summary written
- [ ] Verification checklist complete
- [ ] README updated
- [ ] API docs accurate

### Deployment Readiness
- [ ] Environment variables documented
- [ ] Dependencies listed
- [ ] Configuration validated
- [ ] Rollback plan documented
- [ ] Known limitations documented

---

## Final Verification Status

**Date Verified:** _________________

**Verified By:** _________________

**Overall Status:** 
- [ ] ✅ PASS - Ready for merge
- [ ] ⚠️ PASS WITH NOTES - Minor issues documented
- [ ] ❌ FAIL - Critical issues must be fixed

**Notes:**
```
[Add any additional notes, observations, or recommendations]
```

---

## Next Steps After Verification

1. **If PASS:**
   - Merge PR to main branch
   - Update project tracking
   - Begin PR3.2d (Content Scripts)

2. **If PASS WITH NOTES:**
   - Document minor issues as tech debt
   - Create follow-up tickets
   - Merge PR
   - Address notes in future PR

3. **If FAIL:**
   - Document all failing tests
   - Fix critical issues
   - Re-run verification
   - Do not merge until PASS

---

**Verification Checklist Version:** 1.0  
**Last Updated:** January 3, 2026
