# Copilot Instructions (Global)

- Use .github/prompts/*.prompt.md as primary workflows.
- Prefer Plan mode over Agent/autonomous modes.
- Default coding style:
  - Keep functions small and focused.
  - Use clear, descriptive naming.
  - Add minimal but useful comments where intent is non-obvious.
- When in doubt, consult docs in /docs before inventing behavior.

## LLM Model Standards

- **Gemini:** Always use `gemini-2.0-flash` for all Gemini LLM calls
  - Do NOT use `gemini-1.5-pro`, `gemini-pro`, or other pro variants
  - Flash model provides optimal cost/performance for our use case
- **Groq:** Use for development/testing (fast iteration)
- **Embeddings:** Use `text-embedding-004` (Gemini)
