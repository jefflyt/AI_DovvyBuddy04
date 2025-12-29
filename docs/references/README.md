# External References & Resources

This directory contains links, notes, and references to external documentation, standards, APIs, and research relevant to DovvyBuddy.

---

## Purpose

- Document third-party APIs and services
- Link to industry standards (diving certifications)
- Reference research papers and best practices
- Track competitive analysis and inspiration

---

## Categories

### API Documentation

External service APIs used by DovvyBuddy:

- **Groq API** — Development LLM provider
- **Gemini API** — Production LLM provider
- **Resend API** — Email delivery service
- **Neon/Supabase** — Managed PostgreSQL hosting

### Diving Industry Standards

- **PADI Certification Levels** — Prerequisites, requirements, equivalencies
- **SSI Certification Levels** — Comparison with PADI
- **Dive Site Safety Standards** — Depth limits, experience requirements

### Technical References

- **RAG Best Practices** — Research papers and implementation guides
- **Vector Search Optimization** — pgvector tuning, HNSW parameters
- **LLM Prompt Engineering** — Safety guardrails, grounding techniques

### Competitive Analysis

- **PADI Travel** — Official PADI trip booking platform
- **SSI MySSI** — SSI's dive log and trip planning app
- **Dive Advisor** — Competitor dive trip recommendation service

---

## How to Use This Folder

1. **Create reference documents** for frequently-consulted external resources
2. **Link to live documentation** rather than copying (avoid stale copies)
3. **Add context** — Why this reference is relevant, what problem it solves
4. **Update dates** — Note when links were last verified

---

## Document Template

```markdown
# [Service/Standard Name]

**Category:** API | Standard | Research | Competitor  
**Last Verified:** YYYY-MM-DD  
**Official Link:** [URL]

## Overview

Brief description of the resource and why it's relevant to DovvyBuddy.

## Key Information

- Important details
- Rate limits (for APIs)
- Authentication methods
- Pricing tiers

## Related Documentation

- Link to internal docs that use this reference
- Related ADRs or technical specs

## Notes

Any additional context or gotchas.
```

---

## Contributing

When adding new references:

1. Use clear, descriptive filenames (e.g., `groq-api-reference.md`)
2. Include verification date
3. Link back to internal docs that rely on this reference
4. Keep notes concise — this is a reference index, not a tutorial

---

## Related Documentation

- **Technical Spec:** [../technical/specification.md](../technical/specification.md) — External integrations
- **Decisions:** [../decisions/](../decisions/) — Why we chose specific services
- **Plans:** [../plans/](../plans/) — Where external APIs are integrated

---

**Last Updated:** December 30, 2025
