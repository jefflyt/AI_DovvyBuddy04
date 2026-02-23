# PR6.4: GraphRAG Migration for Enhanced Search Results

**Part of Epic:** V1 Feature Enhancement & Cost Optimization

**Status:** Planning

**Owner:** jefflyt

**Date:** February 18, 2026

---

## 0) Assumptions (max 3)

1. **Content has rich entity relationships:** The diving domain naturally contains structured entities (dive sites → destinations, certifications → prerequisites, safety procedures → conditions) that benefit from graph representation.

2. **PostgreSQL can handle graph queries:** Using recursive CTEs and JSONB for graph storage is acceptable for V1 scale (~100-500 entities). We defer dedicated graph databases (Neo4j, Neptune) until scaling requires it.

3. **Backward compatibility required:** The existing RAG pipeline must continue working during migration, with GraphRAG as an optional enhancement layer that can be toggled via feature flag.

---

## 1) Clarifying questions (max 3, only if blocking)

None - proceeding with explicit decisions based on codebase patterns.

---

## 2) Feature summary

### Goal

Enhance RAG retrieval quality by 30-50% through knowledge graph augmentation, enabling relationship-aware queries like "What certifications do I need for deep wrecks in Tioman?" to return not just matching chunks, but related entities (prerequisites, site depth requirements, recommended courses).

### User story

As a **prospective diver**, when I ask multi-faceted questions involving relationships (certification pathways, site prerequisites, safety conditions), I want **comprehensive answers that connect related concepts**, so that **I understand the full context without asking follow-up questions**.

### Acceptance criteria

1. **Entity graph built:** System extracts and stores entities (dive sites, certifications, destinations, safety concepts) with relationships from existing content.
2. **Graph-enhanced retrieval:** Queries expand to include graph neighbors (e.g., "Tioman sites" also retrieves prerequisite certifications, related safety procedures).
3. **Quality improvement:** Blind A/B test shows 30%+ preference for GraphRAG responses vs. baseline RAG for multi-entity queries.
4. **Performance acceptable:** Graph-enhanced retrieval adds ≤500ms latency (p95) vs. baseline RAG.
5. **Backward compatible:** Feature flag `RAG_USE_GRAPH` allows rollback to baseline RAG with zero code changes.
6. **No regression:** Single-concept queries (e.g., "What is Open Water?") perform ≥ baseline quality.
7. **Cost neutral:** Graph queries stay within existing Gemini free tier limits (no new API costs).
8. **Observable:** Logs distinguish graph-enhanced vs. baseline retrieval with entity counts and traversal depth.
9. **Testable:** Unit tests cover entity extraction, graph building, and retrieval expansion.
10. **Maintainable:** Graph schema documented, with migration path to dedicated graph DB if needed.

### Non-goals (explicit)

- **Dedicated graph database (Neo4j, Neptune):** Use PostgreSQL with JSONB for V1, defer specialized DB until >1000 entities or complex graph algorithms needed.
- **Real-time graph updates:** Entities extracted during content ingestion (batch), not per-query.
- **LLM-based entity extraction:** Use rule-based extraction with regex/NER for V1 cost efficiency, defer LLM extraction to V2.
- **Multi-hop reasoning:** Limit graph traversal to 1-2 hops, avoid complex path finding.
- **Automatic relationship discovery:** Manually define relationship types (prerequisite, located_in, requires_certification), skip ML-based discovery.
- **Visual graph UI:** Graph is backend-only, no frontend visualization in V1.

---

## 3) Approach overview

### Proposed UX (high-level)

**No UI changes.** Chat interface remains identical. Improvements are invisible to users, manifesting as better context and more complete answers.

**Example conversation improvement:**

**Before (baseline RAG):**
```
User: "What certifications do I need for wreck diving in Tioman?"
Bot: "Advanced Open Water is recommended for many sites in Tioman. Tiger Reef is suitable for beginners."
[Misses connection between wreck diving + specific certification requirements]
```

**After (GraphRAG):**
```
User: "What certifications do I need for wreck diving in Tioman?"
Bot: "For wreck diving in Tioman, you'll typically need Advanced Open Water or higher. Specifically:
- Tioman has wreck sites at 18-25m depth requiring AOW certification
- Wreck Diver specialty is recommended but not required
- Deep Diver specialty useful for deeper wrecks (>18m)
The main wreck sites are [site names], which require minimum 20 logged dives."
[Graph traversal connected: wreck diving → depth requirements → certification level → specific sites → dive count prerequisites]
```

### Proposed API (high-level)

**No breaking changes to existing API.** GraphRAG is internal enhancement to RAG pipeline.

**Modified internal flow:**

```
Query: "What certifications for wreck diving in Tioman?"
  ↓
1. Entity Extraction (new step)
   - Extracts: [wreck diving, certifications, Tioman]
   - Entity types: [activity, entity_type, destination]
   ↓
2. Graph Expansion (new step)
   - wreck diving → [Deep Diver, Advanced Open Water, minimum depth]
   - Tioman → [Tiger Reef, Renggis Island, wreck sites]
   - Merge: [wreck sites in Tioman] → depth requirements → certifications
   ↓
3. Enhanced Vector Search (modified)
   - Retrieve chunks matching original query (baseline)
   - UNION with chunks matching expanded entities (graph-enhanced)
   - Re-rank combined results by relevance
   ↓
4. Context Formatting (unchanged)
   - Format top-k chunks for LLM
   ↓
Response with richer, relationship-aware context
```

**Feature flag control:**
- `RAG_USE_GRAPH=false` → Skip steps 1-2, use baseline RAG
- `RAG_USE_GRAPH=true` → Full GraphRAG pipeline

### Proposed data changes (high-level)

**New tables:**

**1. `entities` table:**
```sql
id (uuid PK)
name (text) -- "Advanced Open Water", "Tioman"
entity_type (text) -- "certification", "destination", "dive_site", "safety_concept"
metadata (jsonb) -- {level: "intermediate", agency: "PADI"}
embedding (vector(768)) -- Gemini embedding of entity name + context
created_at, updated_at
```

**2. `entity_relationships` table:**
```sql
id (uuid PK)
source_entity_id (uuid FK -> entities)
target_entity_id (uuid FK -> entities)
relationship_type (text) -- "prerequisite", "located_in", "requires_certification", "related_to"
strength (float) -- 0.0-1.0, extraction confidence
metadata (jsonb) -- {depth_min: 18, depth_max: 40}
created_at
```

**3. `chunk_entities` table (join table):**
```sql
chunk_id (uuid FK -> content_embeddings.id)
entity_id (uuid FK -> entities.id)
relevance (float) -- How central this entity is to the chunk
created_at
```

**Modified ingestion script:**
- Extract entities from markdown during chunk ingestion
- Build relationships based on:
  - Frontmatter metadata (destination → sites)
  - Content structure (headers, lists)
  - Pattern matching (certification prerequisites from text)
  - Co-occurrence within chunks

**Graph query patterns:**
```sql
-- Find 1-hop neighbors
SELECT e2.* FROM entities e1
JOIN entity_relationships er ON er.source_entity_id = e1.id
JOIN entities e2 ON e2.id = er.target_entity_id
WHERE e1.name ILIKE '%wreck diving%';

-- Find chunks related to entity neighborhood
SELECT DISTINCT ce.chunk_id, ce.relevance
FROM chunk_entities ce
WHERE ce.entity_id IN (
  SELECT id FROM entities WHERE name IN ('wreck diving', 'Tioman', 'AOW')
  UNION
  SELECT target_entity_id FROM entity_relationships 
  WHERE source_entity_id IN (...)
)
ORDER BY ce.relevance DESC;
```

### AuthZ/authN rules (if any)

None. Guest sessions only, no auth changes.

---

## 4) PR plan

### PR Title

PR6.4: GraphRAG Migration for Enhanced Search Results

### Branch name

`feature/pr6.4-graph-rag`

### Scope (in)

**Phase 1: Foundation (Days 1-2)**
1. Database schema for entities, relationships, and chunk-entity mappings
2. Alembic migration scripts
3. Entity data models in SQLAlchemy

**Phase 2: Entity Extraction (Days 2-3)**
4. Entity extractor service with rule-based patterns
5. Relationship mapper for common patterns (prerequisite, location, etc.)
6. Modified ingestion script to populate entity graph
7. Re-ingestion of existing content to build initial graph

**Phase 3: Graph-Enhanced Retrieval (Days 3-4)**
8. Graph query service for entity expansion
9. Modified RAGRetriever to incorporate graph neighbors
10. Hybrid ranking of vector + graph results
11. Feature flag `RAG_USE_GRAPH` in config

**Phase 4: Testing & Tuning (Day 5)**
12. Unit tests for entity extraction and graph queries
13. Integration tests for end-to-end GraphRAG pipeline
14. Benchmark comparison (baseline vs. GraphRAG)
15. Query complexity heuristics (when to use graph expansion)

### Out of scope (explicit)

- **LLM-based entity extraction:** V2 enhancement, costs too high for V1
- **Graph algorithms (PageRank, community detection):** Simple 1-2 hop traversal only
- **Real-time graph updates:** Batch during ingestion only
- **Multi-language entity linking:** English-only for V1
- **Automatic relationship type inference:** Manually defined types
- **Graph visualization UI:** Backend only, no frontend tool
- **Neo4j/Neptune migration:** Defer to V2/V3 if scaling requires
- **Ontology management:** Lightweight schema, not formal ontology

### Key changes by layer

#### Frontend

**No changes.** GraphRAG is transparent backend enhancement.

#### Backend

**New modules:**

1. **`backend/app/services/graph/`** (new package)
   - `models.py` — Entity, EntityRelationship, ChunkEntity SQLAlchemy models
   - `extractor.py` — EntityExtractor class with rule-based extraction
   - `mapper.py` — RelationshipMapper for building relationships
   - `query.py` — GraphQueryService for entity expansion queries
   - `types.py` — GraphEntity, Relationship, GraphExpansion dataclasses
   - `__init__.py` — Package exports

2. **`backend/app/services/rag/retriever.py`** (modified)
   - Add `retrieve_with_graph()` method
   - Integrate GraphQueryService for entity expansion
   - Merge vector + graph results with hybrid ranking
   - Log graph statistics (entities found, relationships traversed)

3. **`backend/app/services/rag/pipeline.py`** (modified)
   - Call `retrieve_with_graph()` when `settings.rag_use_graph=True`
   - Query complexity check: skip graph for simple queries (greetings, yes/no)
   - Log graph-enhanced vs. baseline decision

4. **`backend/scripts/ingest_content.py`** (modified)
   - Import EntityExtractor and RelationshipMapper
   - Extract entities from chunks after embedding
   - Build relationships from co-occurrence and metadata
   - Insert into entities, entity_relationships, chunk_entities tables
   - Add `--rebuild-graph` flag to recreate entities without re-embedding

5. **`backend/alembic/versions/add_entity_graph.py`** (new migration)
   - Create entities, entity_relationships, chunk_entities tables
   - Add indexes for graph queries (entity_type, relationship_type, relevance)
   - Add vector index on entities.embedding for entity similarity search

**Modified modules:**

- `backend/app/core/config.py` — Add `rag_use_graph: bool = True`, `rag_graph_max_hops: int = 2`, `rag_graph_min_strength: float = 0.3`
- `backend/app/db/models/__init__.py` — Export new graph models

#### Data

**New tables:** (see "Proposed data changes" above)
- `entities`
- `entity_relationships`
- `chunk_entities`

**Migration strategy:**
1. Run Alembic migration to create tables
2. Re-run ingestion script with `--rebuild-graph` flag
3. Verify entity counts and relationship coverage
4. Enable `RAG_USE_GRAPH=true` after validation

#### Infra/config

**Environment variables:**
```bash
# GraphRAG Configuration
RAG_USE_GRAPH=true                    # Enable/disable GraphRAG
RAG_GRAPH_MAX_HOPS=2                  # Maximum graph traversal depth
RAG_GRAPH_MIN_STRENGTH=0.3            # Minimum relationship strength
RAG_GRAPH_ENTITY_LIMIT=10             # Max entities per query expansion
```

**No new dependencies.** Use standard library for regex/pattern matching.

#### Observability

**Logging enhancements:**
- `backend/app/services/graph/extractor.py` — Log entities extracted per chunk (count, types)
- `backend/app/services/graph/query.py` — Log graph expansion (entities found, hops traversed, relationships used)
- `backend/app/services/rag/retriever.py` — Log graph vs. vector result ratios, merged result count

**Example log output:**
```
INFO: Entity extraction: query="wreck diving Tioman", entities_found=3, types=['activity', 'destination']
INFO: Graph expansion: entities=3, relationships=7, hops=2, expansion_time=45ms
INFO: GraphRAG retrieval: vector_results=5, graph_results=3, merged_results=6, total_time=234ms
```

### Edge cases to handle

1. **No entities extracted from query:**
   - Fallback to baseline RAG (vector-only search)
   - Log: "No entities detected, using baseline RAG"

2. **Graph returns no related entities:**
   - Graph expansion yields empty set
   - Fallback to baseline RAG
   - Log: "Graph expansion empty, using baseline RAG"

3. **Query matches only generic entities:**
   - E.g., "certification" matches 50+ entities
   - Apply relevance filtering (top-10 most relevant to query)
   - Limit graph expansion to prevent over-retrieval

4. **Circular relationships:**
   - E.g., Site A → requires Cert B → recommended for Site A
   - Track visited entities during traversal to prevent cycles
   - Limit max hops to 2 (config: `RAG_GRAPH_MAX_HOPS`)

5. **Low-confidence relationships:**
   - Filter relationships by `strength >= RAG_GRAPH_MIN_STRENGTH`
   - Only traverse high-confidence edges

6. **Performance degradation:**
   - Graph query timeout (500ms hard limit)
   - Fallback to baseline RAG on timeout
   - Log warning for investigation

7. **Conflicting vector vs. graph results:**
   - Merge with weighted ranking (70% vector similarity, 30% graph relevance)
   - Avoid duplicates by deduplicating chunk IDs

8. **Empty graph (migration not run):**
   - Detect empty entities table
   - Automatically disable GraphRAG, log error
   - Prevent breaking existing functionality

### Migration/compatibility notes

**Backward compatibility:**
- GraphRAG is additive, never removes baseline RAG functionality
- Feature flag `RAG_USE_GRAPH=false` reverts to exact PR6.3 behavior
- Existing API contracts unchanged

**Migration steps:**
1. Deploy code with `RAG_USE_GRAPH=false` (dark launch)
2. Run Alembic migration in production
3. Run ingestion script with `--rebuild-graph` in staging
4. Validate entity counts and sample queries
5. Enable `RAG_USE_GRAPH=true` for 10% traffic (A/B test)
6. Monitor quality metrics (user feedback, lead conversion)
7. Ramp to 100% if successful

**Rollback plan:**
- Set `RAG_USE_GRAPH=false` → instant rollback, no data loss
- Graph tables remain but unused
- Can drop tables later if decision is permanent

**Data migration:**
- Initial graph build: ~5-10 minutes for 100-500 chunks
- Zero downtime (background job)
- Idempotent (can re-run safely)

---

## 5) Testing & verification

### Automated tests to add/update

#### Unit tests

**`tests/unit/services/graph/test_extractor.py`**
- `test_extract_entities_from_text()` — Certifications, destinations, sites detected
- `test_extract_no_entities()` — Returns empty list for generic text
- `test_extract_entity_types()` — Correctly classifies entity types
- `test_extract_with_metadata()` — Uses chunk metadata for context

**`tests/unit/services/graph/test_mapper.py`**
- `test_map_location_relationships()` — Sites → Destinations
- `test_map_certification_prerequisites()` — Cert → Prerequisites
- `test_map_co_occurrence_relationships()` — Entities in same chunk
- `test_relationship_strength_calculation()` — Confidence scoring

**`tests/unit/services/graph/test_query.py`**
- `test_find_entity_neighbors_1_hop()` — Direct relationships
- `test_find_entity_neighbors_2_hop()` — Transitive relationships
- `test_expand_query_entities()` — Query → entities → neighbors
- `test_graph_query_with_filters()` — Strength, type filters
- `test_circular_relationship_handling()` — Prevents infinite loops
- `test_empty_graph_handling()` — Graceful degradation

**`tests/unit/services/rag/test_retriever_graph.py`**
- `test_retrieve_with_graph_enabled()` — GraphRAG pipeline
- `test_retrieve_with_graph_disabled()` — Baseline RAG unchanged
- `test_retrieve_hybrid_ranking()` — Vector + graph merge
- `test_graph_timeout_fallback()` — Graceful degradation
- `test_no_entities_fallback()` — Falls back to baseline

#### Integration tests

**`tests/integration/test_graph_rag_pipeline.py`**
- `test_end_to_end_graph_enhanced_query()` — Full pipeline with real DB
- `test_multi_entity_query()` — "Wreck diving in Tioman"
- `test_single_entity_query()` — "What is Open Water?" (no degradation)
- `test_relationship_traversal()` — Verifies 1-2 hop expansion
- `test_graph_result_quality()` — Checks result relevance
- `test_feature_flag_toggle()` — Verifies clean fallback

**`tests/integration/test_content_ingestion_graph.py`**
- `test_ingest_with_entity_extraction()` — Entities created
- `test_relationship_creation()` — Relationships mapped
- `test_chunk_entity_linkage()` — Chunk-entity join works
- `test_rebuild_graph_idempotent()` — Can re-run safely

#### E2E (manual validation, not automated)

- Not adding E2E tests (per project decision ADR-0007)
- Manual validation via debug endpoints and logs

### Manual verification checklist

**Pre-deployment (Staging):**
1. Run `python -m scripts.ingest_content --rebuild-graph` and verify:
   - Entities table populated (check count > 0)
   - Entity types distributed (certifications, sites, destinations)
   - Relationships table populated (check prerequisite, located_in types)
   - Chunk-entity links created
2. Query `/api/debug/rag?q=wreck diving in Tioman` and verify:
   - `graph_entities_found > 0`
   - `graph_relationships_expanded > 0`
   - `graph_enhanced_results` includes related chunks
3. Compare baseline vs. GraphRAG response quality for 5 test queries
4. Check logs for graph expansion timing (target <500ms)

**Post-deployment (Production):**
5. Monitor error rates for graph query failures
6. Check p95 latency for `/api/chat` (should not increase >500ms)
7. Review sample conversations for quality improvement
8. A/B test: 10% traffic GraphRAG vs. 90% baseline, compare user engagement

**Rollback validation:**
9. Set `RAG_USE_GRAPH=false` and verify chat works identically to PR6.3
10. Re-enable and verify graph metrics return

### Commands to run

**Development workflow:**
```bash
# Install dependencies (no new packages)
cd backend && .venv/bin/pip install -e .

# Run migration
cd backend && .venv/bin/alembic upgrade head

# Rebuild entity graph
cd backend && .venv/bin/python -m scripts.ingest_content --rebuild-graph

# Run tests
cd backend && .venv/bin/pytest tests/unit/services/graph/ -v
cd backend && .venv/bin/pytest tests/integration/test_graph_rag_pipeline.py -v

# Debug graph queries
cd backend && .venv/bin/python -c "
from app.services.graph.query import GraphQueryService
service = GraphQueryService()
result = service.expand_query('wreck diving in Tioman')
print(result)
"

# Start dev server
cd backend && .venv/bin/uvicorn app.main:app --reload

# Test endpoint
curl "http://localhost:8000/api/debug/rag?q=wreck%20diving%20in%20Tioman"
```

**Testing commands:**
```bash
# Unit tests only
.venv/bin/pytest tests/unit/services/graph/ -v

# Integration tests
.venv/bin/pytest tests/integration/test_graph_rag_pipeline.py -v

# Full test suite
.venv/bin/pytest

# Check coverage
.venv/bin/pytest --cov=app.services.graph --cov=app.services.rag

# Lint
.venv/bin/ruff check backend/app/services/graph/

# Type check
.venv/bin/mypy backend/app/services/graph/
```

**Production deployment:**
```bash
# Apply migration (zero downtime)
alembic upgrade head

# Rebuild graph (background job, idempotent)
python -m scripts.ingest_content --rebuild-graph

# Verify entity count
psql $DATABASE_URL -c "SELECT entity_type, COUNT(*) FROM entities GROUP BY entity_type;"

# Enable GraphRAG (staged rollout)
# Update env var: RAG_USE_GRAPH=true
# Restart backend service
```

---

## 6) Rollback plan

**Feature flag rollback (zero downtime):**
1. Set `RAG_USE_GRAPH=false` in environment
2. Restart backend service (health check ensures zero downtime)
3. Verify `/api/chat` responses revert to baseline RAG behavior
4. Monitor error rates and latency (should match PR6.3 baseline)

**Database rollback (if graph tables cause issues):**
1. Set `RAG_USE_GRAPH=false` first (as above)
2. Optionally drop graph tables (non-destructive, content_embeddings unchanged):
   ```sql
   DROP TABLE IF EXISTS chunk_entities CASCADE;
   DROP TABLE IF EXISTS entity_relationships CASCADE;
   DROP TABLE IF EXISTS entities CASCADE;
   ```
3. Revert Alembic migration: `alembic downgrade -1`

**Code rollback:**
- Revert PR6.4 branch merge
- Redeploy previous release (PR6.3c)
- No data migration needed (graph tables are additive)

**Recovery time objective (RTO):**
- Feature flag rollback: <5 minutes (config change + restart)
- Database rollback: <15 minutes (drop tables + migration rollback)
- Full code rollback: <30 minutes (redeploy previous release)

**Monitoring for rollback decision:**
- Error rate increase >2% in `/api/chat`
- p95 latency increase >500ms
- User-reported quality degradation >5% in feedback forms
- Graph query timeout rate >10%

---

## 7) Follow-ups (optional)

**PR6.4a: LLM-Based Entity Extraction (V2)**
- Replace rule-based extractor with Gemini API calls
- Extract entities with higher recall and precision
- Cost: ~$0.01 per 100 chunks, one-time during ingestion

**PR6.4b: Graph Algorithm Enhancements (V2)**
- Add PageRank scoring for entity importance
- Community detection for topic clustering
- Multi-hop reasoning for complex queries

**PR6.4c: Real-Time Graph Updates (V2)**
- Incremental entity extraction on new content
- Dynamic relationship strength updates based on query feedback
- Avoid full graph rebuilds

**PR6.4d: Neo4j Migration (V3)**
- Migrate to dedicated graph database when >1000 entities
- Enable advanced graph algorithms (shortest path, centrality)
- Separate graph queries from main OLTP database

**PR6.4e: Visual Graph Explorer (V3)**
- Frontend UI to visualize entity relationships
- Interactive graph navigation for content creators
- Debugging tool for relationship quality

---

**End of Plan**
