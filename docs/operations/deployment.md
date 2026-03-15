# Two-Project Vercel Deployment Guide

**Status:** Active deployment guide
**Target:** Vercel web project (`apps/web`) + Vercel API project (`apps/api`)

## Architecture

DovvyBuddy deploys as two Vercel projects from the same monorepo:

- **Web project:** Next.js app rooted at `apps/web`
- **API project:** FastAPI app rooted at `apps/api`
- **Database:** Neon PostgreSQL + pgvector
- **Email:** Resend

The frontend keeps browser calls on `/api/*` and rewrites them to the API project using `BACKEND_URL`.

## Why Two Projects

- Keeps Next.js and FastAPI runtime concerns separate
- Lets each project own its own environment variables and logs
- Avoids forcing frontend and backend into one Vercel runtime model
- Matches the current repo wiring (`BACKEND_URL` + `/api` rewrites)

## Project Setup

Create two Vercel projects connected to the same GitHub repo.

### Web project

- Root Directory: `apps/web`
- Framework Preset: Next.js
- Install Command: default
- Build Command: default
- Output Directory: default

### API project

- Root Directory: `apps/api`
- Framework Preset: FastAPI / Python
- Install Command: default
- Build Command: default

The API project uses the Python entry point exported in [apps/api/pyproject.toml](/Users/jefflee/Documents/AIProjects/AI_DovvyBuddy04/apps/api/pyproject.toml):

```toml
[project.scripts]
app = "app.main:app"
```

## Environment Variables

### Web project (`apps/web`)

Required:

- `BACKEND_URL=https://<api-project>.vercel.app`
- `NEXT_PUBLIC_API_URL=/api`

Optional / existing:

- `NEXT_PUBLIC_APP_URL=https://<web-project>.vercel.app`
- Analytics and Sentry vars as needed
- `NEXT_PUBLIC_FEATURE_CONVERSATION_FOLLOWUP_ENABLED=true`

### API project (`apps/api`)

Required:

- `ENVIRONMENT=production`
- `DEBUG=false`
- `DATABASE_URL=<neon connection string>`
- `GEMINI_API_KEY=<gemini api key>`
- `SESSION_SECRET=<32+ char secret>`
- `RESEND_API_KEY=<resend api key>`
- `LEAD_EMAIL_TO=<lead destination email>`
- `CORS_ORIGINS=https://<web-project>.vercel.app`

Usually keep:

- `ENABLE_ADK=true`
- `ENABLE_AGENT_ROUTING=true`
- `ENABLE_ADK_NATIVE_GRAPH=true`
- `ENABLE_RAG=true`
- `DEFAULT_LLM_MODEL=gemini-2.5-flash-lite`
- `ADK_MODEL=gemini-2.5-flash-lite`
- `EMBEDDING_MODEL=text-embedding-004`
- `EMBEDDING_DIMENSION=768`

Optional:

- `CORS_ORIGIN_REGEX=https://.*\\.vercel\\.app`
- Sentry vars

## Deployment Flow

### 1. Deploy the API project first

After the first successful deployment, note the API URL:

```bash
https://<api-project>.vercel.app
```

### 2. Configure the web project

Set:

```bash
BACKEND_URL=https://<api-project>.vercel.app
NEXT_PUBLIC_API_URL=/api
```

Then deploy the web project.

### 3. Verify the API project

Run:

```bash
curl https://<api-project>.vercel.app/health
curl https://<api-project>.vercel.app/ready
```

Expected:

- `/health` returns `200`
- `/ready` returns `200` only when DB and critical env are configured

### 4. Verify the web project

Check:

- landing page loads
- `/chat` loads
- browser requests go to `/api/chat`
- rewritten requests succeed against the API project
- lead form submission succeeds

## Preview Deployment Caveat

Vercel preview deployments for the web project do **not** automatically discover the matching API preview URL from the separate API project.

For MVP, use one of these strategies:

- simplest: point web preview `BACKEND_URL` at the API production URL
- stricter: manually set preview `BACKEND_URL` to a stable preview alias for the API project

Do not assume Vercel will automatically pair the two preview deployments.

## Local Validation Before Deploy

From the repo root:

```bash
pnpm test
pnpm typecheck
BACKEND_URL=http://localhost:8000 pnpm build
.venv/bin/python -m pytest apps/api/tests/integration -q
pnpm content:validate
```

If you want browser validation:

```bash
pnpm test:e2e tests/e2e/landing-chat-preview.spec.ts
```

## MVP Launch Checklist

- API project deployed on Vercel
- Web project deployed on Vercel
- `BACKEND_URL` on the web project points to the API project
- `/ready` returns `200` on the API deployment
- Neon DB reachable from Vercel functions
- Gemini key configured
- Resend lead delivery configured
- Chat request works from the public web deployment
- Lead submission works from the public web deployment

## Rollback

Rollback independently per Vercel project:

- rollback the web project if only UI/rewrite issues regress
- rollback the API project if backend behavior or env changes regress

This separation is one of the main reasons to keep the deployment split into two projects.
