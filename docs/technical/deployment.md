# Cloud Run Deployment Guide

**Status:** Ready for Implementation  
**Date:** January 3, 2026  
**Target:** Google Cloud Run (Backend) + Vercel (Frontend)

---

## Overview

DovvyBuddy uses a split-stack architecture:
- **Frontend:** Next.js on Vercel (TypeScript/React)
- **Backend:** FastAPI on Google Cloud Run (Python 3.11)
- **Database:** PostgreSQL + pgvector on Neon
- **Communication:** Frontend → Cloud Run REST API over HTTPS

---

## Prerequisites

### 1. Google Cloud Setup
```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Login and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2. Environment Variables
Prepare these values before deployment:

**Backend (Cloud Run):**
- `DATABASE_URL` - Neon PostgreSQL connection string
- `GEMINI_API_KEY` - Google Gemini API key
- `GROQ_API_KEY` - Groq API key (optional, for dev)
- `CORS_ORIGINS` - Vercel domain(s), comma-separated
- `DEFAULT_LLM_PROVIDER` - `groq` or `gemini`
- `ENABLE_RAG` - `true`

**Frontend (Vercel):**
- `NEXT_PUBLIC_BACKEND_URL` - Cloud Run service URL

---

## Backend Deployment (Cloud Run)

### Step 1: Build and Test Locally

```bash
cd backend

# Build Docker image
docker build -t dovvybuddy-backend .

# Test locally (create .env.docker for testing)
docker run -p 8080:8080 --env-file .env dovvybuddy-backend

# Verify health endpoint
curl http://localhost:8080/health
# Expected: {"status":"healthy","version":"0.1.0"}

# Test chat endpoint
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is Open Water certification?"}'
```

### Step 2: Deploy to Cloud Run

**Option A: Deploy from source (recommended for iteration)**
```bash
cd backend

gcloud run deploy dovvybuddy-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 10 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --set-env-vars DATABASE_URL="$DATABASE_URL" \
  --set-env-vars GEMINI_API_KEY="$GEMINI_API_KEY" \
  --set-env-vars GROQ_API_KEY="$GROQ_API_KEY" \
  --set-env-vars DEFAULT_LLM_PROVIDER="groq" \
  --set-env-vars ENABLE_RAG="true" \
  --set-env-vars CORS_ORIGINS="https://your-vercel-domain.vercel.app"
```

**Option B: Deploy from pre-built image**
```bash
# Build and push to Container Registry
docker build -t gcr.io/YOUR_PROJECT_ID/dovvybuddy-backend .
docker push gcr.io/YOUR_PROJECT_ID/dovvybuddy-backend

# Deploy from registry
gcloud run deploy dovvybuddy-backend \
  --image gcr.io/YOUR_PROJECT_ID/dovvybuddy-backend \
  --region us-central1 \
  --allow-unauthenticated \
  [... same flags as Option A ...]
```

### Step 3: Configure CORS

The backend automatically configures CORS based on `CORS_ORIGINS` environment variable.

**Update CORS origins:**
```bash
gcloud run services update dovvybuddy-backend \
  --update-env-vars CORS_ORIGINS="https://dovvybuddy.vercel.app,https://dovvybuddy-preview.vercel.app"
```

### Step 4: Verify Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe dovvybuddy-backend --region us-central1 --format 'value(status.url)')
echo $SERVICE_URL

# Test health endpoint
curl $SERVICE_URL/health

# Test chat endpoint
curl -X POST $SERVICE_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What dive sites are in Tioman?"}'
```

---

## Frontend Deployment (Vercel)

### Step 1: Set Environment Variables

In Vercel dashboard or CLI:

```bash
# Using Vercel CLI
vercel env add NEXT_PUBLIC_BACKEND_URL

# Enter the Cloud Run service URL when prompted
# Example: https://dovvybuddy-backend-xxxxx-uc.a.run.app
```

### Step 2: Deploy Frontend

```bash
# From project root
vercel --prod

# Or via Git push (if connected to GitHub)
git push origin main
```

### Step 3: Verify Integration

```bash
# Visit your Vercel deployment
open https://your-domain.vercel.app

# Test chat interface
# - Ask a question about certifications or dive sites
# - Verify NO_DATA handling for unknown topics
# - Check developer console for API calls to Cloud Run
```

---

## Configuration Options

### Scaling Configuration

**For low traffic (MVP):**
```bash
gcloud run services update dovvybuddy-backend \
  --min-instances 0 \
  --max-instances 3 \
  --concurrency 80
```

**For moderate traffic:**
```bash
gcloud run services update dovvybuddy-backend \
  --min-instances 1 \
  --max-instances 10 \
  --concurrency 100
```

**Cost optimization:**
- `--min-instances 0` - No idle cost, but cold starts (~2-5s)
- `--min-instances 1` - Always warm, small idle cost (~$10/month)

### Resource Limits

**Default (sufficient for MVP):**
- Memory: 1Gi
- CPU: 1
- Timeout: 300s (5 minutes)

**For higher load:**
```bash
gcloud run services update dovvybuddy-backend \
  --memory 2Gi \
  --cpu 2
```

---

## Monitoring & Debugging

### View Logs

```bash
# Stream logs in real-time
gcloud run services logs tail dovvybuddy-backend --region us-central1

# Filter for errors
gcloud run services logs read dovvybuddy-backend \
  --region us-central1 \
  --filter "severity>=ERROR"
```

### Cloud Console

1. Navigate to: https://console.cloud.google.com/run
2. Select `dovvybuddy-backend` service
3. View:
   - **Metrics:** Request count, latency, errors
   - **Logs:** Application logs, access logs
   - **Revisions:** Deployment history

### Common Issues

**Issue: CORS errors in browser console**
```bash
# Solution: Update CORS_ORIGINS
gcloud run services update dovvybuddy-backend \
  --update-env-vars CORS_ORIGINS="https://your-new-domain.vercel.app"
```

**Issue: Cold start latency**
```bash
# Solution: Set min-instances to 1
gcloud run services update dovvybuddy-backend \
  --min-instances 1
```

**Issue: Database connection timeout**
- Check Neon database is running
- Verify `DATABASE_URL` format: `postgresql+asyncpg://user:pass@host/db`
- Ensure Neon allows connections from Cloud Run IPs (usually allowed by default)

---

## Security Best Practices

### 1. Use Secret Manager (Recommended)

Instead of plain environment variables:

```bash
# Store secrets
echo -n "your-gemini-api-key" | gcloud secrets create gemini-api-key --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role roles/secretmanager.secretAccessor

# Deploy with secrets
gcloud run deploy dovvybuddy-backend \
  --source . \
  --update-secrets GEMINI_API_KEY=gemini-api-key:latest
```

### 2. Enable IAM Authentication (Optional)

For production with authentication:

```bash
gcloud run deploy dovvybuddy-backend \
  --no-allow-unauthenticated

# Frontend needs to authenticate via service account or Identity Platform
```

---

## Rollback Procedure

```bash
# List revisions
gcloud run revisions list --service dovvybuddy-backend --region us-central1

# Rollback to previous revision
gcloud run services update-traffic dovvybuddy-backend \
  --to-revisions REVISION_NAME=100 \
  --region us-central1
```

---

## Cost Estimates

**Cloud Run (Backend):**
- Free tier: 2 million requests/month, 360,000 GB-seconds
- Beyond free tier: ~$0.40 per million requests
- MVP estimate: <$5/month with low traffic

**Neon (Database):**
- Free tier: 0.5GB storage, 100 hours compute
- Pro tier: $19/month (recommended for production)

**Vercel (Frontend):**
- Hobby: Free (personal projects)
- Pro: $20/month (custom domains, team features)

**API Costs:**
- Gemini: ~$0.35 per 1M input tokens (Flash model)
- Groq: Free tier available, then pay-as-you-go

---

## Next Steps After Deployment

1. **Monitor RAF enforcement:**
   - Test NO_DATA handling
   - Verify citations appear
   - Check confidence scores

2. **Performance baseline:**
   - Measure P95 latency
   - Track error rates
   - Monitor database query times

3. **User testing:**
   - Share with beta testers
   - Collect feedback on response quality
   - Iterate on prompts and RAG tuning

4. **Future enhancements:**
   - Add SSE streaming endpoint
   - Implement caching layer (Redis)
   - Set up alerting (Cloud Monitoring)

---

## Support

- **Cloud Run Docs:** https://cloud.google.com/run/docs
- **Vercel Docs:** https://vercel.com/docs
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Project Issues:** GitHub Issues

---

**Last Updated:** January 3, 2026  
**Maintained By:** DovvyBuddy Team
