# ADR-0001: Use Next.js + Vercel for Web Application

**Status:** Accepted  
**Date:** December 20, 2025  
**Deciders:** Solo Founder

---

## Context

DovvyBuddy needs a modern web framework for the initial V1 web application that supports:

- **SEO optimization** — Scuba diving content benefits from search visibility
- **API routes** — Backend logic for chat, lead capture, RAG retrieval
- **Fast development** — Solo founder requires rapid iteration
- **Production-ready** — Minimal DevOps overhead for deployment
- **Cost-effective** — Free tier sufficient for MVP validation

The application has both frontend (landing page, chat UI) and backend (LLM orchestration, database queries) components that need to be tightly integrated.

---

## Decision

Use **Next.js 14 with App Router** as the web framework, deployed on **Vercel**.

**Key Components:**
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript (strict mode)
- **Hosting:** Vercel (serverless functions + edge network)
- **Package Manager:** pnpm (faster, more efficient than npm)

---

### Explicit Constraints (V1 Scope)

- **No WebSocket or bi-directional streaming** in V1.
- Chat interactions use **standard HTTP request/response** via Next.js API routes.
- Optional enhancement: **Server-Sent Events (SSE)** may be evaluated post-V1 for one-way token streaming if UX demands it.

---

## Consequences

### Positive

- ✅ **Unified codebase** — Frontend + API routes in single repo
- ✅ **Excellent Vercel integration** — Zero-config deployment, instant previews
- ✅ **Server Components** — Improved performance, reduced client JS
- ✅ **Built-in optimizations** — Image optimization, code splitting, automatic caching
- ✅ **Strong TypeScript support** — Type-safe API routes and components
- ✅ **Large ecosystem** — Extensive library support, community resources
- ✅ **Free tier** — Sufficient for MVP validation and early users

### Negative

- ❌ **Vercel coupling** — Optimal performance tied to Vercel platform
- ❌ **App Router learning curve** — New paradigm requires adjustment
- ❌ **Serverless constraints** — 10s function timeout, cold starts
- ❌ **Framework churn** — Next.js evolves rapidly, breaking changes possible

### Neutral

- ⚪ **Different deployment model** — Serverless vs traditional servers
- ⚪ **Edge network reliance** — Benefits depend on Vercel's infrastructure

---

## Alternatives Considered

### Alternative 1: Separate React + Express Backend

**Description:** React SPA for frontend, Express.js API server, deployed separately

**Pros:**
- Full control over backend deployment
- Well-understood architecture
- No framework coupling

**Cons:**
- Two separate deployments to manage
- Requires CORS configuration
- More complex local development setup
- Higher DevOps overhead for solo founder

**Why rejected:** Operational complexity not justified for MVP. Solo founder resources better spent on product features than infrastructure management.

---

### Alternative 2: Remix

**Description:** Full-stack React framework with nested routing and Web Fetch API

**Pros:**
- Excellent developer experience
- Progressive enhancement built-in
- Strong data loading conventions

**Cons:**
- Smaller ecosystem than Next.js
- Less optimized for Vercel deployment
- Fewer learning resources
- Newer framework with less production battle-testing

**Why rejected:** While Remix has strong DX, Next.js offers better Vercel integration (critical for solo founder ease), larger community, and more production references for troubleshooting.

---

### Alternative 3: SvelteKit

**Description:** Full-stack framework based on Svelte compiler

**Pros:**
- Smaller bundle sizes
- Simpler reactivity model
- Good performance

**Cons:**
- Smaller ecosystem (fewer libraries)
- Less TypeScript maturity
- Fewer developers familiar with Svelte
- Limited hiring pool if scaling team

**Why rejected:** While technically compelling, React/Next.js ecosystem offers better library support for AI/LLM integrations and larger talent pool if future hiring needed.

---

### Alternative 4: Astro

**Description:** Static-first framework with partial hydration

**Pros:**
- Excellent for content-heavy sites
- Zero JS by default
- Framework-agnostic components

**Cons:**
- Primarily static site generator
- Less suited for dynamic chat application
- API routes less mature
- Session management more complex

**Why rejected:** DovvyBuddy's core feature (AI chat) requires significant dynamic functionality. Astro's static-first approach not well-aligned with conversational UX.

---

## References

- [Next.js Documentation](https://nextjs.org/docs)
- [Vercel Platform Docs](https://vercel.com/docs)
- [App Router Migration Guide](https://nextjs.org/docs/app/building-your-application/upgrading/app-router-migration)
- [copilot-project.md — Tech Stack](../../.github/copilot-project.md#tech-stack--architecture-decided)

---

## Notes

**Migration Path (if needed):**
- Next.js provides export to static HTML if moving away from Vercel
- API routes can be extracted to standalone Express/Fastify server
- Frontend can be separated to pure React SPA if needed

**Review Date:**
- After V1 launch (3-6 months) — Evaluate if Vercel costs scale appropriately
- If adding Telegram bot (PR7) — Consider if agent service extraction affects this decision

---

**Related ADRs:**
- ADR-0002: PostgreSQL + pgvector for Database
- ADR-0003: LLM Provider Strategy (Groq/Gemini/SEA-LION)
