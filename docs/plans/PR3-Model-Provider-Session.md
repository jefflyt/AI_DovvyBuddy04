# PR3: Model Provider & Session Logic

**Status:** Draft  
**Based on:** MASTER_PLAN.md  
**Date:** December 28, 2025

---

## 1. Feature/Epic Summary

### Objective

Implement the "Brain" of DovvyBuddy by creating LLM provider abstraction and session management, enabling the bot to have contextual, stateful conversations with users while maintaining environment-based flexibility between Groq (dev) and Gemini (production).

### User Impact

- Users can send messages and receive intelligent, context-aware responses
- Conversations maintain continuity across multiple messages within a 24-hour session
- System can switch between LLM providers without code changes (dev vs production)
- Session state persists across page refreshes (foundation for PR5 UI integration)

### Dependencies

- **Requires:** PR1 (Database Schema) — needs `sessions` table for state persistence
- **May use (optional):** PR2 (RAG Pipeline) — can mock retrieval for PR3 testing, integrate real RAG when PR2 complete
- **Enables:** PR4 (Lead Capture), PR5 (Chat Interface)

### Assumptions

- **Assumption:** Groq and Gemini APIs have similar enough interfaces that a single abstraction can handle both with minimal provider-specific logic
- **Assumption:** 24-hour session expiry is acceptable; no explicit user logout flow needed for V1
- **Assumption:** Session state can fit comfortably in JSONB column (conversation history ~50-100 messages max before trimming)
- **Assumption:** Next.js Serverless functions will not timeout for typical LLM calls (<10s response time)
- **Assumption:** RAG retrieval function signature is known or can be mocked (returns array of content chunks)

---

## 2. Complexity & Fit

### Classification: `Single-PR`

### Rationale

- **Single user flow:** User sends message → bot responds with context
- **Two main layers:** Backend (API + services) and Data (session CRUD)
- **No UI changes:** API-only PR, UI integration deferred to PR5
- **Self-contained:** ModelProvider and Session services are independent modules with clear interfaces
- **Testable incrementally:** Can unit test providers separately, integration test `/api/chat` with mocked components
- **Low external risk:** LLM API calls are straightforward HTTP requests with known schemas

While this PR touches multiple modules (ModelProvider, Session service, Chat API, Prompts), they form a cohesive "conversation engine" that should be deployed together to be useful. Splitting further would create incomplete, non-functional pieces.

---

## 3. Full-Stack Impact

### Frontend

**No changes planned.**  
This PR is API-only. UI integration happens in PR5 (Chat Interface).

### Backend

**Significant changes:**

- **New modules:**
  - `src/lib/model-provider/` — LLM abstraction layer
    - `types.ts` — Interfaces and types
    - `base-provider.ts` — Abstract base class
    - `groq-provider.ts` — Groq implementation
    - `gemini-provider.ts` — Gemini implementation
    - `factory.ts` — Provider factory based on env var
    - `index.ts` — Public exports
  - `src/lib/session/` — Session management service
    - `types.ts` — Session types
    - `session-service.ts` — CRUD operations
    - `index.ts` — Public exports
  - `src/lib/prompts/` — System prompt templates
    - `system-prompt.ts` — Base system instructions with safety guardrails
    - `certification-prompt.ts` — Certification Navigator mode
    - `trip-prompt.ts` — Trip Research mode
    - `index.ts` — Prompt builder utilities
  - `src/lib/orchestration/` — Chat orchestration logic
    - `chat-orchestrator.ts` — Main conversation flow (retrieve context → build prompt → call LLM)
    - `types.ts` — Orchestration types
    - `index.ts` — Public exports
- **New API endpoints:**
  - `POST /api/chat` — Accept user message, return assistant response
    - Request: `{ sessionId?: string, message: string }`
    - Response: `{ sessionId: string, response: string, metadata?: object }`
  - `POST /api/session/new` — Explicitly create new session (optional, can be implicit in `/api/chat`)
    - Response: `{ sessionId: string }`
  - `GET /api/session/:id` — Retrieve session state (debugging/admin use)
    - Response: `{ session: SessionObject }`

- **Authentication/Authorization:** None (guest sessions only)

- **Validation:**
  - User message: Max length (e.g., 2000 chars), non-empty
  - Session ID: Valid UUID format if provided
- **Error Handling:**
  - Invalid session ID → Create new session
  - Expired session → Create new session, inform user
  - LLM API failure → Return error with retry guidance
  - Database failure → Return 503 with user-friendly message

### Data

**Significant changes:**

- **Tables used:**
  - `sessions` — Read/write for conversation state
    - `CREATE`: New session on first message or explicit request
    - `READ`: Retrieve conversation history for context
    - `UPDATE`: Append new message pair (user + assistant) to `conversation_history` JSONB
    - Expiry check: Filter by `expires_at > NOW()`
- **No migrations needed:** Schema already defined in PR1

- **Session Data Structure (JSONB):**

  ```
  conversation_history: [
    { role: "user", content: "...", timestamp: "..." },
    { role: "assistant", content: "...", timestamp: "..." }
  ]
  diver_profile: {
    certification_level?: string,
    dive_count?: number,
    interests?: string[],
    fears?: string[]
  }
  ```

- **Session Lifecycle:**
  - Create: Generate UUID, set `expires_at = created_at + 24h`
  - Update: Append message to `conversation_history` array
  - Expire: Cron job (future) or lazy check on retrieval
  - No explicit delete in V1 (rely on expiry)

### Infra / Config

**New environment variables:**

- `LLM_PROVIDER` — `groq` or `gemini` (required, default: `groq`)
- `GROQ_API_KEY` — Groq API key (required if `LLM_PROVIDER=groq`)
- `GEMINI_API_KEY` — Google Gemini API key (required if `LLM_PROVIDER=gemini`)
- `SESSION_SECRET` — (Already in PR1, used for cookie signing if needed)
- `MAX_SESSION_DURATION_HOURS` — Session expiry (optional, default: 24)
- `MAX_MESSAGE_LENGTH` — User message max chars (optional, default: 2000)
- `LLM_TIMEOUT_MS` — Timeout for LLM API calls (optional, default: 10000)

**CI/CD:**

- No new jobs; existing `pnpm typecheck && pnpm lint && pnpm test && pnpm build` covers new code

**Secrets Management:**

- LLM API keys stored in Vercel environment variables (or `.env.local` for dev)

---

## 4. PR Roadmap (Single-PR Plan)

Since this is classified as `Single-PR`, we have one PR with organized implementation steps.

### PR3: Model Provider & Session Logic

**Goal**  
Enable DovvyBuddy to conduct intelligent, stateful conversations by implementing LLM provider abstraction (Groq/Gemini), session persistence, and chat orchestration logic. This PR delivers a fully functional chat API that can be tested via curl/Postman and integrated with a UI in PR5.

---

#### Scope

**In scope:**

- ModelProvider interface and implementations (Groq, Gemini)
- Provider factory with env-based switching
- Session service (create, get, update, expire) per MASTER_PLAN
- System prompt templates with safety guardrails
- Chat orchestration (context retrieval → prompt building → LLM call → history update)
- `/api/chat` endpoint with session management
- Unit tests for ModelProvider and Session service
- Integration tests for `/api/chat` endpoint
- Error handling and input validation
- Logging for key events (session creation, LLM calls, errors)

**Out of scope:**

- UI components (deferred to PR5)
- Real RAG retrieval integration (can mock; real integration when PR2 complete)
- Lead capture logic (PR4)
- Session expiry cleanup job (future optimization)
- Rate limiting (future security enhancement)
- Session cookie/localStorage handling (deferred to PR5 frontend work)
- Advanced prompt engineering or multi-turn strategy refinement (iterative post-launch)

---

#### Backend Changes

**Module: `src/lib/model-provider/`**

Create LLM abstraction layer with the following files:

1. **`types.ts`**
   - `ModelConfig` interface: `{ model: string, temperature: number, maxTokens: number, topP?: number }`
   - `ModelMessage` type: `{ role: 'user' | 'assistant' | 'system', content: string }`
   - `ModelResponse` interface: `{ content: string, tokensUsed?: number, model?: string, finishReason?: string }`
   - `ModelProviderType` enum: `GROQ | GEMINI`

2. **`base-provider.ts`**
   - Abstract class `BaseModelProvider`
   - Abstract method: `generateResponse(messages: ModelMessage[], config?: Partial<ModelConfig>): Promise<ModelResponse>`
   - Protected utility: `validateMessages(messages: ModelMessage[]): void`
   - Protected utility: `buildRequestPayload(messages: ModelMessage[], config: ModelConfig): unknown` (provider-specific)

3. **`groq-provider.ts`**
   - Class `GroqProvider extends BaseModelProvider`
   - Implements `generateResponse()` using Groq SDK or fetch to Groq API
   - Default model: `llama-3.1-70b-versatile` (or latest recommended)
   - Error handling: API errors, network timeouts, invalid responses
   - Logging: Log API calls with token usage

4. **`gemini-provider.ts`**
   - Class `GeminiProvider extends BaseModelProvider`
   - Implements `generateResponse()` using Google Generative AI SDK
   - Default model: `gemini-1.5-flash` (or `gemini-1.5-pro` for production)
   - Error handling: API errors, safety blocks, quota limits
   - Logging: Log API calls with token usage

5. **`factory.ts`**
   - Function `createModelProvider(providerType?: ModelProviderType): BaseModelProvider`
   - Reads `process.env.LLM_PROVIDER` if `providerType` not provided
   - Validates API key exists for selected provider
   - Throws error if provider invalid or API key missing
   - Returns singleton instance (optimize for serverless reuse)

6. **`index.ts`**
   - Export all public types and factory function

**Module: `src/lib/session/`**

1. **`types.ts`**
   - `SessionMessage` type: `{ role: 'user' | 'assistant', content: string, timestamp: string }`
   - `DiverProfile` interface: `{ certificationLevel?: string, diveCount?: number, interests?: string[], fears?: string[] }`
   - `SessionData` interface: `{ id: string, conversationHistory: SessionMessage[], diverProfile: DiverProfile, createdAt: Date, expiresAt: Date }`
   - `CreateSessionInput` type: `{ diverProfile?: DiverProfile }`
   - `UpdateSessionInput` type: `{ userMessage: string, assistantMessage: string }`

2. **`session-service.ts`**
   - Function `createSession(input?: CreateSessionInput): Promise<SessionData>`
     - Generate UUID for session ID
     - Set `expiresAt = now + MAX_SESSION_DURATION_HOURS`
     - Insert into `sessions` table with empty conversation history
     - Return `SessionData`
   - Function `getSession(sessionId: string): Promise<SessionData | null>`
     - Query `sessions` table by ID
     - Check if expired (`expiresAt < NOW()`)
     - Return null if not found or expired
     - Parse JSONB fields into `SessionData` type
   - Function `updateSessionHistory(sessionId: string, input: UpdateSessionInput): Promise<void>`
     - Append user message and assistant message to `conversation_history` JSONB
     - Use Drizzle ORM JSONB operations (from PR1)
     - Include timestamp for each message
   - Function `expireSession(sessionId: string): Promise<void>`
     - Mark session as expired by setting `expires_at` to current time
     - Useful for explicit session termination (e.g., "New Chat" button)
   - Function `isSessionExpired(session: SessionData): boolean`
     - Utility to check expiry
   - Error handling: Database errors, invalid session ID format
   - **Note:** Uses Drizzle ORM client from `src/db/client.ts` (PR1)

3. **`index.ts`**
   - Export all session functions and types

**Module: `src/lib/prompts/`**

1. **`system-prompt.ts`**
   - Constant `BASE_SYSTEM_PROMPT`: Core instructions defining DovvyBuddy's identity, tone, and safety guardrails
     - Identity: "You are DovvyBuddy, an AI assistant specialized in scuba diving certifications and trip planning."
     - Scope: "Provide information about PADI and SSI certifications, prerequisites, and dive destinations. Do NOT provide medical advice, safety decisions, or act as a certified instructor."
     - Tone: "Be friendly, non-judgmental, and educational. Normalize common fears (e.g., mask clearing) with factual reassurance."
     - Refusal patterns: "If asked about medical conditions, specific safety decisions, or uncovered destinations, politely decline and suggest consulting a certified professional or dive shop."
     - Disclaimers: "Always include disclaimers when discussing prerequisites, depth limits, or safety considerations."

2. **`certification-prompt.ts`**
   - Function `buildCertificationPrompt(context?: string): string`
   - Extends `BASE_SYSTEM_PROMPT` with certification-specific guidance
   - If `context` provided (from RAG), prepend: "Use the following reference information to answer questions: [context]"
   - Emphasize PADI vs SSI comparison, equivalency, Open Water → Advanced pathways

3. **`trip-prompt.ts`**
   - Function `buildTripPrompt(context?: string): string`
   - Extends `BASE_SYSTEM_PROMPT` with trip planning focus
   - Emphasize destination/site matching based on certification level and dive count
   - Include safety considerations (currents, depth, experience requirements)

4. **`index.ts`**
   - Export prompt builders and base prompt

**Module: `src/lib/orchestration/`**

1. **`types.ts`**
   - `ChatRequest` interface: `{ sessionId?: string, message: string }`
   - `ChatResponse` interface: `{ sessionId: string, response: string, metadata?: { tokensUsed?: number, contextChunks?: number } }`
   - `RetrievalResult` interface: `{ chunks: Array<{ text: string, metadata?: object }> }` (for RAG integration)

2. **`chat-orchestrator.ts`**
   - Function `orchestrateChat(request: ChatRequest): Promise<ChatResponse>`
     - **Step 1:** Validate input (message length, sanitize)
     - **Step 2:** Get or create session
       - If `sessionId` provided, call `getSession()`
       - If session invalid/expired, create new session
       - If no `sessionId`, create new session
     - **Step 3:** Retrieve context (RAG)
       - Call retrieval function (from PR2 or mock)
       - Mock: `async function mockRetrieval(query: string): Promise<RetrievalResult> { return { chunks: [] } }`
       - Concatenate retrieved chunks into context string
     - **Step 4:** Build prompt
       - Determine mode (certification vs trip) based on message content or session history (simple keyword heuristic for V1)
       - Use appropriate prompt builder
       - Construct messages array: `[{ role: 'system', content: systemPrompt }, ...sessionHistory, { role: 'user', content: userMessage }]`
     - **Step 5:** Call LLM
       - Get ModelProvider instance
       - Call `generateResponse(messages)`
       - Handle errors (retry once on transient failure)
     - **Step 6:** Update session
       - Call `updateSessionHistory()` with user + assistant messages
     - **Step 7:** Return response
       - Return `{ sessionId, response: assistantMessage.content, metadata: { tokensUsed } }`
     - Logging: Log each step with session ID and timing

3. **`index.ts`**
   - Export `orchestrateChat` function and types

**API Endpoint: `src/app/api/chat/route.ts`**

- HTTP Method: `POST`
- Request body: `{ sessionId?: string, message: string }`
- Validation:
  - `message` required, string, max length `MAX_MESSAGE_LENGTH`
  - `sessionId` optional, valid UUID format if provided
- Process:
  - Parse and validate request body
  - Call `orchestrateChat(request)`
  - Handle errors:
    - 400 for validation errors
    - 500 for internal errors (log full error, return user-friendly message)
    - 503 for LLM API unavailable
  - Return JSON response with appropriate HTTP status
- Response:
  - 200: `{ sessionId: string, response: string, metadata?: object }`
  - Error: `{ error: string, code: string }`

**API Endpoint: `src/app/api/session/new/route.ts` (Optional)**

- HTTP Method: `POST`
- Request body: `{ diverProfile?: object }` (optional)
- Process:
  - Call `createSession(input)`
  - Return `{ sessionId: string }`
- Rationale: Useful for explicit session creation, but `/api/chat` can handle implicit creation

**API Endpoint: `src/app/api/session/[id]/route.ts` (Optional, for debugging)**

- HTTP Method: `GET`
- Process:
  - Extract session ID from URL params
  - Call `getSession(id)`
  - Return session data or 404
- **Security note:** This exposes session data; consider adding admin auth or removing in production

---

#### Frontend Changes

**No frontend changes in this PR.**  
All work is backend API. UI integration happens in PR5.

---

#### Data Changes

**No migrations needed.**  
Assumes PR1 has already created `sessions` table with required schema:

- `id` (UUID, primary key)
- `diver_profile` (JSONB, nullable)
- `conversation_history` (JSONB, default `[]`)
- `created_at` (timestamp)
- `expires_at` (timestamp)

**ORM:** Drizzle ORM (per MASTER_PLAN) — uses typed schema from `src/db/schema/sessions.ts` (PR1)

**Data operations (via Drizzle):**

- `db.insert(sessions).values(...)` — new session creation
- `db.select().from(sessions).where(eq(sessions.id, sessionId))` — session retrieval with expiry check
- `db.update(sessions).set({ conversation_history: ... })` — append messages to JSONB

**Backward compatibility:**

- All changes are additive (new API endpoints, no schema changes)
- Existing database state unaffected

---

#### Infra / Config

**Environment variables to add to `.env.example`:**

```
# LLM Provider Configuration
LLM_PROVIDER=groq                    # Options: groq | gemini
GROQ_API_KEY=your_groq_key_here      # Required if LLM_PROVIDER=groq
GEMINI_API_KEY=your_gemini_key_here  # Required if LLM_PROVIDER=gemini

# Session Configuration
MAX_SESSION_DURATION_HOURS=24        # Optional, default: 24
MAX_MESSAGE_LENGTH=2000              # Optional, default: 2000

# LLM Configuration
LLM_TIMEOUT_MS=10000                 # Optional, default: 10000
```

**Dependencies to add (package.json):**

- `groq-sdk` (for Groq provider)
- `@google/generative-ai` (for Gemini provider)
- `uuid` (for session ID generation)
- `zod` (for input validation, optional but recommended)
- `pino` (for structured logging per MASTER_PLAN; smaller bundle than Winston)

**CI/CD:**

- No changes; existing pipeline covers new code

---

#### Testing

**Unit Tests:**

1. **ModelProvider tests** (`src/lib/model-provider/__tests__/`)
   - `groq-provider.test.ts`:
     - Mock Groq API responses
     - Test successful generation with valid messages
     - Test error handling (API error, timeout, invalid response)
     - Test token usage tracking
   - `gemini-provider.test.ts`:
     - Mock Gemini API responses
     - Test successful generation
     - Test error handling (safety blocks, quota errors)
   - `factory.test.ts`:
     - Test provider creation based on env var
     - Test error when invalid provider specified
     - Test error when API key missing

2. **Session service tests** (`src/lib/session/__tests__/`)
   - `session-service.test.ts`:
     - Mock Drizzle ORM database queries
     - Test `createSession()` generates valid UUID and sets expiry
     - Test `getSession()` returns session data
     - Test `getSession()` returns null for expired sessions
     - Test `updateSessionHistory()` appends messages correctly
     - Test `expireSession()` sets `expires_at` to current time
     - Test error handling for database failures

3. **Prompts tests** (`src/lib/prompts/__tests__/`)
   - `system-prompt.test.ts`:
     - Test prompt builders return expected structure
     - Test context injection when provided
     - Test refusal patterns present in base prompt

4. **Orchestration tests** (`src/lib/orchestration/__tests__/`)
   - `chat-orchestrator.test.ts`:
     - Mock all dependencies (session service, RAG retrieval, model provider)
     - Test full flow: new session creation → retrieval → LLM call → history update
     - Test existing session flow
     - Test expired session handling
     - Test error propagation (LLM failure, DB failure)

**Integration Tests:**

1. **Chat API tests** (`src/app/api/chat/__tests__/`)
   - `route.test.ts`:
     - Mock database and LLM provider
     - Test POST `/api/chat` with valid message (new session)
     - Test POST `/api/chat` with existing session ID
     - Test POST `/api/chat` with invalid session ID (should create new)
     - Test POST `/api/chat` with message too long (validation error)
     - Test error responses (500, 503)

**Manual Tests:**

1. **Curl tests for `/api/chat`:**
   - Start dev server: `pnpm dev`
   - Test new session: `curl -X POST http://localhost:3000/api/chat -H "Content-Type: application/json" -d '{"message":"What is Open Water certification?"}'`
   - Verify response includes `sessionId` and `response`
   - Test existing session: `curl -X POST http://localhost:3000/api/chat -H "Content-Type: application/json" -d '{"sessionId":"<from-previous-response>","message":"How long does it take?"}'`
   - Verify conversation context maintained

2. **Database verification:**
   - Query sessions table: `SELECT * FROM sessions;`
   - Verify session record created with conversation history
   - Verify `expires_at` is ~24h from `created_at`

3. **Provider switching:**
   - Set `LLM_PROVIDER=groq`, verify chat uses Groq
   - Set `LLM_PROVIDER=gemini`, verify chat uses Gemini
   - Check logs for provider-specific API calls

---

#### Verification

**Commands to run:**

Based on `.github/copilot-project.md`:

- Install dependencies: `pnpm install`
- Dev server: `pnpm dev`
- Run tests: `pnpm test`
- Lint: `pnpm lint`
- Type check: `pnpm typecheck`
- Build: `pnpm build`

**Manual verification checklist:**

1. **Environment setup:**
   - [ ] Copy `.env.example` to `.env.local`
   - [ ] Set `LLM_PROVIDER=groq`
   - [ ] Set `GROQ_API_KEY` (get from Groq console)
   - [ ] Set `DATABASE_URL` (from PR1)
   - [ ] Verify database accessible

2. **Unit tests pass:**
   - [ ] Run `pnpm test`
   - [ ] All ModelProvider tests pass
   - [ ] All Session service tests pass
   - [ ] All Orchestrator tests pass

3. **Integration tests pass:**
   - [ ] Run `pnpm test src/app/api/chat/__tests__/`
   - [ ] All API tests pass

4. **Type checking:**
   - [ ] Run `pnpm typecheck`
   - [ ] No TypeScript errors

5. **Linting:**
   - [ ] Run `pnpm lint`
   - [ ] No linting errors

6. **Build:**
   - [ ] Run `pnpm build`
   - [ ] Build succeeds without errors

7. **Manual API testing:**
   - [ ] Start `pnpm dev`
   - [ ] Send curl request to `/api/chat` with new session
   - [ ] Verify response format: `{ sessionId: string, response: string }`
   - [ ] Response makes sense (not hallucinating, includes disclaimer if appropriate)
   - [ ] Send follow-up message with sessionId from previous response
   - [ ] Verify context maintained (bot "remembers" previous question)
   - [ ] Query database: `SELECT * FROM sessions WHERE id = '<sessionId>';`
   - [ ] Verify `conversation_history` JSONB contains both messages

8. **Provider switching:**
   - [ ] Change `LLM_PROVIDER=gemini` in `.env.local`
   - [ ] Set `GEMINI_API_KEY`
   - [ ] Restart dev server
   - [ ] Send curl request to `/api/chat`
   - [ ] Verify response uses Gemini (check logs or response characteristics)

9. **Error handling:**
   - [ ] Send message with missing body → expect 400
   - [ ] Send message with invalid sessionId format → expect new session created
   - [ ] Send message >2000 chars → expect 400
   - [ ] Temporarily break LLM API key → expect 503 with user-friendly error

10. **Session expiry (optional manual test):**
    - [ ] Manually update session `expires_at` to past timestamp in DB
    - [ ] Send message with that sessionId
    - [ ] Verify new session created (old session treated as expired)

---

#### Rollback Plan

**Feature flags:**

- Not applicable for this PR (no user-facing features yet)

**Revert strategy:**

- If PR causes production issues:
  - Revert the PR via `git revert <merge-commit>`
  - Database schema unchanged, so no migration rollback needed
  - Environment variables can be left as-is or removed (no side effects)
  - Redeploy to restore previous state

**Rollback considerations:**

- If sessions were created with this PR's code, reverting will not delete them
- Sessions table will remain populated; no data loss
- Future re-deploy of PR3 will resume session functionality

**Mitigation:**

- Thorough testing before merge
- Staged rollout: Deploy to preview environment first (Vercel preview)
- Monitor logs for errors in first 24h post-deployment

---

#### Dependencies

**Required before PR3:**

- **PR1 (Database Schema):** `sessions` table must exist
  - Verification: Query `SELECT * FROM sessions LIMIT 1;` succeeds

**Optional dependencies:**

- **PR2 (RAG Pipeline):** Retrieval function can be mocked in PR3, real integration when PR2 complete
  - Mock signature: `async function mockRetrieval(query: string): Promise<{ chunks: Array<{ text: string }> }>`

**External dependencies:**

- **Groq API access:** API key and account setup
  - Get key from: https://console.groq.com/
- **Gemini API access:** API key and Google Cloud project
  - Get key from: https://aistudio.google.com/app/apikey
- **Database connection:** Postgres instance from PR1 must be running

---

#### Risks & Mitigations

**Risk 1: LLM API timeouts or rate limits**

- **Impact:** Chat responses fail or hang
- **Likelihood:** Medium (serverless cold starts, API quotas)
- **Mitigation:**
  - Set aggressive timeout (`LLM_TIMEOUT_MS=10000`)
  - Implement retry logic with exponential backoff
  - Return 503 with clear error message to user
  - Monitor API usage and upgrade tier if needed
  - Consider fallback provider if one fails

**Risk 2: Session data size growth**

- **Impact:** JSONB column bloat, slow queries, storage costs
- **Likelihood:** Medium (long conversations)
- **Mitigation:**
  - Implement conversation history trimming (keep last N messages)
  - Set max conversation length (e.g., 50 messages)
  - Future: Archive old messages to separate table
  - Monitor average `conversation_history` size

**Risk 3: Serverless cold starts**

- **Impact:** First request after idle period takes >5s
- **Likelihood:** High (Next.js Serverless on Vercel)
- **Mitigation:**
  - Minimize dependencies (tree-shake, lazy load)
  - Use Vercel Edge Functions for `/api/chat` if cold starts problematic
  - Consider keep-alive pings to warm functions
  - Optimize imports (avoid importing entire libraries)

**Risk 4: LLM hallucinations or safety violations**

- **Impact:** Bot provides incorrect/dangerous information
- **Likelihood:** Medium (inherent to LLMs)
- **Mitigation:**
  - Strong system prompts with explicit refusal patterns
  - RAG grounding (reduces hallucination)
  - Disclaimers in all safety-related responses
  - Post-launch: User feedback mechanism to flag bad responses
  - Regular prompt testing with edge cases

**Risk 5: Provider API changes**

- **Impact:** Code breaks when Groq/Gemini updates API
- **Likelihood:** Low-Medium (APIs are relatively stable)
- **Mitigation:**
  - Use official SDKs (more stable than raw HTTP)
  - Pin SDK versions in package.json
  - Monitor provider changelogs
  - Abstraction layer isolates changes to provider implementations

**Risk 6: Session ID collision or security**

- **Impact:** User accesses another user's session
- **Likelihood:** Very low (UUID collision probability negligible)
- **Mitigation:**
  - Use UUID v4 (cryptographically random)
  - No additional security measures needed for V1 (guest sessions, no sensitive data)
  - Future: HTTP-only cookies, CSRF tokens if adding authentication

---

## 5. Milestones & Sequence

Since this is a single PR, milestones represent implementation phases within the PR:

### Milestone 1: Foundation (ModelProvider + Session)

**Unlocks:** Ability to call LLMs and persist state
**PRs included:** N/A (internal to PR3)
**"Done" means:**

- ModelProvider interface defined and tested
- Groq and Gemini providers implemented
- Factory function works with env switching
- Session service CRUD operations complete and tested
- Unit tests pass for all modules

### Milestone 2: Orchestration (Chat Logic)

**Unlocks:** End-to-end conversation flow
**PRs included:** N/A (internal to PR3)
**"Done" means:**

- System prompts defined with safety guardrails
- Chat orchestrator integrates session + RAG (mocked) + LLM
- Error handling and logging in place
- Orchestrator unit tests pass

### Milestone 3: API Integration

**Unlocks:** Testable HTTP endpoint for chat
**PRs included:** N/A (internal to PR3)
**"Done" means:**

- `/api/chat` endpoint implemented
- Input validation and error responses
- Integration tests pass
- Manual curl tests work end-to-end

### Milestone 4: Verification & Documentation

**Unlocks:** PR ready for review and merge
**PRs included:** N/A (internal to PR3)
**"Done" means:**

- All tests pass (unit + integration)
- Type check and lint clean
- Build succeeds
- Manual verification checklist complete
- README or docs updated with API usage examples
- `.env.example` updated with new variables

---

## 6. Risks, Trade-offs, and Open Questions

### Major Risks

See section 4 "Risks & Mitigations" for detailed risks and mitigation strategies.

**Summary of top risks:**

1. LLM API timeouts/rate limits → Mitigation: Timeouts, retries, 503 errors
2. Session data growth → Mitigation: History trimming, max length
3. Serverless cold starts → Mitigation: Optimize dependencies, Edge Functions
4. LLM hallucinations → Mitigation: Strong prompts, RAG grounding, disclaimers
5. Provider API changes → Mitigation: Use SDKs, abstraction layer

### Trade-offs

**Trade-off 1: Mocking RAG vs waiting for PR2**

- **Decision:** Mock RAG retrieval in PR3
- **Rationale:** Allows PR3 to proceed independently; real RAG can be integrated when PR2 complete without changing orchestration logic
- **Cost:** Extra work to replace mock later (minimal, just swap function)
- **Benefit:** Parallelizes PR2 and PR3 work

**Trade-off 2: Single `/api/chat` vs separate session endpoints**

- **Decision:** Implement `/api/chat` with implicit session creation; optional `/api/session/new`
- **Rationale:** Simpler for frontend (fewer API calls), session creation is fast
- **Cost:** Less explicit control over session lifecycle
- **Benefit:** Better UX (no extra round-trip), fewer API endpoints to maintain

**Trade-off 3: Conversation history trimming now vs later**

- **Decision:** Defer trimming to future optimization
- **Rationale:** V1 sessions are 24h; unlikely to hit size limits in testing/early users
- **Cost:** Potential performance issues if conversations get very long
- **Benefit:** Simpler implementation, less code to test in PR3
- **Mitigation:** Monitor session sizes, add trimming if issue arises

**Trade-off 4: Groq vs Gemini as default dev provider**

- **Decision:** Groq for dev (per MASTER_PLAN)
- **Rationale:** Faster inference for iteration, lower cost
- **Cost:** Different behavior/quality than production (Gemini)
- **Benefit:** Faster dev cycle, cost savings
- **Mitigation:** Test with Gemini before production deployment

**Trade-off 5: Using official SDKs vs raw HTTP**

- **Decision:** Use official SDKs (`groq-sdk`, `@google/generative-ai`)
- **Rationale:** Better error handling, automatic retries, type safety
- **Cost:** Larger bundle size, dependency on SDK updates
- **Benefit:** More reliable, less code to maintain, better DX
- **Mitigation:** Pin SDK versions, monitor bundle size

### Open Questions

**Q1: Should we implement conversation history trimming in PR3 or defer?**

- **Context:** Long conversations could bloat JSONB column
- **Options:**
  - A) Implement trimming now (keep last 20 messages)
  - B) Defer until data shows it's needed
- **Recommendation:** Defer (Option B) — V1 unlikely to have conversations >50 messages; add if monitoring shows issue
- **Decision criteria:** If average `conversation_history` size >10KB in first week, implement trimming

**Q2: Should we support streaming responses or batch-only?**

- **Context:** Streaming provides better UX (progressive display), but adds complexity
- **Options:**
  - A) Batch-only (wait for full response) — simpler
  - B) Server-Sent Events (SSE) for streaming — better UX
- **Recommendation:** Batch-only for PR3 — simpler to test, defer streaming to future PR after chat UI stable
- **Impact on plan:** None for PR3; streaming can be added to orchestrator later without breaking changes

**Q3: How should we handle Gemini safety blocks?**

- **Context:** Gemini may refuse to generate response if content triggers safety filters
- **Options:**
  - A) Treat as error, return generic message
  - B) Detect safety block, return specific message explaining why
  - C) Retry with modified prompt
- **Recommendation:** Option B — better UX, helps user understand limitation
- **Implementation:** Check `finishReason` in Gemini response, if `SAFETY`, return: "I can't provide information on that topic. Please rephrase or contact a dive professional."

**Q4: Should session expiry be passive (check on retrieval) or active (cron job)?**

- **Context:** Expired sessions clutter database
- **Options:**
  - A) Passive: Check `expires_at` on `getSession()`, treat as non-existent
  - B) Active: Scheduled job to delete expired sessions
- **Recommendation:** Passive for PR3 — simpler, no infra needed; add cleanup job in future if DB size becomes issue
- **Decision criteria:** If sessions table >10K rows with majority expired, add cleanup job

**Q5: Should we log full conversation history in server logs?**

- **Context:** Useful for debugging, but privacy/storage concerns
- **Options:**
  - A) Log full conversation on errors
  - B) Log only last message on errors
  - C) No conversation logging (session ID only)
- **Recommendation:** Option B for PR3 — balance debuggability with storage/privacy
- **Implementation:** On error, log session ID + last user message + error details

**Q6: What model should Groq provider default to?**

- **Context:** Groq offers multiple models with different speed/quality tradeoffs
- **Options:**
  - A) `llama-3.1-70b-versatile` (balanced)
  - B) `mixtral-8x7b-32768` (fast, lower quality)
  - C) `llama-3.1-405b-reasoning` (highest quality, slower)
- **Recommendation:** Option A (`llama-3.1-70b-versatile`) — good balance for dev
- **Configurable:** Add `GROQ_MODEL` env var (optional override)
- **Decision criteria:** Test response quality; switch if output quality insufficient

**Q7: Should we expose session retrieval endpoint (`GET /api/session/:id`) in V1?**

- **Context:** Useful for debugging, but exposes session data
- **Options:**
  - A) Include for debugging, no auth (guest data only)
  - B) Include with basic auth/admin token
  - C) Exclude from V1, use direct DB queries for debugging
- **Recommendation:** Option C — simplest, least surface area; V1 sessions are guest-only, low sensitivity
- **Reconsider if:** Partner shops need to view session context for leads (future feature)

---

## 7. Success Criteria (Recap)

PR3 is considered successful when:

- [ ] All unit tests pass for ModelProvider, Session service, and Orchestrator
- [ ] Integration tests pass for `/api/chat` endpoint
- [ ] `pnpm typecheck` runs clean
- [ ] `pnpm lint` runs clean
- [ ] `pnpm build` succeeds
- [ ] Manual curl test: Send message to `/api/chat`, receive contextual response with session ID
- [ ] Manual curl test: Send follow-up message with session ID, context maintained
- [ ] Database verification: Session record created with conversation history in JSONB
- [ ] Provider switching: Chat works with both Groq (dev) and Gemini (prod) via env var
- [ ] Error handling: Invalid inputs return appropriate 400/500/503 responses
- [ ] Logging: Key events logged (session creation, LLM calls, errors) with context
- [ ] Documentation: `.env.example` updated, README has API usage examples
- [ ] Code review: At least one pass by solo founder (self-review checklist)

---

## 8. Next Steps (Post-PR3)

After PR3 merges:

1. **Integrate real RAG retrieval** when PR2 complete:
   - Replace mock retrieval function in orchestrator
   - Test end-to-end with actual content chunks
   - Verify grounding reduces hallucinations

2. **PR4: Lead Capture & Delivery**
   - Build on session context from PR3
   - Use conversation history to populate lead forms

3. **PR5: Chat Interface & Integration**
   - Connect React UI to `/api/chat` endpoint
   - Implement session persistence (cookie/localStorage)
   - Display conversation history

4. **Prompt refinement:**
   - Test with diverse queries (certification, trip, fear-based, out-of-scope)
   - Iterate on system prompts based on response quality
   - Add domain-specific examples to prompts

5. **Monitoring setup:**
   - Add observability for LLM latency, error rates, token usage
   - Set up alerts for high error rates or timeouts

---

**End of PR3 Plan**
