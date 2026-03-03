# ADR-0004: Google ADK Multi-Agent Architecture

**Status:** Accepted  
**Date:** January 1, 2026  
**Deciders:** Solo Founder

---

## Context

DovvyBuddy's initial architecture (PR3) used a single LLM provider with RAG-enhanced prompts for all queries. While functional, this approach had limitations:

- **Generic responses** — Single prompt tried to handle certification, trip planning, and safety queries with equal competence
- **Prompt complexity** — System prompt became increasingly complex with multiple concerns
- **Limited tool use** — No structured way for LLM to invoke retrieval or validation tools
- **Difficult optimization** — Hard to tune for different query types (certification vs trip planning)
- **Scalability concerns** — Adding new capabilities (booking, community features) would further complicate the single prompt

The application requires:

- **Specialized expertise** — Different knowledge domains (certifications, destinations, safety)
- **Active retrieval** — LLM should decide when to search knowledge base
- **Safety validation** — Responses need automatic checks for required disclaimers
- **Tool composition** — Ability to chain multiple operations (search → generate → validate)
- **Future extensibility** — Easy to add new agent capabilities without breaking existing ones

We needed an orchestration framework that could:

- Coordinate multiple specialized agents
- Enable structured tool use (vector search, session lookup, validation)
- Maintain API contract (no breaking changes for frontend)
- Run on Vercel serverless (Next.js API routes)

---

## Decision

Adopt **Google Agent Development Kit (ADK)** with a **multi-agent architecture** comprising:

**Agent System:**

1. **Retrieval Agent** — Searches knowledge base using vector search tool
2. **Certification Agent** — Specialist for PADI/SSI certification queries
3. **Trip Agent** — Specialist for destination and dive site recommendations
4. **Safety Agent** — Validates responses for required disclaimers

**Orchestration Flow:**

```
User Query → Router → [Retrieval Agent (parallel)] → Specialist Agent → Safety Agent → Response
```

**Key Implementation Details:**

- Query routing logic detects certification vs trip vs general queries
- Retrieval agent runs in parallel with routing (2s timeout)
- Specialist agent uses retrieved context (5s timeout)
- Safety agent validates and appends disclaimers (1s timeout)
- Feature flag `ENABLE_ADK=true` enables ADK, with fallback to legacy provider
- Each agent has defined tools (vector-search, session-lookup, safety-check)

**Technology Choice:**

- Google ADK (Genkit) for agent orchestration
- Gemini 2.0 Flash for all agent LLM calls
- Native integration with existing model-provider abstraction

---

## Consequences

### Positive

- ✅ **Improved response quality** — Specialized agents provide more accurate, contextual answers
- ✅ **Better safety handling** — Dedicated validation ensures consistent disclaimers
- ✅ **Active retrieval** — Agents decide when to search knowledge base (not always-on)
- ✅ **Scalability** — Easy to add new agents (FAQ, booking, community) without touching existing ones
- ✅ **Explicit tool use** — Clear separation between generation and retrieval operations
- ✅ **Maintainable prompts** — Each agent has focused, simple system prompt
- ✅ **Debugging visibility** — Can see which agent handled query and what tools were called
- ✅ **API contract preserved** — Frontend unchanged, transparent upgrade

### Negative

- ⚠️ **Increased complexity** — Orchestration logic more complex than single LLM call
- ⚠️ **Latency overhead** — Multi-agent coordination adds ~1-2s vs single call (still <10s target)
- ⚠️ **Google vendor lock-in** — ADK ties us to Google ecosystem (Gemini, Vertex AI)
- ⚠️ **Debugging difficulty** — Multi-agent failures harder to trace than single call failures
- ⚠️ **Cost increase** — More LLM calls per query (2-3 agents vs 1), though offset by Flash model
- ⚠️ **ADK maturity risk** — ADK is relatively new, potential for breaking changes
- ⚠️ **Serverless compatibility** — ADK cold starts may impact performance on Vercel

### Neutral

- 🔄 **Different mental model** — Developers must think in terms of agent coordination vs single prompt
- 🔄 **New testing approach** — Need to test agent routing, tool calls, and coordination
- 🔄 **Monitoring changes** — Telemetry now tracks per-agent metrics (tokens, latency, tool usage)

---

## Alternatives Considered

### Alternative 1: LangChain Agents

**Description:** Use LangChain's agent framework for multi-agent orchestration

**Pros:**

- Mature ecosystem with extensive documentation
- Provider-agnostic (supports Groq, Gemini, OpenAI, etc.)
- Rich tool library and community integrations
- Better observability tools (LangSmith)

**Cons:**

- Python-first (TypeScript support limited)
- Heavier dependency footprint
- More opinionated about agent structure
- Requires more boilerplate for simple agents

**Why rejected:** Requires Python backend (planned for PR3.2 anyway), but wanted to validate multi-agent approach in TypeScript first. May revisit during Python migration.

### Alternative 2: LangGraph

**Description:** Use LangGraph for explicit agent workflow graphs

**Pros:**

- More control over agent coordination flow
- Visual graph representation of workflow
- Better for complex multi-step workflows
- Built on LangChain ecosystem

**Cons:**

- Overkill for current simple routing logic
- Steeper learning curve
- Python-only
- Adds another abstraction layer

**Why rejected:** Current orchestration is simple (linear with one branch). LangGraph's complexity not justified yet. Consider for V2 if workflows become more complex.

### Alternative 3: Custom Multi-Prompt Orchestration

**Description:** Keep single provider, use different system prompts per query type

**Pros:**

- Simpler implementation
- No external framework dependency
- Lower latency (single LLM call)
- Easier debugging

**Cons:**

- No structured tool use (must rely on RAG always-on or prompt-based retrieval)
- Hard to compose operations (search → generate → validate)
- Prompt engineering becomes bottleneck
- Less extensible for future features

**Why rejected:** Doesn't solve core problems (tool use, composability, extensibility). Would require major refactor when adding booking or community features anyway.

### Alternative 4: Claude Tools API

**Description:** Use Anthropic's Claude with native tool calling

**Pros:**

- Excellent tool use capabilities
- Strong reasoning and safety features
- Good documentation and reliability

**Cons:**

- Vendor lock-in (different vendor than Gemini embeddings)
- Higher cost than Gemini Flash
- No native ADK-style agent framework
- Would need custom orchestration layer anyway

**Why rejected:** Adds another vendor (Anthropic) when already using Google for embeddings. ADK provides orchestration framework, not just tool calling.

---

## References

- **PR3.1 Plan:** [../../archive/plans/PR3.1-ADK-Multi-Agent-RAG.md](../../archive/plans/PR3.1-ADK-Multi-Agent-RAG.md)
- **Google ADK Docs:** https://firebase.google.com/docs/genkit
- **Implementation:** `apps/web/src/shared/lib/agent/` and `apps/web/src/shared/lib/orchestration/chat-orchestrator-adk.ts`
- **Related ADR:** [0003-groq-gemini-strategy.md](./0003-groq-gemini-strategy.md) — LLM provider strategy

---

## Notes

**Implementation Status:** ✅ Completed (PR3.1)

**Migration Strategy:**

- Model-provider code intentionally retained (not deleted per Step 5) to provide fallback during Python migration (PR3.2)
- `ENABLE_ADK=false` reverts to legacy single-provider orchestration
- Gradual rollout possible via feature flag

**Future Considerations:**

- May migrate to LangGraph during Python backend migration (PR3.2) if orchestration complexity increases
- Consider agent memory beyond session history (conversation summarization, user preferences)
- Evaluate agent performance metrics to optimize routing and tool use
- Add agent evaluation framework to measure response quality improvements

**Cost Impact:**

- Average 2-3 agent calls per query (retrieval + specialist + safety)
- Using Flash model mitigates cost increase
- Monitor token usage and optimize prompts if costs escalate

**Performance Monitoring:**

- Track P50/P95/P99 latency per agent
- Monitor tool call success rates
- Track query routing accuracy (correct agent selection)
- Measure end-to-end orchestration latency (<10s target)

---

**Last Updated:** January 1, 2026
