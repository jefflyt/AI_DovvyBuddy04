# ADR-XXXX: [Title]

**Status:** Proposed | Accepted | Deprecated | Superseded  
**Date:** YYYY-MM-DD  
**Deciders:** [Names or role, e.g., "Solo Founder", "Engineering Team"]

---

## Context

What is the issue or problem we're facing that motivates this decision?

- Describe the current situation
- What are the forces at play (technical, business, team constraints)?
- What are the requirements or goals?

---

## Decision

What is the change we're proposing or have decided to implement?

- Be specific and concrete
- Describe the solution clearly
- Include any key implementation details

---

## Consequences

### Positive

What are the benefits of this decision?

- Improved performance
- Better developer experience
- Reduced complexity
- Cost savings
- etc.

### Negative

What are the costs, risks, or drawbacks?

- Technical debt introduced
- Additional complexity
- Learning curve
- Vendor lock-in
- etc.

### Neutral

What are the trade-offs that are neither clearly positive nor negative?

- Different approach required
- Changed workflow
- etc.

---

## Alternatives Considered

What other options did we evaluate and why were they not chosen?

### Alternative 1: [Name]

- **Description:** Brief explanation
- **Pros:** Benefits
- **Cons:** Drawbacks
- **Why rejected:** Reason for not choosing this

### Alternative 2: [Name]

- **Description:** Brief explanation
- **Pros:** Benefits
- **Cons:** Drawbacks
- **Why rejected:** Reason for not choosing this

---

## References

- [Link to relevant documentation]
- [Related ADRs]
- [External resources]

---

## Notes

Any additional context, follow-up actions, or related information.

---

**Example Usage:**

```markdown
# ADR-0001: Use Next.js for Web Application

**Status:** Accepted
**Date:** 2025-12-20
**Deciders:** Solo Founder

## Context

DovvyBuddy needs a modern web framework that supports:

- Server-side rendering for SEO
- API routes for backend logic
- Vercel deployment optimization
- Fast development iteration

## Decision

Use Next.js 14 with App Router for the web application.

## Consequences

### Positive

- Unified codebase (frontend + API routes)
- Excellent Vercel integration
- Strong TypeScript support
- Large ecosystem and community

### Negative

- Vendor coupling with Vercel for optimal performance
- Learning curve for App Router (new paradigm)

## Alternatives Considered

### Alternative 1: Separate React + Express

- **Pros:** Full control, well-understood
- **Cons:** More complex deployment, separate repos
- **Why rejected:** Overhead not justified for solo founder

### Alternative 2: Remix

- **Pros:** Excellent DX, nested routing
- **Cons:** Smaller ecosystem, less Vercel optimization
- **Why rejected:** Next.js has better Vercel integration

## References

- [Next.js Documentation](https://nextjs.org/docs)
- [Vercel Platform](https://vercel.com/docs)
```
