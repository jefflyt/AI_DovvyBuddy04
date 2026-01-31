# PR8b: Telegram Bot Adapter & Basic Chat Flow

**Branch Name:** `feature/pr7b-telegram-bot-adapter`  
**Status:** Planned  
**Date:** December 29, 2025  
**Updated:** January 8, 2026 (Updated for Python backend)  
**Based on:** MASTER_PLAN.md (V1.1 Telegram Integration)

> **✅ ARCHITECTURE UPDATE:** Python/FastAPI backend (PR3.2c) already provides the agent service. No extraction needed (PR8a obsolete). This PR implements a Python Telegram bot that integrates directly with the existing FastAPI backend.

---

## 1. Feature/Epic Summary

### Objective

Implement a Telegram bot that connects to the ADK agent service and provides basic chat functionality (certification guidance, trip research) with the same grounding and safety refusals as the web interface. This extends DovvyBuddy's reach to Telegram users while maintaining consistency in responses and safety guardrails.

### User Impact

**Primary Users (Divers):**
- **Telegram users** can ask certification and trip questions without visiting the website.
- **Mobile-first users** get quick answers on-the-go through a familiar messaging interface.
- **International users** who prefer Telegram over web chat gain access to DovvyBuddy.

**Secondary Impact:**
- Validates multi-channel agent architecture.
- Expands distribution without duplicating business logic.
- Proves Telegram as viable channel before adding lead capture.

### Dependencies

**Upstream:**
- **PR3.2c:** Python agent orchestration (✅ Complete - no PR8a extraction needed)
- **PR1-6:** Full web V1 functionality (database, RAG, sessions, lead capture, landing page)

**External:**
- **Telegram Bot Token:** Obtained from @BotFather
- **Cloud Run:** Hosting for Telegram bot service (or can run alongside FastAPI backend)
- **Database:** Access to existing Postgres instance (for sessions)

### Assumptions

- **Assumption:** Python FastAPI backend from PR3.2c provides chat orchestration at `POST /api/chat`
- **Assumption:** Telegram bot is implemented in **Python** (using `python-telegram-bot` library) for consistency with backend
- **Assumption:** Telegram bot can be deployed as separate Cloud Run service OR integrated into existing FastAPI app
- **Assumption:** Telegram bot uses **webhook mode** (not polling) for production efficiency
- **Assumption:** Session management reuses existing `sessions` table with `channel_type='telegram'` and `channel_user_id=<telegram_user_id>`
- **Assumption:** Telegram bot is **text-only** in V1.1 (no voice, photos, location sharing)
- **Assumption:** Telegram bot username is `@DovvyBuddyBot` or similar (must be unique and available)
- **Assumption:** Rate limiting per Telegram user ID prevents abuse (max 10 messages per minute per user)
- **Assumption:** Bot privacy mode is **disabled** (bot can read all messages in 1-on-1 chats)
- **Assumption:** Group chats are **disabled** in V1.1 (1-on-1 chats only)

---

## 2. Complexity & Fit

### Classification

**Single-PR**

### Rationale

- **Focused Scope:** Basic chat flow only; lead capture deferred to PR8c.
- **Single Service:** One new Cloud Run service (Telegram bot).
- **Reuses Infrastructure:** Agent service, database, RAG, LLM provider all exist.
- **Limited Risk:** Telegram bot is additive; web functionality unaffected.
- **Independently Testable:** Can test Telegram bot in isolation without affecting web.
- **Estimated Scope:** ~12-15 files (bot service, webhook handler, message handler, session manager, tests).

---

## 3. Full-Stack Impact

### Frontend

**Landing Page Update:**

- `/app/page.tsx`:
  - Add "Also available on Telegram" badge/section with link to `https://t.me/DovvyBuddyBot`.
  - Include Telegram icon and brief description ("Chat with DovvyBuddy on Telegram for quick dive advice on the go.").

**Optional Telegram Info Page:**

- `/app/telegram/page.tsx` (new):
  - Explains how to use Telegram bot.
  - Provides QR code for easy mobile access.
  - Lists example questions ("What is Open Water certification?", "Where can I dive in Cozumel?").
  - Shows sample conversation flow.

### Backend

**Implementation Approach:**

Two options for Telegram bot implementation:

**Option A: Separate Python Service** (Recommended for V1.1)
- New standalone Python service using `python-telegram-bot` library
- Communicates with FastAPI backend via HTTP (`POST /api/chat`)
- Deployed as separate Cloud Run service
- Simpler to develop and deploy independently

**Option B: Integrated with FastAPI Backend** (Consider for V2)
- Add Telegram bot handlers directly to FastAPI app
- Share same codebase, database connections, and services
- Single deployment unit
- More complex but better resource utilization

**Recommended:** Option A for V1.1 (clean separation, faster development)

**New Telegram Bot Service Structure (Option A):**

Create standalone Python service in `src/telegram-bot/`:

```
src/telegram-bot/
├── main.py                     # Bot entry point, webhook setup
├── handlers/
│   ├── message.py             # Text message handler
│   ├── command.py             # /start, /help, /newchat commands
│   └── error.py               # Error handler
├── services/
│   ├── backend_client.py      # HTTP client for FastAPI backend
│   ├── session_manager.py     # Telegram session management
│   └── rate_limiter.py        # Per-user rate limiting
├── utils/
│   ├── logger.py              # Structured logging
│   └── formatter.py           # Message formatting (Markdown/HTML)
├── config.py                  # Configuration (env vars)
├── Dockerfile                 # Container for Cloud Run
├── requirements.txt           # Python dependencies
└── README.md                  # Bot documentation
```
│   └── error-handler.ts      # Formats errors for Telegram
├── services/
│   ├── session-manager.ts    # Maps Telegram user ID to session ID
│   ├── agent-client.ts       # HTTP client for agent service
│   └── rate-limiter.ts       # Rate limiting per user
├── utils/
│   ├── logger.ts             # Structured logging
│   ├── formatter.ts          # Formats responses for Telegram (markdown, chunking)
│   └── validator.ts          # Input validation
├── types/
│   └── index.ts              # Telegram bot types
├── config/
│   └── bot-config.ts         # Bot configuration (commands, rate limits)
├── scripts/
│   └── setup-webhook.ts      # Webhook registration script
├── Dockerfile
├── .dockerignore
├── package.json
├── tsconfig.json
└── README.md
```

**Key Components:**

1. **Webhook Handler** (`webhook-handler.ts`):
   - Receives POST requests from Telegram with update objects.
   - Validates webhook secret.
   - Dispatches to message handler or command handler.
   - Returns 200 OK to Telegram within 60s.

2. **Message Handler** (`message-handler.ts`):
   - Extracts Telegram user ID and message text.
   - Calls session manager to get/create session.
   - Calls agent client with `{ sessionId, message, channelType: 'telegram' }`.
   - Formats response for Telegram (handle long messages, markdown).
   - Sends response via Telegram Bot API.
   - Logs message processing with context.

3. **Command Handler** (`command-handler.ts`):
   - `/start`: Welcome message with bot description and example questions.
   - `/help`: Lists available commands and bot capabilities.
   - `/newchat`: Clears current session and starts fresh conversation.
   - `/cancel`: (Reserved for PR8c lead capture flow).

4. **Session Manager** (`session-manager.ts`):
   - `getOrCreateSession(telegramUserId: string) => Promise<string>`: Returns session ID.
   - Queries database for existing session with `channel_type='telegram'` and `channel_user_id=<telegramUserId>`.
   - Creates new session if none exists or previous session expired.
   - Updates `last_active_at` timestamp on session retrieval.

5. **Agent Client** (`agent-client.ts`):
   - HTTP client for calling agent service.
   - Methods: `chat()`, `newSession()`, `getSession()`.
   - Handles authentication (API key in Authorization header).
   - Implements retry logic (3 retries with exponential backoff).
   - Timeout configuration (30s for chat, 10s for session operations).

6. **Rate Limiter** (`rate-limiter.ts`):
   - In-memory rate limiting per Telegram user ID.
   - Max 10 messages per minute per user.
   - Returns error message if limit exceeded: "You're sending messages too quickly. Please wait a moment and try again."
   - Sliding window implementation.

7. **Formatter** (`formatter.ts`):
   - Converts agent responses to Telegram markdown format.
   - Splits long messages (>4096 characters) into multiple messages.
   - Escapes special markdown characters.
   - Adds typing indicator while processing.

**Agent Service (No Changes):**

Agent service from PR8a already supports `channelType='telegram'` parameter. No modifications needed.

**Database (Schema Update):**

Update `sessions` table to support Telegram (migration from PR8a if not already done):

```sql
ALTER TABLE sessions ADD COLUMN channel_type VARCHAR(20) DEFAULT 'web';
ALTER TABLE sessions ADD COLUMN channel_user_id VARCHAR(255);
CREATE UNIQUE INDEX idx_sessions_channel_user ON sessions(channel_type, channel_user_id) WHERE channel_type IS NOT NULL AND channel_user_id IS NOT NULL;
UPDATE sessions SET channel_type='web' WHERE channel_type IS NULL;
```

### Data

**Migrations:**

- `003_add_channel_support_to_sessions.sql` (if not done in PR8a):
  - Add `channel_type` column (varchar, default 'web').
  - Add `channel_user_id` column (varchar, nullable).
  - Add `last_active_at` column (timestamp, for session cleanup).
  - Create unique index on `(channel_type, channel_user_id)`.
  - Backfill existing sessions with `channel_type='web'`.

**Session Data for Telegram:**

- `channel_type`: `'telegram'`
- `channel_user_id`: Telegram user ID (numeric string, e.g., "123456789")
- `diver_profile`: Captured during conversation (same as web)
- `conversation_history`: Array of message objects (same format as web)
- `expires_at`: 24 hours from creation
- `last_active_at`: Updated on each message

**No changes to other tables** (leads changes deferred to PR8c).

### Infra / Config

**Telegram Bot Service Deployment:**

- Service name: `dovvybuddy-telegram-bot`
- Runtime: Cloud Run
- Region: `us-central1` (same as agent service)
- Configuration:
  - CPU: 1 vCPU
  - Memory: 256 MB (lightweight, mostly HTTP proxying)
  - Min instances: 0 (scale to zero when idle)
  - Max instances: 10
  - Concurrency: 80
  - Timeout: 60s
  - Allow unauthenticated (webhook endpoint is public, validated via secret)

**Webhook Endpoint:**

- URL: `https://dovvybuddy-telegram-bot-<hash>.run.app/webhook/telegram`
- Method: POST
- Telegram sends updates to this endpoint.
- Endpoint validates `X-Telegram-Bot-Api-Secret-Token` header.

**Webhook Registration:**

Use setup script to register webhook with Telegram:

```bash
curl -X POST "https://api.telegram.org/bot<BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://dovvybuddy-telegram-bot-<hash>.run.app/webhook/telegram",
    "secret_token": "<WEBHOOK_SECRET>",
    "allowed_updates": ["message"]
  }'
```

**Environment Variables (Telegram Bot Service):**

```
# Telegram Bot
TELEGRAM_BOT_TOKEN=<bot token from BotFather>
TELEGRAM_WEBHOOK_SECRET=<random 32-char string>

# Agent Service
AGENT_SERVICE_URL=https://dovvybuddy-agent-service-<hash>.run.app
AGENT_SERVICE_API_KEY=<shared secret>

# Database (for session management)
DATABASE_URL=<Postgres connection string>

# Rate Limiting
RATE_LIMIT_MAX_REQUESTS=10
RATE_LIMIT_WINDOW_MS=60000

# Logging
LOG_LEVEL=info
NODE_ENV=production
```

**CI/CD Updates:**

Update `.github/workflows/deploy.yml`:

1. Build and deploy agent service (if changed)
2. Build and deploy Telegram bot service
3. Run webhook setup script
4. Deploy Next.js (if changed)
5. Run smoke tests (web + Telegram)

### Security

**Webhook Validation:**

- Telegram sends `X-Telegram-Bot-Api-Secret-Token` header with each request.
- Webhook handler validates this token matches `TELEGRAM_WEBHOOK_SECRET`.
- Reject requests without valid token (return 401).

**API Key for Agent Service:**

- Telegram bot authenticates to agent service using `Authorization: Bearer <AGENT_SERVICE_API_KEY>`.
- API key stored in Google Secret Manager.

**Rate Limiting:**

- Prevent abuse by limiting messages per user (10/minute).
- Implemented in-memory (sufficient for single instance with concurrency 80).
- Future: Use Redis if multi-instance deployment needed.

**Input Sanitization:**

- Sanitize user messages before logging (remove sensitive data).
- Validate message length (max 4096 characters from Telegram).
- Escape markdown in responses to prevent injection.

---

## 4. Implementation Details

### Phase 1: Setup Telegram Bot & Webhook Server

**Tasks:**

1. Create Telegram bot via @BotFather:
   - Get bot token
   - Set bot username (e.g., @DovvyBuddyBot)
   - Set bot description and about text
   - Configure commands: `/start`, `/help`, `/newchat`
   - Disable group chat access
   - Disable privacy mode (bot reads all messages in 1-on-1 chats)

2. Create `src/telegram/` directory structure

3. Initialize `package.json` with dependencies:
   - `telegraf` (Telegram bot framework)
   - `express` or `fastify` (webhook server)
   - `pg` or `drizzle-orm` (database access)
   - `axios` (agent service HTTP client)
   - `winston` or `pino` (logging)
   - `dotenv` (env vars)

4. Implement webhook server (`server.ts`):
   - Express/Fastify app with POST `/webhook/telegram` endpoint
   - Health check endpoint: GET `/health`
   - Graceful shutdown handling

5. Implement webhook handler (`webhook-handler.ts`):
   - Validate secret token
   - Parse Telegram update object
   - Route to message or command handler
   - Error handling with logging

**Files Created:**
- `src/telegram/package.json`
- `src/telegram/tsconfig.json`
- `src/telegram/server.ts`
- `src/telegram/handlers/webhook-handler.ts`
- `src/telegram/.env.example`
- `src/telegram/README.md`

### Phase 2: Implement Message & Command Handlers

**Tasks:**

1. **Message Handler** (`message-handler.ts`):
   - Extract Telegram user ID and message text
   - Call rate limiter to check if user is rate limited
   - Call session manager to get/create session
   - Show "typing..." indicator
   - Call agent service via agent client
   - Format response (markdown, chunk long messages)
   - Send response to user
   - Handle errors gracefully (user-friendly messages)

2. **Command Handler** (`command-handler.ts`):
   - `/start`: Send welcome message with bot description and example questions
   - `/help`: List available commands and bot capabilities
   - `/newchat`: Clear session and confirm to user ("Started a new conversation!")

3. **Bot Setup** (`bot.ts`):
   - Initialize Telegraf bot with token
   - Register command handlers
   - Register message handler
   - Export bot instance

**Files Created:**
- `src/telegram/handlers/message-handler.ts`
- `src/telegram/handlers/command-handler.ts`
- `src/telegram/handlers/error-handler.ts`
- `src/telegram/bot.ts`

### Phase 3: Implement Services (Session, Agent Client, Rate Limiter)

**Tasks:**

1. **Session Manager** (`session-manager.ts`):
   - `getOrCreateSession(telegramUserId)`: Query DB for existing session or create new one
   - Use existing `sessions` table with `channel_type='telegram'`
   - Handle session expiry (check `expires_at`)
   - Update `last_active_at` timestamp

2. **Agent Client** (`agent-client.ts`):
   - `chat(sessionId, message)`: POST to `/agent/chat`
   - Include `Authorization` header with API key
   - Handle timeouts (30s)
   - Retry on 5xx errors (3 retries with exponential backoff)
   - Parse and return response

3. **Rate Limiter** (`rate-limiter.ts`):
   - In-memory sliding window rate limiter
   - Track message counts per Telegram user ID
   - `isRateLimited(userId)`: Returns boolean
   - Configurable limits (default 10 messages/minute)

4. **Formatter** (`formatter.ts`):
   - `formatForTelegram(text)`: Convert to Telegram markdown
   - `splitLongMessage(text, maxLength=4096)`: Split into chunks
   - `escapeMarkdown(text)`: Escape special characters
   - Handle code blocks, lists, bold, italic

**Files Created:**
- `src/telegram/services/session-manager.ts`
- `src/telegram/services/agent-client.ts`
- `src/telegram/services/rate-limiter.ts`
- `src/telegram/utils/formatter.ts`
- `src/telegram/utils/logger.ts`
- `src/telegram/utils/validator.ts`

### Phase 4: Deployment & Webhook Setup

**Tasks:**

1. Create Dockerfile:
   - Multi-stage build (builder + runtime)
   - Use Node 20 Alpine base image
   - Copy only necessary files
   - Expose port 8080
   - Health check command

2. Test locally:
   - Run webhook server locally
   - Use ngrok for public HTTPS endpoint
   - Register webhook with test bot
   - Send messages and verify responses

3. Deploy to Cloud Run:
   - Build Docker image
   - Deploy to `dovvybuddy-telegram-bot` service
   - Configure environment variables
   - Enable Cloud Run service

4. Register webhook:
   - Run `setup-webhook.ts` script
   - Verify webhook info with `getWebhookInfo`

5. Test in production:
   - Send message to @DovvyBuddyBot
   - Verify response
   - Check logs in Cloud Run

**Files Created:**
- `src/telegram/Dockerfile`
- `src/telegram/.dockerignore`
- `src/telegram/scripts/setup-webhook.ts`
- `src/telegram/scripts/delete-webhook.ts`

### Phase 5: Landing Page Update

**Tasks:**

1. Update landing page (`src/app/page.tsx`):
   - Add Telegram section/badge
   - Link to `https://t.me/DovvyBuddyBot`
   - Add Telegram icon (from React Icons or similar)

2. Optional: Create Telegram info page (`src/app/telegram/page.tsx`):
   - QR code for mobile access
   - Example questions
   - Sample conversation
   - Link to web chat as alternative

**Files Modified:**
- `src/app/page.tsx`

**Files Created (Optional):**
- `src/app/telegram/page.tsx`
- `src/components/telegram/TelegramCTA.tsx`

---

## 5. Testing Strategy

### Unit Tests

**Message Handler:**
- Valid message processes successfully
- Long message splits into chunks
- Rate limited user receives error
- Agent service error handled gracefully

**Command Handler:**
- `/start` sends welcome message
- `/help` sends help text
- `/newchat` clears session

**Session Manager:**
- Creates new session for new Telegram user
- Retrieves existing session for returning user
- Handles expired sessions (creates new one)
- Updates last_active_at timestamp

**Agent Client:**
- Successful chat request returns response
- Timeout handled with error
- Retry logic works on 5xx errors
- Authentication header included

**Rate Limiter:**
- Allows requests within limit
- Blocks requests exceeding limit
- Sliding window works correctly
- Different users tracked separately

**Formatter:**
- Long text splits correctly
- Markdown formatting applied
- Special characters escaped
- Code blocks preserved

**Test Files:**
- `src/telegram/tests/handlers/message-handler.test.ts`
- `src/telegram/tests/handlers/command-handler.test.ts`
- `src/telegram/tests/services/session-manager.test.ts`
- `src/telegram/tests/services/agent-client.test.ts`
- `src/telegram/tests/services/rate-limiter.test.ts`
- `src/telegram/tests/utils/formatter.test.ts`

### Integration Tests

**End-to-End Flow:**

1. Mock Telegram webhook request with message
2. Webhook handler processes request
3. Session created/retrieved from database
4. Agent service called (mocked or real)
5. Response formatted and returned
6. Database shows updated session

**Test Scenarios:**
- New user sends first message (session created)
- Returning user sends message (session retrieved)
- User sends multiple messages (conversation history persists)
- User triggers rate limit (error message sent)
- Agent service timeout (graceful error)

**Test Files:**
- `tests/integration/telegram-bot.test.ts`

### Manual Testing Checklist

**Basic Functionality:**
- [ ] Send message to bot, receive relevant response
- [ ] `/start` command shows welcome message
- [ ] `/help` command lists commands
- [ ] `/newchat` clears session and confirms
- [ ] Bot responds within 5 seconds
- [ ] Long response splits into multiple messages
- [ ] Markdown formatting displays correctly

**Session Persistence:**
- [ ] Send message, then send follow-up → Bot remembers context
- [ ] Wait 10 minutes, send message → Session still active
- [ ] Use `/newchat`, send message → New session, no previous context

**Rate Limiting:**
- [ ] Send 11 messages in 1 minute → 11th message gets error
- [ ] Wait 1 minute, send message → Works again

**Error Handling:**
- [ ] Stop agent service, send message → User-friendly error
- [ ] Send very long message (5000 chars) → Handled gracefully
- [ ] Send special characters (markdown syntax) → No crashes

**Database Verification:**
- [ ] Query sessions table → Telegram session exists with correct channel_type
- [ ] Check conversation_history → Messages stored correctly
- [ ] Verify expires_at → 24 hours from creation

**Logging:**
- [ ] Cloud Run logs show incoming messages with context
- [ ] Errors logged with stack traces
- [ ] No sensitive data (bot token, user IDs) in logs

---

## 6. Verification

### Commands

**Development:**

```bash
# Install dependencies
cd src/telegram
pnpm install

# Run locally (requires ngrok for webhook)
pnpm dev

# Start ngrok tunnel
ngrok http 8080

# Register webhook (use ngrok URL)
pnpm telegram:setup-webhook

# Run tests
pnpm test

# Typecheck
pnpm typecheck

# Build
pnpm build
```

**Docker:**

```bash
# Build Docker image
docker build -t dovvybuddy-telegram-bot src/telegram

# Run locally
docker run -p 8080:8080 --env-file src/telegram/.env dovvybuddy-telegram-bot

# Test health endpoint
curl http://localhost:8080/health
```

**Deployment:**

```bash
# Deploy to Cloud Run
gcloud run deploy dovvybuddy-telegram-bot \
  --source src/telegram \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN,AGENT_SERVICE_URL=$AGENT_SERVICE_URL,..."

# Get service URL
gcloud run services describe dovvybuddy-telegram-bot \
  --region us-central1 \
  --format="value(status.url)"

# Register webhook
cd src/telegram
node scripts/setup-webhook.js

# Verify webhook
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"

# Test bot
# Send message to @DovvyBuddyBot on Telegram

# Check logs
gcloud run logs read dovvybuddy-telegram-bot --limit 50
```

**Database Verification:**

```sql
-- Check Telegram sessions
SELECT * FROM sessions WHERE channel_type = 'telegram' ORDER BY created_at DESC LIMIT 10;

-- Count active Telegram sessions
SELECT COUNT(*) FROM sessions WHERE channel_type = 'telegram' AND expires_at > NOW();

-- View conversation history for a session
SELECT conversation_history FROM sessions WHERE id = '<session-id>';
```

### Acceptance Criteria

**Functional:**

- ✅ Bot responds to messages with relevant answers
- ✅ Bot responds to `/start`, `/help`, `/newchat` commands
- ✅ Sessions persist across messages (conversation context maintained)
- ✅ Sessions expire after 24 hours
- ✅ Rate limiting prevents spam (10 messages/minute per user)
- ✅ Long messages split into chunks (<4096 chars each)
- ✅ Markdown formatting displays correctly in Telegram
- ✅ Error messages are user-friendly (no stack traces)
- ✅ Bot handles agent service errors gracefully

**Non-Functional:**

- ✅ Response time < 5 seconds (P95)
- ✅ Webhook processes updates within 60 seconds (Telegram timeout)
- ✅ No crashes or uncaught exceptions
- ✅ Logs include structured context (user ID, session ID, message)
- ✅ Docker image size < 150MB

**Testing:**

- ✅ Unit tests pass (handlers, services, utils)
- ✅ Integration tests pass (end-to-end flow)
- ✅ Manual testing checklist complete
- ✅ No regressions in web chat functionality

**Infrastructure:**

- ✅ Telegram bot service deployed to Cloud Run
- ✅ Webhook registered with Telegram
- ✅ Health check endpoint responds
- ✅ Environment variables configured
- ✅ Logs visible in Cloud Run console

**Documentation:**

- ✅ Telegram bot README with setup instructions
- ✅ Webhook setup script documented
- ✅ Landing page mentions Telegram availability
- ✅ Optional: Telegram info page created

---

## 7. Rollback Plan

### Feature Flag Strategy

Add `TELEGRAM_ENABLED` environment variable:

```typescript
// src/telegram/config/bot-config.ts
export const TELEGRAM_ENABLED = process.env.TELEGRAM_ENABLED !== 'false';

// In webhook-handler.ts
if (!TELEGRAM_ENABLED) {
  return res.status(200).json({ ok: true }); // Acknowledge but don't process
}
```

### Revert Strategy

**Option 1: Disable via Feature Flag (Fast)**

1. Set `TELEGRAM_ENABLED=false` in Cloud Run environment
2. Redeploy Telegram bot service (< 2 minutes)
3. Webhook still responds 200 but doesn't process messages

**Option 2: Delete Webhook (Medium)**

1. Run delete webhook script: `node scripts/delete-webhook.js`
2. Telegram stops sending updates
3. Bot service can be stopped to save costs

**Option 3: Full Revert (Slower)**

1. Delete Cloud Run service: `gcloud run services delete dovvybuddy-telegram-bot`
2. Remove Telegram mention from landing page
3. Delete webhook via Telegram API

**Data Considerations:**

- Telegram sessions remain in database (harmless)
- Can be cleaned up later: `DELETE FROM sessions WHERE channel_type = 'telegram'`
- No migration rollback needed (schema changes are backward compatible)

---

## 8. Dependencies

### Upstream

- **PR8a:** Agent service extracted and deployed to Cloud Run (REQUIRED)
- **PR1-6:** Database, RAG, sessions, lead capture, landing page (REQUIRED)

### External

- **Telegram:**
  - Bot token from @BotFather
  - Bot username available (e.g., @DovvyBuddyBot)

- **Google Cloud Platform:**
  - Cloud Run enabled
  - Service account with Cloud Run Admin role

- **Database:**
  - Postgres instance with session table updated (PR8a migration)

- **Agent Service:**
  - Deployed and accessible via `AGENT_SERVICE_URL`
  - API key available

### Parallel Work

- None. This PR is on the critical path for PR8c (lead capture).

---

## 9. Risks & Mitigations

### Risk: Telegram API Rate Limits

**Impact:** Bot can send max 30 messages/second globally. High traffic could hit rate limits.

**Mitigation:**
- Implement client-side rate limiting (queue outgoing messages)
- Monitor rate limit errors (HTTP 429) in logs
- Use exponential backoff for retries
- Telegram's limits are generous for MVP; defer optimization until needed

---

### Risk: Webhook Reliability

**Impact:** Telegram webhook might fail due to network issues, timeout, or Cloud Run cold start.

**Mitigation:**
- Set min instances=0 (scale to zero) but accept occasional cold starts (~2-3s)
- Implement health check endpoint to keep service warm if needed
- Telegram retries failed webhooks automatically
- Monitor webhook failures in logs

---

### Risk: Session Management Complexity

**Impact:** Mapping Telegram user IDs to sessions could have bugs (duplicate sessions, orphaned sessions).

**Mitigation:**
- Use unique index on `(channel_type, channel_user_id)` to prevent duplicates
- Log session creation/retrieval for debugging
- Add database constraints to enforce data integrity
- Write comprehensive tests for session manager

---

### Risk: Message Formatting Issues

**Impact:** Markdown formatting might break in Telegram (special characters, code blocks).

**Mitigation:**
- Escape special characters in formatter utility
- Test with various message types (lists, code, links)
- Fall back to plain text if markdown parsing fails
- Monitor user reports of formatting issues

---

### Risk: Cold Start Latency

**Impact:** First message after idle period takes 5-10s, poor UX.

**Mitigation:**
- Optimize Docker image size (use Alpine, multi-stage build)
- Accept cold starts for V1.1 (cost vs UX trade-off)
- If cold starts exceed 10% of requests, increase min instances to 1
- Show "typing..." indicator immediately to set expectations

---

### Risk: Agent Service Dependency

**Impact:** If agent service is down, Telegram bot can't respond.

**Mitigation:**
- Implement retry logic in agent client (3 retries)
- Show user-friendly error: "I'm having trouble connecting. Please try again in a moment."
- Monitor agent service uptime (should be >99.5% from PR8a)
- Set up alerts for agent service errors

---

## 10. Success Metrics

### Technical Metrics

- **Response Time:** P95 < 5s (message to response)
- **Error Rate:** < 1% (webhook processing failures)
- **Availability:** > 99% (webhook endpoint uptime)
- **Cold Start Rate:** < 10% (requests hitting cold start)

### Business Metrics

- **Active Users:** Track daily/weekly active Telegram users
- **Message Volume:** Track messages sent/received per day
- **Session Duration:** Average messages per session
- **Retention:** % of users who return within 7 days

### Quality Metrics

- **Test Coverage:** > 80% for Telegram bot code
- **Bug Reports:** < 5 user-reported bugs in first week
- **User Feedback:** Positive sentiment from Telegram users

---

## 11. Post-Deployment Tasks

**Immediate (Day 1):**

- [ ] Monitor Cloud Run logs for errors
- [ ] Verify webhook is receiving updates (check Telegram getWebhookInfo)
- [ ] Send test messages to bot and verify responses
- [ ] Check database for new Telegram sessions
- [ ] Verify rate limiting works (send 11 messages quickly)

**Short-term (Week 1):**

- [ ] Monitor Cloud Run costs vs projections
- [ ] Analyze response time metrics (P50, P95, P99)
- [ ] Track active users and message volume
- [ ] Gather user feedback (if any users in beta)
- [ ] Fix any urgent bugs reported

**Medium-term (Week 2-4):**

- [ ] Evaluate cold start frequency, adjust min instances if needed
- [ ] Optimize Docker image size if >150MB
- [ ] Review logs for patterns (common questions, errors)
- [ ] Document lessons learned for PR8c (lead capture)
- [ ] Consider analytics integration (track events)

---

## 12. Documentation Updates

**Files to Create/Update:**

1. **Telegram Bot README** (`src/telegram/README.md`):
   - Overview and architecture
   - Local development setup (with ngrok)
   - Webhook registration instructions
   - Deployment guide
   - Troubleshooting common issues

2. **Main README** (`README.md`):
   - Add Telegram bot to features list
   - Mention Telegram availability in introduction
   - Link to Telegram bot README

3. **Landing Page** (`src/app/page.tsx`):
   - Add Telegram badge/section with link to bot

4. **Environment Variables** (`.env.example`):
   - Add Telegram bot variables:
     ```
     TELEGRAM_BOT_TOKEN=
     TELEGRAM_WEBHOOK_SECRET=
     AGENT_SERVICE_URL=
     AGENT_SERVICE_API_KEY=
     ```

5. **Deployment Guide** (`docs/deployment/telegram-bot.md`):
   - Step-by-step deployment instructions
   - Webhook setup and troubleshooting
   - Monitoring and alerting setup
   - Cost estimates

---

## 13. Timeline Estimate

**Estimated Duration:** 3-5 days (solo founder)

**Breakdown:**

- **Day 1 (6-8 hours):**
  - Create Telegram bot via BotFather
  - Set up project structure and dependencies
  - Implement webhook server and handler
  - Implement message and command handlers
  - Write unit tests

- **Day 2 (6-8 hours):**
  - Implement session manager
  - Implement agent client with retry logic
  - Implement rate limiter
  - Implement formatter utility
  - Write more unit tests

- **Day 3 (4-6 hours):**
  - Create Dockerfile and test locally
  - Deploy to Cloud Run staging
  - Register webhook and test with real Telegram
  - Fix any issues found during testing
  - Write integration tests

- **Day 4 (4-6 hours):**
  - Update landing page with Telegram mention
  - Optional: Create Telegram info page
  - Deploy to production
  - Run full manual testing checklist
  - Monitor for 2-4 hours

- **Day 5 (2-4 hours):**
  - Fix any urgent issues from production
  - Write documentation
  - Create deployment runbook
  - Post-deployment monitoring

**Potential Delays:**

- Telegram Bot API learning curve (add 2-4 hours)
- Webhook registration issues (add 1-2 hours)
- Message formatting edge cases (add 2-3 hours)
- Session management bugs (add 2-4 hours)

---

## 14. Future Considerations

### Voice Message Support

**Current:** Text-only messages

**Future Option:** Convert voice messages to text using Speech-to-Text API

**Trade-off:** Adds cost (~$0.006 per 15 seconds) and complexity

**Decision Point:** If >10% of users request voice support, implement in V1.2

---

### Inline Keyboards for Quick Replies

**Current:** Text-only responses

**Future Option:** Add inline keyboards for common questions (e.g., "Tell me more", "Connect with a shop")

**Trade-off:** More engaging UX but increases complexity

**Decision Point:** After PR8c launch, add inline keyboards for lead type selection

---

### Photo Support (Dive Site Photos)

**Current:** Text-only

**Future Option:** Send dive site photos when recommending destinations

**Trade-off:** Requires image storage (GCS) and content management

**Decision Point:** Defer to V2 with richer content system

---

### Analytics Integration

**Current:** No analytics tracking for Telegram

**Future Option:** Track events (session_start, message_sent, command_used) to Posthog/GA4

**Trade-off:** Adds latency (~50-100ms) and privacy considerations

**Decision Point:** Add in PR8c along with web analytics

---

### Multi-Language Support

**Current:** English-only

**Future Option:** Detect user language and respond accordingly

**Trade-off:** Requires translation system or multi-language LLM prompts

**Decision Point:** Defer to V2+ based on user demand

---

## Summary

PR8b implements a Telegram bot that provides the same certification guidance and trip research functionality as the web interface. The bot reuses the agent service from PR8a and stores sessions in the existing database with `channel_type='telegram'`. Lead capture functionality is deferred to PR8c to keep this PR focused and manageable.

**Key Deliverables:**
- ✅ Telegram bot service deployed to Cloud Run
- ✅ Webhook-based message processing
- ✅ Session management with 24h expiry
- ✅ Rate limiting (10 messages/minute per user)
- ✅ Command handlers (/start, /help, /newchat)
- ✅ Landing page updated with Telegram mention
- ✅ Comprehensive testing (unit + integration + manual)

**Main Risks:**
- Telegram webhook reliability (mitigated with retries and monitoring)
- Session management bugs (mitigated with tests and database constraints)
- Cold start latency (accepted for V1.1, can optimize later)

**Estimated Timeline:** 3-5 days for solo founder (assuming PR8a complete and agent service stable).
