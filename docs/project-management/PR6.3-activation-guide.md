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

# First, do a dry-run to verify
.venv/bin/python src/backend/scripts/migrate_embeddings_768.py --dry-run

# Then run actual migration
.venv/bin/python src/backend/scripts/migrate_embeddings_768.py
```

**Expected Steps:**
1. Schema check (validates 768 dimension)
2. Clear existing embeddings (confirms deletion)
3. Re-ingest content with new embeddings (takes ~5-10 minutes)
4. Verify 768-dimensional embeddings (automatic)

**Expected Output:**
```
✅ Migration completed successfully!
   - Cleared old 3072-dimensional embeddings
   - Ingested new 768-dimensional embeddings
   - Verified correct dimensions
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
    "conversationId": "test-123"
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
EMBEDDING_MODEL=gemini-embedding-001  # Revert to old model
```

Then restart servers with `dovvy-stop && dovvy-backend` (in background).

## Troubleshooting

### Issue: "No embeddings found after migration"
**Cause:** Content ingestion failed  
**Solution:** Check ingestion logs, ensure GEMINI_API_KEY is valid

### Issue: "Expected embedding dimension 768, got 3072"
**Cause:** Old embeddings not cleared before migration  
**Solution:** Run `clear_embeddings.py` then retry migration

### Issue: "HNSW index not created"
**Cause:** pgvector extension issue  
**Solution:** Verify pgvector installed: `psql $DATABASE_URL -c "SELECT * FROM pg_extension WHERE extname='vector'"`

## Verification Checklist

After activation, verify:

- [ ] Backend starts without errors (`dovvy-status` shows port 8000)
- [ ] Frontend starts without errors (`dovvy-status` shows port 3000)
- [ ] Chat endpoint returns responses
- [ ] RAG retrieval returns relevant results
- [ ] Database has 768-dim embeddings: `psql $DATABASE_URL -c "SELECT pg_column_size(embedding) FROM content_embeddings LIMIT 1"`
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
psql $DATABASE_URL -c "SELECT COUNT(*), pg_column_size(embedding) FROM content_embeddings GROUP BY pg_column_size(embedding)"

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

