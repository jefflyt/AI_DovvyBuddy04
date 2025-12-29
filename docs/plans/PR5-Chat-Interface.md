# PR5: Chat Interface & Integration - Feature Plan

**Status:** Planning
**Created:** December 28, 2025
**Based on:** MASTER_PLAN.md, DovvyBuddy-PSD-V6.2.md

---

## 1. Feature/Epic Summary

### Objective

Connect the frontend chat interface to the backend API (`/api/chat`, `/api/lead`) to enable end-to-end conversational flows for certification guidance, trip research, and lead capture. This PR delivers the first working user-facing feature of DovvyBuddy.

### User Impact

- **Prospective/New Divers** can ask certification questions and receive grounded, AI-powered answers in a chat interface.
- **Certified Divers** can inquire about dive destinations and sites (within covered scope).
- **All Users** can submit training or trip leads directly from the chat flow when ready to connect with a partner shop.
- **Session Persistence:** Users can refresh the page and resume their conversation (24h window).

### Dependencies

**Must be complete before PR5:**

- **PR1:** Database schema + migrations (destinations, dive_sites, leads, sessions, content_embeddings tables exist).
- **PR2:** RAG pipeline (content ingested, retrieval service functional).
- **PR3:** Model provider + session logic (`/api/chat` endpoint working, returns contextually-aware responses).
- **PR4:** Lead capture + delivery (`/api/lead` endpoint working, stores leads and triggers email/webhook).

**External Dependencies:**

- Backend API routes (`/api/chat`, `/api/lead`) must be deployed and accessible.
- Frontend must be able to make HTTP requests (no CORS issues in dev/prod).

### Assumptions

- **Assumption:** The `/api/chat` endpoint accepts `{ sessionId?: string, message: string }` and returns `{ sessionId: string, response: string, metadata?: object }`.
- **Assumption:** The `/api/lead` endpoint accepts `{ type: 'training' | 'trip', data: { name, email, ... } }` and returns `{ success: boolean, leadId?: string, error?: string }`.
- **Assumption:** Session persistence is handled via localStorage (sessionId stored client-side). HTTP-only cookies are a stretch goal if time permits.
- **Assumption:** The bot will return structured hints (e.g., `metadata.suggestLeadCapture: true`) when it's appropriate to show the lead form, or the UI will detect keywords/intent patterns.
- **Assumption:** The UI does not need real-time streaming (no SSE/WebSocket); polling or single-request/response is acceptable for V1.

---

## 2. Complexity & Fit

### Classification

**Single-PR**

### Rationale

- **Single User Flow:** Chat interface with inline lead capture is one cohesive feature.
- **Two Layers:** Frontend (React components) + minimal backend adjustment (cookie handling, if needed).
- **No Schema Changes:** All data models already exist from PR1-4.
- **Low Risk:** Isolated to UI layer; backend APIs are stable contracts from prior PRs.
- **Testable Independently:** Can be verified end-to-end with manual testing and basic integration tests (API mocking).
- **Solo Founder Friendly:** Fits into a single focused work session (2-4 hours for core implementation + 1-2 hours for polish/testing).

**Estimated Scope:** 1 PR, ~8-12 files changed (components, pages, utilities), ~500-800 lines of code.

---

## 3. Full-Stack Impact

### Frontend

**Pages:**

- `/app/chat/page.tsx` — Replace stub with working chat interface.

**New Components (in `src/components/chat/`):**

- `MessageList.tsx` — Scrollable message thread container.
- `MessageBubble.tsx` — Individual message display (user vs assistant, with timestamps).
- `ChatInput.tsx` — Text input + send button with loading state.
- `TypingIndicator.tsx` — Animated "..." while waiting for assistant response.
- `NewChatButton.tsx` — Button to reset session and start fresh.
- `LeadCaptureForm.tsx` — Inline form for training/trip lead submission (shown on-demand).

**New UI States:**

- **Empty State:** First-time visitor, no messages ("Ask me anything about diving...").
- **Loading State:** Message sent, waiting for response (typing indicator).
- **Error State:** API call failed (friendly error message + retry button).
- **Lead Capture State:** Form displayed inline after user expresses interest.
- **Success State:** Lead submitted successfully (confirmation message).

**Navigation/Entry Points:**

- Landing page (`/app/page.tsx`) already has "Start Chatting" CTA → links to `/chat`.
- No new navigation changes needed.

**Styling:**

- Use Tailwind CSS utility classes for responsive design.
- Ensure mobile-friendly (viewport < 768px): single column, input fixed at bottom.

### Backend

**APIs to Modify:**

- **`POST /api/chat`** (existing from PR3):
  - Add session cookie handling (set `Set-Cookie: sessionId=<uuid>; HttpOnly; Secure; SameSite=Strict; Max-Age=86400` on session creation).
  - Accept sessionId from cookie OR request body (cookie takes precedence).
  - Return sessionId in response body for localStorage fallback.
- **`POST /api/lead`** (existing from PR4):
  - No changes needed (already accepts lead payloads).

**New Endpoints:**

- **`POST /api/session/new`** (optional, for explicit "New Chat" button):
  - Create a new session, return `{ sessionId: string }`.
  - Alternative: Frontend can simply discard old sessionId and let `/api/chat` create a new one on next message.

**Services/Modules:**

- Minor: Session service may need to support cookie-based session retrieval (if not already).

**Validation/Auth/Error Handling:**

- **Rate Limiting:** Add simple rate limiting to `/api/chat` (max 10 requests/minute per IP or session).
- **Input Validation:** Ensure message length is capped (e.g., max 1000 chars).
- **Error Responses:** Return structured JSON errors: `{ error: string, code: string }` for client-side handling.

### Data

**No schema changes.** All tables exist from PR1-4.

**Read/Write Patterns:**

- **Sessions:** Read/write on every `/api/chat` call (retrieve history, append new message).
- **Leads:** Write on `/api/lead` call.
- **Content Embeddings:** Read-only (RAG retrieval, already implemented in PR2).

### Infra / Config

**Environment Variables:**

- No new env vars required (all defined in PR3-4).

**Feature Flags:**

- None needed (chat is the core V1 feature, always enabled).

**CI/CD:**

- No changes to CI pipeline (existing lint/typecheck/test/build workflows cover new code).

**Deployment Considerations:**

- Vercel deployment: No special config needed.
- Ensure API routes have appropriate timeout settings (Vercel default is 10s for Hobby tier, sufficient for LLM + RAG).

---

## 4. PR Roadmap

### PR5: Chat Interface & Integration

**Branch Name:** `feature/pr5-chat-interface`

**Goal**

Deliver a fully functional chat interface where users can:

1. Send messages and receive AI-powered responses.
2. Have their session persist across page refreshes.
3. Start a new chat session.
4. Submit a training or trip lead inline when prompted or when ready.

---

### Scope

**In Scope:**

- Chat UI components (MessageList, MessageBubble, ChatInput, TypingIndicator, NewChatButton).
- Integration with `/api/chat` endpoint.
- Session persistence via localStorage (primary) + HTTP-only cookies (stretch).
- Lead capture form (inline, triggered by user intent or bot suggestion).
- Integration with `/api/lead` endpoint.
- Error handling UI (API failures, network errors).
- Mobile-responsive design.
- Basic loading/empty states.

**Out of Scope:**

- Real-time streaming (SSE/WebSocket) — deferred to future PR.
- Advanced chat features (message editing, deletion, search, export) — deferred to V2.
- User authentication — V1 is guest-only.
- Multi-device session sync — not possible without auth.
- Analytics integration (event tracking) — deferred to PR6 (Polish & Launch).
- E2E tests with Playwright — deferred to PR6.
- Accessibility audit (ARIA labels, keyboard nav) — will be addressed but not exhaustively tested in this PR.

---

### Backend Changes

**API Modifications:**

- **`POST /api/chat`:**
  - Accept `sessionId` from HTTP-only cookie (`req.cookies.sessionId`) OR request body.
  - If no sessionId provided, create new session.
  - Set `Set-Cookie` header on response with sessionId (HttpOnly, Secure, SameSite=Strict, Max-Age=86400).
  - Return sessionId in response body as well (for localStorage fallback).
  - Add input validation: `message` must be string, 1-1000 chars.
  - Add basic rate limiting (in-memory map: sessionId → timestamp[], max 10 requests/min).
  - Return structured errors: `{ error: string, code: 'RATE_LIMIT' | 'INVALID_INPUT' | 'SERVER_ERROR' }`.

**New Utility/Service:**

- **`src/lib/utils/rate-limiter.ts`:**
  - Simple in-memory rate limiter (map of sessionId → request timestamps).
  - `checkRateLimit(sessionId: string): boolean` — returns true if under limit.
  - Cleanup old entries periodically (or use LRU cache).

**Auth/Validation:**

- No authentication (guest sessions).
- Validate all user inputs (message length, lead form fields).

**Error Handling:**

- Wrap API route handlers in try/catch.
- Log errors with context (sessionId, message preview, stack trace).
- Return user-friendly error messages (no stack traces).

---

### Frontend Changes

**New Components (`src/components/chat/`):**

1. **`MessageList.tsx`:**
   - Props: `messages: Array<{ id: string, role: 'user' | 'assistant', content: string, timestamp: Date }>`
   - Render scrollable list of `MessageBubble` components.
   - Auto-scroll to bottom on new message.
   - Handle empty state ("Start a conversation...").

2. **`MessageBubble.tsx`:**
   - Props: `role: 'user' | 'assistant', content: string, timestamp: Date`
   - Render message with appropriate styling (user = right-aligned blue, assistant = left-aligned gray).
   - Show timestamp (formatted as "HH:MM" or "Yesterday" if >24h old).
   - Support multiline text (preserve line breaks).

3. **`ChatInput.tsx`:**
   - Props: `onSend: (message: string) => void, disabled: boolean, placeholder?: string`
   - Render textarea + send button.
   - Disable input while waiting for response.
   - Submit on Enter key (Shift+Enter for newline).
   - Clear input after send.
   - Show character count (e.g., "250/1000").

4. **`TypingIndicator.tsx`:**
   - No props (purely presentational).
   - Animated "..." or "DovvyBuddy is thinking..." message.

5. **`NewChatButton.tsx`:**
   - Props: `onClick: () => void`
   - Render button ("New Chat" or "Start Over").
   - Confirm before resetting (if conversation has >2 messages).

6. **`LeadCaptureForm.tsx`:**
   - Props: `type: 'training' | 'trip', onSubmit: (data: LeadData) => void, onCancel: () => void`
   - Render form fields based on type:
     - **Training:** name (required), email (required), phone (optional), agency preference (PADI/SSI/No Preference), certification level (OW/AOW/etc.), location preference (optional), additional message (optional).
     - **Trip:** name (required), email (required), phone (optional), destination (dropdown or text), travel dates (date range or "flexible"), current certification level (dropdown), dive count (number), interests (checkboxes: wrecks, reefs, marine life, etc.), additional message (optional).
   - Validate fields client-side (email format, required fields).
   - Show loading state while submitting.
   - Show success/error message after submission.

**Page Updates:**

- **`/app/chat/page.tsx`:**
  - **State Management:**
    - `messages: Message[]` — conversation history.
    - `isLoading: boolean` — waiting for assistant response.
    - `sessionId: string | null` — current session ID.
    - `error: string | null` — error message to display.
    - `showLeadForm: boolean` — toggle lead capture form.
    - `leadType: 'training' | 'trip' | null` — which form to show.
  - **Lifecycle:**
    - On mount: Load sessionId from localStorage, fetch session history from `/api/session/:id` (optional, or rely on backend to return full history in first `/api/chat` call).
    - On unmount: None (session persists in DB + localStorage).
  - **Handlers:**
    - `handleSendMessage(message: string)` — POST to `/api/chat`, append user message to UI immediately (optimistic update), wait for response, append assistant message.
    - `handleNewChat()` — Clear sessionId from localStorage, reset messages state.
    - `handleLeadSubmit(data: LeadData)` — POST to `/api/lead`, show success message, hide form.
    - `handleLeadCancel()` — Hide lead form.
  - **Layout:**
    - Header: "DovvyBuddy" + NewChatButton.
    - Body: MessageList + TypingIndicator (if loading).
    - Footer: ChatInput (fixed at bottom).
    - Modal/Inline: LeadCaptureForm (overlays or pushes down chat).

**Session Persistence:**

- **Primary:** Store sessionId in `localStorage.setItem('dovvybuddy-session-id', sessionId)`.
- **Fallback:** If cookies are supported, backend sets HTTP-only cookie.
- **Retrieval:** On page load, read sessionId from localStorage, send in `/api/chat` request body.

**Error Handling:**

- Network errors: Show "Connection lost. Please try again." with retry button.
- Rate limit errors: Show "Too many requests. Please wait a moment."
- Server errors: Show "Something went wrong. Please try again later."
- Invalid input: Show inline validation errors (e.g., "Message is too long").

**Mobile Responsiveness:**

- Chat interface uses full viewport height (`h-screen`).
- MessageList scrollable with `overflow-y-auto`.
- ChatInput fixed at bottom with `sticky` or `fixed` positioning.
- LeadCaptureForm renders as modal on mobile (overlay with close button).

---

### Data Changes

**No migrations needed.** All tables exist from PR1.

**Data Flow:**

1. User sends message → Frontend POSTs to `/api/chat` with `{ sessionId?, message }`.
2. Backend retrieves session from `sessions` table (or creates new).
3. Backend appends user message to `conversation_history` JSONB.
4. Backend performs RAG retrieval from `content_embeddings`.
5. Backend calls LLM via ModelProvider.
6. Backend appends assistant message to `conversation_history`.
7. Backend updates `sessions` table.
8. Backend returns `{ sessionId, response, metadata }` to frontend.
9. Frontend displays assistant message in MessageList.

**Lead Capture Flow:**

1. User clicks "Request Training" or "Plan a Trip" (or bot suggests it).
2. Frontend shows LeadCaptureForm.
3. User fills form and submits.
4. Frontend POSTs to `/api/lead` with `{ type, data }`.
5. Backend validates, saves to `leads` table, triggers email/webhook.
6. Backend returns `{ success: true, leadId }`.
7. Frontend shows success message, hides form.

---

### Infra / Config

**No new environment variables.**

**No feature flags.**

**CI/CD:**

- Existing GitHub Actions workflow (lint/typecheck/test/build) will run automatically on PR.

**Deployment:**

- Vercel preview deployment on PR creation.
- Production deployment on merge to `main`.

---

### Testing

**Unit Tests:**

- **`MessageList.test.tsx`:**
  - Renders empty state correctly.
  - Renders list of messages.
  - Auto-scrolls to bottom on new message.
- **`MessageBubble.test.tsx`:**
  - Renders user vs assistant styling correctly.
  - Formats timestamps correctly.
- **`ChatInput.test.tsx`:**
  - Calls onSend with message text.
  - Clears input after send.
  - Disables input when disabled prop is true.
  - Submits on Enter key.
- **`LeadCaptureForm.test.tsx`:**
  - Validates required fields.
  - Calls onSubmit with correct data structure.
  - Shows loading state during submission.
  - Shows error message on failure.

**Integration Tests:**

- **`/app/chat/page.test.tsx`:**
  - Mock `/api/chat` and `/api/lead` endpoints (MSW or fetch mock).
  - Test full chat flow: send message → receive response.
  - Test session persistence: refresh page, verify sessionId restored.
  - Test new chat: click button, verify sessionId cleared.
  - Test lead capture: open form, submit, verify API called.

**Manual Testing Checklist:**

- Send first message, verify session created and persisted.
- Send multiple messages, verify conversation history displayed.
- Refresh page, verify session restored.
- Click "New Chat", verify session reset.
- Trigger lead form (manually or via bot suggestion), fill and submit, verify success.
- Test error states: disconnect wifi, send message, verify error UI.
- Test rate limiting: send 11 messages rapidly, verify rate limit error.
- Test on mobile viewport (Chrome DevTools), verify responsive layout.

**E2E Tests (Deferred to PR6):**

- Playwright tests for critical paths.

---

### Verification

**Commands to Run:**

```bash
# Install dependencies (if not already)
pnpm install

# Start dev server
pnpm dev

# Run unit tests
pnpm test

# Run linter
pnpm lint

# Run type checker
pnpm typecheck

# Build for production
pnpm build
```

**Manual Verification Checklist:**

1. **Smoke Test:**
   - Navigate to `http://localhost:3000/chat`.
   - Verify chat interface loads (no blank page, no console errors).

2. **Message Flow:**
   - Send message: "What is Open Water certification?"
   - Verify assistant response appears within 5 seconds.
   - Verify message is grounded (mentions PADI/SSI, doesn't invent facts).

3. **Session Persistence:**
   - Send 2-3 messages.
   - Refresh page.
   - Verify conversation history persists.
   - Verify sessionId in localStorage matches.

4. **New Chat:**
   - Click "New Chat" button.
   - Verify confirmation prompt (if >2 messages).
   - Confirm.
   - Verify message history cleared.
   - Verify new sessionId generated on next message.

5. **Lead Capture (Training):**
   - Send message: "I want to get certified."
   - Verify bot suggests lead capture OR manually trigger form.
   - Fill form with test data (name, email, agency=PADI).
   - Submit.
   - Verify success message.
   - Check database: `SELECT * FROM leads WHERE type='training' ORDER BY created_at DESC LIMIT 1;`
   - Verify email sent (check Resend logs or inbox).

6. **Lead Capture (Trip):**
   - Start new chat.
   - Send message: "I want to dive in [Destination]."
   - Trigger trip lead form.
   - Fill form (name, email, destination, dates, certification=OW, dive_count=10).
   - Submit.
   - Verify success message and DB entry.

7. **Error Handling:**
   - Disconnect wifi.
   - Send message.
   - Verify "Connection lost" error message + retry button.
   - Reconnect wifi, click retry.
   - Verify message sends successfully.

8. **Rate Limiting:**
   - Send 11 messages rapidly (open console, paste: `for(let i=0; i<11; i++) { fetch('/api/chat', {method:'POST', body:JSON.stringify({message:'test'}), headers:{'Content-Type':'application/json'}}) }`).
   - Verify 11th request returns 429 error.
   - Verify UI shows "Too many requests" message.

9. **Mobile Responsiveness:**
   - Open Chrome DevTools, switch to mobile viewport (iPhone 12, 390x844).
   - Verify chat interface fits screen.
   - Verify input fixed at bottom.
   - Verify lead form renders as modal (overlay).
   - Verify all buttons/inputs are tappable (not too small).

10. **Accessibility (Basic):**
    - Tab through chat interface, verify focus visible.
    - Verify input has label (or aria-label).
    - Verify buttons have accessible names.
    - Verify error messages are announced (check with screen reader if possible).

**Database Verification:**

```sql
-- Verify session created
SELECT id, created_at, expires_at,
       jsonb_array_length(conversation_history) as message_count
FROM sessions
ORDER BY created_at DESC LIMIT 1;

-- Verify leads captured
SELECT id, type, diver_profile->>'name' as name,
       diver_profile->>'email' as email,
       created_at
FROM leads
ORDER BY created_at DESC LIMIT 5;
```

**API Verification (curl):**

```bash
# Test /api/chat (no session)
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is Open Water certification?"}'

# Expected: { "sessionId": "uuid", "response": "...", "metadata": {} }

# Test /api/chat (with session)
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionId=<uuid-from-previous>" \
  -d '{"message":"How long does it take?"}'

# Expected: { "sessionId": "same-uuid", "response": "...", "metadata": {} }

# Test /api/lead (training)
curl -X POST http://localhost:3000/api/lead \
  -H "Content-Type: application/json" \
  -d '{
    "type": "training",
    "data": {
      "name": "John Doe",
      "email": "john@example.com",
      "agency": "PADI",
      "level": "Open Water",
      "message": "Interested in getting certified this summer."
    }
  }'

# Expected: { "success": true, "leadId": "uuid" }
```

---

### Rollback Plan

**Feature Flag:**

Not applicable (chat is core feature, no flag needed).

**Revert Strategy:**

- If critical bugs are discovered post-merge:
  1. Revert PR5 commit (`git revert <commit-sha>`).
  2. Redeploy to production.
  3. Chat interface will return to stub state from PR0.
  4. Backend APIs (`/api/chat`, `/api/lead`) remain functional for testing/debugging.

**Migration Rollback:**

Not applicable (no schema changes).

**Data Considerations:**

- Sessions and leads created during PR5 testing remain in DB (no cleanup needed).
- If reverting, new sessions will continue to be created by backend (no impact).

---

### Dependencies

**Before PR5:**

- ✅ PR1: Database schema (sessions, leads, content_embeddings tables).
- ✅ PR2: RAG pipeline (content ingested, retrieval working).
- ✅ PR3: Model provider + `/api/chat` endpoint.
- ✅ PR4: Lead capture + `/api/lead` endpoint.

**External:**

- None (all APIs are internal to the application).

**Blocking:**

- If PR3 or PR4 are not fully functional, PR5 cannot proceed (integration will fail).
- If backend API responses don't match expected contract, frontend will need adjustments.

---

### Risks & Mitigations

**Risk 1: Backend API Contract Mismatch**

- **Impact:** Frontend expects `{ sessionId, response, metadata }` but backend returns different structure.
- **Likelihood:** Medium (PR3 was planned but may have slight variations).
- **Mitigation:**
  - Review PR3 implementation before starting PR5.
  - Add integration tests with real API (not just mocks).
  - Use TypeScript types for API contracts (shared types in `src/types/api.ts`).

**Risk 2: Session Persistence Fails**

- **Impact:** Users lose conversation history on refresh.
- **Likelihood:** Low (localStorage is reliable, cookie is backup).
- **Mitigation:**
  - Test session persistence extensively on multiple browsers.
  - Add error handling for localStorage quota exceeded.
  - Fallback to in-memory state if localStorage fails.

**Risk 3: Rate Limiting Too Aggressive**

- **Impact:** Legitimate users get blocked after a few messages.
- **Likelihood:** Medium (10 req/min may be too strict).
- **Mitigation:**
  - Make rate limit configurable via env var (`RATE_LIMIT_MAX_REQUESTS=10`, `RATE_LIMIT_WINDOW_MS=60000`).
  - Monitor Vercel logs post-deployment for rate limit errors.
  - Adjust limits based on real usage patterns.

**Risk 4: Mobile UX Issues**

- **Impact:** Chat interface unusable on mobile (input obscured by keyboard, messages not scrollable).
- **Likelihood:** Medium (mobile layout requires careful testing).
- **Mitigation:**
  - Test on real mobile devices (iOS Safari, Android Chrome).
  - Use `vh` units carefully (account for browser chrome).
  - Ensure input remains visible when keyboard is open (use `position: fixed` + `bottom: 0` with safe-area-inset).

**Risk 5: Lead Form Validation Insufficient**

- **Impact:** Invalid leads saved to DB, email delivery fails.
- **Likelihood:** Low (backend validation is primary defense).
- **Mitigation:**
  - Add client-side validation (pre-submit).
  - Add backend validation (PR4 already has this).
  - Use email validation library (e.g., `validator.js` or regex).

**Risk 6: LLM Response Time Exceeds User Patience**

- **Impact:** Users abandon chat due to slow responses (>10s).
- **Likelihood:** Medium (RAG + LLM can be slow, especially cold starts).
- **Mitigation:**
  - Show typing indicator immediately on send.
  - Add timeout (30s) with user-friendly error message.
  - Monitor response times in Vercel logs.
  - Consider switching to Edge Functions or Cloud Run if serverless cold starts are problematic.

---

## 5. Milestones & Sequence

### Milestone 1: Core Chat Flow

**Goal:** Users can send/receive messages with session persistence.

**PRs Included:** PR5 (first half)

**What "Done" Means:**

- Chat interface renders correctly.
- Messages send/receive successfully.
- SessionId persists across refresh.
- Unit tests pass for core components.

**Verification:**

- Manual test: Send 3 messages, refresh, verify history persists.
- Automated: `pnpm test` passes all unit tests.

---

### Milestone 2: Lead Capture Integration

**Goal:** Users can submit training/trip leads from chat.

**PRs Included:** PR5 (second half)

**What "Done" Means:**

- Lead form displays on demand.
- Form submits successfully to `/api/lead`.
- Success/error states handled gracefully.
- Leads appear in database.

**Verification:**

- Manual test: Trigger form, submit, verify DB entry.
- Automated: Integration test for lead submission passes.

---

### Milestone 3: Polish & Error Handling

**Goal:** Production-ready UX (error states, mobile, accessibility).

**PRs Included:** PR5 (final)

**What "Done" Means:**

- All error states implemented (network, rate limit, server errors).
- Mobile responsive layout verified.
- "New Chat" functionality works.
- Basic accessibility (keyboard nav, focus states).

**Verification:**

- Manual checklist complete (all 10 items from Verification section).
- `pnpm lint && pnpm typecheck && pnpm test && pnpm build` passes.
- Vercel preview deployment successful, smoke tested.

---

## 6. Risks, Trade-offs, and Open Questions

### Major Risks

**Risk A: Backend APIs Not Ready**

- **Description:** PR3/PR4 may have incomplete implementations or bugs.
- **Impact:** PR5 blocked until backend is stable.
- **Mitigation:**
  - Start PR5 by reviewing PR3/PR4 code and testing APIs manually.
  - Create mock API responses for frontend development (can proceed in parallel).
  - Add contract tests to ensure API stability.

**Risk B: Session Management Complexity**

- **Description:** Mixing localStorage + cookies may cause inconsistencies.
- **Impact:** Users see duplicate sessions or lose history.
- **Mitigation:**
  - Choose ONE primary method (localStorage) and treat cookies as backend-only.
  - Document session flow clearly in code comments.
  - Add logging to debug session lifecycle.

**Risk C: Lead Form UX Friction**

- **Description:** Multi-field form may feel overwhelming, reducing conversion.
- **Impact:** Fewer leads submitted.
- **Mitigation:**
  - Make most fields optional (only name + email required).
  - Add progress indicator or step-by-step flow (deferred to V2 if needed).
  - Test form completion rate with real users post-launch.

---

### Trade-offs

**Trade-off 1: localStorage vs HTTP-only Cookies**

- **Decision:** Use localStorage as primary, cookies as fallback.
- **Rationale:**
  - localStorage is simpler (no cookie parsing logic needed).
  - Cookies are more secure (HttpOnly prevents XSS) but harder to debug.
- **Impact:**
  - Acceptable for V1 (guest sessions, low security risk).
  - Revisit in V2 if user accounts are added (auth tokens should use HttpOnly cookies).

**Trade-off 2: Inline Lead Form vs Separate Page**

- **Decision:** Inline modal/overlay form.
- **Rationale:**
  - Reduces friction (no navigation away from chat).
  - Maintains conversation context.
- **Impact:**
  - Mobile layout is tighter (modal may feel cramped).
  - Acceptable for V1; consider separate page in V2 if form becomes more complex.

**Trade-off 3: Real-time Streaming vs Request/Response**

- **Decision:** Single request/response (no SSE/WebSocket).
- **Rationale:**
  - Simpler to implement (fewer moving parts).
  - Acceptable latency for V1 (5-10s responses).
- **Impact:**
  - Users wait for full response (no partial streaming).
  - Deferred to V1.1 or V2 if user feedback demands faster perceived speed.

**Trade-off 4: Manual Lead Trigger vs Auto-Detect**

- **Decision:** Manual trigger (button/link in chat) + optional bot metadata hint.
- **Rationale:**
  - Simpler logic (no NLP intent detection needed in frontend).
  - Bot can suggest ("Would you like me to connect you with a dive shop?").
- **Impact:**
  - User must explicitly request form (slightly more friction).
  - Acceptable for V1; consider auto-trigger in V2 based on user behavior.

---

### Design Decisions

| Topic | Decision | Rationale |
|-------|----------|-----------|
| Bot lead suggestion | Metadata hint + soft CTA | Bot returns `suggestLeadCapture: true` when appropriate; frontend shows gentle CTA ("Ready to get started? [Request Info]"). Non-intrusive, user-controlled. |
| Two tabs same session | Accept for V1, last-write-wins | Edge case with low impact. Both tabs share session; race conditions possible but acceptable. WebSocket sync deferred to V2. |
| Expired session handling | SESSION_EXPIRED code → clear localStorage → auto-start new | Backend returns 404/SESSION_EXPIRED; frontend clears sessionId, shows message ("Session expired. Starting new chat..."), auto-creates new session. |
| Pre-fill lead form | Defer to V2 | No auto-fill in V1 (form is blank). Pre-filling from conversation context requires backend extraction logic—add in V2 if conversion needs improvement. |
| Continue after lead | Allow, show confirmation in chat | User can submit lead and continue chatting (session remains active). Show inline confirmation: "Thanks! We'll be in touch soon. Feel free to keep asking questions." |

### Future Enhancements (V2+)

- **Progressive typing indicator:** Animated dots during response generation
- **Session restore UX:** Prompt user to continue previous session on return visit
- **Tab conflict detection:** Warn user if session is active in another tab
- **Form pre-fill:** Extract name/email from conversation context for lead form
- **Real-time streaming:** SSE/WebSocket for partial response display (reduces perceived latency)

---

**End of PR5 Plan**
