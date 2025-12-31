# DovvyBuddy

**AI-powered scuba diving certification and trip planning assistant**

DovvyBuddy helps prospective and recreational divers make informed decisions about certifications (PADI, SSI) and dive trips through conversational AI powered by RAG-enhanced LLMs.

---

## 🌊 What is DovvyBuddy?

DovvyBuddy is a diver-first AI assistant that provides:

- **Certification Guidance** — Navigate PADI/SSI certifications with confidence
- **Fear Normalization** — Friendly, educational support for new divers
- **Trip Research** — Discover dive sites matched to your certification level
- **Lead Capture** — Connect with partner dive shops when you're ready

**Key Principle:** Information-only mode. Always redirects to professionals for training, medical, or safety decisions.

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ (recommend 20+)
- pnpm (install via `npm install -g pnpm`)
- PostgreSQL with pgvector extension (or Neon account)
- LLM API keys (Groq for dev, Gemini for prod)

### Installation

```bash
# Clone the repository
git clone https://github.com/jefflyt/AI_DovvyBuddy04.git
cd AI_DovvyBuddy04

# Install dependencies
pnpm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your API keys and database URL

# Run database migrations (once database is set up)
pnpm db:migrate

# Start development server
pnpm dev
```

Visit `http://localhost:3000` to see the app.

---

## 📁 Project Structure

```
AI_DovvyBuddy04/
├── .github/
│   ├── copilot-instructions.md   # AI coding guidelines
│   ├── copilot-project.md        # Project context for AI
│   └── prompts/                  # Custom AI workflow prompts
│
├── docs/
│   ├── psd/                      # Product Specification Document
│   ├── plans/                    # PR implementation plans (PR1-PR10)
│   ├── technical/                # Technical specs and architecture
│   ├── decisions/                # Architecture Decision Records (ADRs)
│   ├── references/               # External API docs and standards
│   └── project-management/       # AI workflow guides
│
├── src/
│   ├── app/                      # Next.js App Router pages
│   ├── components/               # React components (future)
│   ├── lib/                      # Core services (future)
│   │   ├── model-provider/       # LLM abstraction (PR3)
│   │   ├── rag/                  # RAG pipeline (PR2)
│   │   └── session/              # Session management (PR3)
│   ├── db/                       # Database schema & migrations (PR1)
│   └── types/                    # TypeScript type definitions
│
├── content/                      # Curated diving content for RAG (PR2)
├── tests/                        # Test files (Vitest)
├── public/                       # Static assets
│
├── package.json
├── next.config.js
├── tsconfig.json
├── vitest.config.ts
└── README.md                     # This file
```

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Framework** | Next.js 14 (App Router) | Full-stack React framework |
| **Language** | TypeScript | Type safety |
| **Database** | PostgreSQL + pgvector | Relational data + vector search |
| **Hosting** | Vercel | Serverless deployment |
| **LLM (Dev)** | Groq (`llama-3.1-70b-versatile`) | Fast iteration |
| **LLM (Prod)** | Gemini (`gemini-2.0-flash`) | Production quality |
| **Email** | Resend API | Lead delivery |
| **ORM** | Drizzle | Type-safe database queries |
| **Testing** | Vitest + Playwright | Unit, integration, e2e |
| **Styling** | Tailwind CSS | Utility-first CSS |

---

## 📜 Available Commands

```bash
# Development
pnpm dev              # Start dev server (http://localhost:3000)
pnpm build            # Build for production
pnpm start            # Start production server

# Code Quality
pnpm lint             # Run ESLint
pnpm typecheck        # Run TypeScript type checking
pnpm format           # Format with Prettier

# Testing
pnpm test             # Run unit tests (Vitest)
pnpm test:watch       # Run tests in watch mode
pnpm test:e2e         # Run e2e tests (Playwright)

# Database
pnpm db:generate      # Generate Drizzle migrations
pnpm db:migrate       # Run migrations
pnpm db:seed          # Seed database with sample data
pnpm db:studio        # Open Drizzle Studio

# Complete Check (run before committing)
pnpm typecheck && pnpm lint && pnpm test && pnpm build
```

---

## 🗺 Development Roadmap

### V1 Web Application (PR1-PR6)

- ✅ **PR0:** Bootstrap (Next.js + TypeScript setup)
- ✅ **PR1:** Database Schema (Postgres + pgvector + migrations)
- ✅ **PR2:** RAG Pipeline (content ingestion + retrieval)
- 🚧 **PR3:** Model Provider + Session Logic (Groq/Gemini + chat API)
- 🚧 **PR4:** Lead Capture + Delivery (Resend email integration)
- 🚧 **PR5:** Chat Interface + Integration (React UI + session persistence)
- 🚧 **PR6:** Landing Page + Polish (E2E tests + launch prep)

### V1.1 Telegram Bot (PR7a-7c)

- **PR7a:** Agent Service Extraction (Cloud Run deployment)
- **PR7b:** Telegram Bot Adapter (basic chat flow)
- **PR7c:** Telegram Lead Capture (production hardening)

### V2 Authentication & Profiles (PR8a-8c)

- **PR8a:** Auth Infrastructure (NextAuth.js + user tables)
- **PR8b:** Web UI Auth Integration (signin/signup pages)
- **PR8c:** Telegram Account Linking (cross-channel sync)

See detailed plans in [`docs/plans/`](./docs/plans/)

---

## 📚 Documentation

| Document | Purpose | Location |
|----------|---------|----------|
| **Product Spec (PSD)** | What to build | [`docs/psd/DovvyBuddy-PSD-V6.2.md`](./docs/psd/DovvyBuddy-PSD-V6.2.md) |
| **Technical Spec (TSD)** | How it works | [`docs/technical/specification.md`](./docs/technical/specification.md) |
| **PR Plans** | Implementation steps | [`docs/plans/`](./docs/plans/) |
| **ADRs** | Why we chose this | [`docs/decisions/`](./docs/decisions/) |
| **AI Workflow** | Development process | [`docs/project-management/AI_WORKFLOW.md`](./docs/project-management/AI_WORKFLOW.md) |
| **Project Context** | AI assistant context | [`.github/copilot-project.md`](./.github/copilot-project.md) |

---

## 🤖 AI-Assisted Development

This project uses **GitHub Copilot in Plan Mode** with custom prompts for structured development.

**Key workflow:**
```
PSD → Master Plan → Feature Plan → PR Plan → Implementation → Refactor
```

See the complete guide: [`docs/project-management/AI_WORKFLOW.md`](./docs/project-management/AI_WORKFLOW.md)

---

## 🔐 Environment Variables

Required environment variables (see `.env.example`):

```bash
# Database
DATABASE_URL=postgresql://...

# LLM Providers
LLM_PROVIDER=groq                      # groq | gemini
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key

# Session
SESSION_SECRET=random_32char_string

# Lead Capture (PR4+)
RESEND_API_KEY=your_resend_key
LEAD_EMAIL_TO=partner@diveshop.com

# Optional
MAX_SESSION_DURATION_HOURS=24
MAX_MESSAGE_LENGTH=2000
LLM_TIMEOUT_MS=10000
```

---

## 🧪 Testing Strategy

- **Unit Tests:** Core business logic (model providers, session service, RAG retrieval)
- **Integration Tests:** API endpoints (`/api/chat`, `/api/lead`)
- **E2E Tests (V1):** Single smoke test (landing → chat → message → response → lead form)

Run all checks before committing:
```bash
pnpm typecheck && pnpm lint && pnpm test && pnpm build
```

---

## 🤝 Contributing

This is currently a solo founder project. Contributions are not being accepted at this time, but feedback and suggestions are welcome via issues.

---

## 📄 License

Proprietary — All rights reserved.

---

## 🙏 Acknowledgments

- **PADI & SSI** — Diving certification standards
- **Groq & Google** — LLM API providers
- **Vercel** — Hosting platform
- **Neon** — Managed PostgreSQL

---

## 📧 Contact

**Project Owner:** Jeff Lee  
**Repository:** [github.com/jefflyt/AI_DovvyBuddy04](https://github.com/jefflyt/AI_DovvyBuddy04)

---

**Ready to dive in?** 🤿

Start with the [Product Specification](./docs/psd/DovvyBuddy-PSD-V6.2.md) to understand the vision, then check the [Technical Specification](./docs/technical/specification.md) for architecture details.
