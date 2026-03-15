# DovvyBuddy Developer Guide

**Technical documentation for developers working on DovvyBuddy**

> 👋 **New to the project?** Start with the main [README.md](./README.md) for a high-level overview.

---

## 🚀 Quick Start

### Prerequisites

- **Node.js 20+** — Frontend runtime
- **Python 3.11+** — Backend runtime (recommended: Python 3.11.14)
- **pnpm** — Package manager (`npm install -g pnpm`)
- **PostgreSQL with pgvector** — Database (or Neon account)
- **Gemini API Key** — LLM provider

### Installation

```bash
# Clone the repository
git clone https://github.com/jefflyt/AI_DovvyBuddy04.git
cd AI_DovvyBuddy04

# Install frontend dependencies
pnpm install

# Set up Python backend (use Python 3.11+)
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
.venv/bin/pip install -e apps/api/

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API keys and database URL

# Run database migrations
cd apps/api && ../../.venv/bin/alembic upgrade head && cd ../..

# Start Python backend (terminal 1)
.venv/bin/uvicorn app.main:app --reload --app-dir apps/api

# Start Next.js frontend (terminal 2)
pnpm dev
```

Visit `http://localhost:3000` to see the app.

---

## 📁 Project Structure

```
AI_DovvyBuddy04/
├── apps/api/                  # Python FastAPI backend
│   ├── app/
│   │   ├── main.py               # FastAPI application entry point
│   │   ├── api/                  # API routes (chat, lead, session)
│   │   ├── domain/               # Agent and orchestration domain logic
│   │   ├── infrastructure/       # DB, services, and ADK integrations
│   │   ├── core/                 # Config, lead service, utilities
│   │   └── prompts/              # System prompts per agent
│   ├── scripts/                  # Content ingestion & benchmarking scripts
│   ├── alembic/                  # Database migrations
│   ├── tests/                    # Backend unit & integration tests
│   └── pyproject.toml            # Python dependencies
│
├── apps/web/                      # Next.js frontend app
│   ├── src/
│   │   ├── app/                  # App Router routes/pages
│   │   ├── features/             # Feature-scoped UI (chat, landing)
│   │   └── shared/               # Shared components, libs, hooks, types
│   ├── public/
│   ├── next.config.js
│   └── tsconfig.json
│
├── content/                      # Curated diving content for RAG
│   ├── source/                   # Markdown source of truth
│   ├── generated/                # Generated derivatives (JSON)
│   └── templates/                # Authoring templates
│
├── tooling/config/               # Configuration files
│   ├── playwright.config.ts      # E2E test configuration
│   ├── vitest.config.ts          # Unit test configuration
│   ├── tailwind.config.ts        # Tailwind CSS configuration
│   └── sentry.*.config.ts        # Sentry monitoring configs
├── tooling/scripts/              # Agent wrappers and utility scripts
│
├── docs/                         # Project documentation
│   ├── architecture/             # Technical spec + ADRs
│   ├── operations/               # Deployment/testing/runbooks
│   ├── product/                  # PSD/TDD
│   └── archive/                  # Historical plans and implementation logs
│
└── tests/                        # E2E tests (Playwright)
```

---

## 🛠 Tech Stack

### Frontend

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript 5.4+
- **Styling:** Tailwind CSS
- **State:** React hooks + session persistence
- **Testing:** Vitest (unit), Playwright (E2E)
- **Monitoring:** Sentry, Vercel Analytics

### Backend

- **Framework:** Python FastAPI (async)
- **Language:** Python 3.11+ (recommended: 3.11.14)
- **Database:** PostgreSQL + pgvector extension
- **ORM:** SQLAlchemy 2.0 (async) + Alembic migrations
- **LLM:** Google Gemini (`gemini-2.5-flash-lite`)
- **Embeddings:** Google `text-embedding-004` (768-dim)
- **Testing:** pytest

### Infrastructure

- **Hosting:** Vercel (two projects: `apps/web` + `apps/api`)
- **Database:** Neon (managed PostgreSQL)
- **Email:** Resend API
- **CI/CD:** GitHub Actions

---

## 🔧 Development Commands

### Frontend

```bash
pnpm dev              # Start Next.js dev server (http://localhost:3000)
pnpm build            # Build for production
pnpm start            # Start production server
pnpm lint             # Run ESLint
pnpm lint:fix         # Auto-fix ESLint issues
pnpm format           # Check Prettier formatting
pnpm format:fix       # Auto-format with Prettier
pnpm typecheck        # TypeScript type checking
pnpm test             # Run Vitest unit tests
pnpm test:watch       # Run tests in watch mode
pnpm test:e2e         # Run Playwright E2E tests
pnpm test:e2e:ui      # Run E2E tests with UI
```

### Backend

```bash
# Development server
.venv/bin/uvicorn app.main:app --reload --app-dir apps/api

# Testing
export PYTHONPATH="$PWD/apps/api"
.venv/bin/python -m pytest apps/api/tests/unit -q                                # Unit tests
.venv/bin/python -m pytest apps/api/tests/integration -q                         # Integration tests
.venv/bin/python -m pytest apps/api/tests/unit apps/api/tests/integration -q --import-mode=importlib  # Combined run
.venv/bin/python -m pytest apps/api/tests -v                                     # Verbose output

# Database migrations
cd apps/api && ../../.venv/bin/alembic upgrade head                        # Apply migrations
cd apps/api && ../../.venv/bin/alembic revision --autogenerate -m "msg"    # Create migration
cd apps/api && ../../.venv/bin/alembic downgrade -1                        # Rollback one migration

# Content management
pnpm content:ingest            # Ingest content (incremental by default)
pnpm content:ingest -- --full  # Full re-ingestion
cd apps/api && ../../.venv/bin/python -m scripts.ingest_content --full --content-dir ../../content  # Explicit content path
pnpm content:validate          # Validate markdown content
pnpm content:clear             # Clear all embeddings
pnpm benchmark:rag             # Benchmark RAG performance
cd apps/api && ../../.venv/bin/python -m scripts.evaluate_grounding --cases tests/fixtures/grounding_eval_cases.json
```

### Pre-commit Checks

```bash
# Run all checks before committing
pnpm typecheck && pnpm lint && pnpm test && pnpm build
```

---

## 🔐 Environment Variables

Create `.env.local` in project root:

```bash
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Backend API (server-side)
BACKEND_URL=http://localhost:8000

# Frontend API (client-side, proxied)
NEXT_PUBLIC_API_URL=/api

# LLM Provider (Gemini)
GEMINI_API_KEY=your_gemini_api_key_here
DEFAULT_LLM_MODEL=gemini-2.5-flash-lite

# ADK orchestration
ENABLE_ADK=true
ENABLE_AGENT_ROUTING=true
ENABLE_ADK_NATIVE_GRAPH=true
ADK_MODEL=gemini-2.5-flash-lite
ADK_ROUTER_TIMEOUT_MS=5000
ADK_SPECIALIST_TIMEOUT_MS=10000
RAG_TIMEOUT_MS=4000

# Free-tier quota controls
QUOTA_ENFORCEMENT_ENABLED=true
QUOTA_PROFILE_NAME=gemini_free_tier
RATE_WINDOW_SECONDS=60
LLM_RPM_LIMIT=15
LLM_TPM_LIMIT=250000
LLM_RPD_LIMIT=1000
EMBEDDING_RPM_LIMIT=100
EMBEDDING_TPM_LIMIT=30000
EMBEDDING_RPD_LIMIT=1000

# Session Management
SESSION_SECRET=random_32_character_secret_here

# Lead Capture (Resend)
RESEND_API_KEY=re_your_resend_key
LEAD_EMAIL_TO=leads@yourdiveshop.com

# Optional Configuration
MAX_SESSION_DURATION_HOURS=24
MAX_MESSAGE_LENGTH=2000
LLM_TIMEOUT_MS=10000
EMBEDDING_TIMEOUT_MS=10000
```

---

## 🏗 Architecture Overview

### Multi-Agent System

DovvyBuddy uses a staged Google ADK orchestration runtime:

1. **ADK-native graph path** (`ENABLE_ADK_NATIVE_GRAPH=true`)
   - Coordinator: `dovvy_orchestrator`
   - Specialists: trip, certification, general retrieval, safety
   - Shared ADK tools for RAG/session/safety/policy
2. **Legacy ADK router path** (`ENABLE_ADK_NATIVE_GRAPH=false`)
   - ADK function-calling router + existing local specialist execution
   - Used for compatibility and staged rollout fallback

**Flow:**

```
User Message → Emergency Pre-check → (Native ADK Graph or Legacy ADK Router) →
Response Policy + Formatting → Session Persistence → User
```

Runtime settings:

- `ENABLE_ADK=true`
- `ADK_MODEL=gemini-2.5-flash-lite`
- `ENABLE_AGENT_ROUTING=true`
- `ENABLE_ADK_NATIVE_GRAPH=true` (native-first with legacy compatibility fallback)

Emergency handling remains deterministic and always runs before normal routing.

### API Notes

- `POST /api/chat` keeps stable response shape and may include metadata:
  - `route_decision`
  - `safety_classification`
  - `policy_enforced`
  - `runtime_path`
  - `grounding`
  - `fallbacks` / `timeout_or_fallback`
  - `citations`
  - `quota_snapshot`
- `POST /api/chat/stream` emits SSE events:
  - `route`, `safety`, `token`, `citation`, `final`, `error`

### RAG Pipeline

1. **Content Ingestion** (`apps/api/scripts/ingest_content.py`):
   - Reads markdown files from `content/`
   - Chunks text intelligently (respects headings)
   - Generates embeddings via Gemini
   - Stores in PostgreSQL with pgvector

2. **Retrieval** (`apps/api/app/infrastructure/services/rag/`):
   - Semantic search using cosine similarity
   - Hybrid filtering (metadata + embeddings)
   - Context-aware chunking

3. **Incremental Updates**:
   - File hash tracking (SHA-256)
   - Only re-ingests changed files
   - Default: incremental (use `--full` to override)

### Database Schema

- **content_embeddings** — RAG embeddings (pgvector)
- **chat_sessions** — User sessions with expiration
- **chat_messages** — Conversation history
- **leads** — Captured leads for dive shops

See [PR1-Database-Schema.md](./docs/archive/plans/PR1-Database-Schema.md) for details.

---

## 🧪 Testing Strategy

### Unit Tests (Vitest + pytest)

- **Frontend:** API client, hooks, analytics, error handling
- **Backend:** LLM providers, RAG retrieval, session management

```bash
pnpm test           # Frontend unit tests
export PYTHONPATH="$PWD/apps/api"
.venv/bin/python -m pytest apps/api/tests/unit -q
```

### Integration Tests (pytest)

- API endpoints (`/api/chat`, `/api/leads`, `/api/sessions/{session_id}`)
- Streaming endpoint (`/api/chat/stream`) event ordering/shape
- Service integration tests (skip when `GEMINI_API_KEY` is missing)

```bash
export PYTHONPATH="$PWD/apps/api"
.venv/bin/python -m pytest apps/api/tests/integration -q
```

### Full Backend Suite

```bash
export PYTHONPATH="$PWD/apps/api"
.venv/bin/python -m pytest apps/api/tests -q
```

### E2E Tests (Playwright)

- Landing page → Chat → Message → Response → Lead form
- Session persistence
- Error handling

```bash
pnpm test:e2e
pnpm test:e2e:ui  # Interactive UI mode
```

---

## 📚 Key Documentation

| Document                                                        | Purpose                  |
| --------------------------------------------------------------- | ------------------------ |
| [Master Plan](./docs/archive/plans/MASTER_PLAN.md)              | Project roadmap & status |
| [Product Spec](./docs/product/psd/DovvyBuddy-PSD-V6.2.md)       | What to build            |
| [Technical Spec](./docs/architecture/specification.md)          | System architecture      |
| [Developer Workflow](./docs/operations/developer-workflow.md)   | Development guide        |
| [Technical Debt](./docs/architecture/TECHNICAL_DEBT.md)         | Known issues             |
| [ADRs](./docs/architecture/decisions/)                          | Architecture decisions   |
| [AI Workflow](./docs/archive/project-management/AI_WORKFLOW.md) | AI-assisted development  |

---

## 🗺 Development Roadmap

### ✅ Completed (V0.5)

- **PR0:** Next.js + TypeScript setup
- **PR1:** Database schema (PostgreSQL + pgvector)
- **PR2:** RAG pipeline (content ingestion + retrieval)
- **PR3:** Model provider + session logic
- **PR3.1:** Google ADK multi-agent system
- **PR3.2:** Python backend migration (FastAPI)

### 🚧 In Progress (V1.0)

- **PR4:** Lead capture + email delivery (Resend)
- **PR5:** Chat interface + React UI
- **PR6:** Landing page + polish
- **PR7:** Production deployment

### 🔮 Planned (V1.1+)

- **PR8:** Telegram bot adapter
- **PR9:** Authentication + user profiles
- **PR10:** Advanced features (bookmarking, history)

---

## 🤖 AI-Assisted Development

This project uses **GitHub Copilot in Plan Mode** with custom prompts.

**Workflow:**

```
PSD → Master Plan → Feature Plan → PR Plan → Implementation → Refactor
```

See [AI_WORKFLOW.md](./docs/archive/project-management/AI_WORKFLOW.md) for complete guide.

### Agent Context Preflight (Monorepo)

To keep context windows small and deterministic, run preflight before scanning code:

```bash
# 1) Read required context docs and acknowledge
pnpm agent:preflight -- backend

# 2) Run scoped search through the gated scanner
pnpm agent:scan -- "orchestrator" apps/api/app -n
```

Supported scopes: `backend`, `frontend`, `content`, `docs`.

Notes:

- `agent:scan` refuses to run if preflight was not completed recently.
- Preflight stamp is stored at `.agent-context/preflight.stamp`.
- Max preflight age defaults to 240 minutes and can be changed with `AGENT_PREFLIGHT_MAX_AGE_MINUTES`.

---

## 🐛 Common Issues

### Database Connection Errors

Ensure `.env.local` is in project root (not `apps/api/.env`):

```bash
# Correct location
/Users/you/AI_DovvyBuddy04/.env.local

# Wrong location
/Users/you/AI_DovvyBuddy04/apps/api/.env
```

### Backend Not Starting

Check Python virtual environment:

```bash
which python  # Should show .venv/bin/python
source .venv/bin/activate  # If not activated
```

### Embeddings Not Working

1. Verify Gemini API key in `.env.local`
2. Check database has pgvector extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

### Tests Failing

Clear Next.js cache:

```bash
rm -rf .next && pnpm dev
```

---

## 📄 License

Proprietary — All rights reserved. See [LICENSE](./LICENSE).

---

## 📧 Contact

**Developer:** Jeff Lee  
**Repository:** [github.com/jefflyt/AI_DovvyBuddy04](https://github.com/jefflyt/AI_DovvyBuddy04)

---

**Happy coding!** 🤿✨
