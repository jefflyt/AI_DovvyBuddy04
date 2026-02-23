# Backend Testing Quick Reference

## Running Tests with Real Network Access

### 1. Environment Setup

Create `.env` file in `src/backend/`:

```bash
cd src/backend
cp .env.example .env
```

Edit `.env` with your credentials:
```bash
# Required for integration tests
GEMINI_API_KEY=your_actual_gemini_key
GROQ_API_KEY=your_actual_groq_key
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dovvybuddy_test

# Optional for full testing
EMBEDDING_MODEL=text-embedding-004
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_LLM_MODEL=gemini-2.0-flash
```

### 2. Install Dependencies

```bash
cd src/backend
python3 -m pip install -e .
python3 -m pip install pytest pytest-asyncio pytest-cov
```

### 3. Run Test Suites

#### Full Test Suite (requires network)
```bash
cd src/backend
python3 -m pytest tests/ -v
```

#### Unit Tests Only (mostly offline)
```bash
python3 -m pytest tests/unit/ -v
```

#### Integration Tests (requires network + DB)
```bash
python3 -m pytest tests/integration/ -v
```

#### Specific Test File
```bash
python3 -m pytest tests/integration/api/test_lead.py -v
```

#### With Coverage Report
```bash
python3 -m pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### 4. Database Setup for Integration Tests

#### Option A: Local PostgreSQL with pgvector
```bash
# Install PostgreSQL and pgvector
brew install postgresql pgvector

# Create test database
createdb dovvybuddy_test

# Enable pgvector
psql dovvybuddy_test -c "CREATE EXTENSION vector;"

# Run migrations
export DATABASE_URL="postgresql+asyncpg://localhost/dovvybuddy_test"
python3 -m alembic upgrade head
```

#### Option B: Docker PostgreSQL
```bash
# Run PostgreSQL with pgvector
docker run -d \
  --name dovvybuddy-test-db \
  -e POSTGRES_PASSWORD=testpass \
  -e POSTGRES_DB=dovvybuddy_test \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Update .env
DATABASE_URL=postgresql+asyncpg://postgres:testpass@localhost:5432/dovvybuddy_test

# Run migrations
python3 -m alembic upgrade head
```

### 5. Alembic Migration Testing

#### Check Current Migration State
```bash
cd src/backend
python3 -m alembic current
```

#### View Migration History
```bash
python3 -m alembic history
```

#### Upgrade to Latest
```bash
python3 -m alembic upgrade head
```

#### Upgrade to Specific Revision
```bash
python3 -m alembic upgrade 003_pgvector_embedding_column
```

#### Downgrade One Step
```bash
python3 -m alembic downgrade -1
```

#### Generate SQL (offline mode - needs env.py fix)
```bash
python3 -m alembic upgrade 003_pgvector_embedding_column --sql
```

### 6. Common Test Patterns

#### Run Only Fast Tests
```bash
python3 -m pytest -m "not slow" tests/
```

#### Run Only Integration Tests
```bash
python3 -m pytest -m integration tests/
```

#### Stop at First Failure
```bash
python3 -m pytest -x tests/
```

#### Show Full Traceback
```bash
python3 -m pytest --tb=long tests/
```

#### Run Tests in Parallel (requires pytest-xdist)
```bash
pip install pytest-xdist
python3 -m pytest -n auto tests/
```

### 7. Troubleshooting

#### Import Errors
If you see `ModuleNotFoundError`:
```bash
# Reinstall package in editable mode
cd src/backend
pip install -e .
```

#### Database Connection Errors
```bash
# Verify database is running
pg_isready -h localhost -p 5432

# Check connection string
echo $DATABASE_URL

# Test connection with psql
psql $DATABASE_URL
```

#### Missing API Keys
```bash
# Check if environment variables are loaded
cd src/backend
python3 -c "from app.core.config import settings; print(settings.GEMINI_API_KEY[:10])"
```

### 8. Migration 003 Deployment

#### Staging Deployment
```bash
# Set staging database URL
export DATABASE_URL="postgresql://user:pass@staging.example.com:5432/dovvybuddy"

# Verify current state
python3 -m alembic current

# Preview upgrade (once env.py fixed)
python3 -m alembic upgrade 003_pgvector_embedding_column --sql

# Execute upgrade
python3 -m alembic upgrade 003_pgvector_embedding_column

# Verify new state
python3 -m alembic current
# Expected: 003_pgvector_embedding_column (head)

# Verify pgvector extension
psql $DATABASE_URL -c "SELECT * FROM pg_extension WHERE extname='vector';"

# Verify new column
psql $DATABASE_URL -c "\\d content_embeddings"
```

---

**For CI/CD:** Export environment variables in your CI configuration before running tests.

**For Local Development:** Keep `.env` file with test credentials (don't commit to git).
