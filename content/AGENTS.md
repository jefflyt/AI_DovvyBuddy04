# Content Agent Guide

Scope: `content/`

## Default Focus

- Certification content:
  - `content/certifications/`
- Destinations:
  - `content/destinations/`
- Safety:
  - `content/safety/`

## Scan Discipline

- Read only the changed content paths and nearest templates.
- Do not scan all content files by default.
- For schema questions, check `content/README.md` and related templates first.

## Common Commands

- Validate content:
  - `pnpm content:validate`
- Incremental ingest:
  - `pnpm content:ingest`
- Full ingest (when chunking/schema changed):
  - `pnpm content:ingest -- --full`

## Change Rules

- Keep frontmatter and markdown structure valid.
- Prefer small, targeted edits and keep terminology consistent with existing corpus.
- For content changes that alter retrieval behavior, run ingestion/validation and note impact in `docs/context/CURRENT_STATE.md`.

