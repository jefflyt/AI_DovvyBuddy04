# Neon Database Update Guide

**Last Updated:** January 2, 2026  
**Applies To:** DovvyBuddy AI Database Operations

---

## Overview

This guide explains how to update the Neon PostgreSQL database when metadata or content changes. 

### Two Types of Updates

**1. Structured Data Updates** (This Guide)
- Updates: `dive_sites`, `destinations`, `certifications` tables
- Source: JSON metadata files
- Tools: `scripts/update-dive-sites.ts` and similar
- Use When: Adding/updating dive sites, destinations, certification metadata

**2. Content Embeddings** (See [Content Ingestion Guide](./content-ingestion-guide.md))
- Updates: `content_embeddings` table
- Source: Markdown content files
- Tools: `scripts/ingest-content.ts`
- Use When: Markdown content changes (for RAG/semantic search)

This guide covers:

1. Adding new dive destinations to the database
2. Adding/updating dive sites with metadata
3. Adding new certifications or course data
4. Updating existing structured records

---

## Prerequisites

### Required Access

- Neon database connection string (in root `.env.local`)
- PostgreSQL client (`psql`) installed
- Backend Python environment set up
- API keys for embedding generation (Gemini API)

### Environment Variables

Ensure you have the correct `DATABASE_URL`:

```bash
# For asyncpg (Python backend)
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_1ovLCsZQxqJ7@ep-jolly-hall-a1bialaz-pooler.ap-southeast-1.aws.neon.tech/neondb?ssl=require

# For psql commands (standard PostgreSQL URL)
DATABASE_URL=postgresql://neondb_owner:npg_1ovLCsZQxqJ7@ep-jolly-hall-a1bialaz-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
```

---

## Common Update Scenarios

### Scenario 1: New Items Added to JSON Files

When you add new destinations, certifications, or other data to JSON configuration files:

#### Step 1: Identify What Changed

Check which JSON files were updated:

```bash
# Check git status
git status

# View changes in specific file
git diff src/data/destinations.json
git diff src/data/certifications.json
```

#### Step 2: Run Database Migration (If Schema Changed)

If the JSON structure includes new fields that require database schema updates:

```bash
# From src/backend directory
cd src/backend

# Create new Alembic migration
alembic revision --autogenerate -m "Add new fields for [feature name]"

# Review the generated migration
cat alembic/versions/[newest_file].py

# Apply migration
alembic upgrade head

# Verify schema
psql "$DATABASE_URL" -c "\d [table_name]"
```

#### Step 3: Update Application Code

If new JSON fields need to be processed:

1. Update Pydantic models in `src/backend/app/db/models/`
2. Update repository methods if needed
3. Test locally

#### Step 4: Re-ingest Content (If Content Files Added)

If new JSON entries correspond to new markdown content:

```bash
# From project root
cd /Users/jefflee/Documents/AIProjects/AI_DovvyBuddy04

# Check what content files exist
ls -R content/

# Ingest all new content
pnpm tsx scripts/ingest-content.ts

# Or ingest specific directory
pnpm tsx scripts/ingest-content.ts --dir content/destinations/[NewDestination]
```

#### Step 5: Verify Updates

```bash
# Check total records
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM content_embeddings;"

# Check for new content paths
psql "$DATABASE_URL" -c "SELECT DISTINCT content_path FROM content_embeddings WHERE created_at > NOW() - INTERVAL '1 hour';"

# Test retrieval
cd src/backend
python -m scripts.test_rag "Tell me about [new destination/certification]"
```

---

### Scenario 2: Destination Data Updated

When `src/data/destinations.json` has new destinations:

#### Example: Adding Bali, Indonesia

**1. Create Content Files:**

```bash
# Create destination directory
mkdir -p content/destinations/Bali-Indonesia

# Create content files
touch content/destinations/Bali-Indonesia/overview.md
touch content/destinations/Bali-Indonesia/dive-sites.md
touch content/destinations/Bali-Indonesia/travel-info.md
```

**2. Write Content:**

Edit each markdown file with relevant information about Bali diving.

**3. Update JSON (if applicable):**

If you maintain a `destinations.json`:

```json
{
  "destinations": [
    {
      "id": "bali-indonesia",
      "name": "Bali, Indonesia",
      "country": "Indonesia",
      "region": "Southeast Asia",
      "contentPath": "destinations/Bali-Indonesia",
      "featured": true,
      "difficulty": "all-levels",
      "bestMonths": [6, 7, 8, 9],
      "highlights": [
        "Manta rays at Manta Point",
        "USS Liberty wreck",
        "Coral gardens"
      ]
    }
    // ... other destinations
  ]
}
```

**4. Ingest Content:**

```bash
# Ingest just this destination
pnpm tsx scripts/ingest-content.ts --dir content/destinations/Bali-Indonesia

# Verify
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM content_embeddings WHERE content_path LIKE '%Bali-Indonesia%';"
```

**5. Test:**

```bash
cd src/backend
python -m scripts.test_rag "What are the best dive sites in Bali?"
python -m scripts.test_rag "When is the best time to dive in Bali?"
```

---

### Scenario 3: Certification Data Updated

When `src/data/certifications.json` has new certifications:

#### Example: Adding SSI Advanced Adventurer

**1. Create Content File:**

```bash
mkdir -p content/certifications/ssi
touch content/certifications/ssi/advanced-adventurer.md
```

**2. Write Content:**

```markdown
# SSI Advanced Adventurer Certification

## Overview

The SSI Advanced Adventurer program allows you to explore five different specialty diving activities...

## Prerequisites

- SSI Open Water Diver (or equivalent)
- Minimum age: 12 years

## Course Structure

### Five Adventure Dives

1. Deep Diving (mandatory)
2. Navigation (mandatory)
3. Three specialty dives of your choice

## Skills Covered

- Deep diving techniques
- Underwater navigation
- [Additional skills based on chosen specialties]

## Certification Requirements

- Complete all five adventure dives
- Demonstrate competency in all skills
- Written exam (varies by specialty)
```

**3. Update JSON:**

```json
{
  "certifications": [
    {
      "id": "ssi-advanced-adventurer",
      "name": "SSI Advanced Adventurer",
      "provider": "SSI",
      "level": "intermediate",
      "contentPath": "certifications/ssi/advanced-adventurer.md",
      "prerequisites": ["ssi-open-water"],
      "minAge": 12,
      "dives": 5,
      "depth": "30m"
    }
    // ... other certifications
  ]
}
```

**4. Ingest:**

```bash
pnpm tsx scripts/ingest-content.ts --file content/certifications/ssi/advanced-adventurer.md

# Verify
psql "$DATABASE_URL" -c "SELECT content_path, LEFT(chunk_text, 100) FROM content_embeddings WHERE content_path LIKE '%ssi/advanced-adventurer%';"
```

**5. Test:**

```bash
cd src/backend
python -m scripts.test_rag "What is SSI Advanced Adventurer certification?"
python -m scripts.test_rag "What are the prerequisites for SSI Advanced Adventurer?"
```

---

### Scenario 4: Bulk Update - Multiple New Items

When you've added multiple destinations, certifications, or safety topics:

**1. Review All Changes:**

```bash
# See all modified/new files
git status

# Review each change
git diff src/data/
ls -la content/destinations/
ls -la content/certifications/
ls -la content/safety/
```

**2. Backup Current Database (Optional but Recommended):**

```bash
# Backup embeddings table
psql "$DATABASE_URL" -c "CREATE TABLE content_embeddings_backup_$(date +%Y%m%d) AS SELECT * FROM content_embeddings;"

# Verify backup
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM content_embeddings_backup_$(date +%Y%m%d);"
```

**3. Clear and Re-ingest (Safest for Bulk Updates):**

```bash
# Clear all embeddings
pnpm tsx scripts/clear-embeddings.ts

# Re-ingest all content
pnpm tsx scripts/ingest-content.ts

# Monitor progress (output will show files being processed)
```

**4. Verify Complete Update:**

```bash
# Check total count
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM content_embeddings;"

# Check all content paths
psql "$DATABASE_URL" -c "SELECT DISTINCT substring(content_path from '^[^/]+') as category, COUNT(*) FROM content_embeddings GROUP BY category;"

# Expected output:
#   category      | count
# ----------------+-------
#  certifications |   120
#  destinations   |   350
#  safety         |    80
#  faq            |    45
```

**5. Run Integration Tests:**

```bash
cd src/backend
pytest tests/integration/services/test_rag_integration.py -v

# Expected: All tests pass
```

**6. Spot Test New Content:**

```bash
# Test each new destination/certification/topic
python -m scripts.test_rag "Tell me about [new destination]"
python -m scripts.test_rag "What is [new certification]?"
python -m scripts.test_rag "How do I [new safety topic]?"
```

---

## Database Maintenance

### Check Database Status

```bash
# Connection test
psql "$DATABASE_URL" -c "SELECT version();"

# Table sizes
psql "$DATABASE_URL" -c "
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Embedding statistics
psql "$DATABASE_URL" -c "
SELECT 
    COUNT(*) as total_embeddings,
    COUNT(DISTINCT content_path) as unique_files,
    MIN(created_at) as oldest_embedding,
    MAX(created_at) as newest_embedding,
    pg_size_pretty(pg_total_relation_size('content_embeddings')) as table_size
FROM content_embeddings;"
```

### Clean Up Old Embeddings

If you've removed content files:

```bash
# List embeddings for non-existent files (manual verification needed)
psql "$DATABASE_URL" -c "SELECT DISTINCT content_path FROM content_embeddings ORDER BY content_path;"

# Delete specific path
psql "$DATABASE_URL" -c "DELETE FROM content_embeddings WHERE content_path LIKE 'old-path/%';"

# Verify deletion
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM content_embeddings WHERE content_path LIKE 'old-path/%';"
```

### Optimize Database

```bash
# Vacuum and analyze (reclaim space, update statistics)
psql "$DATABASE_URL" -c "VACUUM ANALYZE content_embeddings;"

# Rebuild indexes (if experiencing slow queries)
psql "$DATABASE_URL" -c "REINDEX TABLE content_embeddings;"

# Check index health
psql "$DATABASE_URL" -c "
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexname::regclass)) as index_size
FROM pg_indexes
WHERE tablename = 'content_embeddings';"
```

---

## Troubleshooting

### Issue: "Embeddings not updating after JSON change"

**Cause:** JSON changes don't automatically trigger re-ingestion.

**Solution:**

1. Delete embeddings for affected content:
   ```bash
   psql "$DATABASE_URL" -c "DELETE FROM content_embeddings WHERE content_path LIKE '%affected-path%';"
   ```

2. Re-ingest that content:
   ```bash
   pnpm tsx scripts/ingest-content.ts --dir content/affected-path
   ```

### Issue: "Database connection timeout"

**Symptoms:** Commands hang or timeout

**Solutions:**

1. Check network connectivity
2. Verify DATABASE_URL is correct
3. Check Neon dashboard for database status
4. Try reconnecting:
   ```bash
   # Test connection
   psql "$DATABASE_URL" -c "SELECT 1;"
   ```

### Issue: "Duplicate embeddings"

**Diagnosis:**

```bash
# Check for duplicates
psql "$DATABASE_URL" -c "
SELECT content_path, COUNT(*) as count
FROM content_embeddings
GROUP BY content_path
HAVING COUNT(*) > 1
ORDER BY count DESC;"
```

**Solution:**

```bash
# Remove duplicates (keeps newest)
psql "$DATABASE_URL" -c "
DELETE FROM content_embeddings
WHERE id NOT IN (
    SELECT MAX(id)
    FROM content_embeddings
    GROUP BY content_path, chunk_text
);"
```

### Issue: "Vector search returns outdated content"

**Cause:** Content updated but embeddings not regenerated

**Solution:**

```bash
# 1. Delete old embeddings for updated file
psql "$DATABASE_URL" -c "DELETE FROM content_embeddings WHERE content_path = 'path/to/updated/file.md';"

# 2. Re-ingest the updated file
pnpm tsx scripts/ingest-content.ts --file content/path/to/updated/file.md

# 3. Verify update
psql "$DATABASE_URL" -c "SELECT created_at, LEFT(chunk_text, 100) FROM content_embeddings WHERE content_path = 'path/to/updated/file.md';"
```

---

## Workflows by JSON File Type

### Updating `destinations.json`

```bash
# 1. Edit destinations.json with new destination
vim src/data/destinations.json

# 2. Create corresponding content directory
mkdir -p content/destinations/[NewDestination]

# 3. Create content files
touch content/destinations/[NewDestination]/overview.md
touch content/destinations/[NewDestination]/dive-sites.md

# 4. Write content in markdown files
vim content/destinations/[NewDestination]/*.md

# 5. Ingest content
pnpm tsx scripts/ingest-content.ts --dir content/destinations/[NewDestination]

# 6. Verify in database
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM content_embeddings WHERE content_path LIKE '%[NewDestination]%';"

# 7. Test retrieval
cd src/backend
python -m scripts.test_rag "Tell me about diving in [NewDestination]"
```

### Updating `certifications.json`

```bash
# 1. Edit certifications.json
vim src/data/certifications.json

# 2. Create content file
mkdir -p content/certifications/[provider]
touch content/certifications/[provider]/[course-name].md

# 3. Write content
vim content/certifications/[provider]/[course-name].md

# 4. Ingest
pnpm tsx scripts/ingest-content.ts --file content/certifications/[provider]/[course-name].md

# 5. Verify and test
psql "$DATABASE_URL" -c "SELECT * FROM content_embeddings WHERE content_path LIKE '%[course-name]%';"
cd src/backend
python -m scripts.test_rag "What is [course-name] certification?"
```

### Updating `safety.json` or FAQ data

```bash
# 1. Edit JSON
vim src/data/safety.json

# 2. Create/update content
touch content/safety/[new-topic].md
vim content/safety/[new-topic].md

# 3. Ingest
pnpm tsx scripts/ingest-content.ts --file content/safety/[new-topic].md

# 4. Verify
psql "$DATABASE_URL" -c "SELECT content_path FROM content_embeddings WHERE content_path LIKE '%safety%';"
```

---

## Best Practices

### 1. Always Sync JSON with Content

**Rule:** Every entry in JSON should have corresponding content files.

```bash
# Check for missing content
# (Manual process - compare JSON entries with content directory)
ls content/destinations/ | sort
cat src/data/destinations.json | jq -r '.destinations[].contentPath' | sort
```

### 2. Use Descriptive Commit Messages

When updating JSON and content together:

```bash
git add src/data/destinations.json
git add content/destinations/Bali-Indonesia/
git commit -m "Add Bali, Indonesia destination with dive site info"
```

### 3. Test Before Deploying

```bash
# 1. Update locally
# 2. Re-ingest content
# 3. Run integration tests
pytest tests/integration/services/test_rag_integration.py -v
# 4. Manual spot tests
python -m scripts.test_rag "query about new content"
# 5. If all pass, commit and push
```

### 4. Document Schema Changes

If JSON structure changes significantly:

1. Update `docs/plans/PR1-Database-Schema.md`
2. Create Alembic migration
3. Update Pydantic models
4. Update this guide

### 5. Backup Before Major Changes

```bash
# Before bulk updates
psql "$DATABASE_URL" -c "CREATE TABLE content_embeddings_backup_$(date +%Y%m%d_%H%M) AS SELECT * FROM content_embeddings;"
```

### 6. Monitor API Usage

Gemini API has rate limits:

```bash
# Check how many embeddings will be generated
find content/ -name "*.md" -type f | wc -l

# Estimate chunks (rough: avg 3 chunks per file)
echo "scale=0; $(find content/ -name "*.md" -type f | wc -l) * 3" | bc

# If large ingestion, consider:
# - Running during off-peak hours
# - Reducing EMBEDDING_BATCH_SIZE
# - Monitoring API quota in Google Cloud Console
```

---

## Quick Reference Commands

### Database Inspection

```bash
# Total embeddings
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM content_embeddings;"

# By category
psql "$DATABASE_URL" -c "SELECT substring(content_path from '^[^/]+') as category, COUNT(*) FROM content_embeddings GROUP BY category;"

# Recent additions
psql "$DATABASE_URL" -c "SELECT content_path, created_at FROM content_embeddings ORDER BY created_at DESC LIMIT 10;"

# Search specific path
psql "$DATABASE_URL" -c "SELECT * FROM content_embeddings WHERE content_path LIKE '%search-term%';"
```

### Content Ingestion

```bash
# Ingest all
pnpm tsx scripts/ingest-content.ts

# Ingest directory
pnpm tsx scripts/ingest-content.ts --dir content/destinations/[Name]

# Ingest single file
pnpm tsx scripts/ingest-content.ts --file content/path/to/file.md

# Clear all embeddings
pnpm tsx scripts/clear-embeddings.ts
```

### Testing

```bash
# RAG test
cd src/backend && python -m scripts.test_rag "your query"

# Integration tests
cd src/backend && pytest tests/integration/services/test_rag_integration.py -v

# Manual embedding test
cd src/backend && python -m scripts.test_embeddings "test text"
```

### Database Maintenance

```bash
# Vacuum
psql "$DATABASE_URL" -c "VACUUM ANALYZE content_embeddings;"

# Check size
psql "$DATABASE_URL" -c "SELECT pg_size_pretty(pg_total_relation_size('content_embeddings'));"

# Rebuild indexes
psql "$DATABASE_URL" -c "REINDEX TABLE content_embeddings;"
```

---

## Quick Reference: When to Use Each Tool

### Use `scripts/update-dive-sites.ts` When:
- ✅ Adding/updating dive site metadata (difficulty, depth, tags)
- ✅ Adding new dive sites to existing destinations
- ✅ Updating structured data in `dive_sites` table
- ✅ JSON files in `content/destinations/*/` change
- ⚠️ Does NOT update embeddings for RAG

### Use `scripts/ingest-content.ts` When:
- ✅ Markdown content changes (descriptions, guides, FAQs)
- ✅ Need to update semantic search results
- ✅ Adding new content for RAG to retrieve
- ✅ Updates `content_embeddings` table
- ⚠️ Does NOT update structured data tables

### Typical Workflow for New Dive Site:
1. **Create JSON file** with metadata → `content/destinations/Malaysia-Tioman/tioman-new-site.json`
2. **Create markdown file** with content → `content/destinations/Malaysia-Tioman/tioman-new-site.md`
3. **Run `update-dive-sites.ts`** → Populates `dive_sites` table with metadata
4. **Run `ingest-content.ts`** → Creates embeddings for RAG from markdown
5. **Verify both**: Query `dive_sites` for metadata, test RAG for content retrieval

---

## Checklist for Database Updates

- [ ] JSON file updated with new entries
- [ ] Content markdown files created/updated
- [ ] Content follows markdown guidelines
- [ ] Database migration created (if schema changed)
- [ ] Migration applied successfully
- [ ] **Structured data updated** (`update-dive-sites.ts` or similar)
- [ ] **Content embeddings ingested** (`ingest-content.ts`)
- [ ] Database record count verified (both tables)
- [ ] RAG retrieval tested with sample queries
- [ ] Integration tests pass
- [ ] Changes committed to git
- [ ] Documentation updated (if needed)

---

## Related Documentation

- **Content Ingestion Guide:** `docs/technical/content-ingestion-guide.md`
- **Database Schema:** `docs/plans/PR1-Database-Schema.md`
- **RAG Pipeline:** `docs/plans/PR3.2b-Core-Services.md`
- **Backend Setup:** `src/backend/README.md`

---

**Last Updated:** January 2, 2026  
**Maintained By:** DovvyBuddy Development Team  
**Status:** Active (TypeScript ingestion) / Python migration in progress
