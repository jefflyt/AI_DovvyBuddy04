---
applyTo: '**'
---

# Global Instructions

## Purpose

Provide guidance for automated workflows, LLMs, and humans working on this project.

## Coding Standards

- Functions: 20-50 lines, single responsibility, descriptive names
- Comments: Only when intent isn't obvious from code
- Preserve existing file style when editing
- Return minimal patches with context, no unrelated changes

## Workflows

- Use `.github/prompts/*.prompt.md` as workflow entry points
- For multi-step changes: plan first, show progress, use small testable diffs
- Consult `/docs` for architectural decisions

## Reference Documentation

**Check these files BEFORE starting work to save context:**

### Backend Work

- `src/backend/README.md` - Backend structure, scripts, quick start commands
- `docs/technical/backend-testing-guide.md` - Test paths, commands, environment setup
- `docs/technical/developer-workflow.md` - General development workflows

### Frontend Work

- `README.md` - Project overview and quick start
- `docs/technical/deployment.md` - Deployment procedures

### Content Work

- `content/README.md` - Content structure and guidelines
- `docs/technical/content-ingestion-guide.md` - Content processing

**Benefits:** Avoids searching for paths, correct commands already documented, saves token usage

## Security

- **NEVER embed API keys, secrets, or credentials in ANY file** — not in source code, scripts, docs, config files, or comments
- All secrets must live exclusively in `.env.local` (gitignored) at the project root
- If a key is accidentally committed, rotate it immediately at the provider dashboard
- `.env.example` files must only contain placeholder values (e.g., `your_api_key_here`)

## Python Environment

- Single virtual environment at project root: `.venv`
- Install backend: `.venv/bin/pip install -e src/backend/`
- All dependencies use the root `.venv` (no subdirectory environments)

## LLM Standards

- Default model: `gemini-2.5-flash-lite` (cost-effective, standardized across backend)
- Embeddings: `text-embedding-004` (768 dimensions, recommended by Google, supports Matryoshka truncation)
- Orchestration: Strict Google ADK runtime for backend routing (`ENABLE_ADK=true`, `ADK_MODEL=gemini-2.5-flash-lite`)

## Documentation

- Place docs appropriately:
  - Technical specs: `/docs/technical/`
  - Architecture decisions: `/docs/decisions/`
  - Implementation plans: `/docs/plans/`
  - **Summaries & retrospectives: `/docs/project-management/`**
  - Backend-specific: `src/backend/docs/`
  - Content guides: `content/`
  - Workflow instructions: `.github/`
- Use `kebab-case` or `snake_case` filenames
- Include purpose, owner, and date in headers
- **Summary documents** (implementation summaries, sprint retrospectives, completion reports) always go in `/docs/project-management/`

---

_Owner: jefflyt_
