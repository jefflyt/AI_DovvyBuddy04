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
.venv/bin/pip install -e src/backend/

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API keys and database URL

# Run database migrations
cd src/backend && ../../.venv/bin/alembic upgrade head && cd ../..

# Start Python backend (terminal 1)
.venv/bin/uvicorn app.main:app --reload --app-dir src/backend

# Start Next.js frontend (terminal 2)
pnpm dev
```

Visit `http://localhost:3000` to see the app.

---

## 📁 Project Structure

```
AI_DovvyBuddy04/
├── src/backend/                  # Python FastAPI backend
│   ├── app/
│   │   ├── main.py               # FastAPI application entry point
│   │   ├── api/                  # API routes (chat, lead, session)
│   │   ├── agents/               # Multi-agent system (certification, trip, safety)
│   │   ├── orchestration/        # Chat orchestration & conversation management
│   │   ├── services/             # Core services (LLM, RAG, embeddings)
│   │   ├── db/                   # Database models, repositories, sessions
│   │   ├── core/                 # Config, lead service, utilities
│   │   └── prompts/              # System prompts per agent
│   ├── scripts/                  # Content ingestion & benchmarking scripts
│   ├── alembic/                  # Database migrations
│   ├── tests/                    # Backend unit & integration tests
│   └── pyproject.toml            # Python dependencies
│
├── src/                          # Next.js frontend
│   ├── app/                      # Next.js App Router pages
│   │   ├── page.tsx              # Landing page
│   │   ├── layout.tsx            # Root layout with analytics
│   │   └── chat/                 # Chat interface
│   ├── components/               # React components
│   │   ├── landing/              # Landing page components
│   │   └── chat/                 # Chat UI & lead capture modals
│   ├── lib/
│   │   ├── api-client/           # Backend API client with retry logic
│   │   ├── analytics/            # Multi-provider analytics (Vercel/GA4)
│   │   ├── monitoring/           # Error monitoring (Sentry)
│   │   └── hooks/                # React hooks (session state)
│   └── types/                    # TypeScript type definitions
│
├── content/                      # Curated diving content for RAG
│   ├── certifications/           # PADI/SSI certification guides
│   ├── destinations/             # Dive site information
│   ├── safety/                   # Safety guidelines & procedures
│   └── faq/                      # Frequently asked questions
│
├── config/                       # Configuration files
│   ├── playwright.config.ts      # E2E test configuration
│   ├── vitest.config.ts          # Unit test configuration
│   ├── tailwind.config.ts        # Tailwind CSS configuration
│   └── sentry.*.config.ts        # Sentry monitoring configs
│
├── docs/                         # Project documentation
│   ├── plans/                    # Implementation plans (PR1-PR10)
│   ├── technical/                # Technical specs and guides
│   ├── decisions/                # Architecture Decision Records (ADRs)
│   └── project-management/       # Implementation summaries
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
- **Hosting:** Vercel (frontend), Google Cloud Run (backend)
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
.venv/bin/uvicorn app.main:app --reload --app-dir src/backend

# Testing
export PYTHONPATH="$PWD/src/backend"
.venv/bin/python -m pytest src/backend/tests/unit -q                                # Unit tests
.venv/bin/python -m pytest src/backend/tests/integration -q                         # Integration tests
.venv/bin/python -m pytest src/backend/tests/unit src/backend/tests/integration -q --import-mode=importlib  # Combined run
.venv/bin/python -m pytest src/backend/tests -v                                     # Verbose output

# Database migrations
cd src/backend && ../../.venv/bin/alembic upgrade head                        # Apply migrations
cd src/backend && ../../.venv/bin/alembic revision --autogenerate -m "msg"    # Create migration
cd src/backend && ../../.venv/bin/alembic downgrade -1                        # Rollback one migration

# Content management
pnpm content:ingest            # Ingest content (incremental by default)
pnpm content:ingest -- --full  # Full re-ingestion
cd src/backend && ../../.venv/bin/python -m scripts.ingest_content --full --content-dir ../../content  # Explicit content path
pnpm content:validate          # Validate markdown content
pnpm content:clear             # Clear all embeddings
pnpm benchmark:rag             # Benchmark RAG performance
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

# Session Management
SESSION_SECRET=random_32_character_secret_here

# Lead Capture (Resend)
RESEND_API_KEY=re_your_resend_key
LEAD_EMAIL_TO=leads@yourdiveshop.com

# Optional Configuration
MAX_SESSION_DURATION_HOURS=24
MAX_MESSAGE_LENGTH=2000
LLM_TIMEOUT_MS=10000
```

---

## 🏗 Architecture Overview

### Multi-Agent System

DovvyBuddy uses a **specialized agent architecture** with strict Google ADK runtime orchestration:

1. **Retrieval Agent** — RAG-based content retrieval
2. **Certification Agent** — PADI/SSI certification guidance
3. **Trip Agent** — Dive site recommendations
4. **Safety Agent** — Safety protocols and emergency procedures

**Flow:**
```
User Message → Orchestrator → Intent Detection → Agent Selection → 
Response Generation → Conversation Management → User
```

Runtime settings:
- `ENABLE_ADK=true`
- `ADK_MODEL=gemini-2.5-flash-lite`
- `ENABLE_AGENT_ROUTING=true`

### RAG Pipeline

1. **Content Ingestion** (`scripts/ingest_content.py`):
   - Reads markdown files from `content/`
   - Chunks text intelligently (respects headings)
   - Generates embeddings via Gemini
   - Stores in PostgreSQL with pgvector

2. **Retrieval** (`app/services/rag/`):
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

See [PR1-Database-Schema.md](./docs/plans/PR1-Database-Schema.md) for details.

---

## 🧪 Testing Strategy

### Unit Tests (Vitest + pytest)

- **Frontend:** API client, hooks, analytics, error handling
- **Backend:** LLM providers, RAG retrieval, session management

```bash
pnpm test           # Frontend unit tests
export PYTHONPATH="$PWD/src/backend"
.venv/bin/python -m pytest src/backend/tests/unit -q
```

### Integration Tests (pytest)

- API endpoints (`/api/chat`, `/api/lead`, `/api/session`)
- Database operations
- RAG retrieval accuracy

```bash
export PYTHONPATH="$PWD/src/backend"
.venv/bin/python -m pytest src/backend/tests/integration -q
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

| Document | Purpose |
|----------|---------|
| [Master Plan](./docs/plans/MASTER_PLAN.md) | Project roadmap & status |
| [Product Spec](./docs/psd/DovvyBuddy-PSD-V6.2.md) | What to build |
| [Technical Spec](./docs/technical/specification.md) | System architecture |
| [Developer Workflow](./docs/technical/developer-workflow.md) | Development guide |
| [Technical Debt](./docs/technical/TECHNICAL_DEBT.md) | Known issues |
| [ADRs](./docs/decisions/) | Architecture decisions |
| [AI Workflow](./docs/project-management/AI_WORKFLOW.md) | AI-assisted development |

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

See [AI_WORKFLOW.md](./docs/project-management/AI_WORKFLOW.md) for complete guide.

---

## 🐛 Common Issues

### Database Connection Errors

Ensure `.env.local` is in project root (not `src/backend/.env`):
```bash
# Correct location
/Users/you/AI_DovvyBuddy04/.env.local

# Wrong location
/Users/you/AI_DovvyBuddy04/src/backend/.env
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

Proprietary — All rights reserved.

---

## 📧 Contact

**Developer:** Jeff Lee  
**Repository:** [github.com/jefflyt/AI_DovvyBuddy04](https://github.com/jefflyt/AI_DovvyBuddy04)

---

**Happy coding!** 🤿✨
