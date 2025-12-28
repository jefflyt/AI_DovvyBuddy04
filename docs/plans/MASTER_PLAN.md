# MASTER PLAN: DovvyBuddy (AI Diving Bot)

**Status:** Draft
**Based on:** DovvyBuddy-PSD-V6.2.md
**Date:** December 22, 2025

---

## 1. Product Summary

**Problem:** Prospective and recreational divers face confusion regarding certification pathways (PADI vs SSI), prerequisites, and trip planning. Existing information is often fragmented or sales-heavy.

**Target Users:**

1. Prospective New Divers (Non-certified, curious, fearful).
2. OW Divers seeking Advanced Certification.
3. Certified Divers planning trips (Secondary).

**Value Proposition:** A diver-first, agency-aware AI assistant that provides grounded, non-judgmental guidance, normalizes fears, and hands off qualified leads to partner shops without pretending to be an instructor.

**Core Features:**

- **Certification Navigator:** Explains pathways, compares agencies, clarifies prerequisites.
- **Confidence Building:** Normalizes common fears (mask clearing, depth) with factual info.
- **Trip Research:** RAG-based search for "covered" destinations/sites.
- **Lead Capture:** Collects context and sends qualified inquiries to partners.
- **Guest Sessions:** 24h ephemeral sessions, no user accounts.

**Key Constraints:**

- Information-only (no medical/safety advice).
- No direct booking.
- Guest-only (V1).
- English only.

---

## 2. Goals, Success Criteria, and Constraints

### Product Goals

- **G-01:** Reduce diver confusion regarding certification steps.
- **G-02:** Build confidence for new students.
- **G-03:** Generate qualified, context-rich leads for partners.
- **G-04:** Establish trust via grounded, safe answers.

### Success Criteria

- **MVP Usable:** Users can complete a chat session about "How to get certified" or "Where to dive in [Covered Destination]".
- **Technical Health:** CI pipeline passing (Lint/Typecheck/Test/Build) on every commit.
- **Lead Delivery:** System successfully captures and logs/emails a lead payload with required context.
- **Safety:** Bot refuses out-of-scope queries (medical, uncovered destinations, booking) correctly 95%+ of time.
- **Content Grounding:** RAG retrieval provides relevant context for certification and destination queries.
- **Session Persistence:** Guest sessions survive page refresh and expire after 24h.
- **Response Quality:** LLM responses include disclaimers where appropriate and do not invent facts.
- **Performance:** Chat responses return within 5 seconds under normal load.

### Constraints & Assumptions

- **Constraint:** Solo founder resources.
- **Constraint:** V1 is Web-only (Telegram deferred).
- **Constraint:** No user authentication (Guest sessions).
- **Assumption:** Content corpus will be small enough for simple vector search (Postgres/pgvector) without a dedicated vector DB service initially.
- **Assumption:** Traffic will be manageable on serverless tiers for V1.

---

## 3. Architecture & Technology Stack

### Frontend

- **Framework:** Next.js 14 (App Router).
- **Language:** TypeScript.
- **Styling:** Tailwind CSS (via global.css setup).
- **State Management:** React Server Components by default; Client Components with hooks for chat history and real-time interaction.
- **Routing:** File-system routing (`/app/page.tsx` for landing, `/app/chat/page.tsx` for chat interface).
- **Key Pages:**
  - Landing Page: Value proposition, CTA to start chat.
  - Chat Interface: Message thread, input field, "New Chat" button.
  - (Future) About/FAQ pages.

### Backend

- **Runtime:** Next.js API Routes (Serverless Functions) for V1 simplicity.
- **Agent Logic:** Google ADK (Agent Development Kit) patterns, potentially hosted within Next.js or as a sidecar service (Cloud Run) if complexity demands. _Decision: Start with Next.js API routes implementing the orchestration to keep deployment simple (Vercel), move to Cloud Run if ADK requires specific runtime environment not supported on Vercel._
- **API Style:** REST endpoints for chat and session management.
- **Key Endpoints:**
  - `POST /api/chat` — Accept user message, return assistant response.
  - `POST /api/session/new` — Create new session.
  - `GET /api/session/:id` — Retrieve session state.
  - `POST /api/lead` — Capture and deliver lead.
- **Orchestration Flow:**
  1. Receive user message.
  2. Retrieve session context from DB.
  3. Query RAG for relevant content chunks.
  4. Construct prompt with system instructions + context + history.
  5. Call LLM via ModelProvider.
  6. Update session history.
  7. Return response.

### Data

- **Database:** PostgreSQL (Neon or Supabase).
- **Vector Search:** pgvector extension on the same Postgres instance.
- **ORM:** Drizzle ORM (preferred for cold start performance and type safety).
- **Schema:**
  - **destinations:** `id`, `name`, `country`, `is_active`, `created_at`.
  - **dive_sites:** `id`, `destination_id`, `name`, `min_certification_level`, `min_logged_dives`, `difficulty_band`, `access_type`, `is_active`, `created_at`.
  - **leads:** `id`, `type` (training|trip), `diver_profile` (JSONB), `request_details` (JSONB), `created_at`.
  - **sessions:** `id`, `diver_profile` (JSONB), `conversation_history` (JSONB), `created_at`, `expires_at`.
  - **content_embeddings:** `id`, `content_path`, `chunk_text`, `embedding` (vector), `metadata` (JSONB), `created_at`.
- **Migrations:** Drizzle Kit with versioned SQL files in `src/db/migrations/`.
- **Seeding:** Initial seed script for 1 destination with 5-10 sites and 2-3 partner shops.

### Auth & Security

- **Authentication:** None (Guest access).
- **Session Handling:** Custom session ID (UUID) stored in HTTP-only cookie or LocalStorage, validated against DB. 24h expiry.
- **Security:** Input sanitization, rate limiting on API routes.

### Infrastructure & Deployment

- **Hosting:** Vercel (Frontend + API).
- **Database:** Managed Postgres (Neon/Supabase).
- **CI/CD:** GitHub Actions (Lint, Test, Build).
- **Observability:** Vercel Analytics / Logs.

### Cross-Cutting Concerns

- **Configuration:** Environment variables (.env) for:
  - `DATABASE_URL` (Postgres connection string)
  - `LLM_PROVIDER` (groq|gemini)
  - `GROQ_API_KEY` (Dev)
  - `GEMINI_API_KEY` (Prod)
  - `SESSION_SECRET` (Cookie signing)
  - `LEAD_WEBHOOK_URL` (Optional)
  - `RESEND_API_KEY` (Email delivery)
- **Error Handling:**
  - API routes return structured JSON errors with appropriate HTTP codes.
  - User-facing messages are friendly (no stack traces).
  - Server logs capture full context (session ID, user message, stack trace).
- **Logging:**
  - Structured logging with context (Winston or Pino).
  - Log levels: ERROR, WARN, INFO, DEBUG.
  - Key events: Session start, Lead capture, RAG retrieval, LLM calls, Errors.
- **Performance/Caching:**
  - Content embeddings pre-computed at build/deploy time.
  - Session state cached in-memory with DB fallback (optional Redis later).
  - Static assets served via Vercel CDN.

---

## 4. Project Phases

### Phase 1: Foundations & Data Layer

- **Objective:** Establish database, schema, and RAG content pipeline.
- **Scope:**
  - Postgres instance setup (Neon/Supabase).
  - Schema definition and migrations.
  - pgvector extension enabled.
  - Content ingestion script (Markdown → Chunks → Embeddings).
  - Seed script for initial destination/sites.
- **Dependencies:** None (starts from PR0 bootstrap).
- **Acceptance Criteria:**
  - Migrations run successfully locally and on hosted DB.
  - Sample content ingested and queryable via vector search.
  - Seed data visible in database tables.

### Phase 2: Core Logic & RAG

- **Objective:** Implement the "Brain" of the bot.
- **Scope:**
  - LLM Provider abstraction (Groq/Gemini with env switch).
  - RAG retrieval service (vector similarity search).
  - Session management service (Create, Get, Update).
  - Chat orchestration logic (Retrieve context → Build prompt → Call LLM → Save history).
  - System prompts with safety guardrails.
- **Dependencies:** Phase 1 (Database and content ready).
- **Acceptance Criteria:**
  - Unit tests for ModelProvider pass.
  - Mock chat endpoint returns contextually-aware responses.
  - Session persists across API calls.

### Phase 3: User Experience & Features

- **Objective:** Build the visible interface and interaction flows.
- **Scope:**
  - Chat UI components (Message bubbles, Input field, Typing indicator).
  - Lead capture inline flow (Training vs Trip forms).
  - Safety refusal UI (Clear messaging when out-of-scope).
  - "New Chat" button with session reset.
  - Session persistence (Cookie/LocalStorage).
  - Mobile-responsive design.
- **Dependencies:** Phase 2 (Backend API ready).
- **Acceptance Criteria:**
  - End-to-end chat flow works in browser.
  - Lead capture form submits and stores data.
  - Session survives page refresh.
  - UI is usable on mobile devices.

### Phase 4: Polish & Launch

- **Objective:** Production readiness.
- **Scope:**
  - Content review and refinement (Certification guides, Destination content).
  - E2E testing for critical paths (Certification inquiry, Lead capture, Trip research).
  - Analytics integration (Vercel Analytics or Posthog).
  - Error monitoring (Sentry).
  - Performance optimization (Response time, bundle size).
  - Production environment setup.
  - Launch checklist and smoke tests.
- **Dependencies:** Phase 3 (Feature-complete application).
- **Acceptance Criteria:**
  - All critical user flows tested end-to-end.
  - Analytics tracking key events (Session start, Lead submit).
  - Production deployment successful with monitoring active.
  - Performance targets met (5s response time).

---

## 5. Initial PR Breakdown (Near-Term Work)

_Note: PR0 (Bootstrap) is already complete._

### PR1: Database Schema & Migrations

- **Branch Name:** `feature/pr1-database-schema`
- **Goal:** Set up the persistent storage layer.
- **Scope:**
  - Install Drizzle ORM, pg driver, and pgvector type support.
  - Create Drizzle schema definitions in `src/db/schema/`:
    - `destinations.ts`
    - `dive_sites.ts`
    - `leads.ts`
    - `sessions.ts`
    - `content_embeddings.ts`
  - Configure Drizzle Kit for migrations (`drizzle.config.ts`).
  - Create initial migration files.
  - Add database connection utility (`src/db/client.ts`).
  - Create seed script (`src/db/seed.ts`) for 1 destination with 5-10 sites.
  - Update `.env.example` with `DATABASE_URL`.
- **Key Changes:**
  - **Backend:** Database schema, connection pooling, migration tooling.
  - **Data:** 5 core tables with pgvector support.
  - **Infra:** None (uses existing Postgres instance).
- **Testing Focus:**
  - Migration script runs without errors.
  - Seed script populates tables with valid data.
  - Connection utility successfully connects to DB.
- **Verification:**
  - Run `pnpm db:migrate` (command to be added in package.json).
  - Run `pnpm db:seed`.
  - Query database to verify tables and seed data exist.
  - Run `pnpm typecheck` to verify schema types.

### PR2: RAG Pipeline (Content Ingestion)

- **Branch Name:** `feature/pr2-rag-pipeline`
- **Goal:** Enable the bot to "read" the documentation.
- **Scope:**
  - Create `content/` directory structure:
    - `content/certifications/` (PADI/SSI guides)
    - `content/destinations/` (Destination overviews)
    - `content/dive-sites/` (Individual site details)
    - `content/safety/` (Safety reference docs)
  - Write initial curated Markdown content:
    - Open Water certification guide (PADI + SSI).
    - 1 destination overview.
    - 5-10 dive site descriptions.
  - Implement ingestion script (`scripts/ingest-content.ts`):
    - Read Markdown files recursively.
    - Split into chunks (semantic chunking, ~500-800 tokens).
    - Generate embeddings via Gemini/Groq API.
    - Store in `content_embeddings` table.
  - Create retrieval utility (`src/lib/rag/retrieval.ts`):
    - Function to query similar chunks by vector similarity.
    - Return top-k results with metadata.
  - Add `pnpm content:ingest` script to package.json.
- **Key Changes:**
  - **Backend:** Content chunking and embedding logic.
  - **Data:** Populated `content_embeddings` table.
  - **Infra:** None.
- **Testing Focus:**
  - Unit tests for chunking logic.
  - Integration test: Ingest sample file, query for similar content.
  - Verify retrieval returns relevant chunks.
- **Verification:**
  - Run `pnpm content:ingest`.
  - Query database: `SELECT COUNT(*) FROM content_embeddings;` returns >0.
  - Test retrieval function with sample query.
  - Run `pnpm test`.

### PR3: Model Provider & Session Logic

- **Branch Name:** `feature/pr3-model-provider-session`
- **Goal:** Connect to LLM and manage conversation state.
- **Scope:**
  - Implement `ModelProvider` interface (`src/lib/model-provider/`):
    - Base interface with `generateResponse()` method.
    - `GroqProvider` implementation.
    - `GeminiProvider` implementation.
    - Factory function based on `LLM_PROVIDER` env var.
  - Implement Session service (`src/lib/session/`):
    - `createSession()` — Generate UUID, store in DB.
    - `getSession()` — Retrieve by ID.
    - `updateSessionHistory()` — Append message to conversation_history JSONB.
    - `expireSession()` — Mark session as expired.
  - Create `/api/chat` endpoint:
    - Accept: `{ sessionId?, message }`.
    - If no sessionId, create new session.
    - Retrieve session context from DB.
    - Call RAG retrieval (mocked or real).
    - Construct prompt with system instructions + context + history.
    - Call LLM via ModelProvider.
    - Update session history.
    - Return: `{ sessionId, response, metadata }`.
  - Add system prompt templates (`src/lib/prompts/`):
    - Base system prompt with safety guardrails.
    - Certification Navigator prompt.
    - Trip Research prompt.
  - Update `.env.example` with `LLM_PROVIDER`, `GROQ_API_KEY`, `GEMINI_API_KEY`.
- **Key Changes:**
  - **Backend:** LLM integration, Session management, Chat orchestration.
  - **Data:** Session CRUD operations.
  - **Frontend:** None (API only).
- **Testing Focus:**
  - Unit tests for ModelProvider implementations.
  - Unit tests for Session service.
  - Integration test for `/api/chat` endpoint.
- **Verification:**
  - Run unit tests: `pnpm test`.
  - Curl request: `curl -X POST http://localhost:3000/api/chat -d '{"message":"What is Open Water certification?"}'`.
  - Verify response includes sessionId and relevant answer.
  - Query database to verify session stored.

### PR4: Lead Capture & Delivery

- **Branch Name:** `feature/pr4-lead-capture`
- **Goal:** Implement the business value conversion point.
- **Scope:**
  - Define Lead types in `src/types/lead.ts`:
    - Training Lead: `{ name, email, phone?, agency?, level?, location?, message? }`.
    - Trip Lead: `{ name, email, phone?, destination?, dates?, certification_level?, dive_count?, interests?, message? }`.
  - Create Lead service (`src/lib/lead/`):
    - `captureLead()` — Validate and save to DB.
    - `deliverLead()` — Send via email (Resend API) or webhook.
  - Create `/api/lead` endpoint:
    - Accept: `{ type, data }`.
    - Validate payload.
    - Save to `leads` table.
    - Trigger email/webhook delivery.
    - Return: `{ success, leadId }`.
  - Implement email template for lead notification.
  - Add lead delivery configuration in `.env.example`:
    - `RESEND_API_KEY`
    - `LEAD_EMAIL_TO`
    - `LEAD_WEBHOOK_URL` (optional)
- **Key Changes:**
  - **Backend:** Lead capture logic, Email integration.
  - **Data:** Writes to `leads` table.
  - **Infra:** Resend API integration.
- **Testing Focus:**
  - Unit tests for lead validation.
  - Integration test for `/api/lead` endpoint.
  - Mock email delivery in tests.
- **Verification:**
  - Curl request: `curl -X POST http://localhost:3000/api/lead -d '{"type":"training","data":{"name":"John Doe","email":"john@example.com"}}'`.
  - Verify lead saved to DB: `SELECT * FROM leads;`.
  - Verify email sent (check Resend logs or mock).
  - Run `pnpm test`.

### PR5: Chat Interface & Integration

- **Branch Name:** `feature/pr5-chat-interface`
- **Goal:** Connect UI to Backend.
- **Scope:**
  - Build Chat UI components (`src/components/chat/`):
    - `MessageList.tsx` — Display conversation thread.
    - `MessageBubble.tsx` — Individual message (user vs assistant).
    - `ChatInput.tsx` — Text input with send button.
    - `TypingIndicator.tsx` — Show while waiting for response.
    - `NewChatButton.tsx` — Clear session and start fresh.
    - `LeadCaptureForm.tsx` — Inline form for training/trip leads.
  - Update `/app/chat/page.tsx`:
    - Integrate chat components.
    - Manage local state (messages, loading, sessionId).
    - Call `/api/chat` on message send.
    - Handle session persistence (store sessionId in localStorage or cookie).
  - Implement "New Chat" functionality:
    - Clear sessionId from storage.
    - Reset message history in UI.
    - Create new session on next message.
  - Add session cookie handling:
    - Set HTTP-only cookie on session creation.
    - Read cookie on subsequent requests.
  - Add error handling UI:
    - Display user-friendly error messages.
    - Retry mechanism for failed requests.
  - Mobile-responsive styling (Tailwind).
- **Key Changes:**
  - **Frontend:** Full chat interface with session management.
  - **Backend:** Cookie handling in `/api/chat`.
  - **Data:** None.
- **Testing Focus:**
  - Manual testing of chat flow.
  - Session persistence across page refresh.
  - Lead form submission.
  - Mobile responsiveness.
- **Verification:**
  - Start dev server: `pnpm dev`.
  - Navigate to `/chat`.
  - Send message, verify response appears.
  - Refresh page, verify session persists.
  - Click "New Chat", verify session resets.
  - Submit lead form, verify success message.
  - Test on mobile viewport.

---

## 6. Risks, Trade-offs, and Open Questions

### Risks

- **LLM Hallucination:** Risk of bot inventing safety/medical advice. _Mitigation: Strict system prompts, RAG grounding, refusal patterns for out-of-scope queries, regular prompt testing._
- **RAG Quality:** Retrieval might miss relevant context or return irrelevant chunks. _Mitigation: Tuning chunk sizes and overlap, testing retrieval quality on sample queries, iterative content refinement._
- **Session Timeout:** 24h sessions may expire mid-conversation for some users. _Mitigation: Clear messaging about session expiry, graceful handling of expired sessions._
- **Email Deliverability:** Lead emails might be flagged as spam. _Mitigation: Use Resend with proper domain authentication (SPF/DKIM), test delivery to multiple providers._
- **Serverless Cold Starts:** Next.js API routes may have latency spikes. _Mitigation: Keep dependencies minimal, optimize bundle size, consider Edge Functions for critical paths._
- **Content Maintenance:** Outdated content may mislead users. _Mitigation: Content review process, version tracking in git, regular audits._

### Trade-offs

- **Guest-only vs Auth:** Simpler V1 but no cross-device history or personalization. _Decision: Acceptable for V1; auth deferred to V2 after proving diver wedge._
- **Embedded Vector vs Managed DB:** Simpler ops but potentially less scalable for large corpus. _Decision: Acceptable for V1 corpus size (<1000 chunks); migrate to dedicated vector DB if scaling requires._
- **Next.js API Routes vs Cloud Run:** Vercel deployment is simpler but may have timeout constraints for long RAG+LLM chains. _Decision: Start with Next.js; migrate agent logic to Cloud Run if timeouts become an issue._
- **Manual Content vs CMS:** Git-based content is simple but requires technical knowledge to update. _Decision: Acceptable for V1 with solo founder; consider CMS in V2 if non-technical content contributors join._

### Open Questions

- **Agent Runtime:** Will Next.js Serverless functions timeout for long RAG+LLM chains? _Contingency: Move to Edge functions or separate Cloud Run service if latency is high (>10s)._
- **Postgres Provider:** Neon vs Supabase for managed Postgres? _Decision criteria: Neon preferred for cold start performance and pgvector support; Supabase if realtime features needed later._
- **Content Scope:** Which destination to launch with first? _Decision: Choose destination with existing partner shop, high diver interest, and diverse site difficulty range._
- **Lead Delivery:** Email-only or webhook-first? _Decision: Start with email (simpler); add webhook if partner prefers CRM integration._
