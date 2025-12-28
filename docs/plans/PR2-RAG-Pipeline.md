# PR2: RAG Pipeline (Content Ingestion)

**Branch Name:** `feature/pr2-rag-pipeline`  
**Status:** Planned  
**Date:** December 23, 2025  
**Based on:** MASTER_PLAN.md (Phase 1: Foundations & Data Layer)

---

## 1. Feature/Epic Summary

### Objective

Build the content ingestion pipeline that enables DovvyBuddy to "read" and semantically search curated markdown documentation about diving certifications, destinations, and dive sites.

### User Impact

- **Internal/Foundation:** No direct user-facing impact in this PR.
- **Enables:** PR3 (Chat endpoint) will use this pipeline to retrieve relevant context for LLM responses.
- **Content Quality:** Establishes the knowledge base that grounds all bot responses, preventing hallucination.

### Dependencies

- **Upstream:** PR1 (Database Schema & Migrations) — Must be complete with `content_embeddings` table available.
- **External:**
  - Gemini API key (`GEMINI_API_KEY`) with `text-embedding-004` access — ✅ Ready.

### Assumptions

- **Assumption:** Initial content corpus will be small (~10-20 markdown files, <1000 total chunks).
- **Assumption:** Content will be written in English only (V1 constraint).
- **Assumption:** Content creation (certification guides, destination, dive sites) is part of PR2 implementation.
- **Assumption:** Gemini API access is already set up with valid `GEMINI_API_KEY`.
- **Assumption:** Dive site template is descriptive (general guide with flexibility allowed).
- **Assumption:** Hybrid chunking (semantic + paragraph split) balances context preservation and size limits.
- **Assumption:** Embeddings will be generated via API calls (not local model) for simplicity.
- **Assumption:** Content will be versioned in git, making re-ingestion on updates straightforward.

---

## 2. Complexity & Fit

### Classification

**Single-PR**

### Rationale

- **Limited Scope:** Content ingestion script + retrieval utility + initial markdown content.
- **No User-Facing Changes:** Backend-only processing; no API endpoints exposed in this PR.
- **Single Layer Focus:** Data pipeline (read → chunk → embed → store) and utility functions.
- **Testable Independently:** Can verify ingestion and retrieval without chat endpoint.
- **Estimated Effort:** 2-3 days for solo founder (write content, build ingestion script, implement retrieval, test).
- **Low Risk:** Idempotent script design allows re-running without data corruption.

---

## 3. Full-Stack Impact

### Frontend

**No changes planned.**

### Backend

**Foundation for future API usage:**

- RAG retrieval utility will be created (`src/lib/rag/retrieval.ts`) but not exposed via API in this PR.
- Content ingestion runs as a standalone script, not part of the web server.
- No API endpoints added in this PR (deferred to PR3).

### Data

**Core changes:**

- **Content Files:**
  - Create `content/` directory structure with markdown files.
  - Write initial curated content (certifications, 1 destination, 5-10 dive sites).
- **Database:**
  - Populate `content_embeddings` table via ingestion script.
  - Each row represents a chunk of content with its vector embedding.
- **Ingestion Process:**
  - Read markdown files recursively from `content/` directory.
  - Parse frontmatter and body (using `gray-matter` or similar).
  - Chunk text semantically (preserve paragraph/section boundaries where possible).
  - Generate embeddings via LLM API.
  - Store chunks + embeddings + metadata in `content_embeddings` table.
- **Retrieval Function:**
  - Query `content_embeddings` using vector similarity (pgvector `<=>` operator).
  - Return top-k most relevant chunks with metadata.

### Infra / Config

- **Environment Variables:**
  - Add to `.env.example`:
    - `EMBEDDING_PROVIDER` (gemini|groq)
    - `GEMINI_API_KEY` (if using Gemini)
    - `GROQ_API_KEY` (if using Groq, though Groq may not have embedding endpoint yet)
  - Note: Gemini `text-embedding-004` is the recommended default.
- **Package Dependencies:**
  - Add `@google/generative-ai` or `groq-sdk` for embedding API.
  - Add `gray-matter` for markdown frontmatter parsing.
  - Add `tiktoken` or similar for token counting (chunking).
  - Add `tsx` (already present from PR1) for running TypeScript scripts.
- **Scripts:**
  - Add `pnpm content:ingest` — Run ingestion script to populate embeddings.
  - Add `pnpm content:clear` (optional) — Clear existing embeddings for re-ingestion.

---

## 4. PR Roadmap

### PR2: RAG Pipeline (Content Ingestion)

**Goal**  
Enable the bot to semantically search curated documentation by building a content ingestion pipeline and retrieval utility.

---

### Scope

**In scope:**

1. **Content Directory Structure:**
   - Create `content/` directory with subdirectories:
     - `content/certifications/` — PADI/SSI certification guides.
     - `content/destinations/` — Destination overviews.
     - `content/dive-sites/` — Individual dive site profiles.
     - `content/safety/` — Safety reference documents.
   - Add `.gitkeep` files to preserve structure.

2. **Initial Content Creation:**
   - Write markdown files for:
     - PADI Open Water certification guide (~1500-2000 words).
     - SSI Open Water Diver certification guide (~1500-2000 words).
     - 1 destination overview (e.g., "Cozumel, Mexico" ~800-1200 words).
     - 5-10 dive site profiles (using the template provided, ~500-800 words each).
   - Include frontmatter with metadata (type, tags, keywords, last_updated).

3. **Ingestion Script (`scripts/ingest-content.ts`):**
   - Read all markdown files from `content/` recursively.
   - Parse frontmatter and body text.
   - Chunk text using hybrid strategy:
     - Target chunk size: 500-800 tokens.
     - Try semantic split first (detect sections via markdown headers `##`, `###`).
     - Keep sections intact if within token limit.
     - Fall back to paragraph split (double newline) if section too large.
     - Include section headers in chunks for context.
   - Generate embeddings via Gemini API (`text-embedding-004`).
   - Store in `content_embeddings` table:
     - `content_path`: Relative file path.
     - `chunk_text`: The text chunk.
     - `embedding`: Vector (1536 dimensions).
     - `metadata`: JSONB with frontmatter + chunk index.
   - Make script idempotent (check if file already ingested by path/hash).
   - Log progress (files processed, chunks generated, embeddings stored).

4. **Retrieval Utility (`src/lib/rag/retrieval.ts`):**
   - Export function `retrieveRelevantChunks(query: string, topK: number)`:
     - Generate embedding for query text.
     - Query `content_embeddings` using vector similarity (cosine distance via `<=>` operator).
     - Return top-k chunks with metadata and similarity scores.
   - Include filtering options (by content type, tags) for future use.

5. **Embedding Provider Abstraction (`src/lib/embeddings/`):**
   - Create interface `EmbeddingProvider` with method `generateEmbedding(text: string)`.
   - Implement `GeminiEmbeddingProvider` (using `@google/generative-ai`).
   - Factory function based on `EMBEDDING_PROVIDER` env var.
   - Handle rate limits and retries gracefully.

6. **Testing:**
   - Unit tests for chunking logic.
   - Integration tests for ingestion (use test database or mock embeddings).
   - Integration test for retrieval (ingest sample content, query, verify results).

7. **Documentation:**
   - Update `content/README.md` with:
     - Content structure and conventions.
     - How to add new content.
     - How to re-run ingestion.
     - **Content quality checklist** for manual review.
   - Update `.env.example` with embedding provider configuration.
   - Add content validation script (`scripts/validate-content.ts`):
     - Check frontmatter schema (required fields present).
     - Validate YAML syntax.
     - Check for safety disclaimers where required (dive sites, certifications).
     - Verify word count ranges.
     - Report missing or malformed metadata.

**Out of scope:**

- Chat API endpoint (deferred to PR3).
- LLM response generation (deferred to PR3).
- Session management (deferred to PR3).
- UI components (deferred to PR5).
- Content management system (deferred to future version).

---

### Backend Changes

**Ingestion Script (`scripts/ingest-content.ts`):**

- Command-line script that runs outside web server context.
- Reads files from `content/` directory.
- Processes markdown → chunks → embeddings → database.
- Idempotent and resumable (skip already-ingested files or allow force re-ingest).

**Embedding Provider (`src/lib/embeddings/`):**

- Module structure:
  - `src/lib/embeddings/types.ts` — Interface definitions.
  - `src/lib/embeddings/gemini-provider.ts` — Gemini implementation.
  - `src/lib/embeddings/index.ts` — Factory function.
- Handles API authentication, rate limiting, retries.

**RAG Retrieval (`src/lib/rag/`):**

- Module structure:
  - `src/lib/rag/chunking.ts` — Hybrid text chunking (semantic + paragraph split).
  - `src/lib/rag/retrieval.ts` — Vector similarity search.
  - `src/lib/rag/types.ts` — Type definitions for chunks and results.
- Exports functions to be used by PR3 (chat orchestration).

---

### Frontend Changes

**No changes planned.**

---

### Data Changes

**Content Files (New):**

- `content/certifications/padi-open-water.md`
- `content/certifications/ssi-open-water.md`
- `content/destinations/cozumel-mexico.md`
- `content/dive-sites/cozumel-palancar-reef.md`
- `content/dive-sites/cozumel-santa-rosa-wall.md`
- `content/dive-sites/cozumel-columbia-reef.md`
- `content/dive-sites/cozumel-punta-sur.md`
- `content/dive-sites/cozumel-devils-throat.md`
- ... (5-10 total dive site files)

**Database (`content_embeddings` table):**

- Populated via ingestion script.
- Expected row count: ~100-300 chunks (depending on content length and chunking strategy).
- Each row contains:
  - Unique ID (UUID).
  - File path reference.
  - Text chunk.
  - 1536-dimension vector embedding.
  - Metadata (frontmatter + chunk index).

**Indexes:**

- HNSW index on `embedding` column (already created in PR1 migration).
- Optional: GIN index on `metadata` JSONB for filtering (can be added later if needed).

**Backward Compatibility:**

- Not applicable (greenfield content ingestion).

---

### Infra / Config

**Environment Variables (`.env.example`):**

```
# Database
DATABASE_URL=postgresql://...

# Embedding Provider
EMBEDDING_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here

# Future variables
# LLM_PROVIDER=groq
# GROQ_API_KEY=
```

**Package Scripts (`package.json`):**

```
"content:validate": "tsx scripts/validate-content.ts",
"content:ingest": "tsx scripts/ingest-content.ts",
"content:clear": "tsx scripts/clear-embeddings.ts"
```

**Dependencies to Add:**

- `@google/generative-ai` — Gemini SDK for embeddings.
- `gray-matter` — Frontmatter parsing.
- `tiktoken` — Token counting for chunking. **Note:** `tiktoken` uses OpenAI's tokenizer which differs from Gemini's, but 500-800 token target is flexible enough that approximate counts are acceptable.
- `zod` — Runtime validation for content frontmatter (optional but recommended).

---

### Testing

**Unit Tests:**

- **Chunking Logic (`src/lib/rag/chunking.test.ts`):**
  - Test hybrid chunking (semantic split on headers).
  - Test fallback to paragraph split for large sections.
  - Test chunk size limits (500-800 tokens).
  - Test preservation of context (section headers included).
- **Embedding Provider (`src/lib/embeddings/gemini-provider.test.ts`):**
  - Mock API calls.
  - Test retry logic on rate limit errors.
  - Verify embedding dimensions (1536).
- **Content Validation (`scripts/validate-content.test.ts`):**
  - Test frontmatter schema validation.
  - Test safety disclaimer detection.
  - Test word count validation.

**Integration Tests:**

- **Ingestion (`tests/integration/ingest-content.test.ts`):**
  - Create test markdown files.
  - Run ingestion script against test database.
  - Verify chunks stored in `content_embeddings` table.
  - Verify idempotency (run twice, no duplicates).
- **Retrieval (`tests/integration/retrieval.test.ts`):**
  - Ingest sample content.
  - Query with test phrases (e.g., "Open Water prerequisites").
  - Verify relevant chunks returned.
  - Verify similarity scores are reasonable (>0.7 for good matches).

**Manual Checks:**

- Read generated markdown content for accuracy and tone.
- Verify embeddings are generated (check dimensions).
- Test retrieval with various queries (certification questions, destination questions).

---

### Verification

**Commands:**

1. **Install Dependencies:**

   ```
   pnpm install
   ```

2. **Set Up Environment:**
   - Ensure `DATABASE_URL` is set (from PR1).
   - Add `GEMINI_API_KEY` to `.env`.
   - Set `EMBEDDING_PROVIDER=gemini`.

3. **Create Content Files:**
   - Write markdown files in `content/` directory during PR2 implementation.
   - Follow frontmatter conventions documented in `content/README.md`.
   - Use dive site template as a descriptive guide (flexibility allowed).

3a. **Validate Content:**

```
pnpm content:validate
```

- Expected: All files pass frontmatter schema validation.
- Expected: Safety disclaimers present where required.
- Expected: Word counts within expected ranges.

4. **Run Ingestion Script:**

   ```
   pnpm content:ingest
   ```

   - Expected: Progress logs, no errors.
   - Expected: Success message with count of chunks ingested.

5. **Verify Database Population:**

   ```sql
   SELECT COUNT(*) FROM content_embeddings;
   ```

   - Expected: >0 rows (should be ~100-300 depending on content).

   ```sql
   SELECT content_path, LENGTH(chunk_text), array_length(embedding, 1)
   FROM content_embeddings
   LIMIT 5;
   ```

   - Expected: Sample rows with file paths, chunk text lengths, embedding dimensions (1536).

6. **Test Retrieval Function:**
   - Create a test script or use Node REPL:
     ```typescript
     import { retrieveRelevantChunks } from './src/lib/rag/retrieval'
     const results = await retrieveRelevantChunks(
       'What are the prerequisites for Open Water certification?',
       5
     )
     console.log(results)
     ```
   - Expected: Array of 5 relevant chunks with similarity scores.

7. **Run Unit Tests:**

   ```
   pnpm test
   ```

   - Expected: All tests pass.

8. **Type Check:**

   ```
   pnpm typecheck
   ```

   - Expected: No type errors.

9. **Lint:**

   ```
   pnpm lint
   ```

   - Expected: No lint errors.

10. **Build:**
    ```
    pnpm build
    ```

    - Expected: Next.js build succeeds (even though new code isn't used in app yet).

**Manual Verification Checklist:**

- [ ] Content validation script passes (`pnpm content:validate`).
- [ ] Content files follow markdown conventions and include frontmatter.
- [ ] Frontmatter includes all required fields per doc type.
- [ ] Safety disclaimers present in certification and dive site content.
- [ ] Content is descriptive (not instructional/directive).
- [ ] Dive site content follows template guidelines (flexible interpretation).
- [ ] Sources cited in frontmatter where applicable.
- [ ] Ingestion script processes all files without errors.
- [ ] `content_embeddings` table populated with expected number of chunks.
- [ ] Embeddings are 1536-dimensional vectors.
- [ ] Retrieval function returns relevant chunks for test queries.
- [ ] Chunks preserve context (headers included, not cut mid-sentence).
- [ ] Hybrid chunking works (sections intact when possible).
- [ ] Idempotency: Re-running ingestion doesn't create duplicates.
- [ ] Content quality: Markdown files are accurate, safety-conscious, and grounded in sources.

---

### Rollback Plan

**Feature Flag / Kill Switch:**

- Not applicable (no user-facing features or API routes).

**Revert Strategy:**

- If PR is reverted:
  - `content_embeddings` table will still contain data (harmless).
  - To clear: Run `DELETE FROM content_embeddings;` or use `pnpm content:clear` script.
  - Content files in `content/` directory are versioned in git (safe to revert).
- **No risk to existing functionality** (PR1 tables remain intact).

---

### Dependencies

**Upstream PRs:**

- PR1 (Database Schema & Migrations) — **Must be complete** ✅

**External Dependencies:**

- Gemini API key (`GEMINI_API_KEY`) with text-embedding-004 access.
- Database connection working (from PR1).
- Sufficient API quota for embeddings (Gemini free tier: 1500 requests/day should be enough for V1 content).

---

### Risks & Mitigations

**Risk 1: Embedding API Rate Limits**

- **Impact:** Ingestion script may fail or slow down with large content corpus.
- **Mitigation:**
  - Implement exponential backoff and retry logic in embedding provider.
  - Process files sequentially (not in parallel) to avoid rate limits.
  - Add `--resume` flag to ingestion script to skip already-processed files.

**Risk 2: Chunking Quality (Context Loss)**

- **Impact:** Chunks may be too small (lose context) or too large (dilute relevance).
- **Mitigation:**
  - Start with 500-800 token chunks and test retrieval quality.
  - Include section headers in chunks for context.
  - Iterate on chunking strategy based on retrieval results (adjust in future PR if needed).

**Risk 3: Content Quality / Accuracy**

- **Impact:** Inaccurate or misleading content will cause bot to give wrong answers.
- **Mitigation:**
  - Review all markdown content before ingestion.
  - Cite sources where possible (in frontmatter).
  - Add content review checklist to `content/README.md`.
  - Version content in git for auditability.

**Risk 4: Embedding Dimensions Mismatch**

- **Impact:** If embedding provider changes or returns wrong dimensions, retrieval will fail.
- **Mitigation:**
  - Validate embedding dimensions (1536) before storing in database.
  - Add unit test to verify embedding provider returns correct shape.
  - Document expected dimensions in code comments.

**Risk 5: Idempotency Failure (Duplicate Chunks)**

- **Impact:** Re-running ingestion may create duplicate embeddings, wasting storage and API quota.
- **Mitigation:**
  - Check if file already ingested (by `content_path` or content hash).
  - Add `--force` flag to allow re-ingestion if content updated.
  - Log skipped files clearly.

---

## 5. Milestones & Sequence

### Milestone 1: Content Pipeline Operational

**What it unlocks:** Database contains searchable knowledge base; retrieval utility ready for PR3 (Chat API).

**PRs included:** PR2 only.

**Definition of Done:**

- [ ] `content/` directory structure created with markdown files.
- [ ] Ingestion script runs successfully and populates `content_embeddings` table.
- [ ] Retrieval utility returns relevant chunks for test queries.
- [ ] Unit and integration tests pass.
- [ ] Content reviewed for accuracy and tone.
- [ ] CI pipeline passes (lint, typecheck, test, build).
- [ ] Documentation added (`content/README.md`, updated `.env.example`).

---

## 6. Risks, Trade-offs, and Open Questions

### Major Risks

1. **Content Creation Time**
   - **Risk:** Writing 10-20 high-quality markdown files (certifications + destination + dive sites) may take longer than expected.
   - **Mitigation:** Start with minimal viable content (1 certification guide, 1 destination, 3 dive sites). Expand later. Prioritize quality over quantity.

2. **Retrieval Relevance**
   - **Risk:** Vector search may not return most relevant chunks for all queries.
   - **Mitigation:** Test with diverse queries during development. Tune chunk size if needed. Consider hybrid search (keyword + vector) in future PR.

3. **API Costs**
   - **Risk:** Gemini API costs for embeddings may accumulate if re-ingesting frequently.
   - **Mitigation:** Make ingestion idempotent to avoid unnecessary re-processing. Cache embeddings in development. Monitor API usage.

### Trade-offs

1. **Fixed Token Chunking vs Semantic Chunking**
   - **Trade-off:** Fixed-size chunks are simpler but may split semantic units awkwardly. Pure semantic chunking may create oversized chunks.
   - **Decision:** ✅ **Hybrid approach** — Try semantic split first (detect markdown headers), fall back to paragraph split if section exceeds 800 tokens. Best of both worlds.

2. **Gemini vs Groq for Embeddings**
   - **Trade-off:** Gemini has proven embedding models (`text-embedding-004`). Groq is faster for inference but may lack embedding endpoint.
   - **Decision:** Use Gemini for embeddings in V1. Abstract provider interface allows switching later if needed.

3. **Content in Git vs CMS**
   - **Trade-off:** Git-based content is simple and version-controlled but requires technical knowledge to update.
   - **Decision:** Acceptable for V1 (solo founder). Revisit CMS in V2 if non-technical contributors join.

4. **Re-ingestion Strategy**
   - **Trade-off:** Manual re-ingestion requires running script. Automated re-ingestion (on file change) adds complexity.
   - **Decision:** Manual for V1. Add file watching or CI-based ingestion if content update frequency increases.

### Open Questions

**All questions resolved for V1:**

1. **Which Embedding Provider?**
   - **Decision:** ✅ **Gemini `text-embedding-004`** — Proven, 1536 dimensions, good performance.
   - **Impact on Plan:** Use `@google/generative-ai` SDK.

2. **Chunk Size?**
   - **Decision:** ✅ **500-800 tokens per chunk** — Balance between context and relevance.
   - **Impact on Plan:** Implement token-based chunking with paragraph boundaries preserved.

3. **Metadata Strategy?**
   - **Decision:** ✅ **Store frontmatter + chunk index in JSONB** — Flexible for filtering and debugging.
   - **Impact on Plan:** Parse frontmatter with `gray-matter`, include in metadata field.

4. **Content Scope for V1?**
   - **Decision:** ✅ **Minimal viable content:**
     - 2 certification guides (PADI + SSI Open Water).
     - 1 destination overview (Cozumel).
     - 5-10 dive sites (Cozumel area).
   - **Impact on Plan:** Reduces content creation time; allows testing with real use cases.

---

## Appendix: Content Frontmatter Schema

All markdown files in `content/` should include YAML frontmatter with the following structure:

**General Fields (All Content Types):**

```
---
doc_type: "certification" | "destination" | "dive_site" | "safety"
title: "Document Title"
tags: ["tag1", "tag2"]
keywords: ["keyword1", "keyword2"]
last_updated: "YYYY-MM-DD"
data_quality: "verified" | "compiled" | "anecdotal"
sources: ["URL1", "URL2"]
---
```

**Certification-Specific:**

```
agency: "PADI" | "SSI" | "NAUI" | etc.
level: "OW" | "AOW" | "Rescue" | "DM"
```

**Dive Site-Specific:**

```
site_id: "cozumel-palancar-reef"
destination: "Cozumel, Mexico"
min_certification: "OW" | "AOW" | etc.
difficulty: "beginner" | "intermediate" | "advanced"
depth_range_m: [10, 30]
```

---

## Appendix: File Structure

```
content/
├── README.md                                    # Content authoring guide
├── certifications/
│   ├── padi-open-water.md
│   └── ssi-open-water.md
├── destinations/
│   └── cozumel-mexico.md
├── dive-sites/
│   ├── cozumel-palancar-reef.md
│   ├── cozumel-santa-rosa-wall.md
│   ├── cozumel-columbia-reef.md
│   ├── cozumel-punta-sur.md
│   └── cozumel-devils-throat.md
├── faq/                                         # Exists in repo; content deferred to future PR
│   └── (future FAQ content)
└── safety/
    └── (future: no-fly times, medical references)

scripts/
├── validate-content.ts                          # Content validation script
├── ingest-content.ts                            # Main ingestion script
└── clear-embeddings.ts                          # Utility to clear embeddings

src/
├── lib/
│   ├── embeddings/
│   │   ├── index.ts                             # Factory function
│   │   ├── types.ts                             # Interface definitions
│   │   └── gemini-provider.ts                   # Gemini implementation
│   └── rag/
│       ├── chunking.ts                          # Text chunking utilities
│       ├── retrieval.ts                         # Vector similarity search
│       └── types.ts                             # Chunk and result types

tests/
└── integration/
    ├── ingest-content.test.ts                   # Ingestion integration test
    └── retrieval.test.ts                        # Retrieval integration test
```

---

**End of PR2 Plan**
