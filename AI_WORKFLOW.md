# 🚀 AI Development Workflow

## End-to-End AI-Driven Development Using Custom Copilot Prompts

This document explains **exactly how to use the custom `.prompt.md` files** in this repo to drive planning, specification, implementation, and refactoring using GitHub Copilot in **Plan mode**.

This workflow gives you:

- deterministic output  
- clean separation of PSD → planning → code  
- repeatable development  
- zero ambiguity for Copilot  
- full control over each feature's implementation  

---

## 1. Directory Responsibilities

Your project uses a strict, AI-friendly structure:

```text
.github/prompts/     → All custom Copilot prompt commands  
docs/psd/            → Product specification documents (PSD)  
docs/plans/          → Master plan + feature plans  
docs/references/     → API docs, glossary, schemas  
docs/decisions/      → Architecture decision records  
plans/               → PR-level execution plans + substeps created by /generate  
src/                 → Actual application code
```

### Copilot reads from

- `.github/prompts/*`
- `docs/**/*`
- Any open VS Code files

### Copilot writes code only into

- `src/`

### Copilot writes implementation docs into

- `plans/`

---

## 2. The AI Pipeline

This repo follows a deterministic 7-step workflow:

```bash
1. /psd             → Create Product Specification Document  
2. /plan            → Create Master Implementation Plan  
3. /plan_feature    → Create Feature-Level Plans  
4. /plan-refactored → Create Single-PR Plans  
5. /generate        → Generate Substep Implementation Docs  
6. /implement       → Write Real Code into src/  
7. /refactor        → Improve or Clean Up Code
```

Each step feeds the next.

---

## 3. Step 1 — Create the PSD

### PSD Command

```text
/psd <high-level idea>
```

### PSD Output Location

```text
docs/psd/<product>.psd.md
```

This PSD becomes the **single source of truth** for all further planning.

A good PSD includes:

- product overview  
- personas  
- full feature list  
- UX rules  
- data models  
- edge cases  
- constraints  
- acceptance criteria

---

## 4. Step 2 — Create Master Plan

### Master Plan Command

```text
/plan Use #file:docs/psd/<product>.psd.md to create the overall implementation plan.
```

### Master Plan Output Location

```text
docs/plans/master_plan.md
```

This defines:

- architecture  
- phases  
- feature list  
- multi-PR breakdown  
- dependencies

---

## 5. Step 3 — Create Feature Plans

### Feature Plan Command

```text
/plan_feature Plan the "Google Calendar Integration" feature as described in #file:docs/plans/master_plan.md.
```

### Feature Plan Output Location

```text
docs/plans/google-calendar/plan.md
```

Each feature plan includes:

- scope  
- objectives  
- success criteria  
- functional requirements  
- edge cases  
- acceptance rules  

---

## 6. Step 4 — Convert Feature Plan → PR Plan

### PR Plan Command

```text
/plan-refactored Create a single-PR development plan for the feature described in #file:docs/plans/google-calendar/plan.md.
```

### PR Plan Output Location

```text
plans/google-calendar/plan.md  
plans/google-calendar/README.md
```

This PR plan defines the **exact implementation steps**, for example:

```text
Step 1 — Create OAuth handler  
Step 2 — Calendar sync service  
Step 3 — Webhook listener
```

---

## 7. Step 5 — Generate Substep Documentation

### Generate Command

```text
/generate Generate all implementation substeps for #file:plans/google-calendar/plan.md.
```

This creates:

```text
plans/google-calendar/
  ├── 1-create-oauth-handler/
  │     ├── 1.1-setup-credentials.md
  │     ├── 1.2-token-storage.md
  ├── 2-sync-service/
  │     ├── 2.1-fetch-events.md
  │     ├── 2.2-push-updates.md
  └── ...
```

Each file contains copy-paste-ready code instructions.

---

## 8. Step 6 — Implement Code

### Implement Command

```text
/implement Implement the feature according to #file:plans/google-calendar/plan.md.
```

Copilot will:

- read PR plan  
- read substeps  
- modify files in `src/` only  
- apply patches step-by-step  
- update checkboxes in plan/substep files

You will:

- review diffs  
- run tests  
- commit after each major step  

This ensures deterministic, structured engineering.

---

## 9. Step 7 — Refactor Code

### Refactor Command

```text
/refactor Create a refactor plan for src/backend/google-calendar/.
```

This creates a **refactor plan**, not code.

It describes:

- file-by-file problems  
- naming issues  
- modularization opportunities  
- dead code removal  
- simplification opportunities  

---

## 10. Using `/search_docs` Anytime

### Examples

```text
/search_docs Show all info related to 'token storage'.
/search_docs Find data models for calendar events.
/search_docs How does auth currently work?
```

This searches:

- `docs/psd/`
- `docs/plans/`
- `docs/references/`
- your code

It eliminates hallucination and reinforces consistency.

---

## 11. Rules You Must Not Break

### 1 — Always use **Plan mode**

Agent mode breaks controlled workflows.

### 2 — Do not mix planning and implementation

- Planning lives in `docs/` and `plans/`
- Code lives in `src/`

### 3 — Never skip planning steps

Skipping → Copilot guesses → bugs.

### 4 — One feature = one PR plan

Your prompts enforce this.

### 5 — Keep PSD and plans updated

Copilot accuracy is **directly proportional** to your documentation quality.

---

## 12. Quick Command Cheat Sheet

```text
/psd                → write product spec  
/plan               → master plan  
/plan_feature       → feature plan  
/plan-refactored    → convert feature → PR  
/generate           → create substep docs  
/implement          → write code  
/refactor           → refactor plan  
/search_docs        → search docs
```

---

## 13. Example Workflow Snapshot

```text
/psd "Build JeffOS MCP"
/plan "Use PSD to create master plan"
/plan_feature "Notion integration"
/plan-refactored "Convert feature to PR plan"
/generate "Generate implementation docs"
/implement "Implement according to PR plan"
/refactor "Plan refactor for backend modules"
```

---

## 14. Conclusion

This workflow gives you:

- full AI-driven development lifecycle  
- predictable output  
- controllable engineering steps  
- scalable multi-feature development  
- PM-friendly planning  
- clean and maintainable code  

You now have a **complete AI-powered software development system** inside your project.
