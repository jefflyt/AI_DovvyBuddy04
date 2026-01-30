# DovvyBuddy - Project Context for AI Assistants

**Last Updated:** January 31, 2026  
**Project Status:** PR0-PR6.2 Complete, Backend Refactored to Root

---

## Project Overview

**DovvyBuddy** is a diver-first AI assistant for certification guidance and dive trip planning. It helps prospective and recreational divers (Open Water → Advanced levels) make informed decisions through:

- Agency-aware certification navigation (PADI, SSI)
- Confidence-building for new students (fear normalization, prerequisite clarity)
- Trip research for covered destinations/sites
- Qualified lead handoffs to partner dive shops/schools

**Key Principle:** Information-only mode, not instructional. Always redirect to professionals for training, medical, or safety decisions.

---

## Tech Stack & Architecture (CURRENT)

### Web Application (V1 - Active)

- **Frontend:** Next.js 14 (App Router) + TypeScript + React
- **Backend:** Python FastAPI + SQLAlchemy + Alembic
- **Package Manager:** pnpm (frontend), pip (backend)
- **Hosting:** Vercel (frontend), Cloud Run (backend planned)
- **Database:** PostgreSQL with pgvector (Neon)
- **Testing:** 
  - Frontend: Vitest (unit), Playwright (E2E)
  - Backend: pytest (unit & integration)
- **Linting/Formatting:** ESLint + Prettier (frontend), ruff (backend)

### Backend Architecture (PR3.2 - Complete)

- **Framework:** FastAPI with async/await
- **Multi-Agent System:** Specialized agents (certification, trip, safety, retrieval)
- **Orchestration:** Conversation manager with mode detection & emergency handling
- **RAG Pipeline:** Vector search with Gemini embeddings (text-embedding-004)
- **Session Management:** PostgreSQL-backed conversation history

### LLM Provider Strategy (Updated)

| Phase | Provider | Model | Use Case |
|-------|----------|-------|----------|
| **Production V1** | Gemini | `gemini-2.0-flash` | Primary production LLM (cost-effective) |
| **Embeddings** | Gemini | `text-embedding-004` | 768-dimension vectors for RAG |

- **Standardized:** All production traffic uses Gemini 2.0 Flash
- **Future:** V2 may add SEA-LION for multilingual support (SEA region)

---

## Repository Structure
 (Current)

```
AI_DovvyBuddy04/
├── .github/
│   ├── instructions/             # Global coding guidelines
│   │   └── Global Instructions.instructions.md
│   ├── workflows/                # CI/CD pipelines
│   │   └── ci.yml                # Automated testing & checks
│   ├── prompts/                  # AI workflow prompt templates
│   │   ├── initiate.prompt.md
│   │   ├── plan.prompt.md
│   │   ├── implement_plan.prompt.md
│   │   └── refactor_plan.prompt.md
│   └── skills/                   # AI agent skills
│
├── backend/                      # Python FastAPI backend (moved from src/backend/)
│   ├── app/
│   │   ├── main.py               # FastAPI application entry
│   │   ├── api/                  # API routes (chat, lead, session)
│   │   ├── agents/               # Multi-agent system
│   │   │   ├── base.py
│   │   │   ├── certification_agent.py
│   │   │   ├── trip_planning_agent.py
│   │   │   └── safety_agent.py
│   │   ├── orchestration/        # Chat orchestration
│   │   │   ├── orchestrator.py
│   │   │   ├── conversation_manager.py
│   │   │   └── mode_detector.py
│   │   ├── services/             # Core services
│   │   │   ├── llm_service.py
│   │   │   ├── rag_service.py
│   │   │   └── embedding_service.py
│   │   ├── db/                   # Database layer
│   │   │   ├── models.py
│   │   │   ├── repositories/
│   │   │   └── session.py
│   │   ├── core/                 # Config & utilities
│   │   │   ├── config.py
│   │   │   └── lead_service.py
│   │   └── prompts/              # System prompts per agent
│   ├── scripts/                  # Content processing scripts
│   │   ├── ingest_content.py
│   │   ├── validate_content.py
│   │   └── benchmark_rag.py
│   ├── tests/                    # Backend tests (pytest)
│   │   ├── unit/
│   │   └── integration/
│   ├── alembic/                  # Database migrations
│   ├── pyproject.toml            # Python dependencies
│   └── README.md
│
├── src/                          # Next.js frontend
│   ├── app/                      # Next.js App Router
│   │   ├── page.tsx              # Landing page
│   │   ├── chat/page.tsx         # Chat interface
│   │   └── layout.tsx            # Root layout with analytics
│   ├── components/               # React components
│   │   ├── landing/              # Landing page sections
│   │   ├── chat/                 # Chat UI & lead capture
│   │   └── ErrorBoundary.tsx
│   ├── lib/
│   │   ├── api-client/           # Backend API client
│   │   ├── analytics/            # Multi-provider analytics
│   │   ├── monitoring/           # Error monitoring (Sentry)
│   │   └── hooks/                # React hooks
│   └── types/                    # TypeScript definitions
│
├── content/                      # Curated diving content for RAG
│   ├── certifications/           # PADI/SSI guides
│   ├── destinations/             # Dive sites
│   ├── safety/                   # Safety procedures
│   └── faq/
│
├── docs/
│   ├── psd/                      # Product specifications
│   ├── plans/                    # PR implementation plans (PR1-PR10)
│   ├── technical/                # Technical guides
│   ├── decisions/                # Architecture Decision Records (ADRs)
│   └── project-management/       # Implementation summaries
│
├── tests/                        # E2E tests (Playwright)
│   ├── e2e/
│   └── fixtures/
│
├── scripts/                      # Node.js utility scripts
│   └── review-content.ts
│
├── package.json                  # Frontend dependencies & scripts
├── next.config.js                # Next.js config (proxies /api/* to backend)
├── tsconfig.json                 # TypeScript configuration
└── README.md                     # Project documentation
```
│   │   ├── model-provider/       # LLM abstraction (PR3)
│   │   ├── rag/                  # RAG pipeline (PR2)
│   │   └── session/              # Session management (PR4)
│   ├── db/                       # Database (PR1)
│   │   ├── schema.sql            # Initial schema (future)
│   │   ├── migrations/           # Migration scripts (future)
│   │   └── queries/              # Typed query functions (future)
│   └── types/                    # TypeScript types
├── tests/                        # Test files (Vitest)
├── public/                       # Static assets
├── package.json
├── tsconfig.json
├── next.config.js
├── vitest.config.ts
├── .eslintrc.json
├── .prettierrc
├── .env.example                  # Environment variable template
└── README.md                     # Setup and command reference
```

---

## Key Decisions

### D-01: Next.js + Vercel for Web, ADK for Agent Service

**Rationale:** Keep Next.js for web experience, use Google ADK for orchestration (retrieval, safety policies, model calls). Agent service deployed separately on Cloud Run, serves both web and future Telegram.

### D-02: Embedded Vector Search (No Managed Vector DB)

**Rationale:** V1 has small content corpus (~1 destination, 5-10 sites, certification guides). Use Gemini embeddings + either:

- **Option A (preferred):** Postgres + pgvector (simple, co-located with main DB)
- **Option B:** Object-storage-backed index (e.g., GCS, local download on startup)

Defer dedicated vector DB (Pinecone, Weaviate) until scaling requires it.

### D-03: Model Provider Abstraction

**Rationale:** Dev uses Groq for fast iteration; production uses Gemini. Abstraction layer (`ModelProvider` interface) allows env-based switching without code changes.

### D-04: Guest Sessions Only (V1)

**Rationale:** No user accounts in V1. Sessions are 24h, stored in Postgres (or in-memory fallback). Reduces scope, proves diver wedge before adding auth.

### D-05: Curated Content in Git (Versioned)

**Rationale:** Content is small, infrequently updated, and benefits from version control + review process. Store markdown files in `content/`, ingest into vector index via build step (PR2).

### D-06: Minimal CI (Lint/Typecheck/Test/Build)

**Rationale:** Catch regressions early. No e2e in PR0; Playwright deferred to later PRs when UI is stable.

### D-07: Pragmatic E2E Testing (PR6)

**Rationale:** Solo founder resources require efficient testing strategy. Full E2E suite is expensive to maintain and flaky with LLM responses.

- **V1 Approach:** Single smoke test (landing → chat → message → response → lead form)
- **Assertions:** Test behavior (response appears), not content (response says X)
- **Manual Checklist:** Covers content quality, edge cases, mobile testing
- **CI Integration:** Non-blocking for V1; made blocking post-launch
- **Deferred:** Comprehensive E2E suite, LLM response mocking

### D-08: NextAuth.js for Authentication (V2)

**Rationale:** Self-hosted authentication for full control, no external service dependencies, and data portability.

- **Provider:** NextAuth.js with Credentials provider (email/password)
- **Session Strategy:** JWT stored in HTTP-only cookie
- **Email Verification:** Custom implementation using Resend API (already integrated)
- **Migration Path:** Can migrate to Clerk later if OAuth complexity or scaling requires managed service
- **Feature Flag:** `FEATURE_USER_AUTH_ENABLED` controls auth feature rollout

---

## Data Model (Planned - PR1)

### Destinations

```
id, name, country, is_active, created_at
```

### DiveSites

```
id, destination_id, name, min_certification_level, min_logged_dives,
difficulty_band, access_type, is_active, created_at
```

### Leads

```
id, type (training|trip), diver_profile (JSONB), request_details (JSONB), created_at
```

### Sessions

```
id, diver_profile (JSONB), conversation_history (JSONB), created_at, expires_at
```

### ContentEmbeddings (if using pgvector)

```
id, content_path, chunk_text, embedding (vector), metadata (JSONB), created_at
```

---

## Environment Variables

See `.env.example` for full list. Key vars:

**Database & Session:**
- `DATABASE_URL` — Postgres connection string
- `SESSION_SECRET` — Random 32+ char string

**LLM Provider (PR3):**
- `LLM_PROVIDER` — `groq` or `gemini`
- `GROQ_API_KEY` — Groq API key (dev)
- `GEMINI_API_KEY` — Google Gemini API key (prod)

**Embedding Provider (PR2):**
- `EMBEDDING_PROVIDER` — `gemini` (default)

**Lead Capture (PR4):**
- `RESEND_API_KEY` — Resend API key for email delivery
- `LEAD_EMAIL_TO` — Destination email for lead notifications
- `LEAD_WEBHOOK_URL` — Optional webhook for lead delivery

**Analytics & Monitoring (PR6):**
- `NEXT_PUBLIC_ANALYTICS_PROVIDER` — `vercel` | `posthog` | `ga4` (default: `vercel`)
- `NEXT_PUBLIC_POSTHOG_KEY` — Posthog API key (if using Posthog)
- `NEXT_PUBLIC_GA_ID` — Google Analytics ID (if using GA4)
- `SENTRY_DSN` — Sentry DSN for error monitoring
- `SENTRY_AUTH_TOKEN` — Sentry auth token (CI only)

**Feature Flags:**
- `ENABLE_TELEGRAM` — Feature flag (V1.1)
- `FEATURE_USER_AUTH_ENABLED` — Feature flag for V2 authentication (default: false)

**Authentication (V2 - PR8):**
- `NEXTAUTH_SECRET` — Random 32+ char string for JWT signing
- `NEXTAUTH_URL` — Full URL of the app (e.g., `http://localhost:3000`)

---

## Coding Guidelines

### TypeScript

- Strict mode enabled (`strict: true`)
- No `any` unless absolutely necessary (use `unknown` + guards)
- Prefer explicit types over inference for public APIs

### React

- Use Server Components by default (Next.js App Router)
- Mark Client Components explicitly (`'use client'`)
- Keep components small and focused

### Naming

- Files: kebab-case (`model-provider.ts`)
- Components: PascalCase (`ChatInterface.tsx`)
- Functions/variables: camelCase (`getUserSession`)
- Constants: UPPER_SNAKE_CASE (`MAX_SESSION_DURATION`)

### Error Handling

- Never swallow errors silently
- Log errors with context (user intent, session ID if available)
- Return user-friendly messages (no stack traces in prod)

### Safety & Grounding

- **Never invent facts** — if not in corpus, say "I don't have information on that"
- Always include disclaimers for safety/medical/prerequisite topics
- Redirect to professionals when appropriate

---

## Workflow: PR Planning with AI

1. **Initiate (PR0):** Use `initiate.prompt.md` to bootstrap project from PSD
2. **Plan (PR1+):** Use `plan.prompt.md` to generate PR breakdown from PSD
3. **Implement:** Follow PR plan, update this file as decisions are made
4. **Verify:** Run `pnpm typecheck && pnpm lint && pnpm test && pnpm build` before merging

---

## Current Status (PR0 Complete)

✅ **Done:**

- Next.js 14 + TypeScript foundation
- Package scripts and toolchain (pnpm/ESLint/Prettier/Vitest)
- CI workflow (GitHub Actions)
- Placeholder pages (landing, chat stub)
- Project structure with READMEs
- Environment template

🚧 **Next PRs:**

**V1 Web (PR1-6):**
- PR1: Database schema + migrations (Postgres + pgvector)
- PR2: RAG pipeline (content → embedding → retrieval)
- PR3: Model provider + session logic (Groq/Gemini abstraction, `/api/chat`)
- PR4: Lead capture + delivery (Resend email integration)
- PR5: Chat interface + integration (React components, session persistence)
- PR6: Landing page, E2E smoke test, content review, launch preparation

**V1.1 Telegram (PR7a-7c):**
- PR7a: Agent Service Extraction to Cloud Run
- PR7b: Telegram Bot Adapter (basic chat flow)
- PR7c: Telegram Lead Capture & Production Hardening

**V2 Auth & Profiles (PR8a-8c):**
- PR8a: Auth Infrastructure (NextAuth.js, user/profile tables, backend APIs)
- PR8b: Web UI Auth Integration (signin, signup, profile pages)
- PR8c: Telegram Account Linking (cross-channel session sync)

**PR Plans:** See `docs/plans/PR1-*.md` through `PR8c-*.md` for detailed specifications.

---

## Future Considerations

### V1.1 (After Web Stabilizes) - PR7a-7c

- Telegram thin client (same agent service backend) — **Planned in PR7a-7c**
- "Email me my plan" feature

### V2 (Auth & Profiles) - PR8a-8c

- User profiles + authentication — **Planned in PR8a-8c (NextAuth.js)**
- Dive log storage
- Enhanced personalization

### V2.1

- Photo-based marine life recognition

### V3

- ML-based recommendation ranking
- Multi-destination trip planning

---

## Links

- **PSD:** [docs/psd/DovvyBuddy-PSD-V6.2.md](../docs/psd/DovvyBuddy-PSD-V6.2.md)
- **Technical Spec:** [docs/technical/specification.md](../docs/technical/specification.md)
- **README:** [README.md](../../README.md)
- **Workflow Prompts:** [.github/prompts/](.github/prompts/)

---

## Notes for AI Assistants

When working on this project:

1. **Consult PSD first** — All requirements come from DovvyBuddy-PSD-V6.2.md
2. **Follow decisions** — Don't re-litigate architecture choices (Next.js, ADK, pgvector, etc.)
3. **Prefer Plan mode** — Use workflow prompts before autonomous implementation
4. **Keep functions small** — Follow coding guidelines above
5. **Update this file** — Add new decisions to "Key Decisions" section as they're made
6. **Safety-first** — Never generate content that could mislead divers or bypass professional consultation

---

**End of Project Context**
