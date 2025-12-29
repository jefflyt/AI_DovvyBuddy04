# ADR-0003: LLM Provider Strategy (Groq/Gemini/SEA-LION)

**Status:** Accepted  
**Date:** December 30, 2025  
**Deciders:** Solo Founder

---

## Context

DovvyBuddy needs a Large Language Model (LLM) provider strategy that balances:

- **Development speed** — Fast iteration during MVP development
- **Production quality** — High-quality responses for users
- **Cost efficiency** — Minimize API costs during validation phase
- **Multilingual support (future)** — Serve Southeast Asian divers in local languages
- **Flexibility** — Ability to switch providers without code changes

The application requires:
- Conversational AI for certification guidance and trip planning
- Grounded responses (RAG-enhanced to reduce hallucinations)
- Safety guardrails (no medical advice, always defer to professionals)

---

## Decision

Implement a **phased LLM provider strategy** with abstraction layer:

| Phase | Provider | Model | Use Case |
|-------|----------|-------|----------|
| **MVP (Dev)** | Groq | `llama-3.1-70b-versatile` | Development, testing, fast iteration |
| **Production V1** | Gemini | `gemini-2.0-flash` | English-language production traffic |
| **Production V2** | Gemini + SEA-LION | Gemini default, SEA-LION for non-English | Multilingual support for SEA audience |

**Key Implementation:**
- `ModelProvider` interface with environment-based switching (`LLM_PROVIDER=groq|gemini`)
- Factory pattern for provider instantiation
- Unified API contracts across providers

---

## Consequences

### Positive

- ✅ **Fast development** — Groq provides <1s inference for rapid iteration
- ✅ **Cost efficiency** — Groq free tier sufficient for development
- ✅ **Production quality** — Gemini 2.0 Flash offers excellent response quality
- ✅ **Flexibility** — Can switch providers via environment variable
- ✅ **Future-ready** — Architecture supports multilingual SEA-LION integration
- ✅ **Risk mitigation** — Not locked into single vendor

### Negative

- ❌ **Provider differences** — Groq vs Gemini may have behavioral variations
- ❌ **Testing complexity** — Need to test with both dev and prod models
- ❌ **Abstraction overhead** — Maintaining provider interface adds code complexity
- ❌ **SEA-LION uncertainty** — V2 multilingual routing not yet validated

### Neutral

- ⚪ **API cost variability** — Costs depend on actual usage patterns
- ⚪ **Language detection** — V2 requires language identification logic

---

## Alternatives Considered

### Alternative 1: OpenAI GPT-4 Only

**Description:** Use OpenAI GPT-4 for all environments (dev + prod)

**Pros:**
- Single provider (no abstraction needed)
- Highest quality responses
- Most mature API
- Extensive documentation

**Cons:**
- Expensive for development ($30-50/1M tokens)
- Slower inference (2-5s typical)
- Rate limits for free tier
- Less cost-effective for high-volume production

**Why rejected:** Cost prohibitive for solo founder during MVP validation. Gemini 2.0 Flash offers comparable quality at lower cost. Can revisit if response quality becomes issue.

---

### Alternative 2: Claude (Anthropic) Only

**Description:** Use Claude 3 (Sonnet/Opus) for development and production

**Pros:**
- Excellent safety alignment (fewer refusals)
- Strong reasoning capabilities
- Good for nuanced diving safety advice

**Cons:**
- Higher cost than Gemini
- Anthropic API less mature than OpenAI/Google
- Longer context windows not needed for V1
- No specific SEA regional focus

**Why rejected:** While Claude has excellent safety properties, Gemini 2.0 Flash offers better cost/performance for DovvyBuddy's use case. Google's regional presence also aligns with future SEA expansion.

---

### Alternative 3: Local LLM (Llama 3.1 via Ollama)

**Description:** Self-hosted Llama 3.1 70B on dedicated GPU server

**Pros:**
- Zero API costs (after hardware)
- Full control and privacy
- No rate limits
- No vendor dependency

**Cons:**
- High upfront cost ($3000+ GPU server)
- DevOps complexity (model management, scaling)
- Slower inference without optimization
- Solo founder overhead unsustainable
- Inferior quality to frontier models

**Why rejected:** Premature optimization. API costs at MVP scale (<1000 users) are negligible compared to hardware + ops overhead. Can revisit if scaling to 100K+ users.

---

### Alternative 4: Single Provider (Gemini) for Dev + Prod

**Description:** Use Gemini for both development and production

**Pros:**
- Simpler (no provider abstraction)
- Consistent behavior across environments
- One fewer dependency

**Cons:**
- Slower development iteration (Gemini ~2-3s vs Groq <1s)
- Higher dev costs (every test run hits paid API)
- No provider fallback if Gemini has outage

**Why rejected:** Development speed is critical for solo founder productivity. Groq's fast inference (via Groq's optimized LPU hardware) dramatically improves iteration cycle. Abstraction cost is worth the dev velocity gain.

---

## V2 Language Routing (Future Implementation)

**When non-English query detected:**
1. Detect input language (library like `franc` or Gemini language detection)
2. Route to SEA-LION provider if non-English
3. Fallback to Gemini if SEA-LION unavailable
4. Log language distribution for optimization

**SEA-LION Advantages for V2:**
- Fine-tuned on Southeast Asian languages (Thai, Indonesian, Vietnamese, etc.)
- Better cultural context for regional diving terms
- Supports Singapore/Malaysia/Thailand dive shop partnerships

---

## References

- [Groq API Documentation](https://console.groq.com/docs)
- [Gemini 2.0 Announcement](https://blog.google/technology/ai/google-gemini-2/)
- [SEA-LION Project](https://github.com/aisingapore/sea-lion)
- [PR3 Plan — Model Provider Implementation](../plans/PR3-Model-Provider-Session.md)
- [Technical Spec — Model Provider Abstraction](../technical/specification.md#23-model-provider-abstraction-pr3)

---

## Notes

**Cost Estimates (Production V1):**
- Gemini 2.0 Flash: ~$0.10 per 1M input tokens, ~$0.40 per 1M output tokens
- Expected usage: 10K conversations/month × 5 messages avg × 1000 tokens = 50M tokens/month
- Estimated monthly cost: $5-20 (well within startup budget)

**Performance Targets:**
- Dev (Groq): <1s response time (achieved via LPU optimization)
- Prod (Gemini): <3s response time (p95)

**Review Date:**
- After V1 launch (1 month) — Evaluate actual costs and response quality
- Before V2 (6 months) — Assess SEA-LION integration feasibility and demand

**Migration Path (if needed):**
- Provider abstraction allows swapping to OpenAI/Claude/other without frontend changes
- Only update: `LLM_PROVIDER` env var and provider implementation
- Factory pattern isolates provider-specific logic

---

**Related ADRs:**
- ADR-0001: Next.js + Vercel for Web Application
- ADR-0002: PostgreSQL + pgvector for Database
