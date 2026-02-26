# PR8c: Telegram Lead Capture & Production Hardening

**Branch Name:** `feature/pr7c-telegram-lead-capture`  
**Status:** Planned  
**Date:** December 29, 2025  
**Based on:** MASTER_PLAN.md (V1.1 Telegram Integration - Final)

---

## 1. Feature/Epic Summary

### Objective

Complete the Telegram bot implementation by adding lead capture flows (Training and Trip leads) using inline keyboards and conversational prompts, and hardening the system for production with error monitoring, analytics, and comprehensive logging. This PR makes the Telegram channel fully feature-complete with the web interface.

### User Impact

**Primary Users (Divers):**

- **Telegram users** can now request training or trip assistance directly through the bot.
- **Mobile-first users** complete the full journey (discovery → guidance → lead capture) without leaving Telegram.
- **Qualified leads** are delivered to partner shops with full Telegram user context.

**Secondary Users (Partner Shops):**

- Receive leads from Telegram channel with context (Telegram username, user ID).
- Can identify Telegram users for follow-up.

**Product Team:**

- Full visibility into Telegram bot performance (analytics, errors, usage patterns).
- Production-ready monitoring and alerting for Telegram channel.
- Ability to optimize based on real usage data.

### Dependencies

**Upstream:**

- **PR8a:** Agent service extracted and deployed to Cloud Run (REQUIRED).
- **PR8b:** Telegram bot with basic chat flow (REQUIRED).
- **PR1-6:** Database, RAG, sessions, lead capture, landing page (REQUIRED).

**External:**

- **Resend API:** Email delivery for leads (same as web).
- **Sentry:** Error monitoring (optional but recommended).
- **Analytics Service:** Posthog, GA4, or Vercel Analytics.

### Assumptions

- **Assumption:** Lead capture uses **inline keyboards** for lead type selection (Training vs Trip) and **conversational prompts** for field collection.
- **Assumption:** Lead form fields match web requirements: name, email, phone (optional), agency/destination, message (optional).
- **Assumption:** Lead delivery uses same email template as web, with additional Telegram-specific fields (username, user ID).
- **Assumption:** Users can `/cancel` lead capture flow at any point to return to normal chat.
- **Assumption:** Error monitoring captures exceptions and sends to Sentry (or Cloud Logging if Sentry not available).
- **Assumption:** Analytics tracks key events: session starts, messages sent, lead submissions, command usage.
- **Assumption:** Production deployment includes smoke tests for critical Telegram flows.

---

## 2. Complexity & Fit

### Classification

**Single-PR**

### Rationale

- **Focused Scope:** Lead capture + monitoring/analytics (two related concerns).
- **Builds on PR8b:** Existing bot infrastructure in place, adding features on top.
- **Limited Risk:** Lead capture is isolated flow; can be disabled via feature flag if needed.
- **Independently Testable:** Lead capture flow can be tested end-to-end without affecting basic chat.
- **Production Hardening:** Error monitoring and analytics are cross-cutting but straightforward to add.
- **Estimated Scope:** ~10-12 files (lead capture handler, state manager, analytics, monitoring, tests).

---

## 3. Full-Stack Impact

### Frontend

**Landing Page Update (Optional):**

- `/app/page.tsx` or `/app/telegram/page.tsx`:
  - Mention lead capture capability: "Ask DovvyBuddy to connect you with dive shops for training or trip planning."
  - No structural changes needed; informational only.

**No other frontend changes.**

### Backend

**Telegram Bot Service Updates:**

Extend existing `src/telegram/` service:

```
src/telegram/
├── handlers/
│   ├── lead-capture-handler.ts    # NEW: Manages lead capture flow
│   ├── callback-handler.ts        # NEW: Handles inline keyboard button clicks
│   └── [existing handlers]
├── services/
│   ├── state-manager.ts           # NEW: Manages conversational state for lead capture
│   ├── lead-service.ts            # NEW: Captures and delivers leads
│   └── [existing services]
├── utils/
│   ├── analytics.ts               # NEW: Analytics event tracking
│   └── [existing utils]
├── config/
│   ├── lead-config.ts             # NEW: Lead capture configuration
│   └── [existing config]
└── [existing files]
```

**Key Components:**

1. **Lead Capture Handler** (`lead-capture-handler.ts`):
   - Detects lead intent from message (keywords: "certified", "book", "trip", "connect", "dive shop").
   - Explicit commands: `/training` or `/trip` to start lead capture directly.
   - Shows inline keyboard with buttons: "🎓 Get Certified" and "🌊 Plan a Trip".
   - Transitions to field collection flow based on button selection.
   - Validates collected data before submission.
   - Calls agent service `POST /agent/lead` with lead payload.
   - Sends confirmation message: "Thanks! We'll connect you with a partner dive shop soon. 🤿"

2. **Callback Handler** (`callback-handler.ts`):
   - Handles inline keyboard button callbacks from Telegram.
   - Routes to appropriate handler (lead type selection, confirmation buttons).
   - Answers callback query (prevents loading spinner in Telegram).
   - Updates state manager based on button clicked.

3. **State Manager** (`state-manager.ts`):
   - Manages multi-step conversational state for lead capture.
   - States: `IDLE → LEAD_TYPE_SELECTION → COLLECTING_NAME → COLLECTING_EMAIL → COLLECTING_PHONE → COLLECTING_AGENCY_OR_DESTINATION → COLLECTING_MESSAGE → LEAD_SUBMITTED`.
   - Stores state in-memory with TTL (10 minutes for abandoned flows).
   - Per-user state keyed by Telegram user ID.
   - Methods:
     - `setState(userId, state, data)`: Set current state and associated data.
     - `getState(userId)`: Get current state.
     - `clearState(userId)`: Clear state (on `/cancel` or completion).

4. **Lead Service** (`lead-service.ts`):
   - `captureLead(leadData, telegramContext)`: Validates and saves lead to database.
   - `deliverLead(leadId)`: Sends lead notification email via Resend API.
   - Email template includes Telegram-specific fields:
     - Telegram username (`@username`)
     - Telegram user ID (for reference)
     - Telegram first name / last name
   - Same email recipient as web leads (`LEAD_EMAIL_TO`).

5. **Analytics** (`analytics.ts`):
   - Track events to analytics provider (Posthog, GA4, or custom).
   - Events:
     - `telegram_session_start`: New session created.
     - `telegram_message_sent`: User sent message.
     - `telegram_command_used`: User used command (start, help, newchat, etc.).
     - `telegram_lead_intent_detected`: Lead capture flow triggered.
     - `telegram_lead_type_selected`: User selected Training or Trip.
     - `telegram_lead_submitted`: Lead successfully captured.
     - `telegram_lead_abandoned`: User cancelled or timed out during lead capture.
   - Async/fire-and-forget (doesn't block response).

6. **Error Monitoring** (integrate into existing error handler):
   - Sentry SDK integration (optional).
   - Capture exceptions with context:
     - Telegram user ID
     - Session ID
     - Current state (if in lead capture flow)
     - Message text (sanitized)
   - Send to Sentry or Cloud Logging.
   - Set up alerts for error rate thresholds.

**Agent Service (No Changes):**

Agent service already has `POST /agent/lead` endpoint from PR4. No modifications needed, but will receive `channelType='telegram'` and `channelMetadata` with Telegram user info.

**Database (Schema Update):**

Update `leads` table to support Telegram leads (if not done in PR8a/7b):

```sql
ALTER TABLE leads ADD COLUMN channel_type VARCHAR(20) DEFAULT 'web';
ALTER TABLE leads ADD COLUMN channel_metadata JSONB;
UPDATE leads SET channel_type='web' WHERE channel_type IS NULL;
CREATE INDEX idx_leads_channel_type ON leads(channel_type);
```

### Data

**Migrations:**

- `004_add_channel_support_to_leads.sql`:
  - Add `channel_type` column (varchar, default 'web').
  - Add `channel_metadata` column (JSONB, stores Telegram user info).
  - Backfill existing leads with `channel_type='web'`.
  - Create index on `channel_type` for filtering.

**Lead Data for Telegram:**

Training Lead:

```json
{
  "type": "training",
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890", // optional
    "agency": "PADI", // or "SSI" or "No preference"
    "level": "Open Water", // or "Advanced"
    "location": "Cozumel", // optional
    "message": "..." // optional
  },
  "channelType": "telegram",
  "channelMetadata": {
    "telegram_user_id": "123456789",
    "telegram_username": "johndoe",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

Trip Lead:

```json
{
  "type": "trip",
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890", // optional
    "destination": "Cozumel",
    "dates": "March 2026", // flexible text
    "certification_level": "Open Water",
    "dive_count": "20", // optional
    "interests": "Wreck diving", // optional
    "message": "..." // optional
  },
  "channelType": "telegram",
  "channelMetadata": {
    "telegram_user_id": "123456789",
    "telegram_username": "johndoe",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### Infra / Config

**Environment Variables (Telegram Bot Service - New/Updated):**

```
# Error Monitoring
SENTRY_DSN=<Sentry DSN>
SENTRY_ENVIRONMENT=production|staging

# Analytics
ANALYTICS_PROVIDER=posthog|ga4|vercel|none
POSTHOG_API_KEY=<Posthog key>
POSTHOG_HOST=<Posthog host, default: https://app.posthog.com>
GA_TRACKING_ID=<GA4 measurement ID>

# Lead Capture (reuse from agent service)
LEAD_EMAIL_TO=<partner email>
RESEND_API_KEY=<Resend key>

# Feature Flags
LEAD_CAPTURE_ENABLED=true|false

# State Management
STATE_TTL_MINUTES=10
```

**CI/CD Updates:**

Update `.github/workflows/deploy.yml`:

1. Deploy agent service (if changed)
2. Deploy Telegram bot service with new env vars
3. Run integration tests (including lead capture flow)
4. Smoke test: Send message, trigger lead capture, verify email delivery
5. Deploy Next.js (if changed)

---

## 4. Implementation Details

### Phase 1: Lead Capture Flow Design

**Tasks:**

1. Design inline keyboard layout:
   - Lead type selection: Two buttons ("🎓 Get Certified" | "🌊 Plan a Trip")
   - Confirmation buttons: ("✅ Submit" | "❌ Cancel")

2. Define conversational prompts for each lead type:

   **Training Lead Prompts:**
   - "Great! Let's connect you with a dive shop. First, what's your name?"
   - "Thanks! What's your email address?"
   - "And your phone number? (Optional - type 'skip' to skip)"
   - "Which agency do you prefer? (PADI, SSI, or 'No preference')"
   - "What certification level are you interested in? (Open Water, Advanced, or 'Not sure')"
   - "Where would you like to get certified? (City or region)"
   - "Any additional details? (Optional - type 'skip' to skip)"
   - [Show confirmation with all details]
   - "Perfect! I'll send your request to our partner dive shops. 🤿"

   **Trip Lead Prompts:**
   - "Awesome! Let's plan your dive trip. What's your name?"
   - "What's your email address?"
   - "Phone number? (Optional - type 'skip' to skip)"
   - "Which destination are you interested in?"
   - "When are you planning to dive? (Month/season is fine)"
   - "What's your current certification level?"
   - "How many logged dives do you have? (Optional - type 'skip' to skip)"
   - "Any specific interests? (Wrecks, reefs, marine life, etc. - Optional)"
   - "Additional details? (Optional - type 'skip' to skip)"
   - [Show confirmation]
   - "Great! I'll connect you with dive operators in that area. 🌊"

3. Define state machine transitions:

   ```
   IDLE → [detect intent or /training or /trip] → LEAD_TYPE_SELECTION
   LEAD_TYPE_SELECTION → [click Training] → COLLECTING_NAME (training)
   LEAD_TYPE_SELECTION → [click Trip] → COLLECTING_NAME (trip)
   COLLECTING_NAME → [valid name] → COLLECTING_EMAIL
   COLLECTING_EMAIL → [valid email] → COLLECTING_PHONE
   COLLECTING_PHONE → [valid phone or skip] → COLLECTING_AGENCY_OR_DESTINATION
   COLLECTING_AGENCY_OR_DESTINATION → [valid input] → COLLECTING_MESSAGE
   COLLECTING_MESSAGE → [any input or skip] → CONFIRM
   CONFIRM → [click Submit] → LEAD_SUBMITTED → IDLE
   [any state] → [/cancel] → IDLE
   ```

4. Define validation rules:
   - Name: Non-empty, 2-100 characters
   - Email: Valid email format (regex)
   - Phone: Optional, E.164 format preferred or free text
   - Agency: "PADI" | "SSI" | "No preference" | free text
   - Destination: Non-empty string
   - Dates: Free text (no strict validation)
   - Certification level: "Open Water" | "Advanced" | "Rescue" | free text
   - Dive count: Optional, numeric or "skip"

**Files Created:**

- `src/telegram/docs/lead-capture-flow.md` (flow documentation)
- `src/telegram/config/lead-config.ts` (prompts and validation rules)

### Phase 2: Implement State Manager

**Tasks:**

1. Create `state-manager.ts`:
   - In-memory Map: `userId -> { state, data, timestamp }`
   - TTL cleanup: Remove states older than 10 minutes
   - Methods:
     - `setState(userId, state, data?)`
     - `getState(userId) => { state, data } | null`
     - `updateData(userId, key, value)`
     - `clearState(userId)`
   - Background job to clean up expired states (every 1 minute)

2. Add state types:

   ```typescript
   type LeadCaptureState =
     | 'IDLE'
     | 'LEAD_TYPE_SELECTION'
     | 'COLLECTING_NAME'
     | 'COLLECTING_EMAIL'
     | 'COLLECTING_PHONE'
     | 'COLLECTING_AGENCY_OR_DESTINATION'
     | 'COLLECTING_ADDITIONAL'
     | 'COLLECTING_MESSAGE'
     | 'CONFIRM'
     | 'LEAD_SUBMITTED'

   interface StateData {
     leadType?: 'training' | 'trip'
     name?: string
     email?: string
     phone?: string
     agency?: string
     destination?: string
     dates?: string
     certificationLevel?: string
     diveCount?: string
     interests?: string
     message?: string
   }
   ```

**Files Created:**

- `src/telegram/services/state-manager.ts`
- `src/telegram/types/lead-capture.ts`

### Phase 3: Implement Lead Capture Handler

**Tasks:**

1. **Lead Intent Detection** (`lead-capture-handler.ts`):
   - Keywords: "certified", "certification", "course", "training", "book", "trip", "plan", "dive shop", "connect", "help me find"
   - Trigger inline keyboard on intent detected or explicit commands

2. **Callback Handler** (`callback-handler.ts`):
   - Handle `training_selected` and `trip_selected` callbacks
   - Answer callback query (prevents spinner)
   - Transition to `COLLECTING_NAME` state
   - Send first prompt

3. **Field Collection Logic** (in `message-handler.ts` - extend existing):
   - Check if user is in lead capture flow (`getState(userId)`)
   - If in flow, route to lead capture processor instead of agent service
   - Validate input based on current state
   - If valid, store data and transition to next state
   - If invalid, show error and re-prompt
   - If user types `/cancel`, clear state and return to normal chat

4. **Confirmation Step**:
   - After all fields collected, show summary:

     ```
     Here's what I have:
     Name: John Doe
     Email: john@example.com
     Phone: +1234567890
     Agency: PADI

     Is this correct?
     [✅ Submit] [❌ Cancel]
     ```

   - On "Submit" callback, call lead service
   - On "Cancel" callback, clear state

5. **Lead Submission**:
   - Call agent service `POST /agent/lead`
   - Include `channelType='telegram'` and `channelMetadata`
   - On success, send confirmation message
   - Clear state
   - Track analytics event

**Files Created:**

- `src/telegram/handlers/lead-capture-handler.ts`
- `src/telegram/handlers/callback-handler.ts`

**Files Modified:**

- `src/telegram/handlers/message-handler.ts` (add lead capture routing)
- `src/telegram/bot.ts` (register callback handler)

### Phase 4: Implement Lead Service

**Tasks:**

1. Create `lead-service.ts`:
   - `validateLeadData(data)`: Validate required fields
   - `captureLead(leadData, telegramContext)`: Save to database via agent service
   - `formatLeadEmail(lead)`: Format email template with Telegram context

2. Update email template (in agent service if needed):
   - Add Telegram user info section:
     ```
     Channel: Telegram
     Telegram User: @johndoe (ID: 123456789)
     Name: John Doe
     ```

3. Error handling:
   - If agent service call fails, show user-friendly error: "Sorry, something went wrong. Please try again or contact us at [email]."
   - Log error with full context to Sentry

**Files Created:**

- `src/telegram/services/lead-service.ts`

### Phase 5: Analytics & Error Monitoring

**Tasks:**

1. **Analytics Integration** (`analytics.ts`):
   - Abstract analytics provider (Posthog, GA4, custom)
   - Methods:
     - `trackEvent(eventName, properties)`
     - `identify(userId, traits)` (optional)
   - Events to track:
     - `telegram_session_start`
     - `telegram_message_sent`
     - `telegram_command_used` (props: command)
     - `telegram_lead_intent_detected`
     - `telegram_lead_type_selected` (props: type)
     - `telegram_lead_field_collected` (props: field)
     - `telegram_lead_submitted` (props: type)
     - `telegram_lead_abandoned` (props: lastState)
   - Async/non-blocking (fire and forget)

2. **Sentry Integration** (in `error-handler.ts`):
   - Initialize Sentry SDK with DSN
   - Capture exceptions with context:
     - User ID (Telegram user ID)
     - Session ID
     - Current state (if in lead capture)
     - Message text (sanitized - remove PII)
   - Set tags: `channel: telegram`, `environment: production`
   - Breadcrumbs for debugging

3. **Structured Logging** (extend existing logger):
   - Log key events with context:
     - Lead capture started
     - Field collected
     - Validation error
     - Lead submitted
     - Lead abandoned
   - Include: timestamp, user ID, session ID, state, event

**Files Created:**

- `src/telegram/utils/analytics.ts`

**Files Modified:**

- `src/telegram/handlers/error-handler.ts` (add Sentry)
- `src/telegram/utils/logger.ts` (enhance with lead capture events)

### Phase 6: Testing & Smoke Tests

**Tasks:**

1. **Unit Tests**:
   - State manager: State transitions, TTL cleanup
   - Lead capture handler: Intent detection, field validation
   - Lead service: Data validation, email formatting
   - Analytics: Event tracking (mock provider)

2. **Integration Tests**:
   - End-to-end lead capture flow (mocked Telegram API and agent service):
     - User sends "I want to get certified"
     - Bot shows inline keyboard
     - User clicks "Training"
     - User completes all prompts
     - Lead submitted successfully
   - Test validation errors (invalid email, etc.)
   - Test `/cancel` at various states
   - Test abandoned flow (timeout)

3. **Smoke Tests** (manual or automated):
   - Send message: "help me get certified" → Keyboard appears
   - Complete training lead flow → Email received
   - Complete trip lead flow → Email received
   - Test `/cancel` mid-flow → Returns to normal chat
   - Test invalid input → Error message and re-prompt

**Files Created:**

- `src/telegram/tests/services/state-manager.test.ts`
- `src/telegram/tests/handlers/lead-capture-handler.test.ts`
- `src/telegram/tests/services/lead-service.test.ts`
- `tests/integration/telegram-lead-capture.test.ts`
- `tests/smoke/telegram-smoke.test.ts`

### Phase 7: Documentation & Deployment

**Tasks:**

1. Update documentation:
   - Telegram bot README with lead capture instructions
   - Lead capture flow diagram
   - Environment variables reference
   - Troubleshooting guide

2. Deploy to staging:
   - Set environment variables (Sentry DSN, analytics keys)
   - Deploy Telegram bot service
   - Run smoke tests

3. Deploy to production:
   - Update production environment variables
   - Deploy with zero-downtime (new revision)
   - Monitor for 24 hours

**Files Updated:**

- `src/telegram/README.md`
- `docs/deployment/telegram-bot.md`

---

## 5. Testing Strategy

### Unit Tests

**State Manager:**

- Set and get state works
- State data updates correctly
- State cleared on clearState()
- TTL cleanup removes expired states
- Concurrent access handled safely

**Lead Capture Handler:**

- Intent detection triggers keyboard
- Field validation accepts valid input
- Field validation rejects invalid input
- State transitions work correctly
- `/cancel` clears state and returns to chat

**Lead Service:**

- Valid lead data passes validation
- Invalid lead data rejected with clear error
- Lead saved to database correctly
- Email formatted with Telegram context

**Callback Handler:**

- Button clicks trigger correct state transitions
- Callback queries answered (prevents spinner)
- Invalid callbacks handled gracefully

**Analytics:**

- Events tracked to provider (mocked)
- Async/non-blocking behavior
- Errors don't crash bot

**Test Files:**

- `src/telegram/tests/services/state-manager.test.ts`
- `src/telegram/tests/handlers/lead-capture-handler.test.ts`
- `src/telegram/tests/handlers/callback-handler.test.ts`
- `src/telegram/tests/services/lead-service.test.ts`
- `src/telegram/tests/utils/analytics.test.ts`

### Integration Tests

**End-to-End Lead Capture Flow:**

1. **Training Lead Flow:**
   - Send message: "I want to get certified"
   - Verify inline keyboard sent
   - Click "Training" button
   - Verify prompt for name
   - Send name: "John Doe"
   - Verify prompt for email
   - Send email: "john@example.com"
   - Verify prompt for phone
   - Send "skip"
   - Verify prompt for agency
   - Send "PADI"
   - Verify confirmation message with summary
   - Click "Submit"
   - Verify lead saved to database
   - Verify confirmation message sent

2. **Trip Lead Flow:**
   - Similar to training, test all fields

3. **Validation Errors:**
   - Send invalid email → Error message and re-prompt
   - Send very long name (>100 chars) → Error and re-prompt

4. **Cancel Flow:**
   - Start lead capture
   - Collect 2 fields
   - Send `/cancel`
   - Verify state cleared
   - Send normal message → Bot responds normally (not in lead flow)

5. **Abandoned Flow:**
   - Start lead capture
   - Wait 11 minutes (past TTL)
   - Send next field
   - Verify state cleared (user not in flow anymore)

**Test Files:**

- `tests/integration/telegram-lead-capture.test.ts`

### Manual Testing Checklist

**Lead Capture Flow:**

- [ ] Send "I want to get certified" → Inline keyboard appears
- [ ] Click "Training" → First prompt appears
- [ ] Complete all prompts with valid data → Lead submitted successfully
- [ ] Complete all prompts with "skip" for optional fields → Lead submitted
- [ ] Send invalid email → Error message and re-prompt
- [ ] Send `/cancel` mid-flow → Returns to normal chat
- [ ] Start flow but don't complete → Wait 11 minutes → State cleared
- [ ] Click "Trip" → Trip-specific prompts appear
- [ ] Complete trip lead flow → Lead submitted successfully

**Email Delivery:**

- [ ] Training lead email received with Telegram user info
- [ ] Trip lead email received with Telegram user info
- [ ] Email includes all captured fields
- [ ] Email formatted correctly (no broken markdown)

**Database Verification:**

- [ ] Query leads table → Telegram leads exist with channel_type='telegram'
- [ ] Verify channel_metadata includes Telegram user info
- [ ] Check timestamps are correct

**Analytics Tracking:**

- [ ] Session start tracked
- [ ] Lead intent detected tracked
- [ ] Lead type selected tracked
- [ ] Lead submitted tracked
- [ ] Verify events appear in analytics dashboard (Posthog/GA4)

**Error Monitoring:**

- [ ] Trigger error (e.g., disconnect agent service) → Error captured in Sentry
- [ ] Verify error includes context (user ID, state, message)
- [ ] User receives friendly error message (not stack trace)

**Edge Cases:**

- [ ] Send very long message (>4096 chars) during lead capture → Handled
- [ ] Send emoji in name field → Accepted
- [ ] Send special characters in fields → Handled correctly
- [ ] Multiple users submit leads simultaneously → No conflicts

---

## 6. Verification

### Commands

**Development:**

```bash
# Run unit tests
cd src/telegram
pnpm test

# Run integration tests
pnpm test:integration

# Run tests in watch mode
pnpm test:watch

# Typecheck
pnpm typecheck

# Lint
pnpm lint
```

**Deployment:**

```bash
# Deploy to staging
gcloud run deploy dovvybuddy-telegram-bot \
  --source src/telegram \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN_STAGING,SENTRY_ENVIRONMENT=staging,..."

# Run smoke tests against staging
pnpm test:smoke:staging

# Deploy to production
gcloud run deploy dovvybuddy-telegram-bot \
  --source src/telegram \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN,SENTRY_ENVIRONMENT=production,..."

# Run smoke tests against production
pnpm test:smoke:production
```

**Database Verification:**

```sql
-- Check Telegram leads
SELECT
  id,
  type,
  channel_type,
  channel_metadata->>'telegram_username' as telegram_user,
  diver_profile->>'name' as name,
  diver_profile->>'email' as email,
  created_at
FROM leads
WHERE channel_type = 'telegram'
ORDER BY created_at DESC
LIMIT 10;

-- Count leads by channel
SELECT channel_type, COUNT(*)
FROM leads
GROUP BY channel_type;

-- Check lead submission rate (last 24h)
SELECT
  DATE_TRUNC('hour', created_at) as hour,
  COUNT(*) as leads
FROM leads
WHERE channel_type = 'telegram'
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour;
```

**Analytics Verification:**

```bash
# Posthog (via API or dashboard)
# Check events for telegram_lead_submitted

# GA4 (via dashboard)
# Check custom events for telegram_lead_submitted

# Or check logs
gcloud run logs read dovvybuddy-telegram-bot \
  --filter="textPayload=~'analytics.*telegram_lead'" \
  --limit 20
```

**Error Monitoring:**

```bash
# Sentry (via dashboard)
# Filter by tag: channel:telegram

# Or check Cloud Logging
gcloud run logs read dovvybuddy-telegram-bot \
  --filter="severity>=ERROR" \
  --limit 20
```

### Acceptance Criteria

**Functional:**

- ✅ User can trigger lead capture via keywords or commands
- ✅ Inline keyboard displays with Training and Trip options
- ✅ Conversational flow collects all required fields
- ✅ Validation rejects invalid inputs with helpful error messages
- ✅ Optional fields can be skipped
- ✅ Confirmation summary shows all collected data
- ✅ Lead saved to database with channel_type='telegram'
- ✅ Lead delivered via email to partner shop
- ✅ Telegram user info included in lead (username, user ID)
- ✅ User receives confirmation message after submission
- ✅ `/cancel` command exits lead capture flow at any point
- ✅ Abandoned flows cleaned up after TTL (10 minutes)

**Non-Functional:**

- ✅ Lead capture flow completes in < 2 minutes (user time)
- ✅ Response time for each step < 3 seconds
- ✅ No data loss (all fields stored correctly)
- ✅ Error rate < 1% for lead submissions
- ✅ State management handles concurrent users (no conflicts)

**Monitoring & Analytics:**

- ✅ Analytics events tracked for all lead capture steps
- ✅ Sentry captures errors with full context
- ✅ Structured logs include lead capture events
- ✅ Dashboard shows Telegram lead volume and conversion rate
- ✅ Alerts configured for error rate > 5%

**Testing:**

- ✅ Unit tests pass (state manager, handlers, services)
- ✅ Integration tests pass (end-to-end flow)
- ✅ Manual testing checklist complete
- ✅ Smoke tests pass in staging and production
- ✅ No regressions in basic chat functionality

**Documentation:**

- ✅ Lead capture flow documented with diagrams
- ✅ README updated with lead capture usage instructions
- ✅ Environment variables documented
- ✅ Troubleshooting guide includes common lead capture issues

---

## 7. Rollback Plan

### Feature Flag Strategy

Add `LEAD_CAPTURE_ENABLED` environment variable:

```typescript
// src/telegram/config/lead-config.ts
export const LEAD_CAPTURE_ENABLED = process.env.LEAD_CAPTURE_ENABLED !== 'false'

// In lead-capture-handler.ts
if (!LEAD_CAPTURE_ENABLED) {
  return // Don't trigger lead capture flow
}
```

When disabled, bot responds with: "Lead capture is temporarily unavailable. Please visit our website to connect with dive shops."

### Revert Strategy

**Option 1: Disable via Feature Flag (Fast - 2 minutes)**

1. Set `LEAD_CAPTURE_ENABLED=false` in Cloud Run environment
2. Redeploy Telegram bot service
3. Lead capture keywords/commands won't trigger flow
4. Basic chat continues to work

**Option 2: Revert Deployment (Medium - 5 minutes)**

1. Revert to previous Cloud Run revision:
   ```bash
   gcloud run services update-traffic dovvybuddy-telegram-bot \
     --to-revisions=<previous-revision>=100
   ```
2. Lead capture functionality removed
3. Basic chat from PR8b restored

**Option 3: Full Rollback (Slower - 10 minutes)**

1. Revert git branch to PR8b state
2. Rebuild and redeploy Telegram bot
3. Rollback database migration (if needed):
   ```sql
   ALTER TABLE leads DROP COLUMN channel_type;
   ALTER TABLE leads DROP COLUMN channel_metadata;
   ```

**Data Considerations:**

- Leads already captured remain in database (safe)
- In-flight lead capture flows will be cleared (users may lose progress)
- Email delivery continues for any leads submitted before rollback

---

## 8. Dependencies

### Upstream

- **PR8a:** Agent service extracted and deployed (REQUIRED)
- **PR8b:** Telegram bot with basic chat flow (REQUIRED)
- **PR1-6:** Database, RAG, sessions, lead capture, landing page (REQUIRED)

### External

- **Resend API:** Email delivery (already configured from PR4)
- **Sentry:** Error monitoring (optional but recommended)
- **Analytics Provider:** Posthog, GA4, or Vercel Analytics

### Parallel Work

- None. PR8c completes V1.1 Telegram integration.

---

## 9. Risks & Mitigations

### Risk: Conversational State Management Complexity

**Impact:** State machine bugs could cause users to get stuck in lead capture flow or lose data.

**Mitigation:**

- Comprehensive unit tests for all state transitions
- TTL ensures abandoned flows are cleaned up
- `/cancel` command always available as escape hatch
- State manager logs all transitions for debugging
- Monitor "abandoned lead" events in analytics
- If issues persist, add Redis for more robust state persistence

---

### Risk: User Confusion in Conversational Flow

**Impact:** Users may not understand what input is expected, leading to frustration and abandoned leads.

**Mitigation:**

- Clear prompts with examples: "What's your email? (e.g., john@example.com)"
- Allow flexible input (e.g., "No preference", "Not sure", "skip")
- Show helpful error messages: "Please enter a valid email like john@example.com"
- Allow `/cancel` at any time
- Track abandonment rate in analytics to identify problem steps
- Iterate on prompts based on user feedback

---

### Risk: Email Deliverability for Telegram Leads

**Impact:** Emails with Telegram user info might be flagged as spam or look suspicious to partner shops.

**Mitigation:**

- Test email delivery to multiple providers (Gmail, Outlook, etc.)
- Use same email template as web, just add Telegram section
- Include clear explanation: "This lead came from our Telegram bot"
- Monitor email bounce rate and spam reports
- Provide fallback: If email fails, log lead to database for manual follow-up

---

### Risk: State Loss on Service Restart

**Impact:** If Cloud Run instance restarts, in-memory state is lost, users lose progress in lead capture.

**Mitigation:**

- Accept this limitation for V1.1 (rare occurrence with Cloud Run min instances)
- Show friendly message if state lost: "Sorry, your session timed out. Let's start over."
- TTL is short (10 minutes), so impact is minimal
- Future: Migrate to Redis for persistent state if this becomes an issue
- Monitor service restart frequency

---

### Risk: Analytics Privacy Concerns

**Impact:** Tracking user events may raise privacy concerns, especially in Europe (GDPR).

**Mitigation:**

- Don't track PII in events (use hashed user IDs, not names/emails)
- Add privacy policy link in bot welcome message
- Allow users to opt-out (future enhancement)
- Use privacy-compliant analytics provider (Posthog with EU hosting)
- Anonymize IP addresses in analytics

---

### Risk: Lead Submission Rate Limits

**Impact:** Multiple users submitting leads simultaneously could overwhelm agent service or email provider.

**Mitigation:**

- Agent service already handles concurrent requests (PR8a)
- Resend has generous rate limits (100 emails/second)
- Implement queue if needed (defer to post-launch optimization)
- Monitor lead submission rate in analytics
- Set up alerts for unusual spikes (potential abuse)

---

## 10. Success Metrics

### Technical Metrics

- **Lead Capture Completion Rate:** > 60% (users who start lead capture complete it)
- **Lead Submission Time:** < 3 minutes average (from intent to submission)
- **Error Rate:** < 1% (lead capture flow failures)
- **State Abandonment Rate:** < 20% (users who start but don't complete)
- **Email Delivery Success Rate:** > 99% (leads successfully delivered)

### Business Metrics

- **Lead Volume:** Track daily/weekly Telegram leads
- **Lead Quality:** Partner shop feedback on Telegram leads vs web leads
- **Conversion Rate:** % of Telegram sessions that result in lead
- **Channel Mix:** Telegram leads as % of total leads

### Quality Metrics

- **Test Coverage:** > 85% for lead capture code
- **Bug Reports:** < 3 user-reported bugs in first week
- **User Feedback:** Positive sentiment from Telegram users
- **Partner Feedback:** Positive feedback on lead quality and context

### Engagement Metrics

- **Lead Intent Detection:** % of sessions where lead intent detected
- **Lead Type Preference:** Training vs Trip lead ratio
- **Repeat Users:** % of users who submit multiple leads (indicates trust)

---

## 11. Post-Deployment Tasks

**Immediate (Day 1):**

- [ ] Monitor lead submissions in real-time (database queries)
- [ ] Check email delivery for first few leads
- [ ] Verify analytics events appearing in dashboard
- [ ] Check Sentry for any exceptions
- [ ] Test lead capture flow manually (training and trip)
- [ ] Monitor state manager memory usage
- [ ] Verify logs show lead capture events with context

**Short-term (Week 1):**

- [ ] Analyze lead capture completion rate
- [ ] Identify drop-off points in flow (which prompts have high abandonment)
- [ ] Review user-reported issues (if any)
- [ ] Compare Telegram lead quality to web leads (partner feedback)
- [ ] Monitor email delivery success rate
- [ ] Track lead volume trends (daily growth)
- [ ] Review analytics events for anomalies

**Medium-term (Week 2-4):**

- [ ] Iterate on prompts based on abandonment data
- [ ] Optimize lead capture flow (remove unnecessary steps)
- [ ] Add FAQ command for lead capture: `/leadhelp`
- [ ] Consider inline keyboard for common field choices (agencies, cert levels)
- [ ] Evaluate need for Redis if state loss is occurring
- [ ] A/B test different prompt wording (if traffic is sufficient)
- [ ] Document lessons learned for future improvements

---

## 12. Documentation Updates

**Files to Create/Update:**

1. **Lead Capture Flow Documentation** (`src/telegram/docs/lead-capture-flow.md`):
   - State machine diagram
   - Prompt sequences for training and trip leads
   - Validation rules for each field
   - Error handling scenarios

2. **Telegram Bot README** (`src/telegram/README.md`):
   - Add "Lead Capture" section with usage instructions
   - Environment variables for Sentry and analytics
   - Troubleshooting lead capture issues

3. **Main README** (`README.md`):
   - Update features list to mention Telegram lead capture
   - Add metrics/analytics section

4. **Environment Variables** (`.env.example`):
   - Add Sentry and analytics variables:

     ```
     # Error Monitoring
     SENTRY_DSN=
     SENTRY_ENVIRONMENT=production

     # Analytics
     ANALYTICS_PROVIDER=posthog
     POSTHOG_API_KEY=
     POSTHOG_HOST=https://app.posthog.com

     # Feature Flags
     LEAD_CAPTURE_ENABLED=true
     ```

5. **Deployment Guide** (`docs/deployment/telegram-bot.md`):
   - Add lead capture deployment checklist
   - Monitoring and analytics setup
   - Troubleshooting lead capture issues

6. **User Guide** (Optional - `docs/guides/telegram-user-guide.md`):
   - How to use Telegram bot for lead capture
   - Example flows with screenshots
   - FAQ about lead capture

---

## 13. Timeline Estimate

**Estimated Duration:** 3-4 days (solo founder)

**Breakdown:**

- **Day 1 (6-8 hours):**
  - Design lead capture flow and prompts
  - Implement state manager
  - Write unit tests for state manager
  - Implement callback handler
  - Test state transitions

- **Day 2 (6-8 hours):**
  - Implement lead capture handler (intent detection)
  - Implement field collection logic
  - Add validation for each field
  - Implement confirmation step
  - Write unit tests for handlers

- **Day 3 (6-8 hours):**
  - Implement lead service
  - Integrate analytics tracking
  - Integrate Sentry error monitoring
  - Write integration tests (end-to-end flow)
  - Test validation and error cases

- **Day 4 (4-6 hours):**
  - Deploy to staging and run smoke tests
  - Fix any issues found
  - Deploy to production
  - Monitor for 4-6 hours
  - Write documentation
  - Create post-deployment checklist

**Potential Delays:**

- State machine complexity (add 2-4 hours)
- Prompt iteration and UX refinement (add 2-3 hours)
- Analytics integration issues (add 1-2 hours)
- Email template formatting (add 1-2 hours)

---

## 14. Future Considerations

### Redis for State Persistence

**Current:** In-memory state with TTL

**Future Option:** Redis for persistent state across restarts

**Trade-off:** Adds cost (~$20-30/month) and complexity but improves reliability

**Decision Point:** If state loss occurs more than once per week, migrate to Redis

---

### Inline Keyboards for Field Selection

**Current:** Text input for all fields

**Future Option:** Inline keyboards for agency, certification level, etc.

**Trade-off:** Faster UX but more complex state management

**Decision Point:** After analyzing field input patterns, add keyboards for most common values

---

### Photo Attachments in Leads

**Current:** Text-only leads

**Future Option:** Allow users to attach photos (certification card, dive log)

**Trade-off:** Adds complexity (file storage, image handling) but richer context

**Decision Point:** Defer to V2 based on partner shop feedback

---

### Lead Status Tracking

**Current:** Lead submitted, no follow-up

**Future Option:** Notify user when partner shop responds or lead is processed

**Trade-off:** Requires bidirectional communication and CRM integration

**Decision Point:** Defer to V2 with user accounts and notification system

---

### A/B Testing for Prompts

**Current:** Single prompt set for all users

**Future Option:** A/B test different prompt wording to optimize completion rate

**Trade-off:** Requires experimentation framework and sufficient traffic

**Decision Point:** Once Telegram traffic exceeds 100 leads/week, implement A/B testing

---

### Multi-Language Support for Leads

**Current:** English-only prompts

**Future Option:** Detect user language and show prompts in their language

**Trade-off:** Requires translation and localization effort

**Decision Point:** Defer to V2+ based on international user demand

---

## Summary

PR8c completes the Telegram integration (V1.1) by adding lead capture functionality with inline keyboards and conversational prompts, plus production hardening with error monitoring and analytics. This PR makes the Telegram channel fully feature-complete with the web interface.

**Key Deliverables:**

- ✅ Lead capture flow with inline keyboards and conversational prompts
- ✅ State management for multi-step flows
- ✅ Lead validation and submission to database
- ✅ Email delivery with Telegram user context
- ✅ Analytics tracking for all lead capture events
- ✅ Error monitoring with Sentry
- ✅ Comprehensive testing (unit + integration + smoke)
- ✅ Documentation and deployment guides

**Main Risks:**

- Conversational state management complexity (mitigated with tests and `/cancel` command)
- User confusion in prompts (mitigated with clear examples and error messages)
- State loss on restart (accepted for V1.1, migrate to Redis if needed)

**Estimated Timeline:** 3-4 days for solo founder (assuming PR8a and PR8b complete and stable).

**Success Criteria:**

- Lead capture completion rate > 60%
- Error rate < 1%
- Email delivery success > 99%
- Positive partner feedback on lead quality
