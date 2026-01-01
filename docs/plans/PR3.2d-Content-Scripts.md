# PR3.2d: Content Processing Scripts

**Status:** Draft  
**Parent Epic:** PR3.2 (Python-First Backend Migration)  
**Date:** January 1, 2026  
**Duration:** 1-2 weeks

---

## Goal

Migrate offline content processing scripts (validation, ingestion, benchmarking) from TypeScript to Python. Content can be validated, ingested with embeddings, and RAG performance benchmarked using Python scripts matching or exceeding TypeScript functionality.

---

## Scope

### In Scope

- Content validation script (markdown parsing, frontmatter validation, structure checks)
- Content ingestion script (file reading, chunking, embedding generation, database insertion)
- Incremental ingestion (detect file changes, skip unchanged files)
- Clear embeddings script (database cleanup utility)
- RAG benchmark script (test queries, accuracy/latency metrics, JSON output)
- Python script wrappers callable from package.json
- CI/CD integration (run validation in GitHub Actions)
- Comparison with TypeScript scripts (validate same files, verify output)

### Out of Scope

- Frontend integration (PR3.2e)
- Production deployment (PR3.2f)
- Content authoring tools or CMS
- Automated content updates or scraping

---

## Backend Changes

### New Modules

**Scripts Structure:**
```
backend/scripts/
├── __init__.py
├── validate_content.py            # Content validation
├── ingest_content.py              # Content ingestion with embeddings
├── benchmark_rag.py               # RAG benchmarking
├── clear_embeddings.py            # Database cleanup
├── common/
│   ├── __init__.py
│   ├── file_utils.py              # File I/O and hashing
│   ├── markdown_parser.py         # Markdown parsing and frontmatter
│   └── cli.py                     # CLI utilities (progress bars, colors)

backend/tests/unit/scripts/
├── test_validate_content.py
├── test_ingest_content.py
├── test_markdown_parser.py
└── test_file_utils.py

backend/tests/integration/scripts/
└── test_full_ingestion.py
```

**Key Scripts:**

1. **validate_content.py**
   - Scan content directory for markdown files
   - Parse frontmatter (YAML)
   - Validate required fields (title, description, tags, etc.)
   - Check markdown structure (headers, links, formatting)
   - Report errors with file path and line number
   - Exit code 0 (success) or 1 (validation errors)

2. **ingest_content.py**
   - Scan content directory
   - Read and parse markdown files
   - Chunk text using RAG chunker (from PR3.2b)
   - Generate embeddings (batch processing)
   - Insert into database (content_embeddings table)
   - Incremental mode: hash files, skip if unchanged
   - Progress bar and statistics (files processed, chunks created, time taken)

3. **benchmark_rag.py**
   - Load test queries from JSON file
   - Run each query through RAG pipeline
   - Measure latency (P50, P95, P99)
   - Measure retrieval accuracy (if ground truth provided)
   - Output results as JSON (for tracking over time)
   - Compare with baseline (TypeScript RAG results)

4. **clear_embeddings.py**
   - Delete all records from content_embeddings table
   - Optional: filter by content_path pattern
   - Confirmation prompt before deletion
   - Statistics (records deleted, execution time)

### Modified Modules

- `backend/README.md` — Add script documentation section
  - Usage examples
  - Command-line options
  - Common workflows

- `.github/workflows/backend-ci.yml` — Add content validation step
  - Run on content/ changes
  - Fail CI if validation errors

- `package.json` — Add Python script wrappers:
  ```json
  {
    "scripts": {
      "content:validate-py": "cd backend && python -m scripts.validate_content",
      "content:ingest-py": "cd backend && python -m scripts.ingest_content",
      "content:ingest-incremental-py": "cd backend && python -m scripts.ingest_content --incremental",
      "content:benchmark-py": "cd backend && python -m scripts.benchmark_rag",
      "content:clear-py": "cd backend && python -m scripts.clear_embeddings"
    }
  }
  ```

---

## Frontend Changes

None (scripts are offline tools)

---

## Data Changes

**No schema changes.** Scripts use existing `content_embeddings` table.

**Data operations:**
- **validate_content.py:** Read-only (no database access)
- **ingest_content.py:** INSERT into content_embeddings (may DELETE old chunks if re-ingesting)
- **benchmark_rag.py:** Read-only (SELECT queries)
- **clear_embeddings.py:** DELETE from content_embeddings

**Incremental ingestion strategy:**
- Calculate file hash (SHA256)
- Store hash in metadata JSONB field
- On re-run: compare hashes, skip if unchanged
- If changed: delete old chunks, re-chunk and insert new

---

## Infra / Config

### Environment Variables (Additions)

```bash
# Content Configuration
CONTENT_DIR=../content              # Path to content directory (relative to backend/)
INGEST_BATCH_SIZE=10                # Embedding batch size
INGEST_INCREMENTAL=false            # Enable incremental ingestion
INGEST_DRY_RUN=false                # Dry run mode (no database writes)

# Benchmark Configuration
BENCHMARK_QUERIES_FILE=../tests/fixtures/benchmark_queries.json
BENCHMARK_OUTPUT_FILE=benchmark-results.json
BENCHMARK_ITERATIONS=1              # Number of iterations per query
```

### CI/CD Additions

**Update `.github/workflows/backend-ci.yml`:**

```yaml
- name: Validate Content
  if: contains(github.event.head_commit.modified, 'content/')
  run: |
    cd backend
    python -m scripts.validate_content
```

**Optional: Content validation workflow**

```yaml
# .github/workflows/content-validation.yml
name: Content Validation

on:
  pull_request:
    paths:
      - 'content/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -e .
      
      - name: Validate content
        run: |
          cd backend
          python -m scripts.validate_content
```

---

## Testing

### Unit Tests

**Coverage Target:** ≥80%

**Test Files:**

1. **test_validate_content.py**
   - Valid markdown passes validation
   - Missing frontmatter detected
   - Invalid frontmatter format (not YAML)
   - Missing required fields
   - Malformed markdown (broken links, invalid headers)
   - Multiple files with errors (report all)

2. **test_ingest_content.py**
   - File reading and parsing
   - Chunking integration (use mocked chunker)
   - Embedding generation (use mocked embedding provider)
   - Database insertion (use mocked repository)
   - Incremental ingestion (file hash comparison)
   - Error handling (corrupted files, API failures)

3. **test_markdown_parser.py**
   - Extract frontmatter (YAML)
   - Parse markdown body
   - Handle edge cases (no frontmatter, empty file, special characters)

4. **test_file_utils.py**
   - File hash calculation (SHA256)
   - File modification detection
   - Directory traversal
   - Path resolution (relative/absolute)

### Integration Tests

**Test Files:**

1. **test_full_ingestion.py**
   - Create test content files (3-5 files)
   - Run ingestion script
   - Verify embeddings inserted in test database
   - Verify chunk count matches expected
   - Verify metadata fields populated
   - Test incremental mode: modify 1 file, re-run, verify only 1 file processed

### Comparison Tests

**Test Scenarios:**

1. **Validate same content with TS and Python**
   - Run both validation scripts on same content directory
   - Compare error reports (should be identical)
   - Acceptance: 100% match on validation results

2. **Compare embedding generation**
   - Ingest same file with TS and Python
   - Compare embedding vectors (cosine similarity)
   - Acceptance: ≥0.98 similarity (already tested in PR3.2b)

3. **Compare chunk boundaries**
   - Chunk same file with both implementations
   - Compare chunk texts and metadata
   - Acceptance: ≥90% boundary match (already tested in PR3.2b)

### Manual Checks

```bash
# 1. Validate content
cd backend
python -m scripts.validate_content
# Expected: Report of all files, any validation errors

# 2. Ingest content (full)
python -m scripts.ingest_content
# Expected: Progress bar, statistics, embeddings in database

# 3. Verify embeddings inserted
psql $DATABASE_URL -c "SELECT COUNT(*), content_path FROM content_embeddings GROUP BY content_path"

# 4. Incremental ingestion (no changes)
python -m scripts.ingest_content --incremental
# Expected: "No changes detected" for all files

# 5. Modify a file and re-run
echo "New content" >> ../content/certifications/padi/open-water.md
python -m scripts.ingest_content --incremental
# Expected: Only modified file processed

# 6. Benchmark RAG
python -m scripts.benchmark_rag --queries 20 --output benchmark-results.json
# Expected: JSON file with latency and accuracy metrics

# 7. Compare with TypeScript
cd ..
pnpm content:ingest
# Compare chunk counts and embedding dimensions
```

---

## Verification

### Commands

```bash
# Unit tests
pytest tests/unit/scripts

# Integration tests
pytest tests/integration/scripts

# Run scripts
cd backend
python -m scripts.validate_content
python -m scripts.ingest_content [--incremental] [--dry-run]
python -m scripts.benchmark_rag
python -m scripts.clear_embeddings

# From project root (via package.json)
cd ..
pnpm content:validate-py
pnpm content:ingest-py
pnpm content:ingest-incremental-py
pnpm content:benchmark-py
```

### Manual Verification Checklist

**Validation Script:**
- [ ] Detects missing frontmatter
- [ ] Detects invalid YAML syntax
- [ ] Detects missing required fields
- [ ] Detects broken markdown links
- [ ] Reports errors with file path and line number
- [ ] Exit code 0 for valid content, 1 for errors

**Ingestion Script:**
- [ ] Processes all markdown files in content directory
- [ ] Chunks text using markdown-aware chunker
- [ ] Generates embeddings in batches
- [ ] Inserts embeddings into database
- [ ] Shows progress bar during execution
- [ ] Reports statistics (files processed, chunks created, time)
- [ ] Incremental mode skips unchanged files (verify with logs)
- [ ] Incremental mode re-processes modified files only

**Benchmark Script:**
- [ ] Loads test queries from JSON file
- [ ] Runs each query through RAG pipeline
- [ ] Measures latency (P50, P95, P99)
- [ ] Outputs results as JSON
- [ ] Benchmark results comparable to TypeScript baseline

**Clear Script:**
- [ ] Prompts for confirmation before deletion
- [ ] Deletes all embeddings (or filtered by pattern)
- [ ] Reports deletion statistics

**CI Integration:**
- [ ] Content validation runs in GitHub Actions
- [ ] CI fails if validation errors detected
- [ ] Workflow triggers on content/ changes

**Comparison:**
- [ ] Validation results match TypeScript 100%
- [ ] Embedding generation matches (≥0.98 similarity)
- [ ] Chunk boundaries match (≥90%)
- [ ] Performance comparable (≤2x slower acceptable)

---

## Rollback Plan

### Feature Flag

None (scripts are offline tools, no feature flag needed)

### Revert Strategy

1. **Continue using TypeScript scripts:** `pnpm content:ingest` (existing)
2. **Delete Python scripts:** Remove `backend/scripts/` directory
3. **No impact:** Scripts run offline, no production system impact
4. **Execution time:** <1 minute

---

## Dependencies

### PRs that must be merged

- ✅ **PR3.2a** (Backend Foundation) — Database layer required for ingestion
- ✅ **PR3.2b** (Core Services) — Chunking and embedding services required

### External Dependencies

- Content files in `content/` directory (already exist)
- Gemini API key (for embedding generation)
- Test database (for integration tests)

---

## Risks & Mitigations

### Risk 1: Python scripts produce different embeddings than TypeScript

**Likelihood:** Low (already tested in PR3.2b)  
**Impact:** High (RAG quality change)

**Mitigation:**
- Comparison tests already passed in PR3.2b (≥0.98 similarity)
- Use same embedding model and parameters
- If drift detected, investigate and fix in PR3.2b services
- Option: Clear and re-ingest all content with Python (clean slate)

**Acceptance Criteria:**
- Embeddings match PR3.2b comparison test results
- RAG retrieval quality maintained

### Risk 2: Performance significantly worse than TypeScript

**Likelihood:** Medium  
**Impact:** Low (offline scripts, not latency-sensitive)

**Mitigation:**
- Benchmark both implementations
- Optimize hot paths (batching, parallelization)
- Acceptable if within 2x slower (offline process)

**Acceptance Criteria:**
- Ingestion completes in reasonable time (<5 minutes for full content set)
- Performance within 2x of TypeScript (or better)

### Risk 3: Incremental ingestion misses changes or re-processes unnecessarily

**Likelihood:** Medium  
**Impact:** Medium (wasted API calls, incorrect embeddings)

**Mitigation:**
- Hash-based change detection (SHA256)
- Manual verification with test files (modify, re-run, check logs)
- Log all file processing decisions (skipped/processed)
- Integration test for incremental behavior

**Acceptance Criteria:**
- Unchanged files skipped (verified in logs)
- Modified files re-processed (verified in logs)
- Hash stored in metadata for debugging

### Risk 4: Validation rules drift from TypeScript

**Likelihood:** Low  
**Impact:** Medium (inconsistent validation)

**Mitigation:**
- Comparison test (validate same content with both)
- Document validation rules explicitly
- Keep rules in sync during transition

**Acceptance Criteria:**
- 100% match in validation results (same errors detected)

---

## Trade-offs

### Trade-off 1: Rewrite Scripts vs Wrap TypeScript

**Chosen:** Rewrite in Python

**Rationale:**
- Consistency (all backend code in Python)
- Easier maintenance (one language)
- Better integration with Python services (chunker, embeddings)
- Learning opportunity for Python best practices

**Trade-off:**
- More upfront work
- Potential behavior differences to test

**Decision:** Accept trade-off. Rewrite provides long-term benefits.

### Trade-off 2: Incremental vs Full Re-ingestion

**Chosen:** Support both (incremental via --incremental flag)

**Rationale:**
- Incremental saves API costs and time for large content sets
- Full ingestion simpler, ensures consistency
- Developer can choose based on use case

**Trade-off:**
- More complex implementation (hash tracking)
- Risk of incremental bugs

**Decision:** Accept trade-off. Incremental important for production use.

### Trade-off 3: CLI Framework vs argparse

**Chosen:** argparse (Python standard library)

**Rationale:**
- No additional dependencies
- Simple CLI needs (few arguments)
- Familiar to Python developers

**Trade-off:**
- Less feature-rich than Click or Typer
- More boilerplate for complex CLIs

**Decision:** Accept trade-off. argparse sufficient for current needs.

---

## Open Questions

### Q1: Should we clear existing embeddings before re-ingestion?

**Context:** If chunking or embedding logic changes, may want fresh start

**Options:**
- A) Always clear before full ingestion (safe, but slow)
- B) Never clear (fast, but may have stale chunks)
- C) Prompt user (manual decision)

**Recommendation:** Option C (prompt with --clear flag)

**Decision:** Option C ✅

### Q2: Should we parallelize embedding generation?

**Context:** Batch API calls already efficient, but could process multiple batches in parallel

**Options:**
- A) Sequential batches (simple)
- B) Parallel batches with thread pool (faster)
- C) Async batches with asyncio (fastest, complex)

**Recommendation:** Option A for V1 (sufficient), Option B if needed

**Decision:** Option A for V1 ✅

### Q3: Should benchmark results be stored in database?

**Context:** Track RAG performance over time

**Options:**
- A) JSON file only (simple)
- B) Database table (queryable, historical tracking)
- C) Both (best of both)

**Recommendation:** Option A for V1, Option B post-migration

**Decision:** Option A (JSON file) ✅

### Q4: Should we implement a "dry-run" mode?

**Context:** Preview what would be ingested without database writes

**Options:**
- A) No dry-run (always write to DB)
- B) Dry-run flag (show what would happen)

**Recommendation:** Option B (useful for testing and previewing)

**Decision:** Option B ✅

---

## Success Criteria

### Technical Success

- [ ] Validation script detects all error types (missing fields, invalid YAML, broken links)
- [ ] Ingestion script processes all content files successfully
- [ ] Embeddings inserted match chunk count
- [ ] Incremental ingestion works correctly (skips unchanged, processes modified)
- [ ] Benchmark script generates metrics JSON
- [ ] Clear script deletes embeddings safely
- [ ] All unit tests pass (≥80% coverage)
- [ ] All integration tests pass
- [ ] All comparison tests pass (100% validation match)

### Quality Success

- [ ] Scripts have clear help text (`--help`)
- [ ] Progress bars for long-running operations
- [ ] Error messages helpful and actionable
- [ ] Logging structured and useful for debugging
- [ ] README documentation complete

### Performance Success

- [ ] Full ingestion completes in reasonable time (<5 min)
- [ ] Performance within 2x of TypeScript (or better)
- [ ] Incremental ingestion saves significant time (≥50% reduction)

### CI/CD Success

- [ ] Content validation runs in GitHub Actions
- [ ] Validation failures block PRs
- [ ] Scripts callable from package.json (developer convenience)

---

## Next Steps

After PR3.2d is merged:

1. **Switch to Python scripts:** Update developer workflow to use Python ingestion by default
2. **Deprecate TypeScript scripts:** Mark as legacy (keep for rollback during transition)
3. **PR3.2e:** Connect frontend to Python backend
4. **Monitor:** Track ingestion performance and API costs

---

## Related Documentation

- **Parent Epic:** `/docs/plans/PR3.2-Python-Backend-Migration.md`
- **Previous PRs:**
  - `/docs/plans/PR3.2a-Backend-Foundation.md`
  - `/docs/plans/PR3.2b-Core-Services.md`
  - `/docs/plans/PR3.2c-Agent-Orchestration.md`
- **TypeScript Scripts:** `scripts/ingest-content.ts`, `scripts/validate-content.ts`
- **Content Structure:** `content/README.md`, `content/DIVE-SITE-TEMPLATE.md`

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-01 | AI Assistant | Initial draft |

---

**Status:** 🟡 Draft — Ready after PR3.2a, PR3.2b, PR3.2c complete

**Estimated Duration:** 1-2 weeks  
**Complexity:** Medium  
**Risk Level:** Low-Medium
