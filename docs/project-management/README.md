# Project Management & Workflow Documentation

This directory contains workflow guides and development process documentation for DovvyBuddy.

---

## Contents

### Workflow Guides

- **[AI_WORKFLOW.md](./AI_WORKFLOW.md)** — Complete AI-driven development workflow using custom Copilot prompts
- **`init_ai_workflow.sh`** — Shell script to initialize AI workflow setup

### Process Documentation

- **[verification-checklist.md](./verification-checklist.md)** — PR0 verification procedures and setup guide
- **[PR2-PR3-INTEGRATION.md](./PR2-PR3-INTEGRATION.md)** — Integration summary for RAG pipeline and chat orchestrator

### Completed PRs

- ✅ **PR0:** Bootstrap & Verification
- ✅ **PR1:** Database Schema (Postgres + pgvector)
- ✅ **PR2:** RAG Pipeline (Chunking, embeddings, vector search)
- ✅ **PR3:** Model Provider & Session Logic
- ✅ **PR3.1:** Google ADK Multi-Agent RAG Integration

### In Progress

- 🚧 **PR3.2:** Python-First Backend Migration (Planning phase)

### Upcoming PRs

- **PR4:** Lead Capture
- **PR5:** Chat Interface
- **PR6:** Landing Polish
- **PR7a-c:** Telegram Bot Integration
- **PR8:** User Auth & Profiles
- **PR9:** Production Launch Readiness
- **PR10:** Post-Launch Iteration

---

## Quick Links

- [AI Workflow Guide](./AI_WORKFLOW.md) — Learn how to use `/psd`, `/plan`, `/plan_feature`, `/generate`, etc.
- [Verification Checklist](./verification-checklist.md) — PR verification procedures
- [PR2-PR3 Integration](./PR2-PR3-INTEGRATION.md) — RAG and orchestrator integration summary
- [PR2-PR3 Performance Analysis](./PR2-PR3-PERFORMANCE-ANALYSIS.md) — Benchmarking results and recommendations

---

## Related Documentation

- **Plans:** [../plans/](../plans/) — Master plan and PR-specific implementation plans
- **Technical:** [../technical/](../technical/) — Technical specifications and architecture
- **PSD:** [../psd/](../psd/) — Product specification documents
- **Decisions:** [../decisions/](../decisions/) — Architecture decision records
- **References:** [../references/](../references/) — External references and API docs

---

**Note:** This directory now contains all verification checklists, integration summaries, and performance analyses. Implementation plans (PR0-PR10) remain in `../plans/`.

---

**Last Updated:** January 1, 2026
