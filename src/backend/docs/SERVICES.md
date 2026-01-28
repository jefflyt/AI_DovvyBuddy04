# DovvyBuddy Backend - Core Services

Python backend implementation for DovvyBuddy, featuring:
- Embedding generation with Gemini
- LLM providers (Groq, Gemini)
- RAG pipeline (chunking, retrieval, orchestration)

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -e .
```

### 2. Configure Environment

Copy `.env.example` to `.env` and set your API keys:

```bash
cp .env.example .env
# Edit .env and add your keys:
# GEMINI_API_KEY=your_key_here
# GROQ_API_KEY=your_key_here
```

### 3. Initialize Database

The database should already be set up from PR3.2a. Verify connection:

```bash
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM content_embeddings;"
```

## Testing

### Unit Tests (Fast)

```bash
pytest tests/unit/
```

### Integration Tests (Slow, requires API keys)

```bash
pytest tests/integration/ -v
```

### Skip Slow Tests (for CI)

```bash
pytest -m "not slow"
```

### Comparison Tests

```bash
pytest tests/comparison/ -v
```

### Code Coverage

```bash
pytest tests/unit/ --cov=app/services --cov-report=html
open htmlcov/index.html
```

## Manual Testing

### Test Embeddings

```bash
python -m scripts.test_embeddings "What is PADI Open Water?"
```

### Test LLM (Groq)

```bash
python -m scripts.test_llm --provider groq "Explain buoyancy control"
```

### Test LLM (Gemini)

```bash
python -m scripts.test_llm --provider gemini "Explain buoyancy control"
```

### Test RAG Pipeline

```bash
python -m scripts.test_rag "What certifications do I need for Tioman?"
python -m scripts.test_rag --top-k 3 --min-similarity 0.7 "What is decompression sickness?"
```

## Code Quality

### Linting

```bash
ruff check .
```

### Formatting

```bash
ruff format .
```

### Type Checking

```bash
mypy app
```

## Project Structure

```
backend/
├── app/
│   ├── services/
│   │   ├── embeddings/       # Embedding generation with Gemini
│   │   │   ├── base.py        # Abstract interface
│   │   │   ├── gemini.py      # Gemini provider
│   │   │   ├── cache.py       # In-memory LRU cache
│   │   │   └── factory.py     # Provider factory
│   │   ├── llm/              # LLM providers
│   │   │   ├── base.py        # Abstract interface
│   │   │   ├── groq.py        # Groq provider
│   │   │   ├── gemini.py      # Gemini provider
│   │   │   ├── factory.py     # Provider factory
│   │   │   └── types.py       # Message/Response types
│   │   └── rag/              # RAG pipeline
│   │       ├── chunker.py     # Text chunking logic
│   │       ├── retriever.py   # Vector similarity search
│   │       ├── pipeline.py    # RAG orchestration
│   │       └── types.py       # RAG types
│   ├── db/                   # Database models and repositories
│   └── core/                 # Configuration and settings
├── tests/
│   ├── unit/                 # Unit tests (mocked)
│   ├── integration/          # Integration tests (real APIs)
│   └── comparison/           # Python vs TypeScript comparison
└── scripts/                  # Manual test scripts
```

## Configuration

All configuration is via environment variables (see `.env.example`):

### LLM Configuration

- `DEFAULT_LLM_PROVIDER`: `groq` or `gemini`
- `DEFAULT_LLM_MODEL`: Model name (default: `gemini-2.0-flash`)
- `LLM_TEMPERATURE`: 0.0-1.0 (default: 0.7)
- `LLM_MAX_TOKENS`: Max tokens per generation (default: 2048)

### Embedding Configuration

- `EMBEDDING_MODEL`: Gemini model (default: `text-embedding-004`)
- `EMBEDDING_BATCH_SIZE`: Max texts per batch (default: 100)
- `EMBEDDING_CACHE_SIZE`: Cache entries (default: 1000)
- `EMBEDDING_CACHE_TTL`: TTL in seconds (default: 3600)

### RAG Configuration

- `ENABLE_RAG`: Enable/disable RAG (default: `true`)
- `RAG_TOP_K`: Number of chunks to retrieve (default: 5)
- `RAG_MIN_SIMILARITY`: Minimum similarity threshold (default: 0.5)

## Development Workflow

1. **Write code** in `app/services/`
2. **Write tests** in `tests/unit/` (run frequently)
3. **Run linter**: `ruff check . && ruff format .`
4. **Run type checker**: `mypy app`
5. **Run unit tests**: `pytest tests/unit/ -v`
6. **Manual test**: Use `scripts/test_*.py`
7. **Integration test** (optional): `pytest tests/integration/`

## Next Steps

After PR3.2b is merged:
- **PR3.2c**: Agent system and orchestration
- **PR3.2d**: Content ingestion scripts
- **PR3.2e**: Frontend integration

## Troubleshooting

### Import Errors

Make sure you've installed the package in editable mode:

```bash
pip install -e .
```

### API Errors

Check that API keys are set:

```bash
echo $GEMINI_API_KEY
echo $GROQ_API_KEY
```

### Database Connection Errors

Verify DATABASE_URL is correct:

```bash
psql "$DATABASE_URL" -c "SELECT version();"
```

### Test Failures

Run with verbose output:

```bash
pytest tests/unit/ -vv
```

Show print statements:

```bash
pytest tests/unit/ -s
```

Run specific test:

```bash
pytest tests/unit/services/test_embeddings.py::TestGeminiEmbeddingProvider::test_embed_text_success -v
```
