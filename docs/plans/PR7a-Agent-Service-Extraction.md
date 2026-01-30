# PR7a: Extract Agent Service to Cloud Run (Prerequisite for Telegram)

**Branch Name:** `feature/pr7a-agent-service-extraction`  
**Status:** ~~Planned~~ **OBSOLETE**  
**Date:** December 29, 2025  
**Based on:** MASTER_PLAN.md (Post-Phase 4, V1.1 Telegram Preparation)

> **⚠️ OBSOLETE:** This PR is no longer needed. The agent orchestration logic was implemented directly in Python/FastAPI backend (PR3.2c) and is already a standalone service. The backend can serve multiple channels (web, Telegram) without requiring extraction.
>
> **Migration Complete:** Python backend at `backend/` already contains:
> - Agent orchestration (`app/agents/`)
> - RAG pipeline (`app/services/rag/`)
> - Session management (`app/db/repositories/session_repository.py`)
> - Multi-agent routing (certification, trip, safety agents)
> - FastAPI service ready for Cloud Run deployment
>
> **Next Steps:** 
> - Skip to **PR7b** (Telegram Bot Adapter) which will integrate directly with existing Python backend
> - No extraction or refactoring needed

---

## Original Plan Summary (Historical Context)

This PR was originally planned to extract agent logic from Next.js API routes into a standalone Cloud Run service. However, during PR3.2a-PR3.2e, the decision was made to implement the entire backend in Python/FastAPI, which naturally created the standalone service architecture this PR intended to achieve.

## 1. Feature/Epic Summary

### Objective

Extract the agent orchestration logic (RAG retrieval, model provider calls, session management, prompt construction) from Next.js API routes into a standalone Cloud Run service. This enables the agent to serve multiple channels (web and Telegram) without duplicating business logic.

**Note:** This PR is only required if the ADK agent logic from PR3 was implemented within Next.js API routes. If the agent service is already standalone, skip to PR7b.

### User Impact

- **End Users:** No visible changes; web chat functionality remains identical.
- **Internal/Architecture:** Agent logic becomes reusable across web and Telegram channels.
- **Developer Experience:** Clear separation of concerns; agent service can be tested and deployed independently.

### Dependencies

**Upstream:**
- **PR1-6:** Complete (database, RAG, model provider, session management, lead capture, landing page, E2E testing).

**External:**
- Google Cloud Platform account with Cloud Run enabled.
- Service account credentials for inter-service authentication.
- Google Secret Manager for API key storage.

### Assumptions

- **Assumption:** Current agent orchestration is implemented in Next.js API routes (`src/app/api/chat/route.ts`, etc.).
- **Assumption:** Agent service will use Express.js or Fastify for HTTP server.
- **Assumption:** Agent service will run on Cloud Run with internal-only access (no public endpoint).
- **Assumption:** Authentication between Next.js and agent service uses shared API key (stored in Secret Manager).
- **Assumption:** Agent service shares the same Postgres database and LLM provider credentials as Next.js.
- **Assumption:** No UI changes required; Next.js API routes act as thin proxy to agent service.

---

## 2. Complexity & Fit

### Classification

**Single-PR**

### Rationale

- **Refactoring-Focused:** Moving existing logic to new service, not adding new features.
- **Single Deployment Unit:** One new Cloud Run service.
- **Limited Risk:** API contract remains unchanged from frontend perspective; regression testing ensures feature parity.
- **Independently Testable:** Agent service can be tested in isolation before integrating with Next.js.
- **Estimated Scope:** ~15-20 files (new agent service structure, updated Next.js API routes, Dockerfile, deployment config).

---

## 3. Full-Stack Impact

### Frontend

**No changes.** API contract with Next.js remains identical from the browser's perspective.

### Backend

**New Agent Service Structure:**

Create standalone service in `src/agent-service/`:

```
src/agent-service/
├── server.ts                  # Express/Fastify server entry point
├── routes/
│   ├── chat.ts               # POST /agent/chat
│   ├── session.ts            # POST /agent/session/new, GET /agent/session/:id
│   └── lead.ts               # POST /agent/lead
├── middleware/
│   ├── auth.ts               # API key validation
│   └── error-handler.ts      # Centralized error handling
├── lib/
│   ├── model-provider/       # Moved from src/lib/model-provider/
│   ├── rag/                  # Moved from src/lib/rag/
│   ├── session/              # Moved from src/lib/session/
│   ├── lead/                 # Moved from src/lib/lead/
│   └── prompts/              # Moved from src/lib/prompts/
├── types/
│   └── index.ts              # Agent service types
├── utils/
│   ├── logger.ts             # Structured logging (Winston/Pino)
│   └── db.ts                 # Database connection utility
├── Dockerfile                # Multi-stage Docker build
├── .dockerignore
├── package.json              # Agent service dependencies
├── tsconfig.json             # TypeScript config for agent service
└── README.md                 # Agent service documentation
```

**Agent Service API Endpoints:**

1. **POST /agent/chat**
   - Request: `{ sessionId?: string, message: string, channelType: 'web' | 'telegram' }`
   - Response: `{ sessionId: string, response: string, metadata: { model: string, latency: number } }`
   - Orchestrates: Retrieve session → RAG retrieval → Construct prompt → Call LLM → Update session → Return response

2. **POST /agent/session/new**
   - Request: `{ channelType: 'web' | 'telegram', channelUserId?: string }`
   - Response: `{ sessionId: string, expiresAt: string }`
   - Creates new session in database

3. **GET /agent/session/:id**
   - Response: `{ sessionId: string, diverProfile: object, conversationHistory: array, expiresAt: string }`
   - Retrieves session context

4. **POST /agent/lead**
   - Request: `{ type: 'training' | 'trip', data: object, channelType: 'web' | 'telegram' }`
   - Response: `{ success: boolean, leadId: string }`
   - Captures and delivers lead

5. **GET /health**
   - Response: `{ status: 'healthy', timestamp: string, version: string }`
   - Health check endpoint for Cloud Run

**Next.js API Route Updates:**

Update existing API routes to proxy to agent service:

- `src/app/api/chat/route.ts`:
  - Extract session ID from cookie
  - Call agent service `POST /agent/chat`
  - Return response to client
  - Update session cookie if new session created

- `src/app/api/lead/route.ts`:
  - Call agent service `POST /agent/lead`
  - Return success response

**Moved Services:**

- `src/lib/model-provider/` → `src/agent-service/lib/model-provider/`
- `src/lib/rag/` → `src/agent-service/lib/rag/`
- `src/lib/session/` → `src/agent-service/lib/session/`
- `src/lib/lead/` → `src/agent-service/lib/lead/`
- `src/lib/prompts/` → `src/agent-service/lib/prompts/`

**Note:** Keep Next.js `src/lib/` for frontend-specific utilities (client-side helpers, UI utilities).

### Data

**No schema changes.** Agent service uses existing database tables.

**Connection Pooling:**

- Agent service manages its own database connection pool (using `pg` or Drizzle's connection pooling).
- Configure pool size based on Cloud Run concurrency settings (e.g., `max: 10` for concurrency of 80).

### Infra / Config

**Cloud Run Deployment:**

- Service name: `dovvybuddy-agent-service`
- Region: `us-central1` (or same region as Postgres for low latency)
- Configuration:
  - CPU: 1 vCPU
  - Memory: 512 MB (adjust based on load testing)
  - Min instances: 1 (to avoid cold starts)
  - Max instances: 10
  - Concurrency: 80
  - Timeout: 60s (LLM calls can take 5-10s)
  - No unauthenticated access (internal-only)

**Authentication:**

- Agent service validates requests using `Authorization: Bearer <API_KEY>` header.
- API key stored in Google Secret Manager: `dovvybuddy-agent-api-key`.
- Next.js and (future) Telegram bot authenticate with same API key.

**Environment Variables (Agent Service):**

```
# Database
DATABASE_URL=<Postgres connection string>

# Authentication
AGENT_API_KEY=<secret from Secret Manager>

# LLM Provider
LLM_PROVIDER=groq|gemini
GROQ_API_KEY=<key>
GEMINI_API_KEY=<key>

# Embedding Provider
EMBEDDING_PROVIDER=gemini

# Lead Delivery
RESEND_API_KEY=<key>
LEAD_EMAIL_TO=<email>
LEAD_WEBHOOK_URL=<optional>

# Logging & Monitoring
LOG_LEVEL=info|debug
SENTRY_DSN=<optional>
```

**Environment Variables (Next.js - New/Updated):**

```
# Agent Service
AGENT_SERVICE_URL=https://dovvybuddy-agent-service-<hash>.run.app
AGENT_SERVICE_API_KEY=<secret from Secret Manager>
```

**CI/CD Updates:**

Update `.github/workflows/deploy.yml`:

1. Build and deploy agent service first
2. Wait for health check to pass
3. Deploy Next.js with updated `AGENT_SERVICE_URL`

**Dockerfile (Agent Service):**

```dockerfile
# Multi-stage build for optimized image size
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package.json ./
EXPOSE 8080
CMD ["node", "dist/server.js"]
```

---

## 4. Implementation Details

### Phase 1: Create Agent Service Structure

**Tasks:**

1. Create `src/agent-service/` directory structure
2. Set up `package.json` with dependencies:
   - `express` or `fastify`
   - `pg` or `drizzle-orm`
   - `dotenv`
   - `winston` or `pino` (logging)
   - `@google-cloud/secret-manager` (optional)
3. Copy existing services from `src/lib/` to `src/agent-service/lib/`
4. Update import paths in copied services

**Files Created:**
- `src/agent-service/package.json`
- `src/agent-service/tsconfig.json`
- `src/agent-service/server.ts`
- `src/agent-service/Dockerfile`
- `src/agent-service/.dockerignore`
- `src/agent-service/README.md`

### Phase 2: Implement Agent Service API

**Tasks:**

1. Implement Express/Fastify server with routes
2. Add authentication middleware (API key validation)
3. Implement `/agent/chat` endpoint:
   - Accept `{ sessionId, message, channelType }`
   - Call existing session service (now in `lib/session/`)
   - Call RAG retrieval service
   - Construct prompt with system instructions + context + history
   - Call model provider
   - Update session history
   - Return response
4. Implement `/agent/session/new` and `/agent/session/:id` endpoints
5. Implement `/agent/lead` endpoint
6. Add `/health` endpoint
7. Add error handling middleware
8. Add structured logging

**Files Created/Modified:**
- `src/agent-service/routes/chat.ts`
- `src/agent-service/routes/session.ts`
- `src/agent-service/routes/lead.ts`
- `src/agent-service/middleware/auth.ts`
- `src/agent-service/middleware/error-handler.ts`
- `src/agent-service/utils/logger.ts`

### Phase 3: Update Next.js API Routes

**Tasks:**

1. Refactor `src/app/api/chat/route.ts`:
   - Remove agent orchestration logic
   - Add HTTP client to call agent service
   - Handle session cookie management
   - Forward errors to client
2. Refactor `src/app/api/lead/route.ts`:
   - Call agent service instead of local lead service
3. Create agent service client utility:
   - `src/lib/agent-client.ts`
   - Handles authentication, retries, timeouts

**Files Modified:**
- `src/app/api/chat/route.ts`
- `src/app/api/lead/route.ts`

**Files Created:**
- `src/lib/agent-client.ts`

### Phase 4: Testing

**Tasks:**

1. Unit tests for agent service:
   - Route handlers (mock dependencies)
   - Authentication middleware
   - Error handling
2. Integration tests:
   - Agent service endpoints (with test database)
   - End-to-end: Next.js → Agent Service → DB/RAG/LLM
3. Load testing (optional):
   - Apache Bench or k6 to verify performance under load

**Files Created:**
- `src/agent-service/tests/routes/chat.test.ts`
- `src/agent-service/tests/routes/session.test.ts`
- `src/agent-service/tests/routes/lead.test.ts`
- `src/agent-service/tests/middleware/auth.test.ts`
- `tests/integration/agent-service.test.ts`

### Phase 5: Deployment

**Tasks:**

1. Build Docker image locally: `docker build -t agent-service src/agent-service`
2. Test locally: `docker run -p 8080:8080 --env-file .env agent-service`
3. Deploy to Cloud Run:
   ```bash
   gcloud run deploy dovvybuddy-agent-service \
     --source src/agent-service \
     --region us-central1 \
     --no-allow-unauthenticated \
     --min-instances 1 \
     --max-instances 10 \
     --memory 512Mi \
     --timeout 60s
   ```
4. Store agent service URL in environment variable
5. Update Next.js deployment with `AGENT_SERVICE_URL` and `AGENT_SERVICE_API_KEY`
6. Deploy Next.js
7. Run smoke tests

**Commands:**

```bash
# Local development
cd src/agent-service
pnpm install
pnpm dev  # Runs on http://localhost:8080

# Build Docker image
docker build -t dovvybuddy-agent-service src/agent-service

# Run locally with Docker
docker run -p 8080:8080 --env-file .env dovvybuddy-agent-service

# Deploy to Cloud Run
gcloud run deploy dovvybuddy-agent-service \
  --source src/agent-service \
  --region us-central1 \
  --no-allow-unauthenticated

# Update Next.js env vars and redeploy
vercel env add AGENT_SERVICE_URL
vercel env add AGENT_SERVICE_API_KEY
vercel --prod
```

---

## 5. Testing Strategy

### Unit Tests

**Agent Service Routes:**

- `POST /agent/chat`:
  - Valid request with sessionId returns response
  - Valid request without sessionId creates new session
  - Invalid channelType returns 400
  - Missing API key returns 401
  - LLM timeout returns 500

- `POST /agent/session/new`:
  - Creates session and returns sessionId
  - Invalid channelType returns 400

- `GET /agent/session/:id`:
  - Valid sessionId returns session data
  - Non-existent sessionId returns 404
  - Expired sessionId returns 410

- `POST /agent/lead`:
  - Valid training lead saves to database
  - Valid trip lead saves to database
  - Invalid email format returns 400
  - Missing required fields returns 400

**Middleware:**

- Authentication:
  - Valid API key passes
  - Missing API key returns 401
  - Invalid API key returns 401

### Integration Tests

**End-to-End Flow:**

1. Next.js receives chat message
2. Next.js calls agent service `/agent/chat`
3. Agent service retrieves session
4. Agent service performs RAG retrieval
5. Agent service calls LLM
6. Agent service updates session
7. Response returned to Next.js
8. Next.js returns response to browser

**Verification:**
- Session created/updated in database
- RAG retrieval returns relevant chunks
- LLM response is grounded
- Response latency < 10s

### Manual Testing Checklist

- [ ] Agent service health check responds: `curl https://agent-service-url/health`
- [ ] Agent service requires authentication: `curl https://agent-service-url/agent/chat` returns 401
- [ ] Next.js chat interface works end-to-end
- [ ] Session persists across multiple messages
- [ ] Lead capture works from web interface
- [ ] Agent service logs show requests from Next.js
- [ ] Database shows sessions with `channel_type='web'`
- [ ] Response times acceptable (< 5s P95)
- [ ] Error handling graceful (test by disconnecting database)

### Performance Testing (Optional)

**Load Test:**

```bash
# Use Apache Bench or k6
ab -n 1000 -c 10 -H "Authorization: Bearer <API_KEY>" \
  -p chat-payload.json \
  https://agent-service-url/agent/chat
```

**Metrics to Monitor:**
- Response time (P50, P95, P99)
- Error rate
- Database connection pool utilization
- Memory usage
- Cold start latency (first request after idle)

---

## 6. Verification

### Commands

**Development:**

```bash
# Agent service local dev
cd src/agent-service
pnpm install
pnpm dev

# Run agent service tests
pnpm test

# Typecheck agent service
pnpm typecheck

# Build agent service
pnpm build
```

**Docker:**

```bash
# Build Docker image
docker build -t dovvybuddy-agent-service src/agent-service

# Run container locally
docker run -p 8080:8080 --env-file .env dovvybuddy-agent-service

# Test health endpoint
curl http://localhost:8080/health
```

**Deployment:**

```bash
# Deploy agent service to Cloud Run
gcloud run deploy dovvybuddy-agent-service \
  --source src/agent-service \
  --region us-central1 \
  --no-allow-unauthenticated \
  --set-env-vars="DATABASE_URL=$DATABASE_URL,LLM_PROVIDER=$LLM_PROVIDER,..."

# Get agent service URL
gcloud run services describe dovvybuddy-agent-service \
  --region us-central1 \
  --format="value(status.url)"

# Test agent service (with service account token)
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://agent-service-url/health

# Deploy Next.js with updated env vars
vercel --prod
```

**Integration Testing:**

```bash
# Run full test suite (including integration tests)
pnpm test:integration

# Run e2e tests (web chat flow)
pnpm test:e2e
```

### Acceptance Criteria

**Functional:**

- ✅ Agent service deployed to Cloud Run and accessible
- ✅ Agent service `/health` endpoint returns 200
- ✅ Agent service requires API key authentication
- ✅ Next.js API routes successfully call agent service
- ✅ Web chat interface works end-to-end (no regressions)
- ✅ Sessions persist across messages
- ✅ Lead capture works from web interface
- ✅ RAG retrieval returns relevant context
- ✅ LLM responses are grounded and include disclaimers

**Non-Functional:**

- ✅ Response time < 5s P95 (web chat)
- ✅ Agent service logs structured with context
- ✅ Error handling graceful (user-friendly messages)
- ✅ Database connection pooling configured
- ✅ No security vulnerabilities in dependencies
- ✅ Docker image size < 200MB

**Testing:**

- ✅ Unit tests pass (agent service routes, middleware)
- ✅ Integration tests pass (Next.js → Agent Service)
- ✅ E2E tests pass (existing PR6 smoke tests)
- ✅ Manual testing checklist complete

**Documentation:**

- ✅ Agent service README with setup instructions
- ✅ API documentation (endpoints, request/response schemas)
- ✅ Deployment runbook (how to deploy, rollback)
- ✅ Environment variable documentation updated

---

## 7. Rollback Plan

### Feature Flag Strategy

Add `USE_AGENT_SERVICE` feature flag to Next.js:

```typescript
// src/lib/feature-flags.ts
export const USE_AGENT_SERVICE = process.env.USE_AGENT_SERVICE === 'true';
```

In Next.js API routes:

```typescript
if (USE_AGENT_SERVICE) {
  // Call agent service
  return await agentClient.chat({ sessionId, message, channelType: 'web' });
} else {
  // Use embedded agent logic (legacy)
  return await localAgentOrchestrator({ sessionId, message });
}
```

**Note:** This requires keeping old agent logic in Next.js temporarily during transition.

### Revert Strategy

**Option 1: Feature Flag Toggle (Fast)**

1. Set `USE_AGENT_SERVICE=false` in Next.js environment
2. Redeploy Next.js (< 2 minutes)
3. Web chat reverts to embedded agent logic

**Option 2: Full Revert (Slower)**

1. Revert Next.js deployment to previous version
2. Stop agent service (optional, to save costs)

**Data Considerations:**

- No data migrations in this PR, so rollback is safe
- Sessions created during agent service deployment remain valid

---

## 8. Dependencies

### Upstream

- **PR1-6:** Complete (all V1 features working)

### External

- **Google Cloud Platform:**
  - Cloud Run enabled
  - Service account with Cloud Run Admin role
  - Secret Manager enabled (for API key storage)

- **Postgres:**
  - Existing Neon/Supabase instance from PR1
  - Connection string accessible from Cloud Run

- **LLM Providers:**
  - Groq API key (dev)
  - Gemini API key (prod)

### Parallel Work

- None. This PR is a prerequisite for PR7b (Telegram bot).

---

## 9. Risks & Mitigations

### Risk: Agent Service Introduces Latency

**Impact:** Extra HTTP hop adds 100-500ms latency to chat responses.

**Mitigation:**
- Deploy agent service and Next.js in same GCP region
- Use HTTP/2 or gRPC for faster communication
- Monitor P95 latency and optimize if >5s total
- Set min instances=1 to avoid cold starts

---

### Risk: Breaking Changes During Refactor

**Impact:** Web chat stops working, users can't interact with bot.

**Mitigation:**
- Comprehensive integration tests before deployment
- Feature flag to toggle between agent service and embedded logic
- Deploy to staging environment first
- Run smoke tests before promoting to production
- Rollback plan ready (feature flag toggle)

---

### Risk: Authentication Security

**Impact:** Leaked API key allows unauthorized access to agent service.

**Mitigation:**
- Store API key in Google Secret Manager (not in code or env files)
- Rotate API key quarterly
- Use service account tokens for Cloud Run inter-service auth (more secure alternative)
- Monitor agent service access logs for suspicious activity
- Rate limit requests per API key

---

### Risk: Database Connection Pool Exhaustion

**Impact:** Agent service can't connect to database under load, requests fail.

**Mitigation:**
- Configure connection pool size based on Cloud Run concurrency
- Monitor pool utilization in logs
- Set max pool size to 10 (for 80 concurrency)
- Implement connection retry with exponential backoff
- Alert if connection errors exceed 1%

---

### Risk: Cold Start Delays

**Impact:** First request after idle takes 5-10s, poor UX.

**Mitigation:**
- Set min instances=1 for agent service (costs ~$10-20/month)
- Optimize Docker image size (use Alpine base, multi-stage build)
- Implement health check endpoint to keep service warm
- Consider Cloud Run gen2 with faster cold starts

---

### Risk: Cost Increase

**Impact:** Agent service with min instances=1 increases monthly costs.

**Mitigation:**
- Monitor Cloud Run costs in GCP billing dashboard
- Set budget alerts (e.g., alert if >$50/month)
- Evaluate cost vs performance trade-off after 1 week
- If costs too high, reduce min instances to 0 and accept cold starts

---

## 10. Success Metrics

### Technical Metrics

- **Response Time:** P95 < 5s (web chat end-to-end)
- **Error Rate:** < 1% (agent service requests)
- **Availability:** > 99.5% (agent service uptime)
- **Cold Start Rate:** < 5% (requests hitting cold start)

### Business Metrics

- **No Regression:** Lead capture rate same as pre-extraction
- **Session Success:** > 95% of sessions complete without errors

### Quality Metrics

- **Test Coverage:** > 80% for agent service code
- **Code Review:** All changes reviewed and approved
- **Documentation:** Agent service README and API docs complete

---

## 11. Post-Deployment Tasks

**Immediate (Day 1):**

- [ ] Monitor Cloud Run logs for errors
- [ ] Check response time metrics (P50, P95, P99)
- [ ] Verify database connection pool is healthy
- [ ] Run manual smoke test (web chat flow)
- [ ] Check Sentry for any new exceptions

**Short-term (Week 1):**

- [ ] Monitor Cloud Run costs vs projections
- [ ] Analyze latency impact (compare pre/post extraction)
- [ ] Gather feedback from any beta testers
- [ ] Optimize Docker image size if >200MB
- [ ] Tune connection pool settings if needed

**Medium-term (Week 2-4):**

- [ ] Evaluate cold start frequency, adjust min instances if needed
- [ ] Assess need for caching layer (Redis) for session retrieval
- [ ] Document lessons learned for PR7b (Telegram bot)
- [ ] Consider gRPC instead of REST for lower latency

---

## 12. Documentation Updates

**Files to Create/Update:**

1. **Agent Service README** (`src/agent-service/README.md`):
   - Overview and architecture
   - Local development setup
   - API endpoints documentation
   - Deployment instructions
   - Environment variables reference
   - Troubleshooting guide

2. **Main README** (`README.md`):
   - Update architecture section to mention agent service
   - Add agent service to local development instructions

3. **API Documentation** (`docs/api/agent-service.md`):
   - Full API reference with request/response schemas
   - Authentication details
   - Error codes and messages
   - Example requests with curl

4. **Deployment Runbook** (`docs/deployment/agent-service.md`):
   - Step-by-step deployment guide
   - Rollback procedures
   - Monitoring and alerting setup
   - Cost optimization tips

5. **Environment Variables** (`.env.example`):
   - Add `AGENT_SERVICE_URL`
   - Add `AGENT_SERVICE_API_KEY`
   - Document agent service env vars

---

## 13. Timeline Estimate

**Estimated Duration:** 2-3 days (solo founder)

**Breakdown:**

- **Day 1 (6-8 hours):**
  - Create agent service structure
  - Move services from `src/lib/` to `src/agent-service/lib/`
  - Implement Express server and routes
  - Add authentication middleware
  - Write unit tests

- **Day 2 (6-8 hours):**
  - Update Next.js API routes to call agent service
  - Write integration tests
  - Create Dockerfile and test locally
  - Deploy to Cloud Run staging
  - Run smoke tests

- **Day 3 (4-6 hours):**
  - Fix any issues from staging testing
  - Deploy to production
  - Monitor for 4-6 hours
  - Write documentation
  - Create post-deployment checklist

**Potential Delays:**

- Debugging authentication issues (add 2-4 hours)
- Unexpected latency problems (add 4-6 hours)
- Docker build issues (add 1-2 hours)

---

## 14. Future Considerations

### gRPC vs REST

**Current:** REST with JSON over HTTP/1.1

**Future Option:** gRPC for lower latency and smaller payloads

**Trade-off:** gRPC adds complexity (protobuf schemas, code generation) but reduces latency by ~20-40%

**Decision Point:** If P95 latency exceeds 5s, consider gRPC migration

---

### Caching Layer

**Current:** No caching; every request queries database for session

**Future Option:** Redis for session caching (TTL 24h)

**Trade-off:** Redis adds cost (~$20-30/month for managed Redis) but reduces database load

**Decision Point:** If database connection pool hits 80% utilization, add Redis

---

### Service Account Auth

**Current:** Shared API key in Secret Manager

**Future Option:** Google Cloud service account tokens for inter-service auth

**Trade-off:** More secure (automatic rotation) but harder to debug

**Decision Point:** After V1.1 launch, migrate to service account auth for better security

---

## Summary

PR7a extracts the agent orchestration logic into a standalone Cloud Run service, enabling multi-channel support (web and future Telegram). This is a prerequisite refactor with no user-facing changes but significant architectural improvement. Key success criteria: no regressions in web chat, response time <5s P95, and comprehensive testing to ensure feature parity.
