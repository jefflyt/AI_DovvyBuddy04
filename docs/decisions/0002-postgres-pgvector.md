# ADR-0002: Use PostgreSQL + pgvector for Database

**Status:** Accepted  
**Date:** December 20, 2025  
**Deciders:** Solo Founder

---

## Context

DovvyBuddy requires a database solution that supports:

- **Relational data** — Structured tables (destinations, dive_sites, leads, sessions)
- **Vector search** — RAG retrieval for grounding LLM responses
- **JSONB storage** — Flexible schema for conversation history, diver profiles
- **Managed service** — Minimal operational overhead for solo founder
- **Cost-effective** — Free tier for MVP validation

The application needs both traditional CRUD operations and semantic search capabilities, typically requiring separate systems (e.g., relational DB + vector DB).

---

## Decision

Use **PostgreSQL with pgvector extension**, hosted on **Neon** (or Supabase as alternative).

**Key Components:**

- **Database:** PostgreSQL 15+
- **Vector Extension:** pgvector (HNSW index for similarity search)
- **Hosting:** Neon (serverless Postgres)
- **ORM:** Drizzle ORM (type-safe, lightweight)
- **Vector Dimensions:** 1536 (Gemini `text-embedding-004`)

---

## Consequences

### Positive

- ✅ **Single database** — No need for separate vector DB (Pinecone, Weaviate)
- ✅ **Relational + vectors** — ACID transactions with semantic search
- ✅ **JSONB support** — Flexible schema for conversation history
- ✅ **Managed service** — Automatic backups, scaling, maintenance
- ✅ **Cost-effective** — Neon free tier sufficient for MVP (<1000 users)
- ✅ **Standard SQL** — Familiar query language, large talent pool
- ✅ **pgvector maturity** — Battle-tested extension, wide adoption

### Negative

- ❌ **Vector search performance** — Not as fast as dedicated vector DBs at massive scale
- ❌ **Scaling complexity** — Eventually may need to separate vector search
- ❌ **pgvector limitations** — Max 2000 dimensions, fewer index options than specialists
- ❌ **Cold starts** — Neon serverless has connection latency (mitigated with connection pooling)

### Neutral

- ⚪ **Migration path** — Can extract vectors to Pinecone/Qdrant later if needed
- ⚪ **Index tuning** — HNSW parameters require optimization for workload

---

## Alternatives Considered

### Alternative 1: PostgreSQL + Pinecone (Separate Vector DB)

**Description:** PostgreSQL for relational data, Pinecone for vector search

**Pros:**

- Best-in-class vector search performance
- Purpose-built for embeddings
- Managed service with auto-scaling

**Cons:**

- Two databases to manage and pay for
- Data sync complexity (keep embeddings updated)
- Additional API calls (latency overhead)
- Pinecone paid plans start at $70/mo
- Over-engineering for small content corpus (~100 chunks)

**Why rejected:** Premature optimization. DovvyBuddy's V1 content is <100 destinations/sites. pgvector can handle this scale efficiently. Can migrate to Pinecone later if scaling demands it.

---

### Alternative 2: MongoDB + Atlas Vector Search

**Description:** MongoDB for document storage, Atlas Vector Search for embeddings

**Pros:**

- Flexible schema (no migrations)
- Integrated vector search in Atlas
- Good for unstructured data

**Cons:**

- Less mature for relational queries (destinations → dive_sites)
- No ACID guarantees for multi-document transactions
- Larger learning curve for team (if scaling)
- Atlas vector search newer, less proven
- Higher cost at scale

**Why rejected:** DovvyBuddy's data is naturally relational (destinations have dive sites, leads reference sessions). PostgreSQL's relational model is better fit. JSONB provides schema flexibility where needed.

---

### Alternative 3: Supabase (Postgres + Auth + Storage)

**Description:** Supabase as all-in-one backend (Postgres + pgvector + Auth + Storage)

**Pros:**

- Same database choice (Postgres + pgvector)
- Integrated authentication (useful for V2)
- Built-in storage for future photo features
- Excellent DX and tooling

**Cons:**

- Vendor lock-in (harder to migrate than raw Postgres)
- Less control over Postgres configuration
- Slightly higher cost than Neon at scale

**Why rejected:** Not rejected — Supabase is a viable alternative to Neon. Both offer Postgres + pgvector. Decision defaulted to Neon for simplicity, but can switch to Supabase if auth/storage integration becomes priority in V2.

---

### Alternative 4: SQLite + In-Memory Vector Index

**Description:** SQLite for data, object-storage-backed vector index (e.g., FAISS)

**Pros:**

- Zero cost
- Single file database
- Extremely fast local development
- FAISS very performant for vectors

**Cons:**

- No horizontal scaling
- No managed backups
- Requires custom vector index loading logic
- Not suitable for production multi-user app
- Cold start penalty (load index from storage)

**Why rejected:** Not production-ready for web application with multiple concurrent users. Acceptable for prototyping but not for MVP launch.

---

## References

- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Neon Postgres](https://neon.tech/)
- [Drizzle ORM](https://orm.drizzle.team/)
- [Gemini Embeddings API](https://ai.google.dev/api/embeddings)
- [Technical Spec — Data Models](../technical/specification.md#41-database-schema)

---

## Notes

**Content Corpus Scale (V1):**

- ~1 destination (Bali)
- ~5-10 dive sites
- Certification guides (PADI, SSI)
- ~100-200 total content chunks

At this scale, pgvector is more than sufficient. Reevaluate if:

- Content grows to >10 destinations (>1000 chunks)
- Query latency exceeds 200ms at p95
- Users report slow response times

**Migration Path (if needed):**

- Extract `content_embeddings` table to Pinecone/Qdrant
- Update retrieval service to query external vector DB
- Keep relational data in Postgres
- Minimal code changes (abstraction layer isolates retrieval logic)

**Review Date:**

- After V1 launch (3-6 months) — Monitor query performance
- Before multi-destination expansion (10+ destinations) — Reevaluate if vector DB separation needed

---

**Related ADRs:**

- ADR-0001: Next.js + Vercel for Web Application
- ADR-0003: LLM Provider Strategy (Groq/Gemini/SEA-LION)
