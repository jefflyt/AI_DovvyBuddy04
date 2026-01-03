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

## Python Environment
- Single virtual environment at project root: `.venv`
- Install backend: `.venv/bin/pip install -e backend/`
- All dependencies use the root `.venv` (no subdirectory environments)

## LLM Standards
- Default model: `gemini-2.0-flash` (cost-effective)
- Embeddings: `text-embedding-004` (768 dimensions)

## Documentation
- Place docs appropriately:
  - Technical specs: `/docs/technical/`
  - Architecture decisions: `/docs/decisions/`
  - Implementation plans: `/docs/plans/`
  - **Summaries & retrospectives: `/docs/project-management/`**
  - Backend-specific: `backend/docs/`
  - Content guides: `content/`
  - Workflow instructions: `.github/`
- Use `kebab-case` or `snake_case` filenames
- Include purpose, owner, and date in headers
- **Summary documents** (implementation summaries, sprint retrospectives, completion reports) always go in `/docs/project-management/`

---
*Owner: jefflyt*
