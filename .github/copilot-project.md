# DovvyBuddy - Project Context for AI Assistants

**Last Updated:** December 22, 2025  
**Project Status:** PR0 Bootstrap Complete

---

## Project Overview

**DovvyBuddy** is a diver-first AI assistant for certification guidance and dive trip planning. It helps prospective and recreational divers (Open Water → Advanced levels) make informed decisions through:

- Agency-aware certification navigation (PADI, SSI)
- Confidence-building for new students (fear normalization, prerequisite clarity)
- Trip research for covered destinations/sites
- Qualified lead handoffs to partner dive shops/schools

**Key Principle:** Information-only mode, not instructional. Always redirect to professionals for training, medical, or safety decisions.

---

## Tech Stack & Architecture (DECIDED)

### Web App (V1)

- **Framework:** Next.js 14 (App Router) + TypeScript + React
- **Package Manager:** pnpm
- **Hosting:** Vercel
- **Database:** Postgres with pgvector (Neon or Supabase planned)
- **Testing:** Vitest (unit/integration), Playwright (e2e, deferred)
- **Linting/Formatting:** ESLint + Prettier

### Agent Service (Future PR)

- **Orchestration:** Google ADK (Agent Development Kit)
- **Deployment:** Google Cloud Run (containerized)
- **Retrieval:** Embedded vector search (Gemini embeddings + pgvector or object-storage-backed index)

### LLM Provider Strategy

- **Dev Environment:** Groq API (fast inference)
- **Production Target:** Google Gemini API
- **Abstraction:** `ModelProvider` interface with env switch (`LLM_PROVIDER=groq|gemini`)

---

## Repository Structure

```
AI_DovvyBuddy04/
├── .github/
│   ├── copilot-instructions.md   # Global AI coding style preferences
│   ├── copilot-project.md        # This file (project context)
│   ├── prompts/                  # Workflow prompt templates
│   │   ├── initiate.prompt.md    # Bootstrap new projects
│   │   ├── plan.prompt.md        # Generate PR plans (future)
│   │   └── feature_epic_plan.prompt.md
│   └── workflows/
│       └── ci.yml                # CI: lint/typecheck/test/build
├── docs/
│   ├── psd/
│   │   └── DovvyBuddy-PSD-V6.2.md  # Product Specification Document
│   ├── decisions/                # Architecture Decision Records (future)
│   ├── plans/                    # PR/Epic plans (future)
│   └── references/               # External references (future)
├── content/                      # Curated markdown for RAG (future PR2)
├── src/
│   ├── app/                      # Next.js pages (App Router)
│   │   ├── page.tsx              # Landing page
│   │   ├── chat/page.tsx         # Chat interface (stub)
│   │   ├── layout.tsx            # Root layout
│   │   └── globals.css           # Global styles
│   ├── components/               # React components (future)
│   ├── lib/                      # Shared utilities (future)
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

- `LLM_PROVIDER` — `groq` or `gemini`
- `GROQ_API_KEY` — Groq API key (dev)
- `GEMINI_API_KEY` — Google Gemini API key (prod)
- `DATABASE_URL` — Postgres connection string
- `SESSION_SECRET` — Random 32+ char string
- `LEAD_WEBHOOK_URL` — Optional webhook for lead delivery
- `ENABLE_TELEGRAM` — Feature flag (V1.1)

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

- PR1: Database schema + migrations (Postgres + pgvector)
- PR2: RAG pipeline (content → embedding → retrieval)
- PR3: Model provider interface (Groq + Gemini)
- PR4: Session management
- PR5: Lead capture
- PR6+: Chat logic, conversation orchestration

---

## Future Considerations

### V1.1 (After Web Stabilizes)

- Telegram thin client (same agent service backend)
- "Email me my plan" feature

### V2

- User profiles + authentication
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
