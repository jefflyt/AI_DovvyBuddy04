# PR6.1: MVP Production Deployment

**Status:** Planned  
**Prerequisite PRs:** PR1-PR6 (Core functionality + Landing page polish)  
**Date:** January 5, 2026  
**Duration:** 3-5 days

---

## Goal

Deploy the Python FastAPI backend to Google Cloud Run with production monitoring, CI/CD pipeline, and DNS configuration. This PR represents the final technical step to launch the DovvyBuddy MVP publicly.

---

## Scope

### In Scope

- Cloud Run deployment configuration (production environment)
- GitHub Actions workflow for automated deployment
- Environment variable management (secrets, API keys)
- Structured logging (JSON format for Cloud Run)
- Basic monitoring (Cloud Run metrics, health checks)
- DNS configuration (`api.dovvybuddy.com` → Cloud Run)
- SSL/TLS certificate (automatic via Cloud Run)
- Deployment runbook and procedures
- Rollback procedures
- Production smoke testing checklist

### Out of Scope

- Advanced monitoring/alerting (Sentry, DataDog) - deferred to post-MVP
- Staging environment - use Cloud Run tags for testing
- Load testing - defer to post-launch optimization
- Auto-scaling tuning - use Cloud Run defaults
- Multi-region deployment - deferred to scaling phase
- Cost optimization - monitor and optimize post-launch

---

## Backend Changes

### Existing Files (Already Complete ✅)

The Python backend is fully implemented with:
- ✅ **Dockerfile** — Production-ready (Python 3.11, non-root user, health check)
- ✅ **FastAPI application** — All endpoints functional
- ✅ **Database migrations** — Alembic ready
- ✅ **RAG pipeline** — Content embeddings ingested
- ✅ **Agent orchestration** — Multi-agent system operational

### New Modules (Production Enhancements)

**Deployment Configuration:**
```
.github/workflows/
├── deploy-production.yml          # Deploy backend to Cloud Run

docs/
├── deployment-runbook.md          # Step-by-step deployment guide
└── rollback-procedures.md         # Emergency rollback steps
```

**Optional Enhancements (if time permits):**
```
src/backend/app/
├── middleware/
│   └── request_id.py              # Request ID tracking
└── core/
    └── logging.py                 # Enhanced structured logging
```

### Modified Modules (Minimal Changes)

1. **src/backend/app/core/config.py** — Add production-specific settings
   - `LOG_LEVEL`: INFO (production default)
   - `ENVIRONMENT`: production indicator
   - Ensure all secrets loaded from environment variables

2. **src/backend/app/main.py** — Production readiness
   - Verify CORS configured for production domain
   - Ensure health check endpoint is robust
   - Optional: Add request ID middleware

---

## Frontend Changes

### Modified Modules

1. **next.config.js** — Production API configuration
   - Configure rewrites for `/api/*` → Cloud Run backend
   - Production backend URL: `https://api.dovvybuddy.com`

2. **.env.production** — Production environment variables
   ```bash
   # Backend API
   BACKEND_URL=https://api.dovvybuddy.com
   NEXT_PUBLIC_API_URL=/api
   
   # Database (same as backend)
   DATABASE_URL=<neon-production-url>
   ```

3. **Vercel Configuration** — Environment variables in dashboard
   - Set `BACKEND_URL` for production deployment
   - Ensure frontend can reach backend (CORS configured)

---

## Data Changes

**None.** Uses existing Neon PostgreSQL database with all migrations already applied.

---

## Infra / Config

### Docker Configuration (Already Complete ✅)

The existing `src/backend/Dockerfile` is production-ready:
- Python 3.11 slim base image
- System dependencies (gcc, postgresql-client)
- Editable pip install (`pip install -e .`)
- Non-root user (appuser)
- Port 8080 exposed (Cloud Run default)
- Health check configured
- Uvicorn with 1 worker

**Minor optimization (optional):**
```dockerfile
# Consider adding if image size is a concern
# Multi-stage build to reduce final image size
FROM python:3.11-slim AS builder
...
FROM python:3.11-slim
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
```

### Cloud Run Configuration

**Production Service Configuration:**
```yaml
# Applied via gcloud CLI or YAML
service: dovvybuddy-backend
region: us-central1  # or us-west1 for lower latency if West Coast focused

container:
  port: 8080
  resources:
    limits:
      cpu: "1"      # 1 vCPU
      memory: 512Mi # 512 MB RAM (adjust based on monitoring)
  
scaling:
  minInstances: 0   # Serverless (cold starts acceptable for MVP)
  maxInstances: 10  # Cap for cost control
  
timeout: 300s       # 5 minutes max request time

env:
  - name: ENVIRONMENT
    value: production
  - name: LOG_LEVEL
    value: INFO
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef: database-url
  - name: GEMINI_API_KEY
    valueFrom:
      secretKeyRef: gemini-api-key
  - name: GROQ_API_KEY
    valueFrom:
      secretKeyRef: groq-api-key
```

**Secret Management:**
Use Google Secret Manager (not environment variables in YAML):
```bash
# Create secrets
gcloud secrets create database-url --data-file=-
gcloud secrets create gemini-api-key --data-file=-
gcloud secrets create groq-api-key --data-file=-

# Grant access to Cloud Run service account
gcloud secrets add-iam-policy-binding database-url \
  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### GitHub Actions Workflows

**Single Workflow for Production Deployment:**

`.github/workflows/deploy-production.yml`
```yaml
name: Deploy Backend to Production

on:
  workflow_dispatch:
    inputs:
      tag:
        description: 'Git tag or branch to deploy (default: main)'
        required: false
        default: 'main'

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          ref: ${{ github.event.inputs.tag || 'main' }}
      
      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v2
      
      - name: Configure Docker for GCR
        run: gcloud auth configure-docker
      
      - name: Build Docker image
        run: |
          cd src/backend
          docker build -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:${{ github.sha }} .
          docker tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:${{ github.sha }} \
                     gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:latest
      
      - name: Push to Container Registry
        run: |
          docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:${{ github.sha }}
          docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:latest
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy dovvybuddy-backend \
            --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:${{ github.sha }} \
            --platform managed \
            --region us-central1 \
            --allow-unauthenticated \
            --set-secrets="DATABASE_URL=database-url:latest,GEMINI_API_KEY=gemini-api-key:latest,GROQ_API_KEY=groq-api-key:latest" \
            --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=INFO,ENABLE_RAG=true,DEFAULT_LLM_PROVIDER=groq" \
            --max-instances=10 \
            --timeout=300 \
            --memory=512Mi \
            --cpu=1
      
      - name: Get service URL
        id: get-url
        run: |
          URL=$(gcloud run services describe dovvybuddy-backend \
            --region us-central1 \
            --format 'value(status.url)')
          echo "service_url=$URL" >> $GITHUB_OUTPUT
      
      - name: Run smoke tests
        run: |
          sleep 10  # Wait for deployment to stabilize
          curl -f ${{ steps.get-url.outputs.service_url }}/health || exit 1
          echo "✅ Health check passed"
      
      - name: Summary
        run: |
          echo "🚀 Deployment complete!"
          echo "Service URL: ${{ steps.get-url.outputs.service_url }}"
          echo "Image: gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:${{ github.sha }}"
```

**Required GitHub Secrets:**
- `GCP_SA_KEY` — Service account JSON key with Cloud Run Admin + Secret Manager Accessor roles
- `GCP_PROJECT_ID` — Google Cloud project ID

### Environment Variables (Production)

**Backend (Cloud Run via Secret Manager):**
```bash
# Database
DATABASE_URL=<neon-production-postgres-url>

# LLM APIs
GEMINI_API_KEY=<gemini-api-key>
GROQ_API_KEY=<groq-api-key>

# Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
DEFAULT_LLM_PROVIDER=groq
DEFAULT_LLM_MODEL=llama-3.3-70b-versatile
ENABLE_RAG=true
SESSION_EXPIRY_HOURS=24

# CORS (frontend domain)
CORS_ORIGINS=https://dovvybuddy.com,https://www.dovvybuddy.com
```

**Frontend (Vercel Environment Variables):**
```bash
# Backend API endpoint
BACKEND_URL=https://api.dovvybuddy.com

# Database (for any server-side operations if needed)
DATABASE_URL=<same-as-backend>
```

### DNS Configuration

**Manual Setup Steps:**

1. **Deploy Cloud Run service** (get auto-generated URL)
   ```bash
   gcloud run deploy dovvybuddy-backend ...
   # Output: Service URL: https://dovvybuddy-backend-xxxxx-uc.a.run.app
   ```

2. **Map custom domain in Cloud Run**
   ```bash
   gcloud run domain-mappings create \
     --service dovvybuddy-backend \
     --domain api.dovvybuddy.com \
     --region us-central1
   ```
   
3. **Add DNS records** (in domain registrar or Cloud DNS)
   - Cloud Run will provide specific DNS records to add
   - Typically: CNAME or A/AAAA records pointing to ghs.googlehosted.com
   - SSL certificate automatically provisioned (may take 15-60 minutes)

4. **Verify DNS propagation**
   ```bash
   dig api.dovvybuddy.com
   curl https://api.dovvybuddy.com/health
   ```

### Monitoring & Observability

**Built-in Cloud Run Metrics (Free):**
- Request count & latency (p50, p95, p99)
- Error rate (4xx, 5xx responses)
- CPU & memory utilization
- Instance count (active containers)
- Cold start frequency

**Access metrics:**
- Cloud Console → Cloud Run → dovvybuddy-backend → Metrics tab
- Or use `gcloud run services describe`

**Structured Logging:**
- Python backend already logs JSON to stdout
- View logs: Cloud Console → Logs Explorer
- Filter by severity, request ID, session ID

**Basic Alerts (Optional for MVP):**
```bash
# Create alert for error rate >5%
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s
```

---

## Testing

### Pre-Deployment Testing

**Local Docker Testing:**
```bash
# Build and test locally
cd src/backend
docker build -t dovvybuddy-backend:local .

# Run with production-like config
docker run -p 8080:8080 \
  -e DATABASE_URL="$DATABASE_URL" \
  -e GEMINI_API_KEY="$GEMINI_API_KEY" \
  -e GROQ_API_KEY="$GROQ_API_KEY" \
  -e ENVIRONMENT=production \
  -e LOG_LEVEL=INFO \
  dovvybuddy-backend:local

# Test endpoints
curl http://localhost:8080/health
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is PADI Open Water certification?"}'
```

### Production Smoke Testing

**Manual Smoke Test Checklist:**

After deployment, verify:

- [ ] Health check responds: `curl https://api.dovvybuddy.com/health`
- [ ] Chat endpoint works: POST `/api/chat` with test query
- [ ] Session persists: Use returned sessionId in second request
- [ ] RAG retrieval: Check `contextChunks` in response
- [ ] Error handling: Send invalid payload, verify 400 response
- [ ] CORS headers: Check `Access-Control-Allow-Origin` in response
- [ ] Response time: Chat response <10s (acceptable for MVP)
- [ ] Logs visible: Check Cloud Run logs for requests

**Automated Smoke Test Script:**
```bash
#!/bin/bash
# smoke-test.sh

API_URL="https://api.dovvybuddy.com"

# Test 1: Health check
echo "Testing health endpoint..."
curl -f "$API_URL/health" || exit 1

# Test 2: Chat endpoint
echo "Testing chat endpoint..."
RESPONSE=$(curl -s -X POST "$API_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"What is PADI Open Water?"}')

# Check response has sessionId
echo "$RESPONSE" | jq -e '.sessionId' || exit 1
echo "$RESPONSE" | jq -e '.response' || exit 1

echo "✅ All smoke tests passed!"
```

---

## Verification

### Deployment Commands

```bash
# 1. Build Docker image locally (optional verification)
cd src/backend
docker build -t dovvybuddy-backend:test .
docker run -p 8080:8080 --env-file .env dovvybuddy-backend:test

# 2. Deploy via GitHub Actions (recommended)
# Go to GitHub → Actions → "Deploy Backend to Production" → Run workflow
# Or push to main branch if auto-deploy configured

# 3. Manual deployment (if needed)
cd src/backend
gcloud builds submit --tag gcr.io/PROJECT_ID/dovvybuddy-backend
gcloud run deploy dovvybuddy-backend \
  --image gcr.io/PROJECT_ID/dovvybuddy-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-secrets="DATABASE_URL=database-url:latest,GEMINI_API_KEY=gemini-api-key:latest,GROQ_API_KEY=groq-api-key:latest" \
  --max-instances=10

# 4. Verify deployment
gcloud run services describe dovvybuddy-backend --region us-central1

# 5. View logs
gcloud run logs read dovvybuddy-backend --region us-central1 --limit 50

# 6. Test endpoints
SERVICE_URL=$(gcloud run services describe dovvybuddy-backend --region us-central1 --format 'value(status.url)')
curl $SERVICE_URL/health
```

### MVP Launch Checklist

**Pre-Launch (Complete Before Deployment):**

- [ ] PR1-PR6 complete (Database, RAG, Chat, Lead Capture, Landing Page)
- [ ] Content ingested (certifications, destinations, FAQ)
- [ ] Environment variables configured in Secret Manager
- [ ] GCP project billing enabled
- [ ] Cloud Run API enabled
- [ ] Service account created with proper roles
- [ ] GitHub secrets configured (GCP_SA_KEY, GCP_PROJECT_ID)
- [ ] Domain owned and accessible (dovvybuddy.com)

**Deployment Phase:**

- [ ] Dockerfile builds successfully
- [ ] GitHub Actions workflow runs without errors
- [ ] Cloud Run service deployed
- [ ] Health check responds (200 OK)
- [ ] Smoke tests pass (health, chat, session)
- [ ] DNS configured (api.dovvybuddy.com)
- [ ] SSL certificate active (https://)
- [ ] CORS configured for frontend domain

**Post-Deployment Validation:**

- [ ] Frontend can reach backend API
- [ ] Chat flow works end-to-end
- [ ] Session persistence verified
- [ ] RAG retrieval working (contextChunks present)
- [ ] Lead capture stores data
- [ ] Logs visible in Cloud Console
- [ ] No critical errors in logs (first 30 minutes)
- [ ] Response times acceptable (<10s)
- [ ] Monitor for 24 hours before announcing

**Launch Announcement:**

- [ ] Create social media posts
- [ ] Update documentation/README
- [ ] Notify test users
- [ ] Monitor metrics daily (week 1)
- [ ] Collect user feedback
- [ ] Plan iteration based on learnings

---

## Rollback Plan

### Emergency Rollback Procedure

**Scenario:** Production deployment has critical issues

**Execution Time:** <2 minutes

**Steps:**

1. **Rollback to previous revision**
   ```bash
   # Find previous revision
   gcloud run revisions list --service=dovvybuddy-backend --region=us-central1
   
   # Rollback (use previous revision name)
   gcloud run services update-traffic dovvybuddy-backend \
     --region us-central1 \
     --to-revisions PREVIOUS_REVISION_NAME=100
   ```

2. **Verify rollback**
   ```bash
   # Check traffic routing
   gcloud run services describe dovvybuddy-backend --region us-central1
   
   # Test endpoints
   curl https://api.dovvybuddy.com/health
   ```

3. **Monitor for recovery**
   - Check error rate drops in Cloud Run metrics
   - Verify logs show requests being served
   - Test critical user flows manually

4. **Communicate**
   - Notify team of rollback
   - Update status page (if applicable)
   - Investigate root cause

### Rollback Triggers

**Immediate Rollback If:**
- Error rate >10% sustained for 5+ minutes
- Complete service outage (health check failing)
- Data corruption or loss detected
- Security vulnerability exposed

**Consider Rollback If:**
- Error rate >5% sustained for 15+ minutes
- P95 latency >15s sustained for 15+ minutes
- Critical user-reported bugs affecting core flows
- Database connection pool exhausted

---

## Dependencies

### PRs that must be merged

- ✅ **PR1** (Database Schema) - Complete
- ✅ **PR2** (RAG Pipeline) - Complete  
- ✅ **PR3** (Model Provider & Session) - Complete
- ✅ **PR3.1** (ADK Multi-Agent) - Complete
- ✅ **PR3.2a-d** (Python Backend Migration) - Complete
- ✅ **PR3.2e** (Frontend Integration) - Complete
- ⏳ **PR4** (Lead Capture) - Recommended for full MVP
- ⏳ **PR5** (Chat Interface) - Required (basic chat exists, needs polish)
- ⏳ **PR6** (Landing Polish) - Recommended before public launch

**Note:** PR6.1 should be completed **after PR6** to ensure the landing page and chat interface are polished before deploying to production.

### External Dependencies

- Google Cloud Platform account with billing enabled
- Cloud Run API enabled (`gcloud services enable run.googleapis.com`)
- Container Registry enabled (`gcloud services enable containerregistry.googleapis.com`)
- Secret Manager API enabled (`gcloud services enable secretmanager.googleapis.com`)
- Service account with roles:
  - Cloud Run Admin
  - Secret Manager Secret Accessor
  - Storage Admin (for Container Registry)
- DNS access for dovvybuddy.com domain
- GitHub repository with required secrets configured

---

## Risks & Mitigations

### Risk 1: Cold start latency on Cloud Run

**Likelihood:** High (serverless with minInstances=0)  
**Impact:** Medium (first request slow, poor UX)

**Mitigation:**
- Accept for MVP (cost savings prioritized)
- Monitor cold start frequency and duration
- If problematic: Set minInstances=1 (~$10-15/month)
- Optimize Docker image size (<500MB)

**Acceptance Criteria:**
- Cold starts <5 seconds
- Occur <10% of requests
- Users informed via UI ("Waking up...")

### Risk 2: Database connection pool exhaustion

**Likelihood:** Low (MVP traffic expected to be light)  
**Impact:** High (service unavailable)

**Mitigation:**
- SQLAlchemy connection pool configured (10-20 connections)
- Cloud Run maxInstances=10 caps total connections
- Monitor active connections in logs
- Neon has built-in connection pooling

**Acceptance Criteria:**
- No connection errors in first week
- Pool utilization <70% under normal load

### Risk 3: Cost spike from traffic surge

**Likelihood:** Low (MVP launch, limited audience)  
**Impact:** Medium (unexpected billing)

**Mitigation:**
- Set maxInstances=10 (hard cap)
- Set up billing alerts ($50, $100 thresholds)
- Monitor costs daily in first week
- Cloud Run free tier covers initial traffic

**Acceptance Criteria:**
- Monthly cost <$50 for first month
- No surprise charges

### Risk 4: DNS propagation delay

**Likelihood:** Medium  
**Impact:** Low (users can't access api.dovvybuddy.com)

**Mitigation:**
- Configure DNS 24-48 hours before announcement
- Test with curl/dig before launch
- Have direct Cloud Run URL as backup
- Use low TTL (300s) for quick updates

**Acceptance Criteria:**
- DNS resolves correctly before launch
- SSL certificate valid
- No certificate warnings

### Risk 5: Missing environment variable

**Likelihood:** Medium  
**Impact:** High (service fails to start)

**Mitigation:**
- Use Secret Manager (not inline env vars)
- Test locally with .env file first
- Deployment script validates required secrets exist
- Health check fails if configuration wrong

**Acceptance Criteria:**
- All secrets present in Secret Manager
- Service starts successfully
- Health check passes on first try

---

## Trade-offs

### Trade-off 1: Serverless (minInstances=0) vs Always-On (minInstances=1)

**Chosen:** Serverless (minInstances=0)

**Rationale:**
- MVP traffic expected to be low (<100 sessions/day)
- Cost savings: $0 vs ~$15/month for always-on
- Cold starts acceptable for MVP (users tolerant during early phase)
- Can easily change to minInstances=1 later if needed

**Trade-off:**
- Cold starts (2-5s) on first request after idle period
- May frustrate impatient users

**Decision:** Accept cold starts for MVP. Revisit after observing traffic patterns.

### Trade-off 2: Basic Cloud Run Metrics vs Sentry/DataDog

**Chosen:** Basic Cloud Run metrics only

**Rationale:**
- Cloud Run provides sufficient observability for MVP
- Sentry adds complexity and cost (~$26/month minimum)
- Focus on launching, not perfect monitoring
- Can add Sentry post-launch if error tracking needed

**Trade-off:**
- No automatic error grouping/alerting
- Less detailed performance tracking
- Manual log searching for debugging

**Decision:** Defer advanced monitoring to post-MVP iteration.

### Trade-off 3: Single Region vs Multi-Region

**Chosen:** Single region (us-central1)

**Rationale:**
- MVP serves single market initially
- Multi-region adds complexity (database replication, etc.)
- Cost increase for low traffic doesn't justify HA benefits
- Can migrate to multi-region when scaling globally

**Trade-off:**
- Higher latency for users far from us-central1
- No automatic failover if region has outage

**Decision:** Single region for MVP. Cloud Run has >99.5% uptime SLA.

### Trade-off 4: Manual Deployment vs GitOps

**Chosen:** Manual deployment trigger (workflow_dispatch)

**Rationale:**
- MVP: Manual control prevents accidental production deployments
- Can verify staging/testing before production push
- Simple to understand and execute

**Trade-off:**
- Not automated on every merge to main
- Requires human intervention to deploy

**Decision:** Manual for MVP. Revisit automation when team grows or deployment frequency increases.

---

## Open Questions

### Q1: Should we use Cloud Run first or second generation?

**Context:** Second generation has faster cold starts but may have different pricing

**Options:**
- A) First generation (default, proven)
- B) Second generation (faster cold starts, newer)

**Recommendation:** Option A (first generation) for MVP - stable and well-documented

**Decision:** Use first generation ✅

### Q2: What should minInstances be set to?

**Context:** Balance between cost and cold start avoidance

**Options:**
- A) 0 (serverless, cold starts)
- B) 1 (always warm, ~$15/month)

**Recommendation:** Option A (0) for MVP, monitor and adjust if needed

**Decision:** Start with 0, increase to 1 if cold starts problematic ✅

### Q3: Should we set up staging environment?

**Context:** Could test deployments in staging before production

**Options:**
- A) No staging (deploy directly to production)
- B) Staging environment (separate Cloud Run service)

**Recommendation:** Option A (no staging) for solo MVP - test locally thoroughly

**Decision:** No staging for MVP, use Cloud Run tags if testing needed ✅

---

## Success Criteria

### Technical Success

- [ ] Dockerfile builds successfully locally and in CI
- [ ] GitHub Actions workflow deploys to Cloud Run without errors
- [ ] Cloud Run service accessible at auto-generated URL
- [ ] Custom domain (api.dovvybuddy.com) resolves correctly
- [ ] SSL certificate valid (https://)
- [ ] Health endpoint responds (200 OK)
- [ ] Chat endpoint functional (returns valid response)
- [ ] Session persistence works across requests
- [ ] RAG retrieval returns context chunks
- [ ] CORS configured for frontend domain
- [ ] Environment variables loaded from Secret Manager
- [ ] Logs visible in Cloud Console (structured JSON)
- [ ] Cloud Run metrics show request counts
- [ ] Response times <10s for P95
- [ ] No critical errors in first 24 hours

### Operational Success

- [ ] Deployment runbook documented and tested
- [ ] Rollback procedure documented and tested
- [ ] Smoke test checklist completed
- [ ] DNS propagation verified
- [ ] Backend accessible from frontend (Vercel)
- [ ] Costs within budget (<$50 first month)
- [ ] Monitoring dashboard accessible
- [ ] Logs searchable and structured

### User Success

- [ ] End-to-end user flow works (landing → chat → response)
- [ ] No user-facing errors during launch
- [ ] Response quality maintained vs development
- [ ] Session survives page refresh
- [ ] Cold starts tolerable (<5s, infrequent)

### Business Success

- [ ] MVP publicly accessible
- [ ] Lead capture functional (if PR4 complete)
- [ ] Analytics tracking enabled (if PR6 complete)
- [ ] Partner shops can receive leads
- [ ] Ready for user feedback collection

---

## Next Steps

After PR6.1 is complete (MVP deployed to production):

1. **Monitor production** — Watch metrics for first week
   - Check Cloud Run dashboard daily
   - Review logs for errors
   - Monitor costs
   - Track user feedback

2. **Iterate based on data** — First week learnings
   - If cold starts problematic: Set minInstances=1
   - If error rate high: Add Sentry integration
   - If costs high: Optimize container size
   - If traffic high: Increase maxInstances

3. **PR7: Telegram Integration** (Optional)
   - Build Telegram bot using Python backend
   - Expand reach beyond web-only

4. **PR8: User Authentication** (Optional)
   - Add user accounts and profiles
   - Enable personalization

5. **PR9: Production Polish** (If not done in PR6)
   - Advanced monitoring (Sentry, alerting)
   - Performance optimization
   - E2E testing automation

6. **PR10: Post-Launch Iteration**
   - Content expansion (more destinations)
   - Feature improvements based on user feedback
   - Scaling optimizations

---

## Related Documentation

- **Master Plan:** `/docs/plans/MASTER_PLAN.md`
- **Prerequisite PRs:** PR1-PR6 (especially PR6 - Landing Polish)
- **Backend Implementation:** PR3.2a-PR3.2e summaries in `/docs/project-management/`
- **Next Steps:** `/docs/NEXT_STEPS.md`
- **Cloud Run Docs:** https://cloud.google.com/run/docs
- **GitHub Actions:** https://docs.github.com/actions

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-01 | AI Assistant | Initial draft (migration-focused as PR3.2f) |
| 0.2 | 2026-01-05 | AI Assistant | Revised for MVP deployment (post-migration) |
| 0.3 | 2026-01-05 | AI Assistant | Renamed from PR3.2f to PR6.1 |

---

**Status:** 🟢 Ready — Scheduled after PR6 (Landing Polish)

**Estimated Duration:** 3-5 days  
**Complexity:** Medium  
**Risk Level:** Medium

**Positioning:** This PR should be completed **after PR6 (Landing Polish)** to ensure the landing page and chat interface are production-ready before deploying to the public internet.

---

**END OF PR6.1 PLAN**
