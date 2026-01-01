# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records that document key architectural and technical decisions made for DovvyBuddy.

---

## What is an ADR?

An Architecture Decision Record (ADR) captures an important architectural decision made along with its context and consequences. ADRs help:

- **Document decisions** — Why we chose specific technologies or approaches
- **Share knowledge** — Help new team members understand past decisions
- **Avoid rehashing** — Prevent revisiting already-decided questions
- **Track evolution** — See how architecture evolved over time

---

## When to Create an ADR

Create an ADR when making decisions about:

- **Technology selection** (frameworks, databases, services)
- **Architectural patterns** (microservices, monolith, event-driven)
- **Design approaches** (authentication, state management, API design)
- **Development practices** (testing strategy, deployment process)
- **Significant trade-offs** (performance vs simplicity, cost vs features)

**Don't create ADRs for:**
- Small implementation details
- Easily reversible decisions
- Standard best practices
- Team process changes (use project-management docs instead)

---

## How to Create an ADR

1. **Copy the template:**
   ```bash
   cp template.md XXXX-your-decision-title.md
   ```

2. **Number sequentially:** Use next available number (e.g., `0001`, `0002`, `0003`)

3. **Fill out all sections:**
   - Context (why this decision is needed)
   - Decision (what we're doing)
   - Consequences (pros, cons, trade-offs)
   - Alternatives (what else was considered)

4. **Use clear language:** Write for future readers who lack current context

5. **Keep it concise:** 1-2 pages max; link to detailed docs if needed

---

## ADR Status Lifecycle

| Status | Meaning |
|--------|---------|
| **Proposed** | Under discussion, not yet decided |
| **Accepted** | Decision made and currently in effect |
| **Deprecated** | No longer recommended but still in use |
| **Superseded** | Replaced by a newer ADR (link to it) |

---

## Current ADRs

| Number | Title | Status | Date |
|--------|-------|--------|------|
| [Template](./template.md) | ADR Template | N/A | 2025-12-30 |
| [0001](./0001-nextjs-vercel.md) | Use Next.js + Vercel for Web App | Accepted | 2025-12-20 |
| [0002](./0002-postgres-pgvector.md) | Use PostgreSQL + pgvector for Database | Accepted | 2025-12-20 |
| [0003](./0003-groq-gemini-strategy.md) | LLM Provider Strategy (Groq/Gemini/SEA-LION) | Accepted | 2025-12-30 |
| [0004](./0004-google-adk-multi-agent.md) | Google ADK Multi-Agent Architecture | Accepted | 2026-01-01 |
| [0005](./0005-gemini-flash-standardization.md) | Gemini 2.0 Flash Model Standardization | Accepted | 2026-01-01 |
| [0006](./0006-python-backend-migration.md) | Python-First Backend Migration Strategy | Accepted | 2026-01-01 |

---

## Related Documentation

- **Technical Spec:** [../technical/specification.md](../technical/specification.md) — System architecture
- **Product Spec:** [../psd/DovvyBuddy-PSD-V6.2.md](../psd/DovvyBuddy-PSD-V6.2.md) — Product requirements
- **PR Plans:** [../plans/](../plans/) — Implementation roadmap
- **Key Decisions in copilot-project.md:** [../../.github/copilot-project.md](../../.github/copilot-project.md)

---

## References

- [ADR GitHub Org](https://adr.github.io/) — ADR best practices and tools
- [Michael Nygard's Original Post](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) — Where ADRs came from

---

**Last Updated:** January 1, 2026
