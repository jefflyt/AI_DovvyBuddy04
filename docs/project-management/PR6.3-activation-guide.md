# PR6.3 Quick Activation Guide

**Purpose:** Step-by-step commands to activate PR6.3 changes in your development environment

## Prerequisites Checklist

- [x] Code changes implemented (PR6.3)
- [ ] Database backup created (optional but recommended)
- [ ] Dev servers stopped (`dovvy-stop`)

## Activation Steps

### 1. Install pytest (if not already installed)

```bash
cd /Users/jefflee/Documents/AIProjects/AI_DovvyBuddy04
.venv/bin/pip install pytest pytest-asyncio
```

### 2. Run Unit Tests (Verify Changes)

```bash
cd /Users/jefflee/Documents/AIProjects/AI_DovvyBuddy04
.venv/bin/python -m pytest src/backend/tests/unit/services/test_embeddings.py -v
```

**Expected Output:** All tests should pass, including the new Matryoshka test

### 3. Apply Database Migration

```bash
cd /Users/jefflee/Documents/AIProjects/AI_DovvyBuddy04/src/backend
../../.venv/bin/alembic upgrade 004_embedding_dimension_768
```

**Expected Output:**

```
INFO  [alembic.runtime.migration] Running upgrade 003_pgvector_embedding_column -> 004_embedding_dimension_768
```

**Verify Migration:**

```bash
# Check the embedding column dimension
psql $DATABASE_URL -c "SELECT COUNT(*) FROM content_embeddings"

# Check HNSW index exists
psql $DATABASE_URL -c "\\d content_embeddings"
```

### 4. Run Data Migration (Re-generate Embeddings)

```bash
cd /Users/jefflee/Documents/AIProjects/AI_DovvyBuddy04

# Apply latest schema migration
cd src/backend
../../.venv/bin/alembic upgrade head

# Rebuild embeddings with current model/dimension
../../.venv/bin/python -m scripts.ingest_content --full --content-dir ../../content
```

**Expected Steps:**

1. Schema migration at latest head
2. Full content re-ingestion
3. New embeddings written at 768 dimensions

If your content directory is at project root (`content/`), run explicit ingestion path:

```bash
cd /Users/jefflee/Documents/AIProjects/AI_DovvyBuddy04/src/backend
../../.venv/bin/python -m scripts.ingest_content --full --content-dir ../../content
```

**Verification Command:**

```bash
cd /Users/jefflee/Documents/AIProjects/AI_DovvyBuddy04/src/backend
../../.venv/bin/python - <<'PY'
from sqlalchemy import text
from app.db.session import SessionLocal

db = SessionLocal()
try:
  dims = db.execute(text("SELECT MIN(vector_dims(embedding)), MAX(vector_dims(embedding)), COUNT(*) FROM content_embeddings WHERE embedding IS NOT NULL")).fetchone()
  print('min_dim=', dims[0], 'max_dim=', dims[1], 'count=', dims[2])
finally:
  db.close()
PY
```

### 5. Restart Development Servers

```bash
# Start backend
dovvy-backend

# In another terminal, start frontend
dovvy-frontend
```

### 6. Verify RAG Pipeline Works

**Test Query:**

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the certifications?",
    "sessionId": "test-123"
  }'
```

**Expected:** Should return relevant results about diving certifications

## Rollback (If Issues Occur)

### Database Rollback

```bash
cd /Users/jefflee/Documents/AIProjects/AI_DovvyBuddy04/src/backend
../../.venv/bin/alembic downgrade 003_pgvector_embedding_column
```

### Configuration Rollback

Edit `.env.local` and change:

```bash
EMBEDDING_MODEL=text-embedding-004
EMBEDDING_DIMENSION=768
```

Then restart servers with `dovvy-stop && dovvy-backend` (in background).

## Troubleshooting

### Issue: "No embeddings found after migration"

**Cause:** Content ingestion failed  
**Solution:** Check ingestion logs, ensure GEMINI_API_KEY is valid

### Issue: "Expected embedding dimension 768, got 3072"

**Cause:** Old embeddings not cleared before migration  
**Solution:** Run `clear_embeddings.py` then retry migration

### Issue: "Content directory not found: .../src/content"

**Cause:** Ingestion default path is wrong for this repo layout  
**Solution:** Use explicit content path: `--content-dir ../../content`

### Issue: "HNSW index not created"

**Cause:** pgvector extension issue  
**Solution:** Verify pgvector installed: `psql $DATABASE_URL -c "SELECT * FROM pg_extension WHERE extname='vector'"`

## Verification Checklist

After activation, verify:

- [ ] Backend starts without errors (`dovvy-status` shows port 8000)
- [ ] Frontend starts without errors (`dovvy-status` shows port 3000)
- [ ] Chat endpoint returns responses
- [ ] RAG retrieval returns relevant results
- [ ] Database has 768-dim embeddings: `psql $DATABASE_URL -c "SELECT MIN(vector_dims(embedding)), MAX(vector_dims(embedding)) FROM content_embeddings WHERE embedding IS NOT NULL"`
- [ ] HNSW index exists: `psql $DATABASE_URL -c "\\di idx_content_embeddings_hnsw"`

## Quick Commands Reference

```bash
# Status check
dovvy-status

# Stop all servers
dovvy-stop

# Start backend only
dovvy-backend

# Start frontend only
dovvy-frontend

# Check database
psql $DATABASE_URL -c "SELECT COUNT(*), MIN(vector_dims(embedding)), MAX(vector_dims(embedding)) FROM content_embeddings WHERE embedding IS NOT NULL"

# View migration history
cd src/backend && ../../.venv/bin/alembic history --verbose
```

## Success Indicators

✅ **Backend logs:** "Initialized GeminiEmbeddingProvider with model=text-embedding-004, dimension=768"  
✅ **Database check:** All embeddings are 768 dimensions (check with pg_column_size)  
✅ **Search works:** RAG queries return relevant results  
✅ **HNSW index:** Index queries shown in EXPLAIN output

---

**Estimated Total Time:** 15-20 minutes  
**Critical Path:** Database migration → Data migration → Server restart  
**Rollback Time:** < 5 minutes (if needed)

**Questions?** See [PR6.3-implementation-summary.md](./PR6.3-implementation-summary.md) for full details.
