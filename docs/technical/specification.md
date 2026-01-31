# DovvyBuddy - Technical Specification Document

**Version:** 1.1  
**Last Updated:** January 31, 2026  
**Status:** Active (Refactored)

---

## 1. System Overview

### Purpose

DovvyBuddy is an AI-powered conversational assistant that helps prospective and recreational divers make informed decisions about scuba diving certifications and trip planning. The system provides grounded, safety-conscious information while generating qualified leads for partner dive shops and training centers.

### High-Level Architecture

```
┌─────────────┐
│   Browser   │
│  (Next.js)  │
└──────┬──────┘
       │ HTTPS
       ▼
┌────────────────────────────────────────────┐
│   Frontend (Vercel)                        │
│   ┌──────────────────────────────────┐     │
│   │  Next.js 14 App Router           │     │
│   │  Location: /src/                 │     │
│   │  - Landing Page                  │     │
│   │  - Chat Interface                │     │
│   │  - Lead Capture Forms            │     │
│   └──────────┬───────────────────────┘     │
└──────────────┼─────────────────────────────┘
               │ /api/* proxy
               ▼
┌────────────────────────────────────────────┐
│   Python Backend (Cloud Run)               │
│   ┌──────────────────────────────────┐     │
│   │  FastAPI Application             │     │
│   │  Location: /backend/             │     │
│   │  - Multi-Agent System            │     │
│   │  - Chat Orchestration            │     │
│   │  - RAG Pipeline                  │     │
│   │  - Session Management            │     │
│   │  - Lead Capture                  │     │
│   └──────────┬───────────────────────┘     │
└──────────────┼─────────────────────────────┘
               │
       ┌───────┴────────┬──────────────┐
       │                │              │
       ▼                ▼              ▼
┌─────────────┐  ┌────────────┐  ┌─────────┐
│  Postgres   │  │   Gemini   │  │ Resend  │
│  +pgvector  │  │  2.0-flash │  │  Email  │
│   (Neon)    │  │    API     │  │   API   │
└─────────────┘  └────────────┘  └─────────┘
```

### Technology Stack

| Layer | Technology | Justification |
|-------|------------|---------------|
| **Frontend** | Next.js 14 (App Router), React, TypeScript | Server Components, type safety, optimized routing |
| **Backend** | Python FastAPI, SQLAlchemy, Alembic | Async performance, robust ORM, type hints |
| **Database** | PostgreSQL + pgvector (Neon) | Relational data + vector embeddings, managed service |
| **LLM** | Gemini 2.0 Flash | Cost-effective, production-ready, 1M token context |
| **Embeddings** | text-embedding-004 | 768 dimensions, optimized for retrieval |
| **Email** | Resend API | Developer-friendly, reliable delivery |
| **Hosting** | Vercel (frontend) + Cloud Run (backend) | Edge network, serverless Python |
| **Testing** | Vitest (frontend), pytest (backend), Playwright (E2E) | Comprehensive test coverage |
| **Monitoring** | Sentry + Vercel Analytics | Error tracking, performance insights |

---

## 2. Core Components

### 2.1 Multi-Agent System (backend/app/agents/)

**Purpose:** Specialized agents handle different types of diving queries with domain expertise.

**Agent Types:**
- **Certification Agent** - PADI/SSI certification guidance, prerequisites, progression paths
- **Trip Planning Agent** - Dive site recommendations, difficulty assessment, logistics
- **Safety Agent** - Emergency procedures, medical contraindications, risk management
- **Retrieval Agent** - RAG-powered content retrieval and context building

**Architecture:**
```
User Query → Mode Detection → Agent Selection → Agent Execution → Response
```

**Key Files:**
- `backend/app/agents/base.py` - Base agent interface
- `backend/app/agents/registry.py` - Agent registration & discovery
- `backend/app/agents/certification_agent.py`
- `backend/app/agents/trip_planning_agent.py`
- `backend/app/agents/safety_agent.py`
- `backend/app/agents/retrieval_agent.py`

---

### 2.2 Chat Orchestration (backend/app/orchestration/)

**Purpose:** Coordinates conversation flow, manages context, and routes to appropriate agents.

**Responsibilities:**
- Session lifecycle management (create, retrieve, update)
- Conversation context building (history + RAG context)
- Emergency detection (safety-critical queries)
- Mode detection (greeting, certification, trip, general)
- Agent selection and execution
- Response formatting and metadata

**Flow:**
```
User Message → Emergency Check → Mode Detection → Agent Selection 
→ Context Building → Agent Execute → History Update → Response
```

**Key Files:**
- `backend/app/orchestration/orchestrator.py` - Main orchestration logic
- `backend/app/orchestration/conversation_manager.py` - Conversation state
- `backend/app/orchestration/mode_detector.py` - Query classification
- `backend/app/orchestration/emergency_detector.py` - Safety detection

---

### 2.3 RAG Pipeline (backend/app/services/)

**Purpose:** Retrieve relevant content chunks to ground LLM responses.

**Components:**
1. **Content Ingestion:** Markdown files → chunks → embeddings → database
2. **Retrieval Service:** Query → vector search → ranked chunks
3. **Context Builder:** Chunks → formatted context string

**Data Flow:**
```
Content Files → Chunking (500-800 tokens) → Gemini Embeddings 
→ Store in pgvector → Query → Retrieve Top-K → Return Context
```

**Key Decisions:**
- Chunk size: 500-800 tokens (balance between context and precision)
- Embedding model: Gemini `text-embedding-004` (1536 dimensions)
- Retrieval: HNSW index for fast similarity search
- Metadata: JSONB fields for filtering (content type, certification level)

**Key Files:**
- `src/lib/rag/ingestion.ts`
- `src/lib/rag/retrieval.ts`
- `src/lib/rag/types.ts`

---

### 2.3 Model Provider Abstraction (PR3)

**Purpose:** Abstract LLM API calls to support multiple providers via environment configuration.

**Providers:**

| Phase | Provider | Model | Use Case |
|-------|----------|-------|----------|
| **MVP (Dev)** | Groq | `llama-3.1-70b-versatile` | Fast iteration, low cost |
| **Production V1** | Gemini | `gemini-2.0-flash` | English-language production |
| **Production V2** | Gemini + SEA-LION | Gemini default, SEA-LION for non-English | Multilingual SEA audience |

**Interface:**
```typescript
interface BaseModelProvider {
  generateResponse(
    messages: ModelMessage[],
    config?: Partial<ModelConfig>
  ): Promise<ModelResponse>;
}
```

**Key Files:**
- `src/lib/model-provider/base-provider.ts`
- `src/lib/model-provider/groq-provider.ts`
- `src/lib/model-provider/gemini-provider.ts`
- `src/lib/model-provider/factory.ts`

---

### 2.4 Session Management (PR3)

**Purpose:** Maintain conversation state for 24-hour sessions without user authentication.

**Session Data Structure:**
```typescript
{
  id: string;                    // UUID
  conversation_history: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  }>;
  diver_profile: {
    certificationLevel?: string;
    diveCount?: number;
    interests?: string[];
    fears?: string[];
  };
  created_at: Date;
  expires_at: Date;              // created_at + 24h
}
```

**Operations:**
- `createSession()` — Generate UUID, set expiry
- `getSession(id)` — Retrieve session, return null if expired
- `updateSessionHistory(id, messages)` — Append user + assistant messages
- `expireSession(id)` — Mark session as expired

**Key Files:**
- `src/lib/session/session-service.ts`
- `src/lib/session/types.ts`

---

### 2.5 Lead Capture (PR4)

**Purpose:** Collect qualified leads and deliver to partner dive shops via email.

**Lead Types:**
1. **Training Leads:** Certification requests, course inquiries
2. **Trip Leads:** Destination research, booking interest

**Lead Data Structure:**
```typescript
{
  id: string;
  type: 'training' | 'trip';
  diver_profile: {
    name: string;
    email: string;
    phone?: string;
    certification_level?: string;
    dive_count?: number;
  };
  request_details: {
    message?: string;
    destination?: string;
    preferred_dates?: string;
    budget?: string;
  };
  session_id?: string;
  created_at: Date;
}
```

**Delivery:**
- **Email:** Resend API → `LEAD_EMAIL_TO` address
- **Webhook (optional):** HTTP POST to `LEAD_WEBHOOK_URL`

**Deduplication:**
- Same `email + type` within 5 minutes → reject as duplicate

**Key Files:**
- `src/lib/lead/lead-service.ts`
- `src/app/api/lead/route.ts`

---

## 3. API Contracts

### 3.1 POST /api/chat

**Request:**
```typescript
{
  sessionId?: string;  // Optional, creates new if omitted
  message: string;     // Max 2000 chars
}
```

**Response (200):**
```typescript
{
  sessionId: string;
  response: string;
  metadata?: {
    tokensUsed?: number;
    contextChunks?: number;
  };
}
```

**Errors:**
- `400` — Invalid input (message too long, invalid format)
- `500` — Internal server error
- `503` — LLM provider unavailable

---

### 3.2 POST /api/lead

**Request:**
```typescript
{
  type: 'training' | 'trip';
  data: {
    name: string;
    email: string;
    phone?: string;
    certification_level?: string;
    dive_count?: number;
    message?: string;
    destination?: string;
    preferred_dates?: string;
    budget?: string;
  };
  sessionId?: string;
}
```

**Response (200):**
```typescript
{
  success: true;
  leadId: string;
}
```

**Errors:**
- `400` — Validation error (missing required fields)
- `409` — Duplicate lead (same email + type within 5 minutes)
- `500` — Internal server error
- `503` — Email delivery failed

---

## 4. Data Models

### 4.1 Database Schema

**destinations**
```sql
CREATE TABLE destinations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  country VARCHAR(100) NOT NULL,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**dive_sites**
```sql
CREATE TABLE dive_sites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  destination_id UUID REFERENCES destinations(id),
  name VARCHAR(255) NOT NULL,
  min_certification_level VARCHAR(50),
  min_logged_dives INTEGER,
  difficulty_band VARCHAR(50),
  access_type VARCHAR(50),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**sessions**
```sql
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  diver_profile JSONB,
  conversation_history JSONB DEFAULT '[]',
  created_at TIMESTAMP DEFAULT NOW(),
  expires_at TIMESTAMP NOT NULL
);
```

**leads**
```sql
CREATE TABLE leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type VARCHAR(20) NOT NULL CHECK (type IN ('training', 'trip')),
  diver_profile JSONB NOT NULL,
  request_details JSONB,
  session_id UUID REFERENCES sessions(id),
  created_at TIMESTAMP DEFAULT NOW()
);
```

**content_embeddings**
```sql
CREATE TABLE content_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  content_path VARCHAR(500) NOT NULL,
  chunk_text TEXT NOT NULL,
  embedding vector(1536),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ON content_embeddings USING hnsw (embedding vector_cosine_ops);
```

---

## 5. Security & Performance

### 5.1 Security Considerations

| Area | Mitigation |
|------|------------|
| **Session Hijacking** | UUID v4 (cryptographically random), no guessable patterns |
| **XSS Prevention** | React auto-escaping, Content Security Policy headers |
| **Input Validation** | Zod schemas, max length checks, sanitization |
| **Rate Limiting** | Vercel edge middleware (future), 10s LLM timeout |
| **API Key Exposure** | Environment variables, never in client code |
| **PII Protection** | Minimal data collection, 24h session expiry, no persistent user data |

### 5.2 Performance

| Component | Strategy | Target |
|-----------|----------|--------|
| **LLM Calls** | 10s timeout, retry once on transient failure | <5s p95 response time |
| **Vector Search** | HNSW index, Top-5 chunks | <100ms query time |
| **Session Retrieval** | Indexed by UUID, check expiry in query | <10ms |
| **Cold Starts** | Minimize dependencies, optimize imports | <2s first request |
| **Caching** | Static assets via Vercel CDN | Edge delivery |

---

## 6. External Integrations

### 6.1 LLM Providers

**Groq (Development)**
- Model: `llama-3.1-70b-versatile`
- API: https://api.groq.com/v1/chat/completions
- Auth: Bearer token (`GROQ_API_KEY`)

**Gemini (Production V1)**
- Model: `gemini-2.0-flash`
- API: Google Generative AI SDK
- Auth: API key (`GEMINI_API_KEY`)

**SEA-LION (Production V2)**
- Model: TBD
- Routing: Detect non-English input → route to SEA-LION
- Fallback: Gemini if SEA-LION unavailable

### 6.2 Email (Resend API)

- Endpoint: https://api.resend.com/emails
- Auth: API key (`RESEND_API_KEY`)
- Template: Plain text email with lead details
- Recipient: `LEAD_EMAIL_TO` environment variable

### 6.3 Database (Neon)

- PostgreSQL 15+ with pgvector extension
- Connection: `DATABASE_URL` environment variable
- ORM: Drizzle (type-safe queries)

---

## 7. Deployment Architecture

### 7.1 Vercel (Web App)

- **Region:** Auto (edge network)
- **Compute:** Serverless functions (Node.js runtime)
- **Environment:** Separate preview/production
- **Build:** `pnpm build` → static + API routes

### 7.2 Environment Variables

See `.env.example` for full list. Critical variables:

```bash
DATABASE_URL=postgresql://...
LLM_PROVIDER=groq|gemini
GROQ_API_KEY=...
GEMINI_API_KEY=...
RESEND_API_KEY=...
LEAD_EMAIL_TO=partner@diveshop.com
SESSION_SECRET=random_32char_string
```

---

## 8. Testing Strategy

### 8.1 Unit Tests (Vitest)

- Model providers (mocked API responses)
- Session service (CRUD operations)
- RAG retrieval (mocked embeddings)
- Lead validation and deduplication

### 8.2 Integration Tests (Vitest)

- `/api/chat` — End-to-end with mocked LLM
- `/api/lead` — Email delivery with mocked Resend

### 8.3 E2E Tests (Playwright)

- **V1 Scope:** Single smoke test
  - Landing page → Chat → Send message → Receive response → Open lead form
- **Assertions:** Behavior, not content (response appears, not "response says X")

---

## 9. Future Architecture (V1.1+)

### 9.1 Agent Service Extraction (PR8a)

```
┌─────────────┐       ┌─────────────┐
│  Web App    │       │ Telegram Bot│
│  (Vercel)   │       │  (Adapter)  │
└──────┬──────┘       └──────┬──────┘
       │                     │
       └─────────┬───────────┘
                 │ HTTPS
                 ▼
         ┌───────────────┐
         │ Agent Service │
         │ (Cloud Run)   │
         │ - ADK         │
         │ - RAG         │
         │ - LLM         │
         └───────┬───────┘
                 │
         ┌───────┴───────┐
         │               │
    ┌────▼────┐    ┌─────▼─────┐
    │Postgres │    │  Gemini   │
    │+pgvector│    │    API    │
    └─────────┘    └───────────┘
```

### 9.2 Authentication (V2 - PR8)

- NextAuth.js with Credentials provider
- User profiles table
- JWT sessions in HTTP-only cookies
- Cross-channel account linking (web ↔ Telegram)

---

## 10. Maintenance & Operations

### 10.1 Monitoring

- **Error Tracking:** Sentry (future)
- **Analytics:** Vercel Analytics or Posthog (PR6)
- **Logs:** Vercel function logs, Pino structured logging

### 10.2 Backup & Recovery

- **Database:** Neon automatic backups (point-in-time recovery)
- **Code:** Git repository on GitHub
- **Rollback:** Vercel instant rollback to previous deployment

---

## Related Documents

- **Product Spec:** [../psd/DovvyBuddy-PSD-V6.2.md](../psd/DovvyBuddy-PSD-V6.2.md)
- **PR Plans:** [../plans/](../plans/)
- **Decisions:** [../decisions/](../decisions/)
- **Project Context:** [../../.github/copilot-project.md](../../.github/copilot-project.md)

---

**End of Technical Specification Document**
