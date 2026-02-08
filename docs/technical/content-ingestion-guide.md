# Content Ingestion Guide

**Last Updated:** January 2, 2026  
**Applies To:** DovvyBuddy AI Backend (Python)

---

## Overview

This guide explains how to ingest **markdown content** for RAG (Retrieval-Augmented Generation) and semantic search. Content ingestion involves:

1. Creating/updating markdown content files
2. Chunking content into searchable segments
3. Generating embeddings for vector search
4. Storing chunks and embeddings in PostgreSQL with pgvector

### ⚠️ Scope of This Guide

**This guide covers:**
- ✅ Generating embeddings from markdown files
- ✅ Updating `content_embeddings` table
- ✅ RAG pipeline for semantic search

**This guide does NOT cover:**
- ❌ Updating structured metadata (dive sites, destinations, certifications)
- ❌ Updating `dive_sites`, `destinations`, or other data tables
- ❌ Schema migrations or JSON metadata

👉 **For structured data updates, see:** [Neon Database Update Guide](./neon-database-update-guide.md)

---

## Prerequisites

### System Requirements

- Python 3.9+ installed
- Backend dependencies installed (`pip install -e .` from `backend/` directory)
- PostgreSQL with pgvector extension enabled
- Access to Gemini API (for embeddings)

### Environment Setup

Ensure your `backend/.env` file contains:

```bash
# API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database?ssl=require

# Embedding Configuration
EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_BATCH_SIZE=100
```

### Verify Database Setup

```bash
# Check pgvector extension
psql "$DATABASE_URL" -c "SELECT * FROM pg_extension WHERE extname = 'vector';"

# Check content_embeddings table
psql "$DATABASE_URL" -c "\d content_embeddings"
```

Expected table structure:
- `id` (UUID, primary key)
- `content_path` (TEXT, path to source file)
- `chunk_text` (TEXT, content chunk)
- `embedding` (VECTOR(768), embedding vector)
- `metadata` (JSONB, additional metadata)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

---

## Content File Structure

### Directory Layout

```
content/
├── certifications/
│   ├── padi/
│   │   ├── open-water.md
│   │   └── advanced.md
│   └── ssi/
│       └── open-water.md
├── destinations/
│   ├── Malaysia-Tioman/
│   │   ├── overview.md
│   │   ├── dive-sites.md
│   │   └── travel-info.md
│   └── [other-destinations]/
├── safety/
│   ├── decompression-safety.md
│   ├── emergency-procedures.md
│   └── equalization-techniques.md
└── faq/
    └── [faq-files].md
```

### Content File Format

Use markdown with the following structure:

```markdown
# Main Title

Brief introduction or overview.

## Section 1

Content for section 1...

### Subsection 1.1

Detailed information...

## Section 2

Content for section 2...
```

**Best Practices:**
- Use clear, descriptive headings (H1, H2, H3)
- Keep paragraphs focused and concise
- Use bullet points for lists
- Include code blocks for technical information
- Add metadata at the top (optional):
  ```yaml
  ---
  title: "PADI Open Water Certification"
  type: "certification"
  provider: "PADI"
  level: "beginner"
  ---
  ```

---

## Ingestion Process

### Step 1: Create or Update Content Files

1. **Create new content file:**
   ```bash
   cd content/destinations/
   mkdir New-Destination
   cd New-Destination
   touch overview.md
   ```

2. **Edit the file with your content:**
   ```bash
   # Use your preferred editor
   vim overview.md
   # or
   code overview.md
   ```

3. **Follow the markdown structure guidelines above**

### Step 2: Run the Ingestion Script

**⚠️ Important:** This script only generates embeddings for RAG. If your content includes structured metadata (dive sites, destinations), you must **also** run the appropriate database update script. See [Neon Database Update Guide](./neon-database-update-guide.md) for details.

**Current Status:** ⚠️ The ingestion script is being migrated from TypeScript to Python as part of PR3.2d.

#### Option A: Use TypeScript Ingestion (Temporary)

Until PR3.2d is complete, use the existing TypeScript script:

```bash
# From project root
cd /path/to/AI_DovvyBuddy04

# Ingest all content
pnpm tsx scripts/ingest-content.ts

# Ingest specific directory
pnpm tsx scripts/ingest-content.ts --dir content/destinations/New-Destination

# Ingest specific file
pnpm tsx scripts/ingest-content.ts --file content/destinations/New-Destination/overview.md

# Clear existing embeddings first (use with caution)
pnpm tsx scripts/clear-embeddings.ts
pnpm tsx scripts/ingest-content.ts
```

**TypeScript Script Behavior:**
- Reads all markdown files from `content/` directory
- Chunks content using markdown-aware splitting
- Generates embeddings via Gemini API (gemini-embedding-001)
- Stores in PostgreSQL `content_embeddings` table
- Shows progress and statistics
- **Does NOT update structured data tables** (use `update-dive-sites.ts` separately)

#### Option B: Use Python Ingestion (Coming in PR3.2d)

Once PR3.2d is complete, use the Python script:

```bash
# From backend directory
cd backend

# Ingest all content
python -m scripts.ingest_content

# Ingest specific directory
python -m scripts.ingest_content --dir ../content/destinations/New-Destination

# Ingest specific file
python -m scripts.ingest_content --file ../content/destinations/New-Destination/overview.md

# Clear and re-ingest
python -m scripts.clear_embeddings
python -m scripts.ingest_content

# Dry run (preview without saving)
python -m scripts.ingest_content --dry-run

# Verbose output
python -m scripts.ingest_content --verbose
```

### Step 3: Verify Ingestion

#### Check Database Records

```bash
# Count embeddings
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM content_embeddings;"

# View recent ingestions
psql "$DATABASE_URL" -c "SELECT content_path, LENGTH(chunk_text) as chunk_size, created_at FROM content_embeddings ORDER BY created_at DESC LIMIT 10;"

# Check specific content path
psql "$DATABASE_URL" -c "SELECT id, content_path, LEFT(chunk_text, 100) as preview FROM content_embeddings WHERE content_path LIKE '%New-Destination%';"
```

#### Test RAG Retrieval

```bash
# From backend directory
cd backend

# Test query related to new content
python -m scripts.test_rag "What can you tell me about [New Destination]?"

# Expected: Should return relevant chunks from newly ingested content
```

#### Verify with Integration Test

```bash
# Run RAG integration tests
pytest tests/integration/services/test_rag_integration.py -v

# Expected: All tests should pass
```

---

## Ingestion Configuration

### Chunking Parameters

Default configuration in `backend/app/core/config.py`:

```python
RAG_CHUNK_SIZE = 512         # Target chunk size in tokens
RAG_CHUNK_OVERLAP = 50       # Overlap between chunks (tokens)
```

**To customize chunking:**

1. Edit `backend/app/services/rag/chunker.py`
2. Adjust `chunk_size` and `overlap` parameters
3. Or set environment variables:
   ```bash
   export RAG_CHUNK_SIZE=768
   export RAG_CHUNK_OVERLAP=100
   ```

### Embedding Parameters

Default configuration:

```python
EMBEDDING_MODEL = "gemini-embedding-001"  # Gemini model (768 dimensions)
EMBEDDING_BATCH_SIZE = 100              # Max texts per API call
```

**To customize:**

Set in `backend/.env`:
```bash
EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_BATCH_SIZE=50  # Reduce if hitting rate limits
```

---

## Common Workflows

### Workflow 1: Add New Destination (Complete)

**Note:** Adding a new destination requires TWO operations:
1. **Structured data** (metadata) → See [Neon Database Update Guide](./neon-database-update-guide.md)
2. **Content embeddings** (RAG) → This guide

```bash
# 1. Create directory and files
mkdir content/destinations/Bali-Indonesia
cd content/destinations/Bali-Indonesia

# 2. Create JSON metadata file (for structured data)
touch bali-overview.json
# Edit JSON with: destination_id, name, country, etc.

# 3. Create markdown content files (for RAG)
touch overview.md dive-sites.md travel-info.md

# 4. Edit markdown files with descriptive content
vim overview.md dive-sites.md travel-info.md

# 5. Update structured data (destinations table)
# See: docs/technical/neon-database-update-guide.md
# Example: pnpm tsx scripts/update-destinations.ts (if such script exists)

# 6. Ingest content for RAG (THIS GUIDE)
cd ../../..
pnpm tsx scripts/ingest-content.ts --dir content/destinations/Bali-Indonesia

# 7. Verify embeddings
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM content_embeddings WHERE content_path LIKE '%Bali-Indonesia%';"

# 8. Test RAG retrieval
cd backend
python -m scripts.test_rag "Tell me about diving in Bali"
```

### Workflow 2: Update Existing Content

```bash
# 1. Edit the content file
vim content/certifications/padi/open-water.md

# 2. Clear old embeddings for that file
psql "$DATABASE_URL" -c "DELETE FROM content_embeddings WHERE content_path = 'certifications/padi/open-water.md';"

# 3. Re-ingest the file
pnpm tsx scripts/ingest-content.ts --file content/certifications/padi/open-water.md

# 4. Verify update
psql "$DATABASE_URL" -c "SELECT created_at FROM content_embeddings WHERE content_path = 'certifications/padi/open-water.md' ORDER BY created_at DESC LIMIT 1;"
```

### Workflow 3: Bulk Content Addition

```bash
# 1. Add multiple files to content directory
# ... (create files)

# 2. Clear all existing embeddings (optional, use with caution)
pnpm tsx scripts/clear-embeddings.ts

# 3. Ingest all content
pnpm tsx scripts/ingest-content.ts

# 4. Verify total count
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM content_embeddings;"

# 5. Run full integration tests
cd backend
pytest tests/integration/services/test_rag_integration.py -v
```

### Workflow 4: Re-generate Embeddings (Model Change)

If the embedding model changes (e.g., upgrading to a new version):

```bash
# 1. Backup existing embeddings (optional)
psql "$DATABASE_URL" -c "CREATE TABLE content_embeddings_backup AS SELECT * FROM content_embeddings;"

# 2. Clear embeddings
pnpm tsx scripts/clear-embeddings.ts

# 3. Update embedding model in config
# Edit backend/.env:
# EMBEDDING_MODEL=new-model-name

# 4. Re-ingest all content
pnpm tsx scripts/ingest-content.ts

# 5. Verify new embeddings
psql "$DATABASE_URL" -c "SELECT COUNT(*), AVG(array_length(embedding::text::float[], 1)) as avg_dims FROM content_embeddings;"

# 6. Test retrieval quality
cd backend
pytest tests/integration/services/test_rag_integration.py -v
```

---

## Troubleshooting

### Issue: "API rate limit exceeded"

**Symptoms:** Ingestion script fails with 429 errors

**Solutions:**
1. Reduce batch size:
   ```bash
   export EMBEDDING_BATCH_SIZE=50
   ```
2. Add delay between batches (modify script)
3. Use smaller content chunks (reduce `RAG_CHUNK_SIZE`)

### Issue: "No embeddings found after ingestion"

**Diagnosis:**
```bash
# Check if content was processed
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM content_embeddings WHERE created_at > NOW() - INTERVAL '1 hour';"
```

**Possible Causes:**
1. Database connection issue (check `DATABASE_URL`)
2. Content files not in correct directory
3. Empty or invalid markdown files
4. API key not set (`GEMINI_API_KEY`)

**Solutions:**
1. Verify environment variables
2. Check file paths and content
3. Run with `--verbose` flag (Python) or check logs (TypeScript)

### Issue: "Embedding dimensions mismatch"

**Symptoms:** Vector search fails with dimension error

**Diagnosis:**
```bash
# Check embedding dimensions
psql "$DATABASE_URL" -c "SELECT array_length(embedding::text::float[], 1) as dims, COUNT(*) FROM content_embeddings GROUP BY dims;"
```

**Expected:** All embeddings should be 768 dimensions (for gemini-embedding-001)

**Solution:**
1. Verify `EMBEDDING_MODEL=gemini-embedding-001` in `.env`
2. Clear and re-ingest all content:
   ```bash
   pnpm tsx scripts/clear-embeddings.ts
   pnpm tsx scripts/ingest-content.ts
   ```

### Issue: "PostgreSQL connection failed"

**Symptoms:** Cannot connect to database

**Solutions:**
1. Verify `DATABASE_URL` format:
   ```bash
   # Correct format
   postgresql+asyncpg://user:password@host:port/database?ssl=require
   ```
2. Test connection:
   ```bash
   psql "$DATABASE_URL" -c "SELECT version();"
   ```
3. Check SSL requirements (Neon requires `?ssl=require`)
4. Verify credentials and network access

### Issue: "Chunks too large or too small"

**Symptoms:** RAG returns incomplete information or too much irrelevant data

**Solution:** Adjust chunking parameters:

```bash
# For more detailed chunks (larger)
export RAG_CHUNK_SIZE=768
export RAG_CHUNK_OVERLAP=100

# For more concise chunks (smaller)
export RAG_CHUNK_SIZE=256
export RAG_CHUNK_OVERLAP=25

# Re-ingest content with new settings
pnpm tsx scripts/clear-embeddings.ts
pnpm tsx scripts/ingest-content.ts
```

---

## Performance Considerations

### API Costs

**Gemini Embedding API:**
- Model: gemini-embedding-001
- Free tier: Up to 1,500 requests/day
- Cost estimate: ~$0.00025 per 1,000 characters

**Optimization Tips:**
1. Cache embeddings (avoid re-generating for unchanged content)
2. Use batch processing (100 texts per request)
3. Run ingestion during off-peak hours

### Database Performance

**Indexes:**
- HNSW index on `embedding` column (for vector similarity search)
- B-tree index on `content_path` (for filtering)
- B-tree index on `created_at` (for temporal queries)

**Verify indexes:**
```bash
psql "$DATABASE_URL" -c "SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'content_embeddings';"
```

**Query performance:**
```bash
# Test retrieval speed
cd backend
python -m scripts.benchmark_rag --queries 10
```

Target: <500ms P95 latency for RAG retrieval

---

## Best Practices

### Content Guidelines

1. **Use clear headings** - H1 for title, H2/H3 for sections
2. **Write concise paragraphs** - Target 3-5 sentences per paragraph
3. **Include keywords** - Use dive industry terminology naturally
4. **Avoid duplication** - Don't repeat information across files
5. **Update regularly** - Keep information current and accurate

### Ingestion Guidelines

1. **Test queries first** - Verify what information is missing
2. **Ingest incrementally** - Add content in batches, test retrieval
3. **Monitor API usage** - Track embedding API calls
4. **Verify quality** - Run RAG tests after ingestion
5. **Document changes** - Note what content was added/updated

### Maintenance Guidelines

1. **Regular audits** - Review content relevance monthly
2. **Remove outdated content** - Delete obsolete information
3. **Re-generate embeddings** - When upgrading embedding models
4. **Monitor database size** - Track `content_embeddings` table growth
5. **Backup before major changes** - Save embeddings before re-ingestion

---

## Migration Notes

### TypeScript to Python Migration

**Status:** In progress (PR3.2d)

**Current State:**
- ✅ Python RAG services implemented (PR3.2b)
- ⏳ Python ingestion script (PR3.2d)
- ✅ TypeScript ingestion working (temporary)

**Timeline:**
- PR3.2d expected: January 2026
- Full migration: Q1 2026

**Impact:**
- Ingestion workflow will change to Python CLI
- Same data format and embeddings
- No re-ingestion required after migration

---

## References

### Related Documentation

- **Neon Database Update Guide:** `docs/technical/neon-database-update-guide.md` ⭐ (for structured data)
- **Backend Services:** `backend/VERIFICATION_SUMMARY_PR3.2b.md`
- **RAG Pipeline:** `docs/plans/PR3.2b-Core-Services.md`
- **Database Schema:** `docs/plans/PR1-Database-Schema.md`
- **Master Plan:** `docs/plans/MASTER_PLAN.md`

### External Resources

- [Gemini Embedding API](https://ai.google.dev/tutorials/python_quickstart#embeddings)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Markdown Guide](https://www.markdownguide.org/)

---

## Quick Reference

### Essential Commands

```bash
# Ingest all content (TypeScript - current)
pnpm tsx scripts/ingest-content.ts

# Ingest specific file (TypeScript - current)
pnpm tsx scripts/ingest-content.ts --file content/path/to/file.md

# Clear embeddings (TypeScript - current)
pnpm tsx scripts/clear-embeddings.ts

# Test RAG (Python)
cd backend && python -m scripts.test_rag "your query here"

# Check embedding count
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM content_embeddings;"

# View recent ingestions
psql "$DATABASE_URL" -c "SELECT content_path, created_at FROM content_embeddings ORDER BY created_at DESC LIMIT 5;"
```

### Environment Variables

```bash
GEMINI_API_KEY=your_key_here
DATABASE_URL=postgresql+asyncpg://...
EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_BATCH_SIZE=100
RAG_CHUNK_SIZE=512
RAG_CHUNK_OVERLAP=50
```

---

**Last Updated:** January 2, 2026  
**Maintained By:** DovvyBuddy Development Team  
**Status:** Active (TypeScript ingestion) / Python migration in progress
