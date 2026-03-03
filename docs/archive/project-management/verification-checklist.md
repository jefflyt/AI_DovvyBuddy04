# PR0 Bootstrap - Verification Guide

## Prerequisites Installation

Before running the verification checklist, you need to install:

### 1. Node.js (Required)

**Option A: Using Homebrew (Recommended for macOS)**

```bash
brew install node@20
```

**Option B: Using nvm (Node Version Manager)**

```bash
# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash

# Restart terminal, then install Node.js
nvm install 20
nvm use 20
```

**Option C: Official Installer**
Download from: https://nodejs.org/ (LTS version 20.x)

### 2. pnpm (Required)

After Node.js is installed:

```bash
npm install -g pnpm
```

Or using Homebrew:

```bash
brew install pnpm
```

---

## Verification Checklist

Run these commands in order from the project root (`AI_DovvyBuddy04/`):

### ✅ 1. Install Dependencies

```bash
pnpm install
```

**Expected:** All packages install successfully, `node_modules/` created.

### ✅ 2. Type Check

```bash
pnpm typecheck
```

**Expected:** No type errors.

### ✅ 3. Lint Check

```bash
pnpm lint
```

**Expected:** No linting errors.

### ✅ 4. Format Check

```bash
pnpm format
```

**Expected:** All files properly formatted (or shows files that need formatting).

### ✅ 5. Run Tests

```bash
pnpm test
```

**Expected:** 1 test suite (example.test.ts), 2 tests passing.

### ✅ 6. Build Production Bundle

```bash
pnpm build
```

**Expected:** Next.js builds successfully, `.next/` folder created.

### ✅ 7. Start Development Server

```bash
pnpm dev
```

**Expected:** Server starts on http://localhost:3000

### ✅ 8. Verify Pages

- Open http://localhost:3000 in browser
  - **Expected:** Landing page loads with "Welcome to DovvyBuddy"
- Navigate to http://localhost:3000/chat
  - **Expected:** Chat stub page loads with placeholder message

---

## Common Issues & Fixes

### Issue: `pnpm: command not found`

**Fix:** Install Node.js and pnpm (see Prerequisites above)

### Issue: Type errors in `src/app/` files

**Fix:** Run `pnpm install` to generate Next.js types

### Issue: Port 3000 already in use

**Fix:** Either:

- Stop other process using port 3000
- Or use different port: `pnpm dev -- -p 3001`

### Issue: CI failing on GitHub

**Fix:**

- Ensure `pnpm-lock.yaml` is committed
- Check GitHub Actions secrets if needed for deployment

---

## Post-Verification: Next Steps

Once all checks pass ✅:

1. **Commit PR0 changes:**

   ```bash
   git add .
   git commit -m "feat: PR0 - Bootstrap Next.js foundation"
   git push origin main
   ```

2. **Verify CI passes** on GitHub Actions

3. **Run planning prompt for PR1:**
   Follow `.github/prompts/plan.prompt.md` to generate database schema PR

4. **Update project documentation** as needed

---

## Files Created in PR0

Configuration:

- `package.json` — Dependencies and scripts
- `tsconfig.json` — TypeScript config
- `next.config.js` — Next.js config
- `.eslintrc.json` — ESLint rules
- `.prettierrc` — Prettier config
- `vitest.config.ts` — Test framework config
- `.env.example` — Environment template
- `.gitignore` — Git ignore rules
- `.github/workflows/ci.yml` — CI pipeline

Application Structure:

- `src/app/layout.tsx` — Root layout
- `src/app/page.tsx` — Landing page
- `src/app/chat/page.tsx` — Chat stub
- `src/app/globals.css` — Global styles
- `src/types/index.ts` — TypeScript types
- `tests/example.test.ts` — Example test

Documentation:

- `README.md` — Setup guide
- `.github/copilot-project.md` — Project context for AI
- `src/lib/README.md` — Lib folder guide
- `src/db/README.md` — Database folder guide
- `content/README.md` — RAG content guide
- `VERIFICATION.md` — This file

---

## Questions?

Refer to:

- Main README: [README.md](../../README.md)
- Product Spec: [docs/psd/DovvyBuddy-PSD-V6.2.md](../psd/DovvyBuddy-PSD-V6.2.md)
- Project Context: [.github/copilot-project.md](../../.github/copilot-project.md)
