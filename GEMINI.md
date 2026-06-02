# Gemini Developer Guidelines for DovvyBuddy

Welcome to DovvyBuddy! As a developer or agent utilizing the Google Gemini models (e.g., `gemini-2.5-flash-lite`), follow these guidelines to maintain visual excellence, solid performance, and structured code quality.

---

## 🚀 Tech Stack & Structure

DovvyBuddy is structured as a monorepo:

- **Frontend:** Next.js 14 (App Router) + TypeScript in [apps/web/](file:///Users/jefflee/Documents/AIProjects/AI_DovvyBuddy04/apps/web/)
- **Backend:** FastAPI + SQLAlchemy async in [apps/api/](file:///Users/jefflee/Documents/AIProjects/AI_DovvyBuddy04/apps/api/)
- **Data:** PostgreSQL + pgvector (Neon)
- **Content:** Curated diving corpus in [content/source/](file:///Users/jefflee/Documents/AIProjects/AI_DovvyBuddy04/content/source/)

---

## 🛠️ Developer Commands Cheat Sheet

Use these commands for local execution, verification, and builds:

### Frontend

- **Development Server:** `pnpm --filter web dev` or run from root: `pnpm run dev`
- **Production Build:** `pnpm --filter web build`
- **Run Unit/E2E Tests:** `pnpm test` or `pnpm --filter web test`
- **Static Analysis:** `pnpm typecheck && pnpm lint`

### Backend

- **Run API Server:** Executed via poetry/venv: `poetry run uvicorn apps.api.app.main:app --reload`
- **Run Tests:** `.venv/bin/python -m pytest apps/api/tests -q`
- **Linting / Formatting:** `ruff check` and `ruff format`

### Content Validation

- **Validate Corpus Structure:** `pnpm content:validate`

---

## 🎨 Premium Visual & Design Aesthetics

Every UI component and page in DovvyBuddy must wow the user at first glance.

1. **Harmonious Palettes:** Use tailored HSL color tokens and elegant dark modes. Avoid generic, plain browser-default red, blue, or green colors.
2. **Modern Typography:** Use premium Google Fonts (e.g., _Inter_, _Outfit_, or _Roboto_) via Next.js Font loading.
3. **Vanilla CSS First:** Prefer Vanilla CSS stylesheets (`index.css` or CSS modules) over Tailwind CSS unless Tailwind is explicitly requested. Keep styles centered around custom CSS tokens.
4. **Dynamic Experience:** Incorporate subtle micro-animations, glassmorphism (`backdrop-filter`), smooth gradients, and hover transitions.
5. **No Placeholders:** Never use simple boxes or text placeholders. For graphics, generate high-quality assets.
6. **SEO Best Practices:** Auto-inject descriptive titles, meta descriptions, semantic HTML5 tags (e.g., `<main>`, `<article>`), and unique target IDs for testing.

---

## 🤖 Multi-Agent Orchestration with Ruflo

We have decommissioned and **deleted Letta** to focus exclusively on **Ruflo** (formerly Claude Flow) for multi-agent capabilities. Ruflo manages specialized agent swarms, shared memory, and advanced context routing.

### Ruflo Commands & Setup

- **Initialize Ruflo:** `npx ruflo@latest init`
- **Start Swarm Daemon:** `npx ruflo@latest daemon start`
- **Perform Diagnostics:** `npx ruflo@latest doctor`
- **Search Swarm Memory:** `npx ruflo@latest memory search --query "..."`

### Specialized Ruflo Skills Reference

| Category                   | Skill / Method                             | Purpose                                           |
| :------------------------- | :----------------------------------------- | :------------------------------------------------ |
| **UI/UX & Design**         | `ui-ux-pro-max` / `stitch-design-taste`    | High-fidelity component layouts & modern theming  |
| **Accessibility & Perf**   | `a11y-debugging` / `debug-optimize-lcp`    | Web performance (LCP/INP) and ARIA auditing       |
| **System Architecture**    | `sparc:architect` / `sparc:designer`       | API layout, routing protocols, db schemas         |
| **Memory & Orchestration** | `swarm-orchestration` / `ruflo`            | Multi-agent collaboration, memory persistence     |
| **Planning & Execution**   | `superpowers:writing-plans` / `sparc:code` | SPARC framework-driven test-driven implementation |

---

## 📐 Context & Monorepo Working Rules

- **Small Contexts:** Keep task context minimal. Do not scan directories recursively unless necessary.
- **Scan Budget:** Open at most **12 files** and about **1,500 lines total** on a first-pass analysis.
- **Preflight Check:** Before scanning code, run the preflight script:
  `pnpm agent:preflight -- <backend|frontend|content|docs>`
- **Gated Scanner:** Use `pnpm agent:scan -- <rg args>` to scan securely.
