---
applyTo: '**'
---
# Global Instructions (LLM-friendly)

applyTo: '**'

Purpose:
- Provide concise, machine-readable guidance for automated workflows, LLMs, and humans.
- Keep language explicit, use examples, and prefer deterministic defaults.

How to use this file (for an LLM or automation):
- Read the `applyTo` value to determine scope.
- Follow the ordered lists exactly (prefer top-to-bottom decisions).
- When a choice requires an environment variable or code change, return a short patch or a specific command to run.

Primary workflows:
- Use files under `.github/prompts/*.prompt.md` as the authoritative prompt templates and workflow entry points.
- Prefer the "Plan" mode for multi-step changes: enumerate steps, mark progress, and show small, testable diffs.

Coding conventions (explicit, LLM-friendly rules):
- Keep functions small and focused: ideally 20-50 lines, single responsibility.
- Use clear, descriptive names for functions, classes, and variables (no single-letter names except loop indices).
- Add minimal but useful comments only when the intent is not obvious from code.
- Preserve existing style in a file; do not reformat unrelated code.
- When editing files, return only a patch (diff) with minimal context and no unrelated changes.

When unsure:
- Consult `/docs` for architectural decisions before inventing behavior.

LLM Model Standards (mandatory):
- Gemini family:
  - Default: `gemini-2.0-flash` for all Gemini LLM calls.
  - Do NOT use `gemini-1.5-pro`, `gemini-pro`, or other pro variants.
  - Rationale: flash models provide the best cost/performance trade-off for this project.
- Embeddings:
  - Use `text-embedding-004` (Gemini) as the canonical embedding model and vector dimensionality (768).

Explicit prompt and results rules (for LLMs used by engineers or automation):
- Return short patches when proposing code changes. Example output format for a code change:
  - { "action": "apply_patch", "patch": "*** Begin Patch\n*** Update File: path/to/file\n@@\n- old line\n+ new line\n*** End Patch" }
- When giving commands, return them in a single code block and prefix with the shell (e.g. `bash`).
- Avoid excessive natural-language preamble when producing machine-actionable outputs; be concise and deterministic.

Examples (recommended patterns):
- Configuration change example (shell):
  ```bash
  # Add environment variable to .env.example
  echo "ENABLE_ADK=true" >> .env.example
  ```
- Patch example (diff):
  ```diff
  *** Begin Patch
  *** Update File: src/lib/example.ts
  @@
  -const a = 1
  +const a = 2
  *** End Patch
  ```

Why these rules:
- Deterministic outputs (patches, commands) are easier to verify and apply automatically.
- Explicit defaults reduce back-and-forth and accidental use of non-standard models.

Notes for reviewers and automation:
- If a change is larger than a small patch (e.g., >3 files), propose a multi-step plan first and request confirmation.
- For multi-step tasks, produce a todo list and mark progress (not-started, in-progress, completed) for each step.

- Documentation and validation files:
  - When creating documentation or validation Markdown files (design docs, API schemas, validation rules), ensure they are necessary and not duplicative.
  - Place them in the appropriate folder for discovery (for example: `docs/` for long-form docs, `backend/` for backend-specific docs, `content/` for content templates, or `.github/` for workflow prompts).
  - Use clear, descriptive filenames (prefer `kebab-case` or `snake_case`) and include a short header with purpose, owner, and date.
  - Avoid ad-hoc or scattered docs; if in doubt, propose the doc path in the PR description and get reviewer sign-off.

Contact / owner:
- Code owner: `jefflyt` (repository owner)

-- End of instructions --
