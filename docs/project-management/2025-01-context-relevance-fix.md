# Context Relevance Fix - January 2026

**Date**: 2026-01-31  
**Author**: GitHub Copilot  
**Issue**: Chat responses contextually wrong - mixing information from previous questions

---

## Problem Statement

Users reported that chat responses were contextually incorrect:

1. **Geography Confusion**: Asked "where can I dive in Indonesia?" → Response about Tioman (Malaysia)
2. **Context Contamination**: Asked "what certification does PADI offer?" → Response started with "I do not have information about diving in Tioman"
3. **Poor Follow-ups**: Generic, repetitive follow-up questions like "Is this for learning, planning a dive, or just curious?"

## Root Cause Analysis

### Issue 1: Conversation History Not Prioritized

**Location**: [backend/app/agents/retrieval.py](../backend/app/agents/retrieval.py)

The system included conversation history BUT didn't teach the LLM to prioritize the **current question** over historical context. When users changed topics:
- History contained Tioman → Indonesia question got Tioman answer
- History influenced interpretation even when irrelevant

**Key Insight**: The problem wasn't the AMOUNT of history, but the LACK OF PRIORITIZATION

### Issue 2: Missing Content

**Location**: `content/destinations/` only contains `Malaysia-Tioman/`

**Impact**: When asked about Indonesia:
1. RAG retrieval found no Indonesia content
2. Returned Tioman chunks (highest similarity match available)
3. LLM used Tioman information without recognizing topic mismatch

### Issue 3: Generic Follow-up Questions

**Location**: [backend/app/orchestration/conversation_manager.py](../backend/app/orchestration/conversation_manager.py)

Follow-up templates were too generic:
- "Is this for learning, planning a dive, or just curious?" (repetitive)
- "Which destination are you considering?" (too abrupt)
- No context awareness or variation

## Solution Implemented (v2 - Intelligent Context)

### Fix 1: Smart Context Prioritization

**File**: [backend/app/agents/retrieval.py](../backend/app/agents/retrieval.py)

**Changed**: ~~Reduce history window~~ → Keep 6 messages (3 turns) BUT mark current query as primary focus

```python
# Conversation history (recent context for continuity)
for msg in context.conversation_history[-6:]:  # Last 3 turns (6 messages)
    messages.append(LLMMessage(role=msg["role"], content=msg["content"]))

# Current query (marked as primary focus)
messages.append(LLMMessage(role="user", content=f"[CURRENT QUESTION]: {context.query}"))
```

**Rationale**:
- Keeps sufficient history for conversational continuity
- Explicitly marks current question with `[CURRENT QUESTION]` tag
- LLM learns to prioritize tagged query over historical context

### Fix 2: Topic Change Detection in Prompt

**File**: [backend/app/agents/retrieval.py](../backend/app/agents/retrieval.py)

Added explicit context handling rules to system prompt:

```python
CONTEXT HANDLING RULES (CRITICAL):
1. The user's message marked [CURRENT QUESTION] is your PRIMARY FOCUS
2. Previous conversation provides context but NEVER overrides the current question
3. If the current question is about a DIFFERENT topic than previous messages:
   - Answer ONLY the current question
   - Do NOT reference previous topics unless explicitly asked
4. If the current question relates to previous messages (uses "it", "there", "that"):
   - Use conversation history for context
5. When topics change (e.g., from Tioman to Indonesia, or from destinations to certifications):
   - Treat it as a NEW conversation thread
   - Do NOT carry over location/topic context from previous questions
```

**Rationale**:
- Teaches LLM to detect topic changes
- Maintains continuity for follow-up questions ("tell me more about that")
- Prevents cross-contamination between unrelated topics

### Fix 3: Contextual, Varied Follow-ups

**File**: [backend/app/orchestration/conversation_manager.py](../backend/app/orchestration/conversation_manager.py)

**Improved Templates**:
```python
FOLLOW_UP_TEMPLATES: Dict[IntentType, str] = {
    IntentType.INFO_LOOKUP: "Would you like more details or have other questions?",
    IntentType.DIVE_PLANNING: "What time of year are you thinking of diving?",
    IntentType.CONDITIONS: "Are you looking at any specific months?",
    # ... more contextual variations
}
```

**Enhanced Generation Rules**:
- Increased character limit: 100 → 120 for more natural questions
- Removed overly strict validations (e.g., no numbers allowed)
- Added examples of good vs bad follow-ups
- Required contextual relevance to user's last message

**Rationale**:
- More natural, conversational follow-ups
- Context-aware (responds to what user just asked)
- Avoids repetitive generic questions

### Fix 4: Enhanced RAG Logging

**File**: [backend/app/services/rag/pipeline.py](../backend/app/services/rag/pipeline.py)

Added detailed similarity scoring and debug logging:

```python
avg_similarity = sum(r.similarity for r in results) / len(results)
logger.info(
    f"RAG pipeline: retrieved {len(results)} chunks | "
    f"avg_similarity={avg_similarity:.3f}, max_similarity={max_similarity:.3f}"
)
logger.debug(f"Top RAG result: similarity={top_result.similarity:.3f}, ...")
```

**Rationale**:
- Visibility into RAG retrieval quality
- Helps identify when irrelevant content is being returned
- Aids future debugging of context issues

## Testing

### Test Scenario 1: Topic Change Detection

**Query Sequence**:
1. "tell me about Tioman diving"
2. "where can I dive in Indonesia?"

**Expected Behavior**:
- Question 2 should recognize Indonesia ≠ Tioman
- Should NOT return Tioman information
- Should explicitly state Indonesia content is not available yet

### Test Scenario 2: Conversational Continuity

**Query Sequence**:
1. "tell me about Tioman diving"
2. "what are the best sites there?"

**Expected Behavior**:
- Question 2 should maintain context ("there" = Tioman)
- 6-message history window provides continuity
- Seamless conversation flow

### Test Scenario 3: Multiple Unrelated Questions

**Query Sequence**:
1. "where can I dive in Tioman?"
2. "what certification does PADI offer?"
3. "tell me about equalization techniques"

**Expected Behavior**:
- Each question treated independently
- No contamination (e.g., PADI response shouldn't mention Tioman)
- Follow-ups are contextual and varied

### Test Scenario 4: Follow-up Quality

**Expected**:
- No repetitive "Is this for learning or planning?" questions
- Contextual follow-ups based on user's actual question
- Natural conversation flow

## Validation

After deploying changes:

1. ✅ Backend auto-reloaded with changes
2. ⏳ Test with topic changes (Tioman → Indonesia)
3. ⏳ Test with follow-up questions ("tell me more about that")
4. ⏳ Verify follow-up questions are contextual and varied
5. ⏳ Check RAG logs show proper similarity scores

## Key Design Principles

1. **Preserve Context, Add Prioritization**: Don't discard history - teach LLM to use it intelligently
2. **Explicit Markers**: Use `[CURRENT QUESTION]` tag to signal focus
3. **Topic Change Detection**: Detect when user switches topics (location, certification, technique)
4. **Contextual AI**: Follow-ups must respond to what user just asked, not generic templates
5. **Conversational Flow**: Balance continuity with independence

## Future Improvements

### Short-term (Next Sprint)

1. **Add More Content**: Create Indonesia destination guides
2. **Semantic Topic Detection**: Use embeddings to detect topic similarity between questions
3. **Dynamic History Windowing**: Adjust window size based on topic coherence

### Long-term

1. **Multi-Thread Conversations**: Separate conversation threads by topic
2. **Entity Tracking**: Track mentioned entities (locations, certifications) and clear when topic changes
3. **Context Relevance Scoring**: Score each history message for relevance to current query

## Lessons Learned

1. **History ≠ Problem**: Conversation history is essential for continuity - the issue is prioritization
2. **Explicit > Implicit**: Explicit markers (`[CURRENT QUESTION]`) work better than expecting LLM to infer
3. **Context Rules Matter**: Clear rules about topic changes prevent cross-contamination
4. **Follow-ups Need Context**: Generic templates create robotic conversation - contextual variety is key
5. **Balance is Key**: Need sufficient history (6 messages) but with proper prioritization

## Related Documentation

- [backend/app/agents/retrieval.py](../backend/app/agents/retrieval.py) - Retrieval agent implementation
- [backend/app/services/rag/pipeline.py](../backend/app/services/rag/pipeline.py) - RAG pipeline
- [backend/app/orchestration/conversation_manager.py](../backend/app/orchestration/conversation_manager.py) - Follow-up generation
- [backend/app/orchestration/context_builder.py](../backend/app/orchestration/context_builder.py) - Context building

---

**Status**: Deployed  
**Version**: 2.0 (Intelligent Context)  
**Next Review**: After user testing with topic changes and follow-up quality
