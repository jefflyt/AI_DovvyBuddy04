# DovvyBuddy — MASTER PLAN

**Generated:** December 22, 2025  
**Based on:** DovvyBuddy PSD V6.2  
**Planning Agent Version:** Plan Mode (plan.prompt.md)

---

## 1. Product Summary (from PSD)

### Problem Statement

Prospective and recreational divers face confusion when navigating certification pathways (PADI vs SSI vs others), understanding prerequisites, managing diving anxieties, and researching dive destinations. Existing resources are fragmented, dive shop directories lack context, and there's no trusted AI assistant designed specifically for diver decision-making without pretending to be an instructor.

### Target Users

- **P-01:** Prospective new divers (non-certified, curious, may have tried Discover Scuba)
- **P-02:** Open Water divers seeking advanced certification (4–20 dives)
- **P-03:** Certified divers planning dive trips (OW/AOW, 10–100+ dives)
- **P-04:** Dive shop owners/managers (indirect, receive qualified leads)

### Value Proposition

DovvyBuddy is a diver-first AI assistant that reduces confusion and builds confidence through agency-aware certification guidance, fear normalization, curated destination research (covered set only), and warm handoffs to professional instructors/operators — without booking, medical advice, or invented facts.

### Core Features (Grouped Logically)

#### Group A — Certification Navigation

- Agency-aware certification pathways (PADI, SSI explicit; others via equivalency mapping)
- Prerequisite information (info-only, no medical judgments)
- Confidence/fear support (normalize common anxieties, explain training structure)

#### Group B — Trip Research

- Covered-set destination discovery (1 destination initially, expand cautiously)
- Dive site details with certification-level suitability (min_certification_level, min_logged_dives)
- Out-of-scope rejection (no booking, no uncovered destinations, no medical advice)

#### Group C — Lead Capture

- Session-based diver profile (agency, level, dive count, concerns, travel intent)
- Inline lead capture (training or trip inquiries)
- Automated delivery to partner shops/schools

#### Group D — RAG + Safety

- Retrieval over curated markdown content (certifications, destinations, safety)
- Hallucination guardrails (say unknown, provide ranges, no invention)
- Safety response mode (general info only, disclaimers, redirect to professionals)

### Non-Functional Requirements

| ID | Requirement |
|---|---|
| **NFR-01** | Response latency <2s for chat |
| **NFR-02** | Session-based memory (24hr inactivity timeout) |
| **NFR-03** | Mobile-responsive web UI (desktop + mobile web) |
| **NFR-04** | Basic observability (logging, error tracking) |
| **NFR-05** | No user authentication in V1 (guest-only) |
| **NFR-06** | English-only (defer multi-language) |

### Explicit Constraints

- Solo founder, full-stack responsibility
- Lean V1: 1 destination, 5–10 sites, 2–3 partners initially
- No booking, no dive logs, no marine life recognition in V1
- Google ADK for agent orchestration (PSD §6.1)
- Next.js + Vercel for web app (PSD §6.1)
- Postgres + pgvector for data + embeddings (PSD §6.2 Option A2)
- Model provider switch: Groq (dev) → Gemini (prod) (PSD §6.1A)
- RAG over versioned markdown content in Git (PSD §6.2)

---

## 2. Goals, Success Criteria, and Constraints

### Product Goals

#### Diver-Focused Goals (Primary)

- **G-01:** Reduce confusion for prospective divers explaining Open Water pathways (agency-aware, non-advisory)
- **G-02:** Help OW divers understand advanced-level options with clear tradeoffs
- **G-03:** Help travel divers shortlist covered destinations/sites matching constraints
- **G-04:** Build trust via grounded answers, explicit uncertainty, and safety disclaimers

#### Business Goals (Secondary)

- **G-05:** Convert high-intent conversations into qualified, context-rich leads for partners
- **G-06:** Prove diver-first wedge (repeat usage + lead conversion) in limited set before scaling

#### Timeframe Expectation

MVP usable within 6–8 weeks (Assumption based on solo founder + lean scope).

### Success Criteria

#### MVP Usable Criteria

1. A guest user can visit the web app, ask certification questions, and receive grounded, agency-aware answers (UC-00, UC-01, UC-02)
2. A guest user can ask about the covered destination, see 2–5 site suggestions, and submit a trip inquiry lead (UC-03, UC-04, UC-05)
3. Partner shops receive email notifications with lead context (name, email, certification level, dive count, inquiry type, message)
4. Out-of-scope requests (uncovered destinations, booking, medical advice) are politely refused with clear boundaries (UC-06, FR-05)

#### Technical Health Criteria

5. All core flows have unit test coverage (>70% for critical paths: session management, lead capture, RAG retrieval logic)
6. CI pipeline passes (lint, typecheck, tests) on every commit
7. Basic error tracking active (e.g., Sentry or Vercel Analytics error monitoring)
8. Response latency monitored (<2s p95 for chat interactions)

### Constraints & Assumptions

#### Constraints (from PSD)

- **C-01:** Guest-only, session-based (no user accounts in V1)
- **C-02:** 1 destination initially; add 2nd only after stability (≥5 leads/week, 0 critical bugs, partner satisfaction)
- **C-03:** RAG content must be versioned in Git (curated markdown)
- **C-04:** Agent service (Google ADK) deployment on Google Cloud Run (separate from Next.js web app)
- **C-05:** No booking flow, no dive logs, no payments in V1

#### Assumptions (Explicit)

- **Assumption A-01 (Scale):** Initial traffic <1000 sessions/week; single Cloud Run instance + Vercel deployment sufficient for 6 months
- **Assumption A-02 (Agent Service Repo):** The Google ADK agent service will be developed in a separate repository or monorepo workspace (not in the Next.js repo). This plan focuses on the Next.js web app only; agent service integration is via HTTPS API calls.
- **Assumption A-03 (Content Availability):** Curated markdown content (certifications, 1 destination, safety docs) will be written/curated in parallel with technical development and available by Phase 2 completion.

---

## 3. Architecture & Technology Stack

### 1) Frontend

#### Framework

Next.js 14+ (App Router) with React 18+ and TypeScript

#### Routing Approach

- App Router file-based routing
- Server Components by default for static/marketing pages
- Client Components for interactive chat UI

#### High-Level Structure

- `app/page.tsx` — Landing page (marketing, value prop, CTA to chat)
- `app/chat/page.tsx` — Chat interface (main app)
- `app/legal/privacy/page.tsx`, `terms/page.tsx` — Legal pages
- `components/` — Reusable React components (ChatInterface, Header, Footer, MessageBubble, LeadForm)
- `lib/` — Client utilities (API client, session helpers, formatting)

#### State Management

- React Context for session state (diver profile, conversation history within session)
- No heavy state library needed (Zustand or Redux overkill for V1)

#### Styling

Tailwind CSS for utility-first styling + responsive design

#### Justification

Next.js App Router provides modern React patterns, Vercel deployment simplicity, and built-in API routes for lead capture. Tailwind ensures rapid UI iteration for solo founder. React Context sufficient for V1 session state (defer Redux/Zustand until V2 if needed for complex state management).

### 2) Backend

#### Where Backend Lives

Hybrid architecture (PSD §6.1 Architecture Option 1):

- **Next.js API Routes** (`src/frontend/app/api/`) handle:
  - Lead submission (POST `/api/leads`)
  - Session management helpers (GET/POST `/api/session`)
- **External Agent Service** (Google ADK on Cloud Run) handles:
  - Chat orchestration (RAG retrieval, safety policies, model calls)
  - Exposed via POST `/chat` endpoint (separate service, called from Next.js `/api/chat` proxy route)

#### Framework/Runtime

- **Next.js API Routes:** Node.js runtime (Vercel Edge Runtime optional for future optimization)
- **Agent Service:** Python (Google ADK is Python-based) on Cloud Run

#### Model Provider Strategy

PSD §6.1A specifies a model provider switch:

- **Development / early production:** Groq API for LLM inference (fast, cost-effective for prototyping)
- **Production target:** Google Gemini API (long-term, integrated with Google Cloud ecosystem)

**Implementation requirement:**

- All model calls in the agent service go through a `ModelProvider` interface/abstraction layer
- Environment variable `LLM_PROVIDER=groq|gemini` controls which provider is active
- **Embeddings:** Use Gemini embeddings from day 1 (even in dev with Groq for generation) to ensure retrieval behavior consistency

**Rationale:** This dual-provider strategy allows rapid iteration with Groq's speed during development while maintaining a clear migration path to Gemini for production. Gemini embeddings ensure retrieval quality doesn't regress during the generation provider switch.

#### API Style

REST (JSON over HTTPS)

#### Layering Approach (Next.js API Routes)

- Route handlers (`app/api/*/route.ts`) → thin controllers
- Service layer (`src/backend/services/`) for business logic (lead validation, email sending, DB writes)
- Data access layer (`src/backend/db/`) via Drizzle ORM

#### Background Jobs/Scheduled Tasks

Not needed in V1. Lead delivery is synchronous (email sent immediately on submission).

#### Justification

Separating the agent service keeps Next.js focused on UI + lead capture. Google ADK orchestration complexity (RAG, model switching, safety policies) stays isolated in a Python service, aligning with PSD §6.1.

### 3) Data

#### DB Type/Product

PostgreSQL (Neon or Supabase recommended for managed hosting + pgvector support)

#### ORM/Query Approach

Drizzle ORM (type-safe, lightweight, migration-friendly)

#### Data Modeling Approach

**Entities:**

- **sessions** — `id`, `session_id`, `diver_profile` (JSONB), `conversation_history` (JSONB), `created_at`, `expires_at`
- **leads** — `id`, `session_id` (FK nullable), `lead_type` (ENUM training/trip), `contact_name`, `contact_email`, `certification_agency`, `certification_level`, `dive_count`, `destination_id` (FK nullable), `message` (TEXT), `partner_id` (FK), `created_at`
- **destinations** — `id`, `name`, `country`, `is_active`, `created_at`
- **dive_sites** — `id`, `destination_id` (FK), `name`, `min_certification_level`, `min_logged_dives` (nullable), `difficulty_band`, `access_type`, `is_active`, `created_at`
- **partners** — `id`, `destination_id` (FK nullable), `name`, `contact_email`, `partner_type` (ENUM training/trip), `is_active`, `created_at`
- **content_embeddings** — `id`, `content_type` (ENUM certification/destination/safety), `content_id` (nullable), `chunk_text` (TEXT), `embedding` (VECTOR(768)), `metadata` (JSONB), `created_at`

**Relationships:**

- `destinations` 1:N `dive_sites`
- `destinations` 1:N `partners` (nullable for training-only partners)
- `sessions` 1:N `leads` (nullable FK, guest sessions may not persist)
- `content_embeddings` standalone (no FK; metadata contains source references)

#### Migrations Strategy

Drizzle Kit for schema generation and migration application (`pnpm db:generate`, `pnpm db:migrate`)

#### Justification

Postgres + pgvector enables embedded vector search (PSD §6.2 Option A2) without external vector DB. Drizzle ORM provides type safety and incremental schema evolution for solo founder velocity.

### 4) Auth & Security

#### Authentication Approach

None in V1 (guest-only). Sessions identified by auto-generated `session_id` (UUID) stored in cookies (httpOnly, secure, sameSite=lax).

#### Authorization Model

N/A (no user roles; all guests have same access)

#### Session/Token Handling

- Server-generated `session_id` on first chat interaction
- Stored in Postgres `sessions` table (24hr TTL)
- Cookie-based session tracking (no JWT needed for V1)

#### PSD-Specific Access Control

None required (all content publicly accessible to guests)

#### Security Considerations

- Rate limiting on API routes (Next.js middleware or Vercel rate limits)
- Input validation (Zod schemas for lead forms, chat messages)
- CSRF protection via Next.js built-in (SameSite cookies)
- Secrets management via environment variables (Vercel + Cloud Run env config)

#### Justification

Guest-only sessions eliminate auth complexity for V1 MVP. Cookie-based sessions sufficient for 24hr memory. Defer OAuth/authentication to V2 when user profiles are introduced (PSD §12 Roadmap).

### 5) Infrastructure & Deployment

#### Hosting Model

- **Web App (Next.js):** Vercel (auto-deployment from GitHub main branch)
- **Agent Service (Google ADK):** Google Cloud Run (containerized Python service)
- **Database:** Neon or Supabase (managed Postgres with pgvector)

#### Environments

- **dev:** Local development (localhost:3000 for Next.js, localhost:8080 for agent service if running locally)
- **staging:** Vercel preview deployments (per-PR) + Cloud Run staging service
- **prod:** Vercel production + Cloud Run production service

#### CI/CD Approach

**GitHub Actions for Next.js repo:**

- Lint, typecheck, test on every PR
- Auto-deploy to Vercel on merge to main

**Cloud Build or GitHub Actions for agent service repo:**

- Build Docker image, push to Artifact Registry
- Deploy to Cloud Run on merge to main

#### Observability Baseline

- **Logging:** Vercel logs (Next.js), Cloud Run logs (agent service)
- **Error Tracking:** Sentry (or Vercel Analytics error monitoring)
- **Performance Monitoring:** Vercel Analytics (Web Vitals), Cloud Run metrics (latency, CPU, memory)
- **Lead Funnel Tracking:** Custom analytics events (session start, lead submitted, out-of-scope rejection) sent to simple logging table or analytics service (PostHog or Plausible optional)

#### Justification

Vercel provides zero-config Next.js deployment with excellent DX for solo founders. Cloud Run suits Python-based agent service (serverless scaling, pay-per-use, container-based). Neon/Supabase eliminates Postgres ops burden and provides native pgvector support. This stack aligns with PSD §6.1 architecture decision (Option 1) and solo founder velocity constraints.

### 6) Cross-Cutting Concerns

#### Config/Environment Variables

**Next.js Web App:**

- `DATABASE_URL` — Postgres connection string (Neon or Supabase)
- `AGENT_SERVICE_URL` — Cloud Run endpoint for chat API (e.g., `https://agent-service-xyz.run.app`)
- `SESSION_SECRET` — cookie signing key (random string, 32+ chars)
- `SENDGRID_API_KEY` or SMTP credentials — lead email delivery
- `SENTRY_DSN` — error tracking (optional but recommended)
- `NEXT_PUBLIC_ANALYTICS_ID` — analytics tracking ID (if using Plausible/PostHog)

**Agent Service (separate repo/deployment):**

- `DATABASE_URL` — same Postgres DB (for reading content_embeddings)
- `LLM_PROVIDER` — `groq` | `gemini` (model provider switch)
- `GROQ_API_KEY` — Groq API credentials (for dev/early prod)
- `GEMINI_API_KEY` — Google Gemini API credentials (for prod)
- `EMBEDDING_PROVIDER` — default to `gemini` (PSD §6.1A: use Gemini embeddings from day 1)

**Stored in:**

- `.env.local` — local dev (gitignored)
- `.env.example` — template with placeholders (committed)
- Vercel environment variables (web app)
- Cloud Run environment variables (agent service)

#### Error Handling Strategy

- **User-facing:** Graceful degradation (show "Something went wrong, please try again" for transient errors)
- **Developer-facing:** Structured error logs + Sentry alerts for uncaught exceptions
- **Boundary cases:** Out-of-scope requests return polite refusal messages (not errors)

#### Logging Strategy

- Structured JSON logs (timestamp, level, message, context)
- Log key events: `session_start`, `chat_message_sent`, `lead_submitted`, `out_of_scope_rejection`, `rag_retrieval_performed`, `model_call_latency`
- Sensitive data exclusion (no PII in logs; user messages logged only in aggregate/anonymized form)

#### Performance/Caching Considerations

- Static pages (landing, legal) served as static HTML (Next.js ISR or SSG)
- Chat API responses: no caching (session-specific)
- RAG content embeddings: cached in Postgres (no per-request embedding generation; embeddings pre-computed during content ingestion)
- CDN caching for static assets (Vercel CDN)

#### Justification

Environment-driven config enables dev/staging/prod separation. Structured logging + Sentry provide operational visibility for solo founder. No heavy caching needed for V1 scale (Assumption A-01).

---

## 4. Project Phases

### Phase 1: Foundations (Bootstrap + Infrastructure)

#### Objective

Establish a runnable Next.js web app with database, session management, and basic UI shell. No agent integration yet.

#### High-Level Scope

- **PR0:** Project Bootstrap (see initiate.prompt.md output already completed)
- Database schema + migrations for sessions, leads, destinations, dive_sites, partners
- Seed data (1 destination, 5 dive sites, 2 partners)
- Landing page + chat UI shell (no live chat yet, just UI mockup)
- Session management (cookie-based, DB-backed)
- CI pipeline (lint, typecheck, test)

#### Layers Touched

Frontend (pages, components), Backend (DB schema, session service), Data (Postgres setup), Infra (CI, Vercel setup)

#### Dependencies

None (greenfield start)

#### Acceptance Criteria

- [ ] `pnpm dev` starts locally; landing page and chat UI shell render
- [ ] Database migrations apply successfully (sessions, leads, destinations, dive_sites, partners tables created)
- [ ] Seed script inserts 1 destination + 5 dive sites + 2 partners
- [ ] Session cookie set on `/chat` page visit; session row created in DB with 24hr TTL
- [ ] CI passes (lint, typecheck, unit tests) on GitHub Actions
- [ ] Vercel preview deployment works for PRs

### Phase 2: Core Chat Flow (Agent Integration + RAG)

#### Objective

Integrate the external agent service (Google ADK) and enable basic chat interactions grounded in curated RAG content.

#### High-Level Scope

- Agent service development (separate repo/workspace; out of scope for this plan, but HTTPS API contract defined here)
- Next.js `/api/chat` route (proxy to agent service)
- Curated content ingestion (markdown → chunks → embeddings → Postgres content_embeddings table)
- ChatInterface component (frontend) sends messages, displays responses
- Session-based diver profile capture (agency, level, dive count, concerns) via conversational flow
- Hallucination guardrails (agent service logic, but frontend displays "I don't have information on that" gracefully)

#### Layers Touched

Frontend (ChatInterface, message rendering), Backend (chat API route, agent service integration), Data (content_embeddings table, RAG retrieval logic)

#### Dependencies

Phase 1 complete (session management, DB schema)

#### Acceptance Criteria

- [ ] User can type a message in chat UI, hit send, and receive a response from the agent service
- [ ] Agent service retrieves relevant content from content_embeddings table (RAG working)
- [ ] Session `diver_profile` JSONB updated as user shares certification level, dive count, etc.
- [ ] Out-of-scope requests (e.g., "Book me a flight") return polite refusal
- [ ] Response latency <2s p95 measured via Vercel Analytics
- [ ] Unit tests for `/api/chat` route (mock agent service responses)

### Phase 3: Certification Navigator (UC-00, UC-01, UC-02)

#### Objective

Enable prospective and OW divers to ask certification questions (PADI vs SSI, prerequisites, next steps) and receive agency-aware, grounded answers.

#### High-Level Scope

- Curated certification content (PADI OW/AOW, SSI OW/Advanced Adventurer, equivalency notes, prerequisites, FAQs)
- Agent service logic for certification pathway comparisons (concept-first → agency-specific)
- Confidence/fear support flow (detect anxiety-related questions, ask clarifying questions, reassure)
- Prerequisite information mode (info-only, no medical judgments, disclaimers)
- Training lead capture inline (if user says "I want to find a school")

#### Layers Touched

Backend (agent service prompts/logic, RAG content), Frontend (no major changes; existing chat UI displays certification answers), Data (certification content in content_embeddings)

#### Dependencies

Phase 2 complete (chat flow + RAG working)

#### Acceptance Criteria

- [ ] User asks "What's the difference between PADI and SSI Open Water?" → receives concept-first comparison with verify disclaimer
- [ ] User asks "I'm scared of depth" → agent asks 1–2 follow-up questions, provides reassurance based on training structure
- [ ] User asks "What are the prerequisites for OW?" → receives age bands, swim checks, medical questionnaire notes (info-only, with verify disclaimer)
- [ ] User says "I want to find a school near me" → training lead capture form appears, collects name/email/location/message
- [ ] Training lead submitted → stored in leads table, email sent to partner(s)
- [ ] Unit tests for certification content retrieval and lead capture logic

### Phase 4: Trip Research (UC-03, UC-04)

#### Objective

Enable certified divers (OW/AOW) to research the covered destination, discover suitable dive sites, and submit trip inquiry leads.

#### High-Level Scope

- Curated destination content (1 destination: overview, logistics, seasonal notes, 5–10 dive sites with certification suitability)
- Destination discovery flow (ask constraints: time, season, interests, certification level; return 1–3 covered suggestions or refuse uncovered)
- Dive site recommendation logic (filter by `min_certification_level`, `difficulty_band`; present 2–5 sites)
- Trip lead capture inline (if user says "I want to connect with an operator")

#### Layers Touched

Backend (agent service destination logic, RAG content), Frontend (no major changes; existing chat UI displays destination info), Data (destination/dive site content in content_embeddings + structured DB tables)

#### Dependencies

Phase 3 complete (certification navigator working, lead capture proven)

#### Acceptance Criteria

- [ ] User asks "Where can I dive in [covered destination]?" → receives overview + 2–5 site suggestions with certification suitability noted
- [ ] User asks "Where can I dive in [uncovered destination]?" → receives "I currently only cover [list], but I can help you plan for those"
- [ ] User asks "I'm an OW diver, show me beginner sites" → receives filtered list (`min_certification_level` = 'Open Water' or 'DSD/Non-certified')
- [ ] User says "I want to book a trip" → polite refusal ("I don't handle booking, but I can connect you with an operator")
- [ ] User says "Connect me with an operator" → trip lead capture form appears, collects name/email/dates/message
- [ ] Trip lead submitted → stored in leads table with `destination_id`, email sent to destination partner(s)
- [ ] Unit tests for destination filtering and trip lead routing

### Phase 5: Safety Guidance & Analytics (UC-06, FR-16–FR-18)

#### Objective

Handle safety/medical queries safely (general info only, disclaimers, redirects) and add basic analytics tracking for lead funnel visibility.

#### High-Level Scope

- Curated safety content (general dive safety, no-fly time, DCS overview, emergency contact info)
- Safety response mode in agent service (detect medical/decompression questions, return general info + disclaimers + redirect to professionals)
- Analytics events table (or integration with PostHog/Plausible): track `session_start`, `chat_message_sent`, `lead_submitted`, `out_of_scope_rejection`
- Simple dashboard or query interface for lead funnel (sessions → leads conversion, lead type breakdown)

#### Layers Touched

Backend (agent service safety logic, analytics event logging), Frontend (analytics event triggers), Data (analytics_events table or external service), Infra (dashboard or SQL queries)

#### Dependencies

Phase 4 complete (trip research + lead capture working)

#### Acceptance Criteria

- [ ] User asks "Can I fly after diving?" → receives general no-fly time info (12–24hr range, surface interval recommendation) + disclaimer ("Consult DAN or your physician")
- [ ] User asks "I have asthma, can I dive?" → receives "I can't provide medical advice; consult a dive physician" + link to authoritative resource
- [ ] User asks "Calculate my decompression stop" → receives "I don't perform decompression calculations; use a dive computer or consult a professional"
- [ ] Analytics events logged for key actions (100% of sessions tracked)
- [ ] Lead funnel query runnable: sessions_started, leads_submitted (by type: training vs trip), conversion rate
- [ ] Zero critical bugs reported in 2-week stability window

### Phase 6: Polish & Launch Readiness

#### Objective

Finalize UI/UX polish, legal pages, error handling, and operational readiness for public V1 launch.

#### High-Level Scope

- Legal pages (Privacy Policy, Terms of Service)
- Error handling improvements (user-friendly error messages, retry logic)
- Mobile responsiveness testing + fixes
- Performance optimization (lazy loading, image optimization, Lighthouse audit)
- Sentry setup + alert configuration
- Partner onboarding (2–3 partners for initial destination)
- Soft launch (friends & family testing, collect feedback)

#### Layers Touched

Frontend (polish, legal pages, error states), Backend (error handling hardening), Infra (Sentry, monitoring alerts)

#### Dependencies

Phase 5 complete (safety + analytics working)

#### Acceptance Criteria

- [ ] Legal pages (Privacy, Terms) published and linked in footer
- [ ] Mobile web chat UI tested on iOS Safari + Android Chrome (no major layout issues)
- [ ] Lighthouse score >90 for Performance, Accessibility, Best Practices, SEO
- [ ] Sentry configured; test error sent and received
- [ ] 2–3 partners onboarded (contact info in partners table, lead email delivery tested)
- [ ] Soft launch with 10 users → collect feedback, fix any critical bugs
- [ ] Public launch readiness checklist complete

---

## 5. Initial PR Breakdown (Near-Term Work)

This section provides a detailed breakdown for Phase 1 only (Foundations). PRs for Phase 2+ will be planned after Phase 1 completion using a separate feature planning session.

### PR0: Project Bootstrap

**Branch Name:** `feat/bootstrap`

#### Goal

Establish a runnable Next.js web app skeleton with database tooling, all required commands, and CI.

#### Scope

(See initiate.prompt.md output already completed — included here for completeness)

#### Key Changes

**Backend:**

- Drizzle ORM setup (`schema.ts` placeholder, migrations folder, `seed.ts` placeholder)
- Database connection utility (`lib/db.ts`)

**Frontend:**

- Next.js 14+ App Router scaffold
- Tailwind CSS configuration
- Placeholder pages (landing, chat UI shell)
- Basic components (Header, Footer, ChatInterface shell)

**Data:**

- `.env.example` with `DATABASE_URL`, `AGENT_SERVICE_URL`, `SESSION_SECRET` placeholders

**Infra:**

- GitHub Actions CI workflow (lint, typecheck, test)
- pnpm workspace configuration
- ESLint, Prettier, Vitest configs
- `.github/copilot-project.md` (repo truth file)

#### Testing Focus

- At least 1 passing placeholder test (e.g., test that landing page renders "DovvyBuddy" text)
- CI pipeline runs successfully

#### Verification Steps

1. `pnpm install`
2. Copy `.env.example` to `.env.local`, add dummy Postgres URL
3. `pnpm dev` → localhost:3000 loads
4. `pnpm typecheck` → passes
5. `pnpm lint` → passes
6. `pnpm format:check` → passes
7. `pnpm test` → 1+ test passes
8. Push to GitHub → CI green

### PR1: Database Schema & Migrations

**Branch Name:** `feat/db-schema`

#### Goal

Define complete database schema for sessions, leads, destinations, dive_sites, partners, content_embeddings and generate initial migration.

#### Scope

**Implement full Drizzle schema in `src/backend/db/schema.ts`:**

- `sessions` — `id` (UUID PK), `session_id` (UUID unique), `diver_profile` (JSONB), `conversation_history` (JSONB), `created_at`, `expires_at`
- `leads` — `id` (UUID PK), `session_id` (UUID nullable FK), `lead_type` (ENUM: 'training' | 'trip'), `contact_name`, `contact_email`, `certification_agency` (nullable), `certification_level` (nullable), `dive_count` (nullable INT), `destination_id` (nullable FK), `message` (TEXT), `partner_id` (FK), `created_at`
- `destinations` — `id` (UUID PK), `name`, `country`, `is_active` (BOOLEAN), `created_at`
- `dive_sites` — `id` (UUID PK), `destination_id` (FK), `name`, `min_certification_level` (VARCHAR, e.g., 'DSD/Non-certified', 'Open Water', 'Advanced Open Water', 'Rescue+', 'Tech-only', 'Unknown'), `min_logged_dives` (nullable INT), `difficulty_band` (VARCHAR: 'Beginner' | 'Intermediate' | 'Advanced'), `access_type` (VARCHAR: 'Shore' | 'Boat'), `is_active` (BOOLEAN), `created_at`
- `partners` — `id` (UUID PK), `destination_id` (nullable FK), `name`, `contact_email`, `partner_type` (ENUM: 'training' | 'trip'), `is_active` (BOOLEAN), `created_at`
- `content_embeddings` — `id` (UUID PK), `content_type` (ENUM: 'certification' | 'destination' | 'safety'), `content_id` (nullable), `chunk_text` (TEXT), `embedding` (vector(768)), `metadata` (JSONB), `created_at`

Note: `min_certification_level` on dive_sites is a typical suitability signal (PSD §6.3), not an approval gate. Always accompanied by disclaimers to confirm with operator/instructor.

**Additional tasks:**

- Run `pnpm db:generate` → create initial migration
- Update `seed.ts` to insert 1 destination, 5 dive sites, 2 partners (placeholder data with realistic `min_certification_level` values)
- Add TypeScript types in `src/shared/types/` matching schema

#### Key Changes

**Backend:**

- `src/backend/db/schema.ts` (complete schema)
- `src/backend/db/seed.ts` (seed script with placeholder data)

**Data:**

- `migrations/0000_initial_schema.sql` (generated by Drizzle)

**Shared:**

- `src/shared/types/session.ts` (Session, DiverProfile types)
- `src/shared/types/lead.ts` (Lead, LeadType enum)
- `src/shared/types/destination.ts` (Destination, DiveSite, Partner types)

#### Testing Focus

- Unit test for seed script (mock DB, verify insert calls)
- Integration test (optional, requires test DB): apply migration, run seed, query data

#### Verification Steps

1. `pnpm db:generate` → migration file created
2. Create test Postgres DB (Neon free tier or local Docker)
3. Update `.env.local` with test DB URL
4. `pnpm db:migrate` → schema applied
5. `pnpm db:seed` → 1 destination + 5 sites + 2 partners inserted
6. `pnpm db:studio` → Drizzle Studio opens, verify data visible
7. `pnpm test` → seed test passes
8. `pnpm typecheck` → no errors (types aligned with schema)

### PR2: Session Management (Cookie-Based)

**Branch Name:** `feat/session-management`

#### Goal

Implement session creation, retrieval, and expiration logic with cookie-based tracking.

#### Scope

**Session service (`src/backend/services/sessionService.ts`):**

- `createSession()` → generate UUID, insert into DB, return `session_id`
- `getSession(session_id)` → fetch from DB, check expiration
- `updateSession(session_id, updates)` → merge `diver_profile` or `conversation_history` updates
- `expireSession(session_id)` → mark expired or delete

**Next.js middleware (`middleware.ts`) or API route helper to:**

- Read `session_id` from cookie
- Create new session if missing
- Set httpOnly, secure, sameSite=lax cookie

**Add session reset endpoint (`/api/session/reset`) for "New chat" button**

#### Key Changes

**Backend:**

- `src/backend/services/sessionService.ts` (session CRUD logic)
- `src/frontend/app/api/session/route.ts` (GET `/api/session` → create or retrieve session)
- `src/frontend/middleware.ts` (optional, or inline in API routes)

**Frontend:**

- Update ChatInterface component to call `/api/session` on mount (ensure session exists)
- Add "New chat" button → calls `/api/session/reset`, clears UI state

#### Testing Focus

- Unit tests for sessionService (mock DB calls)
- Integration test: POST `/api/session` → cookie set, session row created
- Test session expiration (set TTL to 1 second, wait, verify expired session returns 401 or creates new session)

#### Verification Steps

1. `pnpm dev`
2. Visit `/chat` → inspect cookies → `session_id` cookie present
3. Check DB → sessions table has 1 row with matching `session_id`
4. Refresh page → same `session_id` (not recreated)
5. Click "New chat" → new `session_id` cookie, old session expired in DB
6. `pnpm test` → sessionService tests pass
7. `pnpm typecheck` → no errors

### PR3: Lead Capture (Backend + Frontend Form)

**Branch Name:** `feat/lead-capture`

#### Goal

Implement lead submission flow (frontend form + backend validation + DB insert + email delivery).

#### Scope

**Lead service (`src/backend/services/leadService.ts`):**

- `submitLead(leadData)` → validate with Zod schema, insert into leads table, send email to partner

**Email utility (`src/backend/services/emailService.ts`):**

- `sendLeadNotification(partner, lead)` → use SendGrid or SMTP to send email

**API route (`/api/leads` POST) → calls `leadService.submitLead()`**

**Frontend LeadForm component:**

- Fields: name, email, certification level (dropdown), dive count (number), message (textarea)
- Submit → POST `/api/leads`, show success/error message

**Zod schemas for lead validation (`src/shared/validation/leadSchema.ts`)**

#### Key Changes

**Backend:**

- `src/backend/services/leadService.ts` (lead submission logic)
- `src/backend/services/emailService.ts` (email sending)
- `src/frontend/app/api/leads/route.ts` (POST handler)

**Shared:**

- `src/shared/validation/leadSchema.ts` (Zod schema for lead input)

**Frontend:**

- `src/frontend/components/LeadForm.tsx` (form component)
- Update ChatInterface to show LeadForm inline when user triggers lead capture intent

#### Testing Focus

- Unit tests for leadService (mock DB insert, mock email send)
- Unit tests for LeadForm (render, validation, submit)
- Integration test: POST `/api/leads` with valid data → 201 response, lead row created, email sent (use email testing tool like Mailtrap or mock SMTP)

#### Verification Steps

1. `pnpm dev`
2. Navigate to `/chat`, trigger lead capture (type "I want to find a school" or click inline CTA)
3. Fill form, submit
4. Check DB → leads table has 1 row
5. Check email inbox (or Mailtrap) → lead notification received
6. Submit invalid form (missing email) → validation error shown
7. `pnpm test` → leadService + LeadForm tests pass
8. `pnpm typecheck` → no errors

### PR4: Chat UI Shell (Frontend Interactions, No Agent Yet)

**Branch Name:** `feat/chat-ui-shell`

#### Goal

Build a functional chat interface with message input, message display, and loading states (no agent integration yet; mock responses).

#### Scope

**ChatInterface component enhancements:**

- Message list (scrollable, auto-scroll to bottom)
- Message input (textarea + send button, Enter to send)
- Loading indicator while "waiting for response"
- Mock agent responses (hardcoded: "Thanks for your message! I'm DovvyBuddy, here to help you with diving questions.")

**Message components:**

- MessageBubble (user vs assistant styling, timestamp)

**Session state (React Context):**

- Store messages in memory (array of `{role: 'user' | 'assistant', content: string, timestamp}`)
- Later: sync with DB `conversation_history` (defer to Phase 2)

#### Key Changes

**Frontend:**

- `src/frontend/components/ChatInterface.tsx` (message list, input, send logic)
- `src/frontend/components/MessageBubble.tsx` (message rendering)
- `src/frontend/lib/ChatContext.tsx` (React Context for session messages)
- `src/frontend/app/chat/page.tsx` (wrap in ChatContext.Provider)

#### Testing Focus

- Unit tests for MessageBubble (render user vs assistant message)
- Integration test (Playwright optional, or manual): type message, hit send, mock response appears

#### Verification Steps

1. `pnpm dev`
2. Navigate to `/chat`
3. Type "Hello" in input, press Enter → user message appears in list
4. Wait 500ms → mock assistant response appears
5. Scroll works (if many messages)
6. Timestamp displayed for each message
7. `pnpm test` → MessageBubble tests pass
8. `pnpm typecheck` → no errors

### PR5: Landing Page & Navigation

**Branch Name:** `feat/landing-page`

#### Goal

Create a polished landing page with value proposition, CTA to chat, and navigation (header/footer).

#### Scope

**Landing page (`app/page.tsx`):**

- Hero section (headline: "Your AI Diving Buddy", subheadline: "Get certification guidance and trip advice without the confusion", CTA button: "Start chatting")
- Features section (3 cards: Certification Navigator, Trip Research, Lead Handoff)
- Footer (links: Privacy, Terms, Contact)

**Header component:**

- Logo/brand name, navigation links (Home, Chat)

**Footer component:**

- Legal links, copyright

**Responsive design (mobile + desktop)**

#### Key Changes

**Frontend:**

- `src/frontend/app/page.tsx` (landing page content)
- `src/frontend/components/Header.tsx` (navigation)
- `src/frontend/components/Footer.tsx` (footer links)
- `src/frontend/styles/globals.css` (Tailwind custom styles if needed)

#### Testing Focus

- Visual regression test (optional, Playwright screenshot comparison)
- Accessibility test (Lighthouse audit: >90 Accessibility score)

#### Verification Steps

1. `pnpm dev`
2. Visit `http://localhost:3000` → landing page renders
3. Click "Start chatting" CTA → navigates to `/chat`
4. Click "Home" in header → returns to landing page
5. Click legal links in footer → navigates to `/legal/privacy`, `/legal/terms` (placeholder pages if not yet created)
6. Resize browser to mobile width → responsive layout works
7. `pnpm typecheck` → no errors
8. Lighthouse audit → Accessibility >90, Performance >80

### PR6: CI Hardening & Documentation

**Branch Name:** `feat/ci-docs`

#### Goal

Harden CI pipeline (add test coverage reporting, enforce format check) and update README with onboarding instructions.

#### Scope

**Update `.github/workflows/ci.yml`:**

- Add `pnpm format:check` step
- Add test coverage reporting (Vitest coverage, upload to Codecov optional)
- Add build step (`pnpm build`) to catch build-time errors

**Update `README.md`:**

- Prerequisites (Node 18+, pnpm, Postgres)
- Setup instructions (clone, `pnpm install`, copy `.env.example`, run migrations, seed)
- Commands reference (dev, test, lint, etc.)
- Architecture overview (link to PSD, link to copilot-project.md)

**Update `.github/copilot-project.md`:**

- Add "Phase 1 complete" marker
- Document all established conventions (folder structure, naming, testing patterns)

#### Key Changes

**Infra:**

- `.github/workflows/ci.yml` (add format:check, coverage, build)
- `README.md` (onboarding + commands)
- `.github/copilot-project.md` (repo truth file updates)

#### Testing Focus

- CI pipeline runs all checks (lint, format, typecheck, test, build)
- Coverage report generated (even if <70% at this stage, baseline established)

#### Verification Steps

1. Push PR → CI runs
2. Verify CI steps: install, lint, format:check, typecheck, test, build → all pass
3. Review README → clear onboarding path for new developer
4. Review copilot-project.md → accurate reflection of current repo state
5. Merge to main → CI passes on main branch

---

## 6. Risks, Trade-offs, and Open Questions

### Major Risks (Technical + Product)

#### Risk R-01: Agent Service Integration Complexity

The Google ADK agent service is a separate codebase (Python, Cloud Run). If the agent service development lags or the HTTPS API contract is unclear, the Next.js web app cannot function.

**Mitigation:**

- Define API contract early (Phase 1 completion): POST `/chat` endpoint (input: `{session_id, message, diver_profile}`, output: `{response, updated_profile, citations}`)
- Build Next.js `/api/chat` route in PR2 (Phase 2) with mock agent responses initially
- Agent service development happens in parallel; integrate real endpoint in Phase 2 completion
- Use feature flags (env var `AGENT_SERVICE_ENABLED=mock|real`) to toggle mock vs real agent

#### Risk R-02: RAG Content Quality & Coverage

If curated markdown content (certifications, destinations, safety) is incomplete or low-quality by Phase 2–3, the bot will fail to answer key questions, breaking trust (G-04).

**Mitigation:**

- Content authoring happens in parallel with Phase 1 (database + UI setup)
- Minimum viable content defined: 1 destination (full guide + 5 sites), PADI/SSI OW/AOW comparison, 1 safety doc (no-fly time, DCS basics)
- Content review checklist before Phase 3 launch: each use case (UC-00 through UC-06) must have ≥3 answerable questions grounded in content
- If content not ready, delay Phase 3; do not launch with insufficient content

#### Risk R-03: Postgres + pgvector Setup Friction

Setting up pgvector extension on local Postgres or ensuring Neon/Supabase enables it may cause onboarding delays for developers or deployment issues.

**Mitigation:**

- Document exact setup steps in README (Neon: auto-enabled; local Docker: include pgvector in Dockerfile)
- Provide `docker-compose.yml` for local Postgres + pgvector (optional, for developers who prefer local DB)
- Test migration on Neon free tier before Phase 1 completion

#### Risk R-04: Lead Email Delivery Failures

If email service (SendGrid, SMTP) is misconfigured or rate-limited, leads will be lost, breaking core value prop (G-05).

**Mitigation:**

- Use transactional email service with high reliability (SendGrid recommended, 100 free emails/day)
- Implement retry logic for email send failures (queue lead in DB, retry 3x with exponential backoff)
- Add fallback: if email fails after retries, log to Sentry + admin notification
- Monitor email delivery rate (track sent vs failed in analytics_events table or SendGrid dashboard)

#### Risk R-05: Session Expiration UX Confusion

24-hour session lifetime may surprise users who return after a day and find their conversation history gone.

**Mitigation:**

- Display session expiration notice in chat UI: "Your session will expire after 24 hours of inactivity. Start a new chat anytime!"
- Phase V1.1 (per PSD §12 Roadmap): Add "Email me my plan" feature to export conversation summary before expiration
- Defer persistent user accounts to V2

### Key Trade-offs (Simplicity vs Flexibility)

#### Trade-off T-01: Embedded Vector Search (Postgres + pgvector) vs Managed Vector DB (Pinecone, Weaviate)

**Decision:** Embedded vector search (PSD §6.2 Option A2).

**Trade-off:**

- **Simplicity:** Single database (Postgres) for relational + vector data; no additional service to manage; lower cost; easier local dev.
- **Flexibility sacrificed:** Postgres pgvector less optimized for high-scale vector search (millions of embeddings); if content grows to 10k+ chunks, query latency may degrade.

**Rationale:** V1 scope is 1 destination + certifications + safety docs (estimated <1000 content chunks). Postgres + pgvector sufficient for 6–12 months. PSD §6.2 explicitly recommends Option A2 (Postgres + pgvector) for persistence simplicity and single-DB operations. If scale demands (>5000 chunks with slow queries), migrate to Pinecone/Weaviate in V2.

#### Trade-off T-02: Guest-Only Sessions vs User Accounts (V1)

**Decision:** Guest-only, session-based (no user accounts in V1).

**Trade-off:**

- **Simplicity:** No auth flows, no password management, no email verification; faster MVP launch; lower complexity.
- **Flexibility sacrificed:** No cross-device continuity, no conversation history beyond 24hr, no personalized recommendations based on past trips.

**Rationale:** PSD §1.3 NG-02 explicitly defers dive logs and persistent profiles to V2. Guest sessions prove core value (certification guidance + lead conversion) without auth friction. Add OAuth in V2 once product-market fit proven.

#### Trade-off T-03: Monorepo (Next.js + Agent Service) vs Separate Repos

**Decision:** Separate repos (Assumption A-02).

**Trade-off:**

- **Simplicity (separate repos):** Independent deploy cycles, no shared tooling complexity (pnpm workspace for TypeScript + Python mixed).
- **Flexibility sacrificed:** Shared TypeScript types (e.g., API contracts) require manual sync or published packages; no atomic commits across frontend + agent service.

**Rationale:** Next.js (TypeScript) and Google ADK (Python) have different tooling ecosystems. Separate repos reduce cognitive load for solo founder. Shared types maintained via OpenAPI spec or manual TypeScript type definitions in Next.js repo (agent service contract as source of truth).

#### Trade-off T-04: Build vs Buy (Email Service)

**Decision:** Buy (use SendGrid or similar transactional email service).

**Trade-off:**

- **Simplicity:** SendGrid API is 3 lines of code; 100 free emails/day sufficient for early testing; no SMTP server management.
- **Cost:** After free tier, SendGrid costs $15/month for 40k emails (acceptable for solo founder at 100–500 leads/month scale).
- **Flexibility sacrificed:** Vendor lock-in; if SendGrid has outage, lead delivery fails (mitigated by retry queue).

**Rationale:** Building a reliable email delivery system (handling bounces, retries, reputation management) is weeks of work. SendGrid is boring, reliable, and cheap enough for V1–V2 scale.

### Open Questions (PSD Ambiguities)

#### Question Q-01: Agent Service Deployment & Repository Structure

The PSD mentions Google ADK agent service on Cloud Run (§6.1) but does not specify:

- Will the agent service be a separate GitHub repo or a folder in this monorepo?
- Who owns the agent service development (solo founder doing both, or future hire)?

**Current Assumption (from Assumption A-02):** Agent service will be developed in a separate repository or monorepo workspace. This MASTER PLAN focuses on the Next.js web app only.

**Recommendation:** Clarify before Phase 2 start. If solo founder owns both, a separate repo is recommended to avoid Python/TypeScript tooling conflicts. Define the HTTPS API contract (OpenAPI spec) as the interface boundary: POST `/chat` endpoint (input: `{session_id, message, diver_profile}`, output: `{response, updated_profile, citations}`). Next.js web app treats agent service as an external API.

#### Question Q-02: Lead Routing Logic (Multiple Partners per Destination)

The PSD mentions "2–3 partner shops/schools per destination" (§1.4) but does not specify:

- When a user submits a trip lead, do we send to all partners or just one?
- If just one, what's the selection logic (round-robin, partner capacity, user preference)?

**Recommendation:** For V1, send lead to all partners for the destination (simple broadcast). Add partner selection logic (round-robin or capacity-based) in V1.1 or V2 based on partner feedback.

#### Question Q-03: Content Authoring Workflow

The PSD specifies curated markdown content in Git (§6.2) but does not specify:

- Who writes the content (solo founder, hired writer, community-sourced)?
- What's the review/approval process before content goes live?
- How often is content updated (seasonal changes for destinations, certification standards updates)?

**Recommendation:** For V1, solo founder writes initial content (certifications + 1 destination). Establish a content review checklist (accuracy, tone, disclaimers present). Defer content management UI to V2; V1 updates happen via Git commits + re-run content ingestion script.

---

## Summary: Execution Readiness

This MASTER PLAN provides a complete, actionable roadmap for DovvyBuddy V1, optimized for a solo founder building a diver-first AI assistant.

**Key Characteristics:**

- **Lean scope:** 1 destination, guest-only sessions, no booking/payments in V1
- **Proven stack:** Next.js + Vercel (web), Python + Google ADK + Cloud Run (agent), Postgres + pgvector (data)
- **Incremental delivery:** 6 phases, with Phase 1 broken into 7 detailed PRs (PR0–PR6)
- **Risk-aware:** 5 major risks identified with concrete mitigations; 4 trade-offs explicitly documented
- **PSD-aligned:** Every architecture decision traces back to PSD §6.1–§6.3; all FR/NFR requirements mapped to phases

**Next Steps:**

1. **Begin Phase 1:** Execute PR0–PR6 (detailed breakdown provided in §5)
2. **Parallel content authoring:** Write curated markdown for certifications (PADI/SSI OW/AOW) + 1 destination + safety docs by Phase 2 completion
3. **Agent service contract:** Define OpenAPI spec for `/chat` endpoint before Phase 2 start
4. **Phase 2+ planning:** After Phase 1 completion, run a separate feature planning session to break down Phase 2–6 into PRs using the same detailed breakdown format

**Success Metric (MVP Usable):**

By Phase 4 completion, a guest user can ask certification questions (UC-00, UC-01, UC-02), research the covered destination (UC-03, UC-04), submit training/trip leads (UC-05), and receive safe refusals for out-of-scope requests (UC-06) — with >70% test coverage, <2s response latency, and zero critical bugs in 2-week stability window.

---

**End of MASTER PLAN**