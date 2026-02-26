# Backend Testing Quick Reference

## Running Tests with Real Network Access

### 1. Environment Setup

Use project root `.env.local`:

```bash
# from project root
cp .env.example .env.local
```

Edit `.env.local` with your credentials:
```bash
# Required for integration tests
GEMINI_API_KEY=your_actual_gemini_key
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dovvybuddy_test

# Optional for full testing
EMBEDDING_MODEL=text-embedding-004
EMBEDDING_DIMENSION=768
DEFAULT_LLM_PROVIDER=gemini
DEFAULT_LLM_MODEL=gemini-2.5-flash-lite
ENABLE_ADK=true
ADK_MODEL=gemini-2.5-flash-lite
```

### 2. Install Dependencies

```bash
cd src/backend
../../.venv/bin/pip install -e .
../../.venv/bin/pip install pytest pytest-asyncio pytest-cov
```

### 3. Run Test Suites

Use these commands from project root (verified passing on 2026-02-26):

```bash
export PYTHONPATH="$PWD/src/backend"
```

#### Unit Tests (verified)
```bash
.venv/bin/python -m pytest src/backend/tests/unit -q
```

#### Integration Tests (verified: network + DB)
```bash
.venv/bin/python -m pytest src/backend/tests/integration -q
```

#### Full Backend Validation (recommended sequence)

Run unit and integration as two explicit commands:

```bash
.venv/bin/python -m pytest src/backend/tests/unit -q
.venv/bin/python -m pytest src/backend/tests/integration -q
```

Or run a single combined command (verified):

```bash
.venv/bin/python -m pytest src/backend/tests/unit src/backend/tests/integration -q --import-mode=importlib
```

#### Specific Test File
```bash
.venv/bin/python -m pytest src/backend/tests/integration/api/test_lead.py -q
```

#### With Coverage Report
```bash
.venv/bin/python -m pytest src/backend/tests --cov=app --cov-report=html
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
.venv/bin/python -m pytest -m "not slow" src/backend/tests
```

#### Run Only Integration Tests
```bash
.venv/bin/python -m pytest -m integration src/backend/tests
```

#### Stop at First Failure
```bash
.venv/bin/python -m pytest -x src/backend/tests
```

#### Show Full Traceback
```bash
.venv/bin/python -m pytest --tb=long src/backend/tests
```

#### Run Tests in Parallel (requires pytest-xdist)
```bash
pip install pytest-xdist
.venv/bin/python -m pytest -n auto src/backend/tests
```

### 7. Troubleshooting

#### Import Errors
If you see `ModuleNotFoundError`:
```bash
# Ensure backend package path is visible
export PYTHONPATH="$PWD/src/backend"

# Reinstall backend in editable mode
cd src/backend && ../../.venv/bin/pip install -e .
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

### 8. Migration Deployment (Current Head)

#### Staging Deployment
```bash
# Set staging database URL
export DATABASE_URL="postgresql://user:pass@staging.example.com:5432/dovvybuddy"

# Verify current state
python3 -m alembic current

# Preview upgrade SQL
python3 -m alembic upgrade head --sql

# Execute upgrade
python3 -m alembic upgrade head

# Verify new state
python3 -m alembic current
# Expected: latest head (embedding dimension 768 migration)

# Verify pgvector extension
psql $DATABASE_URL -c "SELECT * FROM pg_extension WHERE extname='vector';"

# Verify new column
psql $DATABASE_URL -c "\\d content_embeddings"
```

---

**For CI/CD:** Export environment variables in your CI configuration before running tests.

**For Local Development:** Keep test credentials in root `.env.local` (don't commit to git).
