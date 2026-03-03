# TDD — Project Status Snapshot

**Date:** 2026-01-01

## Summary

This document captures the current status of the DovvyBuddy project (PR3.2b work, content ingestion and Neon database updates) to support Test-Driven Development and verification tracking.

## Objectives

- Migrate RAG, embedding and LLM services from TypeScript to Python (PR3.2b)
- Provide tools and docs to ingest content and update Neon DB
- Keep Drizzle (TypeScript) schema as source-of-truth; mirror schema in Python models
- Verify RAG/embeddings/LLM integration with real API keys

## Completed (High Priority)

- PR3.2b: Core services implemented in Python (embeddings, LLM abstractions, RAG pipeline). All individual integration tests pass.
- Unit tests: 48/55 passed (~87%). Several fixes applied.
- RAG integration: 4/4 passed individually; batch pooling issue noted and tracked.
- Drizzle schema updated for `dive_sites` (added `dive_site_id`, `difficulty_rating`, `depth_min_m`, `depth_max_m`, `tags`, `last_updated`, `updated_at`). Migration applied to Neon (manual fixed SQL with IF NOT EXISTS and data population).
- A legacy TypeScript metadata update script was used during early migration for Tioman metadata updates (historical reference).
- Legacy TypeScript ingestion was used earlier for Malaysia-Tioman; current ingestion runs from `apps/api/scripts/ingest_content.py` via `pnpm content:ingest`.
- Documentation created/updated: `docs/operations/content-ingestion-guide.md` and `docs/operations/neon-database-update-guide.md` with clear separation of responsibilities.

## In-Progress / Recent Fixes

- Legacy update scripts were enhanced during migration to extract descriptions from markdown; those notes remain historical.
- Summary queries in the script adjusted to avoid JSON casting errors; verified descriptions and fields via `psql` queries.

## Pending / Next Actions

- Update Python `SQLAlchemy` models to mirror the Drizzle schema changes (sync models for `dive_sites`, `destinations`, `content_embeddings`).
- Address connection-pooling issue affecting batch RAG tests (investigate asyncpg pool configuration).
- Python ingestion migration is complete in current structure (`apps/api/scripts/ingest_content.py`).
- Add integration test coverage for the updated `update-dive-sites` flow and content → embeddings consistency.
- Consider adding automated CI checks to ensure Drizzle schema changes trigger model sync review notes.

## Verification Checklist (current status)

- [x] Embeddings generation — verified (individual tests)
- [x] LLM provider calls — verified (individual tests)
- [x] RAG retrieval — verified individually
- [x] Schema migration applied to Neon — verified
- [x] Dive site metadata populated — verified (5 Tioman sites)
- [ ] Batch RAG tests — flaky due to pooling; investigation needed
- [ ] Python ingestion script — TODO (PR3.2d)

## Notes & Recommendations

- Keep Drizzle `.ts` schema as source-of-truth. Update Python models to reflect schema changes when Drizzle migrations are applied.
- Use the two-guide approach: `content-ingestion-guide.md` for embeddings/RAG and `neon-database-update-guide.md` for structured metadata. Both updated and cross-referenced.
- For future schema changes, prefer generating Drizzle migrations and then applying them (or a reviewed manual SQL patch) — follow up by updating Python models and Alembic no-op if appropriate.

## Contacts / Owners

- Code owner / committer: `jefflyt` (solo founder)
- Maintainers: DovvyBuddy Development Team

---

_Last updated by tooling on repository snapshot — use this file as the canonical TDD status snapshot and update it after major merges or verification runs._
