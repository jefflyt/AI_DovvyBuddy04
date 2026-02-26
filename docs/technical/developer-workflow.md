# Developer Workflow Guide

**Last Updated:** January 31, 2026  
**Status:** Active - Refactored Structure (Backend at Root)

---

## Overview

This guide covers the standard developer workflow for DovvyBuddy, with emphasis on the new Python-first backend approach.

---

## Setup

### Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/jefflyt/AI_DovvyBuddy04.git
cd AI_DovvyBuddy04

# 2. Install frontend dependencies
pnpm install

# 3. Install backend dependencies
cd src/backend
python3 -m pip install -e .
cd ..

# 4. Set up environment
cp .env.example .env.local
# Edit .env.local with your:
# - DATABASE_URL (PostgreSQL with pgvector)
# - GEMINI_API_KEY
# - Other required variables

# 5. Set up database
pnpm db:push
```

### Verify Setup

```bash
# Check Python imports
cd src/backend && python3 -c "import scripts.common; print('✓ OK')" && cd ../..

# Run tests
cd src/backend && python3 -m pytest tests/unit/scripts/ -v && cd ../..
**Status:** Active - Refactored Structure (Backend at src/backend)
# Test validation script
```

---

## Daily Workflow

### Content Authoring

cd src/backend

1. **Create/edit content files** in `content/` directory
   cd ../..

   # Add frontmatter to each .md file:

   ***

   title: "Your Title"
   description: "Your description"
   tags: ["tag1", "tag2"]

   ***

   cd src/backend && python3 -c "import scripts.common; print('✓ OK')" && cd ../..

2. **Validate content**
   cd src/backend && python3 -m pytest tests/unit/scripts/ -v && cd ../..
   pnpm content:validate-py

   ```

   ```

3. **Fix any validation errors** reported

4. **Ingest content** (full or incremental)

   ```bash
   # Incremental (recommended for daily work)
   pnpm content:ingest-incremental-py

   # Full re-ingestion (if chunking logic changed)
   pnpm content:ingest-py
   ```

### Code Development

1. **Start development server**

   ```bash
   pnpm dev
   ```

2. **Make code changes**

3. **Run tests**

   ```bash
   # Frontend/integration tests
   pnpm test

   # Backend unit tests
   cd src/backend
   python3 -m pytest tests/unit/ -v
   cd ..
   ```

4. **Type check**

   ```bash
   pnpm typecheck
   ```

5. **Lint and format**
   ```bash
   pnpm lint
   pnpm format:fix
   ```

### Git Workflow

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes and commit
git add .
cd src/backend

# 3. Push and create PR
git push origin feature/your-feature-name

# 4. After PR approval, merge to main
git checkout main
git pull origin main
```

---

cd ../..

### Python Scripts (Default)

All content processing now uses Python scripts with better UX:

```bash
# Validate content
pnpm content:validate-py
cd src/backend

# Ingest content (full)
pnpm content:ingest-py
# Output: Progress bar, statistics (files, chunks, time)

# Ingest content (incremental)
pnpm content:ingest-incremental-py
# Output: Only processes changed files

# Benchmark RAG
pnpm content:benchmark-py
cd ../..

# Clear embeddings
pnpm content:clear-py
# Output: Confirmation prompt, deletion statistics
```

### Advanced Options

cd src/backend

```bash
cd ../..
cd src/backend
python3 -m scripts.validate_content --required-fields title description category

# Ingestion dry run
python3 -m scripts.ingest_content --dry-run

# Benchmark with custom queries
python3 -m scripts.benchmark_rag --queries-file my_queries.json --iterations 3
cd src/backend
# Clear specific pattern
cd ../..

cd ..

### Legacy TypeScript Scripts (Deprecated)

**Note:** These will be removed in a future release.

- **API:** `src/backend/README.md`
# Old commands (still work but deprecated)
pnpm content:validate
pnpm content:ingest
pnpm content:clear
pnpm benchmark:rag
```

---

## Testing

### Test Structure

```
tests/
├── unit/                    # Fast, isolated tests
│   ├── frontend/           # Frontend unit tests (Vitest)
| Import errors | `cd src/backend && python3 -m pip install -e .` |
│   └── src/backend/            # Backend unit tests (pytest)
│       └── scripts/        # Script unit tests
└── integration/            # E2E tests
    └── scripts/            # Script integration tests
```

### Running Tests

```bash
# All frontend tests
pnpm test

# Backend unit tests
cd src/backend
python3 -m pytest tests/unit/ -v

# Backend integration tests (requires DB)
python3 -m pytest tests/integration/ -v

# Script tests only
python3 -m pytest tests/unit/scripts/ -v

# With coverage
python3 -m pytest tests/ --cov=scripts --cov=app

cd ..
```

### Writing Tests

**Frontend (Vitest):**

```typescript
import { describe, it, expect } from 'vitest'

describe('MyComponent', () => {
  it('should render correctly', () => {
    // Test code
  })
})
```

**Backend (pytest):**

```python
import pytest

def test_my_function():
    """Test description."""
    result = my_function()
    assert result == expected
```

---

## Database Operations

### Common Operations

```bash
# Generate migration
pnpm db:generate

# Apply migrations
pnpm db:push

# Open database GUI
pnpm db:studio

# Verify embeddings
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM content_embeddings"

# Check pgvector extension
psql "$DATABASE_URL" -c "SELECT * FROM pg_extension WHERE extname='vector'"
```

### Troubleshooting

**Clear all embeddings:**

```bash
pnpm content:clear-py
```

**Reset database schema:**

```bash
pnpm db:push --force-reset
```

**Check database connection:**

```bash
cd src/backend
python3 -c "from app.db.session import SessionLocal; db = SessionLocal(); print('✓ Connected')"
cd ..
```

---

## Debugging

### Backend Debugging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
cd src/backend
python3 -m scripts.ingest_content --dry-run
cd ..

# Check service logs
tail -f logs/app.log  # If logging to file
```

### Frontend Debugging

```bash
# Start with debug mode
DEBUG=* pnpm dev

# Check Next.js build
pnpm build
```

### Common Issues

**Import errors:**

```bash
# Reinstall backend package
cd src/backend
python3 -m pip install -e . --force-reinstall
cd ..
```

**Database connection failures:**

```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Test connection
psql "$DATABASE_URL" -c "SELECT 1"
```

**Embedding generation failures:**

```bash
# Check API key
echo $GEMINI_API_KEY

# Test API
cd src/backend
python3 -c "from app.services.embedding import EmbeddingService; s = EmbeddingService(); print(s.generate_embeddings(['test']))"
cd ..
```

---

## Performance Optimization

### Content Ingestion

```bash
# Use incremental mode for daily updates
pnpm content:ingest-incremental-py

# Adjust batch size for slower networks
cd src/backend
python3 -m scripts.ingest_content --batch-size 5
cd ..
```

### RAG Performance

```bash
# Benchmark regularly
pnpm content:benchmark-py

# Track metrics over time
ls -lt benchmark-results-*.json | head -5
```

---

## CI/CD

### GitHub Actions Workflows

- **CI** (`.github/workflows/ci.yml`): Frontend tests, build, lint
- **Content Validation** (`.github/workflows/content-validation.yml`): Validates content on PR

### Pre-commit Checks

```bash
# Run before committing
pnpm typecheck
pnpm lint
pnpm test
cd src/backend && python3 -m pytest tests/unit/ && cd ../..
```

---

## Deployment

### Vercel (Frontend)

Automatic deployment on push to `main`:

- Build: `pnpm build`
- Environment variables set in Vercel dashboard

### Cloud Run (Backend)

```bash
# Build Docker image
cd src/backend
docker build -t dovvybuddy-backend .

# Deploy to Cloud Run
gcloud run deploy dovvybuddy-backend \
  --image gcr.io/your-project/dovvybuddy-backend \
  --platform managed \
  --region us-central1

cd ..
```

---

## Documentation

### Key Files

- **Setup:** `README.md`
- **Architecture:** `docs/technical/`
- **Plans:** `docs/plans/`
- **API:** `src/backend/README.md`
- **Content Guide:** `content/README.md`

### Updating Documentation

```bash
# After implementing features
# 1. Update relevant docs in docs/
# 2. Add to project-management/ for summaries
# 3. Update NEXT_STEPS.md if workflow changes
```

---

## Quick Troubleshooting

| Issue             | Solution                                                                        |
| ----------------- | ------------------------------------------------------------------------------- |
| Import errors     | `cd src/backend && python3 -m pip install -e .`                                 |
| Database errors   | Check `DATABASE_URL`, verify pgvector extension                                 |
| API key errors    | Check `GEMINI_API_KEY` in `.env.local`                                          |
| Test failures     | `python3 -m pytest tests/unit/ -v`                                              |
| Build failures    | `pnpm clean && pnpm install`                                                    |
| Validation errors | Check frontmatter format in `.md` files                                         |
| Slow ingestion    | Incremental mode is default; run normal ingest and avoid `--full` unless needed |

---

## Next Steps

After PR3.2d completion:

1. ✅ Validate all content passes validation
2. ✅ Ingest content with Python scripts
3. ⏳ Set up integration tests with test DB
4. ⏳ Frontend integration (PR3.2e)
5. ⏳ Production deployment (PR3.2f)

---

**Questions?** Check:

- Backend: `src/backend/README.md`
- General: `docs/NEXT_STEPS.md`
- Implementation: `docs/project-management/PR3.2d-implementation-summary.md`
