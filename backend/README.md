# DovvyBuddy Python Backend

This folder contains the FastAPI + SQLAlchemy Python backend for DovvyBuddy, including content processing scripts, RAG pipeline, and agent orchestration.

## Quick Start

Assumes Python 3.11+ and poetry:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install "poetry>=1.5"
poetry install
cp .env.example .env
# Edit DATABASE_URL and GEMINI_API_KEY in .env
uvicorn app.main:app --reload --port 8000
```

## APIs

- `GET /health` — health check
- `POST /api/chat` — placeholder chat endpoint
- `GET/POST /api/sessions` — placeholder session endpoints
- `POST /api/leads` — placeholder lead endpoint

## Content Processing Scripts

The backend includes offline scripts for content validation, ingestion, and benchmarking.

### Prerequisites

- Python 3.11+ with backend dependencies installed
- PostgreSQL database with pgvector extension
- Gemini API key (for embedding generation)
- Content files in `../content` directory

### Available Scripts

#### 1. Content Validation

Validates markdown files for proper frontmatter and structure.

```bash
# Run from backend directory
python -m scripts.validate_content

# Or from project root using npm/pnpm
pnpm content:validate-py
```

**Options:**
- `--content-dir PATH` — Content directory to validate (default: `../content`)
- `--required-fields FIELD [FIELD ...]` — Required frontmatter fields (default: `title description`)
- `--no-structure-check` — Skip markdown structure checks
- `--pattern GLOB` — File pattern to match (default: `**/*.md`)

**Examples:**
```bash
# Validate specific directory
python -m scripts.validate_content --content-dir ../content/certifications

# Skip structure checks
python -m scripts.validate_content --no-structure-check

# Custom required fields
python -m scripts.validate_content --required-fields title description category
```

#### 2. Content Ingestion

Ingests markdown content by chunking text, generating embeddings, and storing in database.

```bash
# Run from backend directory
python -m scripts.ingest_content

# Or from project root
pnpm content:ingest-py
```

**Options:**
- `--content-dir PATH` — Content directory to ingest (default: `../content`)
- `--pattern GLOB` — File pattern to match (default: `**/*.md`)
- `--incremental` — Skip unchanged files (hash-based)
- `--dry-run` — Preview without database writes
- `--clear` — Clear existing embeddings before ingestion
- `--batch-size N` — Embedding batch size (default: 10)

**Examples:**
```bash
# Full ingestion
python -m scripts.ingest_content

# Incremental ingestion (skip unchanged files)
python -m scripts.ingest_content --incremental
pnpm content:ingest-incremental-py

# Dry run (preview only)
python -m scripts.ingest_content --dry-run

# Clear and re-ingest
python -m scripts.ingest_content --clear
```

**How Incremental Ingestion Works:**
- Calculates SHA256 hash of each file
- Stores hash in embedding metadata
- On subsequent runs, compares hashes
- Skips files with unchanged hashes
- Re-processes modified files only

#### 3. RAG Benchmarking

Benchmarks RAG pipeline performance with test queries.

```bash
# Run from backend directory
python -m scripts.benchmark_rag

# Or from project root
pnpm content:benchmark-py
```

**Options:**
- `--queries-file PATH` — Path to queries JSON file (default: `../tests/fixtures/benchmark_queries.json`)
- `--output PATH` — Output JSON file (default: `benchmark-results-{timestamp}.json`)
- `--iterations N` — Number of iterations per query (default: 1)
- `--top-k N` — Number of results to retrieve (default: 5)

**Examples:**
```bash
# Benchmark with default queries
python -m scripts.benchmark_rag

# Multiple iterations for more stable metrics
python -m scripts.benchmark_rag --iterations 3

# Custom queries file
python -m scripts.benchmark_rag --queries-file my_queries.json

# Custom output file
python -m scripts.benchmark_rag --output my-results.json
```

**Query File Format:**
```json
{
  "queries": [
    "What equipment do I need for diving?",
    {
      "query": "How deep can I dive with Open Water certification?",
      "expected_paths": ["certifications/padi/open-water.md"]
    }
  ]
}
```

**Output Metrics:**
- Latency statistics (mean, median, P95, P99)
- Retrieval accuracy (if ground truth provided)
- Per-query results with result paths
- JSON output for historical tracking

#### 4. Clear Embeddings

Utility for clearing embeddings from database.

```bash
# Run from backend directory
python -m scripts.clear_embeddings

# Or from project root
pnpm content:clear-py
```

**Options:**
- `--pattern PATTERN` — Content path pattern to match (e.g., `certifications/*`)
- `--force` — Skip confirmation prompt (use with caution)
- `--dry-run` — Show what would be deleted without deleting

**Examples:**
```bash
# Clear all embeddings (with confirmation)
python -m scripts.clear_embeddings

# Clear specific pattern
python -m scripts.clear_embeddings --pattern "certifications/*"

# Force clear without confirmation
python -m scripts.clear_embeddings --force

# Dry run
python -m scripts.clear_embeddings --dry-run
```

### Common Workflows

#### Initial Content Ingestion

```bash
# 1. Validate content
python -m scripts.validate_content

# 2. Ingest all content
python -m scripts.ingest_content

# 3. Verify embeddings
psql $DATABASE_URL -c "SELECT COUNT(*), content_path FROM content_embeddings GROUP BY content_path"

# 4. Benchmark RAG
python -m scripts.benchmark_rag
```

#### Daily Content Updates

```bash
# Use incremental mode to skip unchanged files
python -m scripts.ingest_content --incremental
```

#### Content Re-ingestion

```bash
# Clear and re-ingest (e.g., after chunking logic changes)
python -m scripts.ingest_content --clear
```

#### CI/CD Integration

Content validation runs automatically on PRs that modify `content/` files. See `.github/workflows/content-validation.yml`.

### Troubleshooting

**"No embeddings generated"**
- Check `GEMINI_API_KEY` in `.env`
- Verify Gemini API quota/billing
- Check network connectivity

**"Validation errors"**
- Review error messages for specific files
- Ensure frontmatter has required fields (`title`, `description`)
- Check YAML syntax in frontmatter

**"Database connection failed"**
- Verify `DATABASE_URL` in `.env`
- Ensure PostgreSQL is running
- Check pgvector extension: `CREATE EXTENSION IF NOT EXISTS vector`

**"Incremental mode not skipping files"**
- Verify embeddings have `file_hash` in metadata
- Re-ingest once without `--incremental` to populate hashes
- Check database connection (hashes stored in DB)

### Testing

```bash
# Run unit tests
pytest tests/unit/scripts

# Run integration tests (requires database)
pytest tests/integration/scripts

# Run all tests with coverage
pytest tests/ --cov=scripts
```
