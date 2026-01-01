# PR3.2e: Frontend Integration

**Status:** Draft  
**Parent Epic:** PR3.2 (Python-First Backend Migration)  
**Date:** January 1, 2026  
**Duration:** 1-2 weeks

---

## Goal

Connect TypeScript Next.js frontend to Python FastAPI backend. Frontend makes API calls to Python backend, session management works end-to-end, error handling is robust, and TypeScript backend is deprecated (but kept for rollback).

---

## Scope

### In Scope

- API client implementation (`src/lib/api-client/client.ts`)
- HTTP client wrapper (fetch-based, with retry logic)
- Error handling and mapping (API errors → user-friendly messages)
- Session management (cookies or Authorization header)
- Update Next.js API routes to proxy to Python backend
- CORS configuration in Python backend (allow Next.js origins)
- Environment variable configuration
- Local development workflow documentation (run both servers)
- Integration tests (frontend → Python backend)
- Manual E2E testing checklist

### Out of Scope

- Production deployment (PR3.2f)
- Deleting TypeScript backend code (kept for rollback until PR3.2f)
- Redesigning chat UI (PR5 — future)
- Real-time features (WebSockets, SSE)

---

## Backend Changes

### Modified Modules

1. **backend/app/main.py** — Update CORS configuration
   - Add Next.js dev server origin: `http://localhost:3000`
   - Add Next.js preview origins (Vercel): `https://*.vercel.app`
   - Add production origin: `https://dovvybuddy.com` (for future)
   - Enable credentials: `allow_credentials=True`
   - Allow all headers and methods (for development convenience)

2. **backend/app/core/config.py** — Add CORS origins configuration
   - `CORS_ORIGINS`: List[str] from environment variable (comma-separated)
   - Default: `["http://localhost:3000", "http://localhost:3001"]`

3. **backend/app/api/routes/chat.py** — Add CORS headers in response (if needed)
   - FastAPI CORS middleware should handle, but verify

---

## Frontend Changes

### New Modules

**API Client Structure:**
```
src/lib/api-client/
├── client.ts                      # Main API client class
├── config.ts                      # API configuration (already exists from PR3.2a)
├── types.ts                       # Request/response types (already exists from PR3.2a)
├── error-handler.ts               # Error mapping and handling
├── retry.ts                       # Retry logic for transient failures
└── __tests__/
    ├── client.test.ts
    ├── error-handler.test.ts
    └── retry.test.ts
```

**Key Files:**

1. **client.ts** — HTTP client wrapper
   - `ApiClient` class with methods:
     - `chat(request: ChatRequest): Promise<ChatResponse>`
     - `getSession(sessionId: string): Promise<SessionResponse>`
     - `createLead(request: LeadRequest): Promise<LeadResponse>`
   - Error handling (parse API errors)
   - Retry logic (exponential backoff for 5xx errors)
   - Request/response logging (structured)
   - Session ID management (store in cookie or localStorage)

2. **error-handler.ts** — Error mapping
   - Map API error codes to user-friendly messages
   - `VALIDATION_ERROR` → "Please check your input"
   - `LLM_API_ERROR` → "Service temporarily unavailable"
   - `INTERNAL_ERROR` → "Something went wrong, please try again"
   - Extract validation details for form errors

3. **retry.ts** — Retry logic
   - Retry on 5xx errors (server errors)
   - Exponential backoff (1s, 2s, 4s)
   - Max 3 retries
   - Don't retry on 4xx errors (client errors)
   - Cancel retries if request takes >30s total

### Modified Modules

1. **src/app/api/chat/route.ts** — Proxy to Python backend (or remove if direct calls)
   - **Option A (Proxy):** Forward request to Python backend, return response
   - **Option B (Direct):** Remove route, frontend calls Python directly
   - **Recommendation:** Option A (proxy) for V1 to hide backend URL
   - Implementation:
     ```typescript
     export async function POST(request: NextRequest) {
       const body = await request.json();
       const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
       
       const response = await fetch(`${backendUrl}/api/chat`, {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify(body),
       });
       
       return NextResponse.json(await response.json(), { status: response.status });
     }
     ```

2. **next.config.js** — Add API rewrites (if using proxy)
   ```javascript
   module.exports = {
     async rewrites() {
       return [
         {
           source: '/api/chat',
           destination: `${process.env.BACKEND_URL}/api/chat`,
         },
         {
           source: '/api/session/:path*',
           destination: `${process.env.BACKEND_URL}/api/session/:path*`,
         },
       ];
     },
   };
   ```

3. **.env.local.example** — Add backend URL
   ```bash
   # Python Backend URL
   BACKEND_URL=http://localhost:8000
   # Or for production:
   # BACKEND_URL=https://api.dovvybuddy.com
   
   # Next.js Public API URL (for client-side calls if needed)
   NEXT_PUBLIC_API_URL=/api
   ```

4. **src/app/page.tsx** or **src/app/chat/page.tsx** — Update to use new API client
   - Import `ApiClient`
   - Replace old fetch calls with `apiClient.chat(...)`
   - Handle errors with `error-handler`
   - Display user-friendly error messages

---

## Data Changes

None (uses existing database, no schema changes)

---

## Infra / Config

### Environment Variables

**Backend (Python):**
```bash
# Update CORS_ORIGINS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,https://dovvybuddy.com,https://*.vercel.app
```

**Frontend (Next.js):**
```bash
# .env.local
BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=/api
```

**Production:**
- Backend CORS_ORIGINS: `https://dovvybuddy.com`
- Frontend BACKEND_URL: `https://api.dovvybuddy.com`

### Feature Flags

- `USE_PYTHON_BACKEND` (optional, for gradual rollout):
  - If `true`: Call Python backend
  - If `false`: Call TypeScript backend (Next.js API routes)
  - Implementation: Environment variable or runtime config

---

## Testing

### Unit Tests

**Coverage Target:** ≥80%

**Frontend Tests:**

1. **test_client.test.ts**
   - ApiClient initialization
   - chat() method with valid request
   - getSession() method with valid session ID
   - Error handling (4xx, 5xx responses)
   - Retry logic (mock fetch to return 503, then 200)
   - Request timeout

2. **test_error-handler.test.ts**
   - Map API error codes to messages
   - Extract validation details
   - Handle unknown error codes (fallback message)

3. **test_retry.test.ts**
   - Retry on 5xx errors
   - Don't retry on 4xx errors
   - Exponential backoff timing
   - Max retries honored
   - Cancel on timeout

**Mocking Strategy:**
- Mock `fetch` for all API calls
- Use `vitest` mock utilities
- Test with various response scenarios

### Integration Tests

**Test Files:**

1. **tests/integration/api-client.test.ts**
   - Start Python backend (test server)
   - Start Next.js frontend (test server)
   - Call frontend API routes
   - Verify requests reach Python backend
   - Verify responses return to frontend
   - Test session persistence (multiple requests)
   - Test error scenarios (backend down, invalid input)

**Test Scenarios:**
- Happy path: Send chat message → receive response
- Session persistence: Send 3 messages in same session
- Error handling: Invalid message (empty string)
- Error handling: Backend unreachable (503)
- CORS: Verify no CORS errors in browser console (manual)

### E2E Tests (Manual)

**Test Checklist:**

1. **Start servers:**
   ```bash
   # Terminal 1: Python backend
   cd backend && uvicorn app.main:app --reload
   
   # Terminal 2: Next.js frontend
   pnpm dev
   ```

2. **Open browser:** `http://localhost:3000`

3. **Test scenarios:**
   - [ ] Send first message (certification query)
   - [ ] Verify response appears
   - [ ] Verify session ID in browser (cookie or localStorage)
   - [ ] Send follow-up message (same session)
   - [ ] Verify conversation history maintained
   - [ ] Refresh page
   - [ ] Verify session persists (if using cookies)
   - [ ] Send invalid input (empty message)
   - [ ] Verify error message displayed
   - [ ] Stop Python backend
   - [ ] Send message
   - [ ] Verify graceful error message ("Service unavailable")
   - [ ] Restart Python backend
   - [ ] Send message
   - [ ] Verify system recovers

4. **Check browser console:**
   - [ ] No CORS errors
   - [ ] No JavaScript errors
   - [ ] API calls logged correctly

5. **Check backend logs:**
   - [ ] Requests logged with session ID
   - [ ] CORS headers present
   - [ ] No errors

### Performance Tests

**Baseline measurements:**
- Measure latency with direct TypeScript backend: `pnpm dev` (current)
- Measure latency with Python backend proxy: Python + Next.js
- Compare P50, P95, P99 latencies

**Acceptance:** Latency increase ≤ 100ms (acceptable for proxy hop)

---

## Verification

### Commands

```bash
# Frontend tests
pnpm test src/lib/api-client

# Integration tests (requires both servers running)
pnpm test:integration

# Manual E2E (development)
# Terminal 1:
cd backend && uvicorn app.main:app --reload

# Terminal 2:
pnpm dev

# Open browser: http://localhost:3000
```

### Manual Verification Checklist

**Setup:**
- [ ] Python backend starts: `cd backend && uvicorn app.main:app --reload`
- [ ] Next.js frontend starts: `pnpm dev`
- [ ] `.env.local` has correct `BACKEND_URL`

**Functionality:**
- [ ] Frontend calls Python backend successfully
- [ ] Chat messages sent and responses received
- [ ] Session ID persists across requests (check cookies/localStorage)
- [ ] Conversation history maintained (3+ messages)
- [ ] Error messages displayed correctly:
  - [ ] Empty message → validation error
  - [ ] Backend down → service unavailable
  - [ ] Invalid session ID → not found
- [ ] No CORS errors in browser console
- [ ] Backend logs show requests from frontend

**Session Management:**
- [ ] Session ID stored (cookie or localStorage)
- [ ] Session ID sent with each request
- [ ] Server retrieves correct session
- [ ] Conversation history persists
- [ ] Session expiry works (24 hours)

**Error Handling:**
- [ ] Network errors handled gracefully
- [ ] Retry logic works (simulate 503, then 200)
- [ ] Timeout after 30 seconds
- [ ] User-friendly error messages
- [ ] No crashes or blank screens

**Performance:**
- [ ] Response time acceptable (<5s for chat)
- [ ] Proxy overhead minimal (<100ms)
- [ ] No memory leaks (check DevTools)

**Code Quality:**
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Linting passes (`pnpm lint`)
- [ ] Type checking passes (`pnpm typecheck`)

---

## Rollback Plan

### Feature Flag

**Environment variable:** `USE_PYTHON_BACKEND=false`

**Implementation:**
```typescript
// src/lib/api-client/config.ts
const usePythonBackend = process.env.USE_PYTHON_BACKEND !== 'false';

export const API_CONFIG = {
  baseURL: usePythonBackend 
    ? process.env.BACKEND_URL || '/api'
    : '/api', // TypeScript backend (Next.js API routes)
  // ...
};
```

### Revert Strategy

1. **Quick rollback (< 5 minutes):**
   - Set `USE_PYTHON_BACKEND=false` in `.env.local`
   - Restart Next.js: `pnpm dev`
   - Frontend now calls TypeScript backend

2. **Full rollback (< 10 minutes):**
   - Revert frontend changes (git revert)
   - Redeploy frontend
   - Stop Python backend (no longer needed)

3. **Production rollback:**
   - Update environment variable in Vercel
   - Redeploy frontend (automatic on Vercel)
   - No data loss (database unchanged)

---

## Dependencies

### PRs that must be merged

- ✅ **PR3.2a** (Backend Foundation)
- ✅ **PR3.2b** (Core Services)
- ✅ **PR3.2c** (Agent Orchestration)
- Recommended: **PR3.2d** (Content Scripts) — for complete backend

### External Dependencies

- Python backend running and accessible
- Next.js frontend running
- Network connectivity between services
- CORS configured correctly

---

## Risks & Mitigations

### Risk 1: CORS configuration incorrect (frontend can't call backend)

**Likelihood:** Medium  
**Impact:** High (frontend completely broken)

**Mitigation:**
- Test CORS in multiple environments (local, staging, production)
- Document exact CORS_ORIGINS values needed
- Test with browser DevTools (check preflight requests)
- Provide troubleshooting guide in README

**Acceptance Criteria:**
- No CORS errors in browser console
- OPTIONS preflight requests succeed
- Credentials (cookies) sent correctly

### Risk 2: Session management broken (cookies not working)

**Likelihood:** Medium  
**Impact:** High (no conversation history)

**Mitigation:**
- Test session persistence with multiple requests
- Test with same-site and cross-site scenarios
- Consider alternative: Authorization header instead of cookies
- Integration tests for session lifecycle

**Acceptance Criteria:**
- Session ID persists across requests
- Conversation history maintained
- Session works after page refresh (if using cookies)

### Risk 3: Increased latency (extra network hop for proxied requests)

**Likelihood:** Medium  
**Impact:** Medium (slower user experience)

**Mitigation:**
- Benchmark latency before/after (P50, P95)
- Optimize if needed (direct calls instead of proxy)
- Set performance budget (<5s P95 for chat)
- Monitor in production

**Acceptance Criteria:**
- Latency increase ≤100ms for proxy hop
- Overall response time <5s P95

### Risk 4: Developer experience degraded (must run two servers)

**Likelihood:** High  
**Impact:** Medium (slower iteration, more complex setup)

**Mitigation:**
- Document clear setup instructions in README
- Provide helper scripts (e.g., `pnpm dev:full` starts both)
- Consider docker-compose for one-command setup (optional)
- Add troubleshooting section

**Acceptance Criteria:**
- README has step-by-step setup guide
- Common issues documented with solutions
- Developers can start both servers easily

### Risk 5: Error messages not user-friendly

**Likelihood:** Low-Medium  
**Impact:** Medium (poor UX during errors)

**Mitigation:**
- Design error message mapping (API codes → user messages)
- Test all error scenarios (validation, server, network)
- Manual UX review of error states
- Provide actionable guidance ("Try again" vs "Check your input")

**Acceptance Criteria:**
- All error codes have user-friendly messages
- No technical jargon exposed to users
- Clear next steps provided

---

## Trade-offs

### Trade-off 1: Proxy Through Next.js vs Direct Frontend Calls

**Chosen:** Proxy through Next.js API routes (Option A)

**Rationale:**
- Hides backend URL from client (security through obscurity)
- Enables server-side rendering (SSR) in future
- Easier to switch backends (only server-side change)
- Consistent API surface for frontend

**Trade-off:**
- Extra network hop (slight latency increase)
- More complex setup (two services)
- Potential for proxy bugs

**Decision:** Accept trade-off. Proxy for V1, revisit direct calls post-PR5 if latency is issue.

### Trade-off 2: Cookie-Based Sessions vs Authorization Header

**Chosen:** Cookies (with HttpOnly, SameSite flags)

**Rationale:**
- More secure (HttpOnly prevents XSS)
- Automatic with fetch (no manual header management)
- Standard pattern for web apps

**Trade-off:**
- CORS complexity (must enable credentials)
- SameSite issues for cross-domain (if backend on different domain)
- Mobile app support harder (future Telegram bot)

**Decision:** Cookies for web V1, consider Authorization header for mobile (PR7b).

### Trade-off 3: Retry Logic Complexity

**Chosen:** Simple exponential backoff (1s, 2s, 4s, max 3 retries)

**Rationale:**
- Handles transient failures (503, network glitches)
- User doesn't see errors for temporary issues
- Reasonable balance (not too aggressive)

**Trade-off:**
- Adds latency on failure (up to 7s for 3 retries)
- Could mask persistent issues (if always retrying)

**Decision:** Accept trade-off. Monitor retry frequency in production, adjust if needed.

---

## Open Questions

### Q1: Should frontend call Python backend directly or proxy through Next.js?

**Context:** Trade-off between simplicity (direct) and flexibility (proxy)

**Options:**
- A) Direct calls (frontend → Python directly)
- B) Proxy through Next.js API routes (frontend → Next.js → Python)

**Recommendation:** Option B (proxy) for V1, revisit in PR5

**Decision:** Option B ✅

### Q2: How should session ID be stored on client?

**Context:** Cookie vs localStorage vs sessionStorage

**Options:**
- A) HttpOnly cookie (secure, automatic)
- B) localStorage (persists, but XSS risk)
- C) sessionStorage (cleared on tab close)

**Recommendation:** Option A (HttpOnly cookie)

**Decision:** Option A ✅

### Q3: Should we implement request/response caching in API client?

**Context:** Reduce redundant API calls

**Options:**
- A) No caching (simple, always fresh)
- B) In-memory cache with TTL
- C) Browser cache (Cache-Control headers)

**Recommendation:** Option A for V1 (chat is not cacheable)

**Decision:** Option A ✅

### Q4: Should we add loading states and optimistic updates?

**Context:** Better UX during API calls

**Options:**
- A) No optimistic updates (wait for response)
- B) Optimistic updates (show message immediately)

**Recommendation:** Option A for V1 (simpler), revisit in PR5 (Chat UI)

**Decision:** Option A ✅

---

## Success Criteria

### Technical Success

- [ ] API client implemented and tested
- [ ] Frontend calls Python backend successfully
- [ ] Session management works end-to-end
- [ ] Error handling robust (all error types covered)
- [ ] Retry logic works correctly
- [ ] CORS configured correctly (no errors)
- [ ] All unit tests pass (≥80% coverage)
- [ ] All integration tests pass
- [ ] Manual E2E checklist 100% complete

### UX Success

- [ ] Chat functionality works (send message → receive response)
- [ ] Conversation history maintained
- [ ] Error messages user-friendly
- [ ] No crashes or blank screens
- [ ] Performance acceptable (<5s P95)

### Documentation Success

- [ ] README has setup instructions (both servers)
- [ ] Troubleshooting guide for common issues
- [ ] Environment variables documented
- [ ] Rollback procedure documented

### Developer Success

- [ ] Easy to run locally (documented steps)
- [ ] Helper scripts provided (if needed)
- [ ] No surprises or hidden gotchas

---

## Next Steps

After PR3.2e is merged:

1. **Test in staging:** Deploy both services to staging environment
2. **Gather feedback:** Test with real users (if available)
3. **PR3.2f:** Production deployment and rollout
4. **Monitor:** Watch for errors, performance issues

---

## Related Documentation

- **Parent Epic:** `/docs/plans/PR3.2-Python-Backend-Migration.md`
- **Previous PRs:**
  - `/docs/plans/PR3.2a-Backend-Foundation.md`
  - `/docs/plans/PR3.2b-Core-Services.md`
  - `/docs/plans/PR3.2c-Agent-Orchestration.md`
  - `/docs/plans/PR3.2d-Content-Scripts.md`
- **Next PR:** `/docs/plans/PR3.2f-Production-Deployment.md`
- **TypeScript Backend:** `src/app/api/chat/route.ts`
- **CORS Docs:** https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-01 | AI Assistant | Initial draft |

---

**Status:** 🟡 Draft — Ready after PR3.2a-PR3.2d complete

**Estimated Duration:** 1-2 weeks  
**Complexity:** Medium  
**Risk Level:** Medium
