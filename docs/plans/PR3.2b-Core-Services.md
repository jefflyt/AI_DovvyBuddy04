# PR3.2b: Core Services (Embeddings, LLM, RAG Pipeline)

**Status:** Draft  
**Parent Epic:** PR3.2 (Python-First Backend Migration)  
**Date:** January 1, 2026  
**Duration:** 2-3 weeks

---

## Goal

Migrate embedding generation, LLM provider abstraction, and RAG pipeline (chunking + retrieval) from TypeScript to Python. Backend can generate embeddings, call LLMs, and perform vector retrieval with behavior equivalent to TypeScript implementation.

---

## Scope

### In Scope

- Embedding provider abstraction (base class + Gemini implementation)
- Batch embedding generation and caching (in-memory)
- LLM provider abstraction (base class + Groq/Gemini implementations)
- Retry logic and error handling (tenacity library)
- Text chunking logic (markdown-aware, token counting with tiktoken)
- Vector retrieval service using SQLAlchemy + pgvector
- RAG pipeline orchestration (query → embed → retrieve → format)
- Comparison tests: Python vs TypeScript RAG results (50+ queries)
- Benchmark tests: latency and accuracy metrics

### Out of Scope

- Agent logic and chat orchestration (PR3.2c)
- Content ingestion scripts (PR3.2d)
- Frontend integration (PR3.2e)
- Production deployment (PR3.2f)
- Redis-based caching (deferred to post-migration optimization)

---

## Backend Changes

### New Modules

**Services Structure:**
```
backend/app/services/
├── __init__.py
├── embeddings/
│   ├── __init__.py
│   ├── base.py                    # Embedding provider interface
│   ├── gemini.py                  # Gemini embedding provider
│   ├── cache.py                   # In-memory embedding cache
│   └── factory.py                 # Provider factory
├── llm/
│   ├── __init__.py
│   ├── base.py                    # LLM provider interface
│   ├── groq.py                    # Groq provider implementation
│   ├── gemini.py                  # Gemini provider implementation
│   └── factory.py                 # Provider factory (env-based)
└── rag/
    ├── __init__.py
    ├── chunker.py                 # Text chunking logic
    ├── retriever.py               # Vector retrieval service
    ├── pipeline.py                # RAG orchestration
    └── types.py                   # RAG-specific types

backend/tests/
├── unit/services/
│   ├── test_embeddings.py
│   ├── test_llm.py
│   ├── test_chunker.py
│   ├── test_retriever.py
│   └── test_rag_pipeline.py
├── integration/services/
│   ├── test_embeddings_integration.py
│   ├── test_llm_integration.py
│   └── test_rag_integration.py
└── comparison/
    ├── test_embedding_comparison.py
    ├── test_chunking_comparison.py
    └── test_rag_comparison.py

backend/scripts/
├── test_embeddings.py             # Manual embedding test
├── test_llm.py                    # Manual LLM test
├── test_rag.py                    # Manual RAG test
└── benchmark_rag.py               # RAG benchmarking (placeholder for PR3.2d)
```

**Key Implementation Files:**

1. **Embedding Provider** (`services/embeddings/`)
   - Base interface with `embed_text()` and `embed_batch()` methods
   - Gemini provider using `google.generativeai` SDK
   - In-memory LRU cache (1000 entries, TTL 1 hour)
   - Batch processing (up to 100 texts per API call)
   - Retry logic with exponential backoff

2. **LLM Provider** (`services/llm/`)
   - Base interface with `generate()` method
   - Groq provider using `groq` SDK
   - Gemini provider using `google.generativeai` SDK
   - Factory pattern for env-based provider selection
   - Error handling and retry logic
   - Token counting and usage tracking

3. **RAG Pipeline** (`services/rag/`)
   - Text chunker: markdown-aware splitting, tiktoken token counting
   - Retriever: vector search with pgvector, similarity scoring
   - Pipeline: orchestrate query → embed → retrieve → format
   - Configurable top-k and similarity threshold

### Modified Modules

- `backend/app/core/config.py` — Add LLM/embedding configuration
  - `DEFAULT_LLM_PROVIDER`: groq | gemini
  - `DEFAULT_LLM_MODEL`: Model name
  - `EMBEDDING_MODEL`: text-embedding-004
  - `ENABLE_RAG`: true | false
  - `RAG_TOP_K`: Default 5
  - `RAG_MIN_SIMILARITY`: Default 0.5

- `backend/pyproject.toml` — Add dependencies:
  - `google-generativeai>=0.3.2`
  - `groq>=0.4.2`
  - `tiktoken>=0.5.2`
  - `tenacity>=8.2.3`

---

## Frontend Changes

None (backend-only PR)

---

## Data Changes

None (uses existing embeddings in `content_embeddings` table)

---

## Infra / Config

### Environment Variables (Additions)

```bash
# LLM Provider Configuration
DEFAULT_LLM_PROVIDER=groq              # groq | gemini
DEFAULT_LLM_MODEL=gemini-2.0-flash     # Model name (Gemini standard per copilot-instructions.md)
LLM_TEMPERATURE=0.7                    # Generation temperature (0.0-1.0)
LLM_MAX_TOKENS=2048                    # Maximum tokens per generation

# Embedding Configuration
EMBEDDING_MODEL=text-embedding-004     # Gemini embedding model (768 dimensions)
EMBEDDING_BATCH_SIZE=100               # Max texts per batch request
EMBEDDING_CACHE_SIZE=1000              # In-memory cache size
EMBEDDING_CACHE_TTL=3600               # Cache TTL in seconds

# RAG Configuration
ENABLE_RAG=true                        # Enable/disable RAG pipeline
RAG_TOP_K=5                            # Number of chunks to retrieve
RAG_MIN_SIMILARITY=0.5                 # Minimum cosine similarity threshold
RAG_CHUNK_SIZE=512                     # Target chunk size in tokens
RAG_CHUNK_OVERLAP=50                   # Token overlap between chunks

# Retry Configuration
LLM_MAX_RETRIES=3                      # Max retry attempts for LLM calls
LLM_RETRY_DELAY=1.0                    # Initial retry delay (seconds)
EMBEDDING_MAX_RETRIES=3                # Max retry attempts for embeddings
EMBEDDING_RETRY_DELAY=1.0              # Initial retry delay (seconds)
```

### Feature Flags

- `ENABLE_RAG`: Toggle RAG pipeline on/off (for testing without RAG)

---

## Testing

### Unit Tests

**Coverage Target:** ≥80%

**Test Files:**

1. **test_embeddings.py**
   - Embedding provider interface compliance
   - Gemini provider initialization
   - Batch embedding generation (mocked API)
   - Cache hit/miss behavior
   - Error handling (API errors, invalid inputs)
   - Retry logic (simulate failures)

2. **test_llm.py**
   - LLM provider interface compliance
   - Groq provider initialization
   - Gemini provider initialization
   - Provider factory (env-based selection)
   - Generation with different parameters
   - Error handling and retries
   - Token counting

3. **test_chunker.py**
   - Text chunking with various inputs
   - Markdown-aware splitting (preserve headers, code blocks)
   - Token counting accuracy
   - Chunk overlap behavior
   - Metadata preservation
   - Edge cases (empty text, very long text, special characters)

4. **test_retriever.py**
   - Vector retrieval (mocked database)
   - Similarity scoring
   - Top-k selection
   - Filtering by similarity threshold
   - Error handling (no results, database errors)

5. **test_rag_pipeline.py**
   - End-to-end RAG flow (mocked components)
   - Query → embed → retrieve → format
   - Error handling at each stage
   - Empty results handling

**Mocking Strategy:**
- Mock external API calls (Gemini, Groq)
- Mock database queries (use in-memory test data)
- Use pytest fixtures for common test data

### Integration Tests

**Test Files:**

1. **test_embeddings_integration.py**
   - Generate embeddings with real Gemini API (5 test texts)
   - Verify embedding dimensions (768)
   - Batch embedding generation
   - Cache behavior with real data
   - Rate limiting behavior

2. **test_llm_integration.py**
   - Call Groq API with test prompts (3 prompts)
   - Call Gemini API with test prompts (3 prompts)
   - Verify response format and quality
   - Test different temperature values
   - Error handling with invalid API keys (temporarily)

3. **test_rag_integration.py**
   - End-to-end RAG pipeline with test database
   - Insert test embeddings
   - Query similar chunks
   - Verify retrieval accuracy
   - Test with various query types

**API Rate Limiting:**
- Limit integration test runs (use `pytest -m "not slow"` for CI)
- Cache API responses for repeated tests (VCR.py or similar)
- Use test API keys with lower rate limits

### Comparison Tests (Critical)

**Test Files:**

1. **test_embedding_comparison.py**
   - Generate embeddings for 20 sample texts with both TS and Python
   - Compare embedding vectors (cosine similarity ≈ 1.0)
   - Verify dimensions match (768)
   - Acceptance: cosine similarity ≥ 0.98 for same input

2. **test_chunking_comparison.py**
   - Chunk 10 sample markdown files with both implementations
   - Compare chunk boundaries and IDs
   - Compare token counts
   - Acceptance: ≥90% chunk boundary match

3. **test_rag_comparison.py**
   - Run 50+ test queries through both RAG systems
   - Compare top-5 results for each query
   - Calculate result overlap percentage
   - Acceptance: ≥80% overlap in top-5 results

**Test Data:**
- Use actual content files from `content/` directory
- Use hand-crafted test queries covering all domains (cert, trip, safety)
- Document any expected differences

### Manual Checks

```bash
# 1. Test embedding generation
cd backend
python -m scripts.test_embeddings "What is PADI Open Water?"

# 2. Test LLM call (Groq)
python -m scripts.test_llm --provider groq "Explain buoyancy control"

# 3. Test LLM call (Gemini)
python -m scripts.test_llm --provider gemini "Explain buoyancy control"

# 4. Test RAG pipeline
python -m scripts.test_rag "What certifications do I need for Tioman?"

# 5. Compare with TypeScript RAG
# Run same query through TypeScript implementation
cd ..
pnpm tsx scripts/test-rag.ts "What certifications do I need for Tioman?"

# 6. Benchmark RAG performance
cd backend
python -m scripts.benchmark_rag --queries 50 --output benchmark-results.json
```

---

## Verification

### Commands

```bash
# Testing
pytest tests/unit/services                          # Unit tests only
pytest tests/integration/services                   # Integration tests (real APIs)
pytest tests/comparison                             # Comparison tests
pytest tests/integration/services -m "not slow"     # Skip slow tests (for CI)

# Coverage
pytest tests/unit/services --cov=app/services --cov-report=html

# Manual Scripts
python -m scripts.test_embeddings "test text"
python -m scripts.test_llm --provider groq "test prompt"
python -m scripts.test_rag "test query"
```

### Manual Verification Checklist

**Embedding Provider:**
- [ ] Embedding generation returns 768-dimensional vectors
- [ ] Batch embedding processes multiple texts correctly
- [ ] Cache reduces API calls (verify logs)
- [ ] Retry logic works (test with invalid API key, then restore)
- [ ] Embeddings for same text (TS vs Python) have cosine similarity ≥ 0.98

**LLM Provider:**
- [ ] Groq provider returns coherent responses
- [ ] Gemini provider returns coherent responses (using gemini-2.0-flash per standards)
- [ ] Provider factory selects correct provider based on env var
- [ ] Error handling graceful (invalid API key, rate limits)
- [ ] Token counting accurate

**RAG Pipeline:**
- [ ] Text chunking produces same boundaries as TypeScript (≥90% match)
- [ ] Token counts match between implementations
- [ ] Vector retrieval returns relevant chunks for test queries
- [ ] RAG comparison tests pass (≥80% result overlap)
- [ ] Pipeline handles empty results gracefully
- [ ] Performance acceptable (latency benchmarks)

**Code Quality:**
- [ ] All unit tests pass (≥80% coverage)
- [ ] All integration tests pass
- [ ] All comparison tests pass
- [ ] Linting passes (`ruff check .`)
- [ ] Formatting passes (`ruff format --check .`)
- [ ] Type checking passes (`mypy app`)

---

## Rollback Plan

### Feature Flag

`ENABLE_RAG=false` to disable RAG pipeline (backend uses empty context)

### Revert Strategy

1. **Partial revert:** Remove service modules, keep database layer from PR3.2a
2. **No impact:** Python backend still not connected to frontend
3. **No database changes:** No schema or data modifications
4. **Execution time:** <5 minutes (git revert + redeploy if needed)

---

## Dependencies

### PRs that must be merged

- ✅ **PR3.2a** (Backend Foundation) — Database layer and repositories required for vector retrieval

### External Dependencies

- Gemini API key (already have) — for embeddings and LLM
- Groq API key (already have) — for LLM
- Existing content embeddings in database (from TypeScript ingestion)
- Python 3.11+ with required packages

---

## Risks & Mitigations

### Risk 1: Embedding generation behavior differs from TypeScript

**Likelihood:** Medium  
**Impact:** High (RAG quality degradation if embeddings incompatible)

**Mitigation:**
- Extensive comparison tests with 20+ sample texts
- Calculate cosine similarity for same inputs (expect ≥0.98)
- Use same Gemini model and parameters as TypeScript
- Document any observed differences
- If similarity <0.98, investigate API version differences

**Acceptance Criteria:**
- Cosine similarity ≥0.98 for same text input
- Embedding dimensions match (768)
- Batch vs single embedding produce same results

### Risk 2: Chunking logic produces different boundaries

**Likelihood:** Medium  
**Impact:** Medium (different RAG results, but not necessarily worse)

**Mitigation:**
- Detailed comparison tests with 10 sample markdown files
- Manual review of chunk boundaries for edge cases
- Document intentional differences (if any optimization made)
- Accept minor differences if RAG quality maintained

**Acceptance Criteria:**
- ≥90% chunk boundary match with TypeScript
- Token counts within 5% tolerance
- Markdown structure preserved (headers, code blocks)

### Risk 3: RAG retrieval quality degrades

**Likelihood:** Low-Medium  
**Impact:** High (user experience degradation)

**Mitigation:**
- Extensive comparison tests (50+ queries)
- Measure result overlap (expect ≥80%)
- Benchmark latency (should be equal or better)
- Manual review of 20+ sample results
- A/B test with TypeScript implementation if needed

**Acceptance Criteria:**
- ≥80% overlap in top-5 results for same query
- Latency ≤ TypeScript implementation (target: <500ms P95)
- No obvious quality regressions in manual review

### Risk 4: API rate limits during testing

**Likelihood:** Medium  
**Impact:** Low (test execution delays)

**Mitigation:**
- Limit integration test runs (use markers: `@pytest.mark.slow`)
- Cache API responses for repeated tests (VCR.py)
- Use separate test API keys with lower quotas
- Run full integration tests manually, not in every CI run

**Acceptance Criteria:**
- CI completes in <10 minutes (skip slow tests)
- Manual integration tests can be run on-demand
- No production API key usage in tests

### Risk 5: LLM provider abstraction leaks details

**Likelihood:** Low  
**Impact:** Medium (difficult to switch providers)

**Mitigation:**
- Design clean provider interface (base class)
- Test both Groq and Gemini providers
- Ensure factory pattern works correctly
- Document provider-specific quirks

**Acceptance Criteria:**
- Switching providers requires only env var change
- Both providers return compatible response format
- No provider-specific code outside provider classes

---

## Trade-offs

### Trade-off 1: Custom RAG Pipeline vs LangChain

**Chosen:** Custom RAG pipeline

**Rationale:**
- More control over chunking and retrieval logic
- Simpler dependencies (no LangChain)
- Easier to optimize and debug
- Proven pattern from TypeScript implementation

**Trade-off:**
- More code to maintain
- Missing LangChain ecosystem features (document loaders, advanced retrievers)

**Decision:** Accept trade-off. Custom pipeline sufficient for V1, can migrate to LangChain later if needed.

### Trade-off 2: In-Memory Cache vs Redis

**Chosen:** In-memory cache for V1

**Rationale:**
- Simpler setup (no Redis dependency)
- Sufficient for single-instance deployment
- Faster for local development

**Trade-off:**
- Cache doesn't persist across restarts
- Not shared across multiple instances (future scaling)

**Decision:** Accept trade-off. Revisit Redis in PR3.2f if production needs multi-instance caching.

### Trade-off 3: Comparison Test Threshold (80% vs 95%)

**Chosen:** 80% result overlap threshold

**Rationale:**
- Allows for minor differences in vector search (floating point, sorting)
- Embeddings may differ slightly between API versions
- Focus on "no quality regression" vs "exact match"

**Trade-off:**
- May miss subtle quality issues
- Requires manual review to confirm 80% is acceptable

**Decision:** Accept 80% threshold, but manually review all failing cases.

---

## Open Questions

### Q1: Should we batch all embedding calls or allow single calls?

**Context:** Batching improves performance but adds complexity

**Options:**
- A) Always batch (even single texts)
- B) Single calls for 1 text, batch for ≥2 texts
- C) Configurable (caller decides)

**Recommendation:** Option B (smart batching)

**Decision:** Option B ✅

### Q2: What should embedding cache TTL be?

**Context:** Balance freshness vs API cost

**Options:**
- A) 1 hour (frequent refresh)
- B) 24 hours (daily refresh)
- C) No expiry (until restart)

**Recommendation:** 1 hour for dev, 24 hours for production

**Decision:** Configurable via `EMBEDDING_CACHE_TTL` env var ✅

### Q3: Should we re-ingest content with Python embeddings?

**Context:** Existing embeddings from TypeScript, new embeddings from Python may differ

**Options:**
- A) Keep existing embeddings (faster)
- B) Re-ingest with Python (cleaner)
- C) Dual embeddings (comparison)

**Recommendation:** Option A if comparison tests pass (≥0.98 similarity), Option B if they fail

**Decision:** Defer to comparison test results ⏳

### Q4: Should RAG pipeline return raw chunks or formatted context?

**Context:** Affects how agents consume RAG results

**Options:**
- A) Raw chunks (agents format)
- B) Formatted text (pipeline formats)
- C) Both (configurable)

**Recommendation:** Option A (raw chunks) for flexibility

**Decision:** Option A ✅

---

## Success Criteria

### Technical Success

- [ ] Embedding provider generates 768-dimensional vectors
- [ ] LLM providers (Groq + Gemini) return coherent responses
- [ ] Text chunking produces markdown-aware chunks with token counts
- [ ] Vector retrieval returns relevant results for test queries
- [ ] RAG pipeline orchestrates query → embed → retrieve → format
- [ ] All unit tests pass (≥80% coverage)
- [ ] All integration tests pass
- [ ] All comparison tests pass:
  - [ ] Embedding similarity ≥0.98
  - [ ] Chunking boundary match ≥90%
  - [ ] RAG result overlap ≥80%
- [ ] Performance acceptable (latency ≤ TypeScript baseline)

### Quality Success

- [ ] Code review complete (self-review + peer if available)
- [ ] Linting, formatting, type checking pass
- [ ] Documentation complete (docstrings, README updates)
- [ ] No obvious bugs in manual testing

### Comparison Success

- [ ] 50+ test queries run through both implementations
- [ ] Result overlap ≥80% achieved
- [ ] Manual review of differences shows no quality regressions
- [ ] Benchmark results documented

---

## Next Steps

After PR3.2b is merged:

1. **Analyze comparison results:** Document any differences and confirm acceptability
2. **PR3.2c:** Implement agent system and orchestration using these services
3. **Monitor:** Watch for any issues in local development

---

## Related Documentation

- **Parent Epic:** `/docs/plans/PR3.2-Python-Backend-Migration.md`
- **Previous PR:** `/docs/plans/PR3.2a-Backend-Foundation.md`
- **TypeScript RAG:** `/docs/plans/PR2-RAG-Pipeline.md`
- **TypeScript Orchestration:** `/docs/plans/PR3-Model-Provider-Session.md`
- **Gemini Embeddings:** https://ai.google.dev/tutorials/python_quickstart#embeddings
- **Groq API:** https://console.groq.com/docs/quickstart
- **tiktoken:** https://github.com/openai/tiktoken

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-01 | AI Assistant | Initial draft |

---

**Status:** 🟡 Draft — Ready after PR3.2a complete

**Estimated Duration:** 2-3 weeks  
**Complexity:** High  
**Risk Level:** Medium
