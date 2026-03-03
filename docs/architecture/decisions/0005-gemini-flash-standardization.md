# ADR-0005: Gemini 2.0 Flash Model Standardization

**Status:** Accepted  
**Date:** January 1, 2026  
**Deciders:** Solo Founder

---

## Context

DovvyBuddy uses Google Gemini for production LLM inference. Google offers multiple Gemini model tiers:

- **Gemini 2.0 Flash** — Optimized for speed and cost, multimodal, good for most tasks
- **Gemini 1.5 Flash** — Previous generation Flash model
- **Gemini 1.5 Pro** — Higher quality reasoning, better for complex tasks, more expensive
- **Gemini 2.0 Pro** (experimental) — Latest high-quality model, premium pricing

The codebase had **inconsistent model usage**:

- Model provider default: `gemini-2.0-flash-exp` (experimental version)
- ADK agents: Mix of `gemini-1.5-pro` (specialists) and `gemini-1.5-flash` (retrieval/safety)
- Environment examples: Mix of pro and flash models

**Cost Considerations:**

- Flash model: ~15x cheaper than Pro for input tokens, ~30x cheaper for output tokens
- Our use case: Conversational AI with RAG enhancement (grounded responses)
- Target audience: Prospective and recreational divers (not requiring research-grade reasoning)
- Query patterns: Relatively straightforward certification and trip planning questions

**Quality Considerations:**

- Flash 2.0 is significantly improved over Flash 1.5
- RAG enhancement (vector search) provides grounding, reducing need for Pro-level reasoning
- Multi-agent architecture uses specialized prompts, reducing complexity per agent
- Safety validation is rule-based (doesn't need Pro reasoning)

---

## Decision

**Standardize on `gemini-2.0-flash` for all Gemini LLM calls.**

**Applies to:**

- Model provider default (`apps/web/src/shared/lib/model-provider/gemini-provider.ts`)
- All ADK agent models:
  - `ADK_MODEL` (general)
  - `ADK_RETRIEVAL_MODEL` (retrieval agent)
  - `ADK_SPECIALIST_MODEL` (certification/trip agents)
  - `ADK_SAFETY_MODEL` (safety validation agent)
- Environment variable defaults (`.env.example`)
- All code examples and documentation

**Explicit prohibition:**

- ❌ Do NOT use `gemini-1.5-pro`, `gemini-2.0-pro`, or any pro variants
- ❌ Do NOT use experimental models (`gemini-2.0-flash-exp`) in production
- ✅ Only use `gemini-2.0-flash` (stable release)

**Documentation:**

- Added to `.github/copilot-instructions.md` as coding standard
- Noted in code comments where models are configured
- Updated in `.env.example` with explicit note

---

## Consequences

### Positive

- ✅ **Cost optimization** — 15-30x cost reduction vs Pro models
- ✅ **Consistency** — Single model across all agents and use cases
- ✅ **Simplicity** — No need to decide which model for which agent
- ✅ **Sufficient quality** — Flash 2.0 + RAG + specialized agents provides good responses
- ✅ **Fast inference** — Flash optimized for low latency (<1s vs Pro's 1-3s)
- ✅ **Clear guidance** — Explicit instruction for future development
- ✅ **Budget predictability** — Easier to forecast API costs

### Negative

- ⚠️ **Potential quality ceiling** — Pro models may handle edge cases better
- ⚠️ **Complex reasoning limitations** — Flash may struggle with multi-step reasoning (though rare in our domain)
- ⚠️ **Future limitations** — If requirements change (research-grade content, complex itinerary planning), may need Pro

### Neutral

- 🔄 **Re-evaluation needed** — Should monitor response quality and revisit if issues arise
- 🔄 **Model improvements** — Flash 2.0 will improve over time, reducing gap with Pro

---

## Alternatives Considered

### Alternative 1: Use Pro for Specialists, Flash for Retrieval/Safety

**Description:** Hybrid approach with Pro for certification/trip agents, Flash for retrieval/safety

**Pros:**

- Better quality for complex queries (certification comparisons, multi-destination planning)
- Still saves cost on retrieval and safety (cheaper operations)
- Balanced approach

**Cons:**

- Inconsistent model usage creates confusion
- Harder to debug (is quality issue due to model or prompt?)
- Cost still 15-30x higher for main query path (specialists)
- Quality improvement unclear (RAG + specialized prompts may be sufficient)

**Why rejected:** Cost savings not worth added complexity. Flash 2.0 with RAG should be sufficient for our domain.

### Alternative 2: Use Pro for All Agents

**Description:** Standardize on Pro across the board

**Pros:**

- Maximum quality for all operations
- Simpler than hybrid approach
- Better handling of complex or ambiguous queries

**Cons:**

- 15-30x higher cost
- Slower inference (1-3s vs <1s)
- Overkill for simple operations (safety validation, retrieval)
- Budget risk during validation phase (unknown query volume)

**Why rejected:** Cost prohibitive for MVP/validation phase. Can revisit if revenue supports it.

### Alternative 3: Dynamic Model Selection Based on Query Complexity

**Description:** Use heuristics to route complex queries to Pro, simple queries to Flash

**Pros:**

- Cost-optimized (only pay for Pro when needed)
- Best quality where it matters
- Potential for machine learning-based routing later

**Cons:**

- Significantly more complex orchestration logic
- Hard to define "complexity" heuristics reliably
- Latency added by routing decision
- Difficult to debug and optimize
- May lead to inconsistent user experience

**Why rejected:** Premature optimization. Too complex for uncertain benefit. Revisit if clear use case emerges.

### Alternative 4: Use Claude Sonnet (Anthropic)

**Description:** Switch from Gemini to Claude Sonnet for balance of cost/quality

**Pros:**

- Excellent reasoning and safety features
- Good tool use capabilities
- Competitive pricing

**Cons:**

- Vendor switch (already committed to Google ecosystem)
- Would need to revalidate entire agent system
- Claude doesn't have Flash-tier pricing (Haiku is weaker than Flash)
- Google embeddings + Claude LLM creates vendor mixing

**Why rejected:** Already invested in Google ecosystem (embeddings, ADK). Claude doesn't offer clear advantage to justify switch.

---

## References

- **Gemini Pricing:** https://ai.google.dev/pricing
- **Model Comparison:** https://ai.google.dev/gemini-api/docs/models
- **Code Changes:** PR implementing standardization (January 1, 2026)
- **Related ADR:** [0004-google-adk-multi-agent.md](./0004-google-adk-multi-agent.md) — Multi-agent architecture

---

## Notes

**Implementation Status:** ✅ Completed (January 1, 2026)

**Files Updated:**

- `apps/web/src/shared/lib/model-provider/gemini-provider.ts`
- `apps/web/src/shared/lib/agent/certification-agent.ts`
- `apps/web/src/shared/lib/agent/trip-agent.ts`
- `apps/web/src/shared/lib/agent/config.ts`
- `.env.example`
- `.github/copilot-instructions.md`
- `docs/archive/plans/PR3.1-ADK-Multi-Agent-RAG.md`

**Monitoring Plan:**

- Track user feedback on response quality
- Monitor completion rates (do users get satisfactory answers?)
- Spot-check responses for accuracy vs knowledge base
- Compare against Pro model responses periodically (A/B test if volume allows)

**Re-evaluation Triggers:**

- Significant user complaints about response quality
- Specific query patterns where Flash consistently fails
- Revenue reaches level where cost difference becomes negligible
- New Gemini model releases with better Flash tier

**Cost Impact:**

- Estimated 15-30x reduction vs Pro models
- With multi-agent architecture (2-3 calls per query), still cheaper than single Pro call
- Budget: ~$X/month at estimated query volume (to be measured)

**Quality Safeguards:**

- RAG enhancement grounds responses in curated content
- Multi-agent specialization reduces per-agent complexity
- Safety validation catches missing disclaimers
- User feedback loop for continuous improvement

---

**Last Updated:** January 1, 2026
