# PR3.2f: Production Deployment & Rollout

**Status:** Draft  
**Parent Epic:** PR3.2 (Python-First Backend Migration)  
**Date:** January 1, 2026  
**Duration:** 2-3 weeks

---

## Goal

Deploy Python backend to Cloud Run, configure production monitoring and logging, execute staged production rollout with rollback capability, and archive TypeScript backend code after successful migration. Complete the Python-first backend migration with production-ready infrastructure.

---

## Scope

### In Scope

- Dockerfile for Python backend (multi-stage, optimized for Cloud Run)
- Cloud Run deployment configuration (staging + production)
- GitHub Actions workflows for backend deployment (CI/CD)
- Sentry SDK integration (Python backend + TypeScript frontend)
- Structured logging (JSON logs to stdout for Cloud Run)
- Cloud Run metrics and monitoring dashboards
- Alerting rules (error rate, latency, CPU, memory)
- DNS configuration (`api.dovvybuddy.com` → Cloud Run)
- SSL/TLS certificate (automatic via Cloud Run)
- Staging environment testing (full E2E)
- Staged production rollout (10% → 50% → 100%)
- Rollback procedures documentation
- Deployment runbook
- Load testing (50+ concurrent users)
- Archive TypeScript backend code (after 1 week stability)

### Out of Scope

- Cost optimization (deferred to post-migration)
- Multi-region deployment (deferred to future scaling)
- Advanced monitoring (Prometheus, Grafana)
- Auto-scaling configuration beyond defaults
- Database migration to Cloud SQL (use existing Postgres for now)

---

## Backend Changes

### New Modules

**Deployment & Infrastructure:**
```
src/backend/
├── Dockerfile                     # Multi-stage Docker build
├── .dockerignore                  # Docker build exclusions
├── cloudbuild.yaml                # Cloud Build configuration (optional)
└── app/
    ├── middleware/
    │   ├── __init__.py
    │   ├── request_id.py          # Request ID middleware
    │   └── logging.py             # Request/response logging
    └── core/
        ├── sentry.py              # Sentry initialization
        └── logging.py             # Structured logging setup

docs/
├── deployment.md                  # Deployment runbook
└── rollback.md                    # Rollback procedures

.github/workflows/
├── deploy-backend-staging.yml     # Deploy to staging
└── deploy-backend-production.yml  # Deploy to production
```

**Key Files:**

1. **Dockerfile** — Multi-stage build
   - Stage 1: Dependencies (pip install)
   - Stage 2: Application (copy code, set entrypoint)
   - Optimizations: minimize layers, use slim base image
   - Non-root user for security
   - Health check endpoint

2. **app/middleware/request_id.py** — Request ID tracking
   - Generate UUID for each request
   - Add to request context
   - Include in all logs
   - Return in response headers

3. **app/core/sentry.py** — Error tracking
   - Initialize Sentry SDK
   - Capture exceptions
   - Add context (request ID, user ID, session ID)
   - Performance monitoring (transactions)

4. **app/core/logging.py** — Structured logging
   - JSON formatter for Cloud Run
   - Log levels (DEBUG, INFO, WARNING, ERROR)
   - Include request ID, timestamp, context
   - Separate logger for each module

### Modified Modules

1. **src/backend/app/main.py** — Production configuration
   - Add request ID middleware
   - Add request/response logging middleware
   - Initialize Sentry (if DSN provided)
   - Configure structured logging
   - Health check returns more details (version, uptime)

2. **src/backend/app/core/config.py** — Production settings
   - `SENTRY_DSN`: Sentry project DSN
   - `SENTRY_ENVIRONMENT`: production | staging | development
   - `SENTRY_TRACES_SAMPLE_RATE`: 0.1 (10% of transactions)
   - `LOG_LEVEL`: INFO (default for production)
   - `LOG_JSON`: true (for Cloud Run)

3. **src/backend/pyproject.toml** — Add dependencies
   - `sentry-sdk[fastapi]>=1.40.0`

---

## Frontend Changes

### Modified Modules

1. **next.config.js** — Production backend URL
   - Update rewrites/redirects for production
   - `BACKEND_URL=https://api.dovvybuddy.com`

2. **.env.production** — Production environment variables
   ```bash
   BACKEND_URL=https://api.dovvybuddy.com
   NEXT_PUBLIC_API_URL=/api
   NEXT_PUBLIC_SENTRY_DSN=<frontend-sentry-dsn>
   ```

3. **src/lib/sentry.ts** — Sentry configuration (if not already present)
   - Initialize Sentry SDK for Next.js
   - Capture errors
   - Add context (user ID, session ID)

---

## Data Changes

None (uses existing database, no schema changes)

---

## Infra / Config

### Docker Configuration

**Dockerfile:**
```dockerfile
# Multi-stage build for Python backend

# Stage 1: Dependencies
FROM python:3.11-slim AS dependencies

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Stage 2: Application
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy installed dependencies from previous stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser alembic/ ./alembic/
COPY --chown=appuser:appuser alembic.ini ./

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**.dockerignore:**
```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.env
.env.*
tests/
*.md
.git/
.github/
.vscode/
*.log
```

### Cloud Run Configuration

**Service Configuration:**
```yaml
# cloud-run-staging.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: dovvybuddy-backend-staging
  labels:
    environment: staging
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: '0'
        autoscaling.knative.dev/maxScale: '5'
    spec:
      containerConcurrency: 80
      timeoutSeconds: 300
      containers:
        - image: gcr.io/PROJECT_ID/dovvybuddy-backend:TAG
          ports:
            - containerPort: 8000
          env:
            - name: ENVIRONMENT
              value: staging
            - name: LOG_LEVEL
              value: DEBUG
          resources:
            limits:
              cpu: '1'
              memory: 512Mi
```

**Production (more resources):**
```yaml
# cloud-run-production.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: dovvybuddy-backend
  labels:
    environment: production
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: '1'  # Always warm
        autoscaling.knative.dev/maxScale: '10'
    spec:
      containerConcurrency: 100
      timeoutSeconds: 300
      containers:
        - image: gcr.io/PROJECT_ID/dovvybuddy-backend:TAG
          ports:
            - containerPort: 8000
          env:
            - name: ENVIRONMENT
              value: production
            - name: LOG_LEVEL
              value: INFO
          resources:
            limits:
              cpu: '2'
              memory: 1Gi
```

### GitHub Actions Workflows

**Deploy to Staging:**
`.github/workflows/deploy-backend-staging.yml`
```yaml
name: Deploy Backend to Staging

on:
  push:
    branches: [main]
    paths:
      - 'src/backend/**'
      - '.github/workflows/deploy-backend-staging.yml'

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}
      
      - name: Configure Docker
        run: gcloud auth configure-docker
      
      - name: Build Docker image
        run: |
          cd src/backend
          docker build -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:${{ github.sha }} .
          docker tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:${{ github.sha }} \
                     gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:staging
      
      - name: Push Docker image
        run: |
          docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:${{ github.sha }}
          docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:staging
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy dovvybuddy-backend-staging \
            --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:${{ github.sha }} \
            --platform managed \
            --region us-central1 \
            --allow-unauthenticated \
            --set-env-vars "DATABASE_URL=${{ secrets.DATABASE_URL_STAGING }}" \
            --set-env-vars "GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}" \
            --set-env-vars "GROQ_API_KEY=${{ secrets.GROQ_API_KEY }}" \
            --set-env-vars "SENTRY_DSN=${{ secrets.SENTRY_DSN_BACKEND }}" \
            --set-env-vars "ENVIRONMENT=staging" \
            --set-env-vars "CORS_ORIGINS=https://staging.dovvybuddy.com"
      
      - name: Run smoke tests
        run: |
          STAGING_URL=$(gcloud run services describe dovvybuddy-backend-staging --region us-central1 --format 'value(status.url)')
          curl -f $STAGING_URL/health || exit 1
```

**Deploy to Production (manual trigger):**
`.github/workflows/deploy-backend-production.yml`
```yaml
name: Deploy Backend to Production

on:
  workflow_dispatch:
    inputs:
      tag:
        description: 'Git tag to deploy'
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.inputs.tag }}
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}
      
      - name: Configure Docker
        run: gcloud auth configure-docker
      
      - name: Build Docker image
        run: |
          cd src/backend
          docker build -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:${{ github.event.inputs.tag }} .
          docker tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:${{ github.event.inputs.tag }} \
                     gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:production
      
      - name: Push Docker image
        run: |
          docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:${{ github.event.inputs.tag }}
          docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:production
      
      - name: Deploy to Cloud Run (0% traffic initially)
        run: |
          gcloud run deploy dovvybuddy-backend \
            --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/dovvybuddy-backend:${{ github.event.inputs.tag }} \
            --platform managed \
            --region us-central1 \
            --allow-unauthenticated \
            --no-traffic \
            --tag v${{ github.event.inputs.tag }} \
            --set-env-vars "DATABASE_URL=${{ secrets.DATABASE_URL_PRODUCTION }}" \
            --set-env-vars "GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}" \
            --set-env-vars "GROQ_API_KEY=${{ secrets.GROQ_API_KEY }}" \
            --set-env-vars "SENTRY_DSN=${{ secrets.SENTRY_DSN_BACKEND }}" \
            --set-env-vars "ENVIRONMENT=production" \
            --set-env-vars "CORS_ORIGINS=https://dovvybuddy.com" \
            --min-instances 1 \
            --max-instances 10
      
      - name: Run smoke tests
        run: |
          REVISION_URL=$(gcloud run services describe dovvybuddy-backend --region us-central1 --format 'value(status.traffic[0].url)')
          curl -f $REVISION_URL/health || exit 1
      
      - name: Update traffic (10%)
        run: |
          gcloud run services update-traffic dovvybuddy-backend \
            --region us-central1 \
            --to-tags v${{ github.event.inputs.tag }}=10
```

### Environment Variables (Production)

**Backend (Cloud Run):**
```bash
DATABASE_URL=<production-postgres-url>
GEMINI_API_KEY=<gemini-api-key>
GROQ_API_KEY=<groq-api-key>
SENTRY_DSN=<backend-sentry-dsn>
ENVIRONMENT=production
LOG_LEVEL=INFO
LOG_JSON=true
CORS_ORIGINS=https://dovvybuddy.com
DEFAULT_LLM_PROVIDER=groq
DEFAULT_LLM_MODEL=gemini-2.0-flash
ENABLE_RAG=true
SESSION_EXPIRY_HOURS=24
```

**Frontend (Vercel):**
```bash
BACKEND_URL=https://api.dovvybuddy.com
NEXT_PUBLIC_API_URL=/api
NEXT_PUBLIC_SENTRY_DSN=<frontend-sentry-dsn>
```

### DNS Configuration

**Setup:**
1. Create Cloud Run service: `dovvybuddy-backend`
2. Get Cloud Run URL: `https://dovvybuddy-backend-<hash>-uc.a.run.app`
3. Create DNS A/AAAA records:
   - `api.dovvybuddy.com` → Cloud Run URL (via Cloud DNS or domain registrar)
4. Map custom domain in Cloud Run:
   ```bash
   gcloud run domain-mappings create \
     --service dovvybuddy-backend \
     --domain api.dovvybuddy.com \
     --region us-central1
   ```
5. SSL certificate provisioned automatically by Cloud Run

### Monitoring & Alerting

**Sentry Configuration:**
- Create 2 Sentry projects: backend, frontend
- Configure error tracking, performance monitoring
- Set up alerts: error rate >5%, P95 latency >10s

**Cloud Run Metrics:**
- Request count (requests/sec)
- Latency (P50, P95, P99)
- Error rate (5xx responses)
- CPU utilization
- Memory utilization
- Instance count (active instances)

**Alerting Rules (Cloud Monitoring):**
```yaml
# Error rate alert
- name: High error rate
  condition: error_rate > 0.05  # 5%
  duration: 5 minutes
  notification: email, Slack
  severity: critical

# Latency alert
- name: High latency
  condition: p95_latency > 10s
  duration: 5 minutes
  notification: email, Slack
  severity: warning

# CPU alert
- name: High CPU usage
  condition: cpu_utilization > 0.8  # 80%
  duration: 10 minutes
  notification: email
  severity: warning

# Memory alert
- name: High memory usage
  condition: memory_utilization > 0.9  # 90%
  duration: 10 minutes
  notification: email
  severity: critical
```

---

## Testing

### Staging Environment Testing

**Pre-Production Checklist:**

1. **Deploy to staging:**
   - Push to main branch (triggers staging deployment)
   - Verify deployment successful: `gcloud run services describe dovvybuddy-backend-staging`
   - Verify health check: `curl https://staging-api.dovvybuddy.com/health`

2. **Run smoke tests:**
   - POST /api/chat with test query
   - GET /api/session/{id}
   - Verify responses correct
   - Check logs in Cloud Run

3. **Run full E2E test suite:**
   - Update frontend staging environment: `BACKEND_URL=https://staging-api.dovvybuddy.com`
   - Deploy frontend to Vercel preview
   - Run E2E tests (manual or Playwright)
   - Test all user flows (certification, trip, safety queries)

4. **Load testing:**
   ```bash
   # Using k6
   k6 run --vus 50 --duration 5m tests/load/chat-endpoint.js
   ```
   - Target: 50 concurrent users for 5 minutes
   - Verify P95 latency <5s
   - Verify error rate <1%
   - Verify auto-scaling works (instances scale up/down)

5. **Monitor metrics:**
   - Cloud Run dashboard (request rate, latency, errors)
   - Sentry dashboard (error tracking)
   - Structured logs (search for errors)

### Load Testing

**k6 Script (`tests/load/chat-endpoint.js`):**
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 10 },  // Ramp up
    { duration: '5m', target: 50 },  // Steady state
    { duration: '2m', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<5000'],  // 95% <5s
    http_req_failed: ['rate<0.01'],     // Error rate <1%
  },
};

const BASE_URL = __ENV.BASE_URL || 'https://api.dovvybuddy.com';

export default function () {
  const payload = JSON.stringify({
    message: 'What is PADI Open Water certification?',
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  let response = http.post(`${BASE_URL}/api/chat`, payload, params);

  check(response, {
    'status is 200': (r) => r.status === 200,
    'response has sessionId': (r) => JSON.parse(r.body).sessionId !== undefined,
    'response has message': (r) => JSON.parse(r.body).response.length > 0,
  });

  sleep(1);  // Think time
}
```

**Run load test:**
```bash
k6 run --env BASE_URL=https://staging-api.dovvybuddy.com tests/load/chat-endpoint.js
```

### Rollback Testing

**Practice rollback in staging:**

1. Deploy version A (current)
2. Deploy version B (new) with 100% traffic
3. Simulate issue (introduce bug, stop backend, etc.)
4. Execute rollback:
   ```bash
   gcloud run services update-traffic dovvybuddy-backend-staging \
     --region us-central1 \
     --to-revisions PREVIOUS_REVISION=100
   ```
5. Verify rollback successful (version A serving traffic)
6. Measure rollback time (<1 minute)

---

## Verification

### Commands

```bash
# Build Docker image locally
cd src/backend
docker build -t dovvybuddy-backend:local .
docker run -p 8000:8000 --env-file .env dovvybuddy-backend:local

# Deploy to staging (via GitHub Actions or manual)
git push origin main  # Triggers staging deployment

# Deploy to production (manual workflow)
# 1. Create Git tag
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0

# 2. Trigger workflow in GitHub Actions UI
# Workflow: deploy-backend-production
# Input: tag = v1.0.0

# Check deployment status
gcloud run services describe dovvybuddy-backend --region us-central1

# View logs
gcloud run logs read dovvybuddy-backend --region us-central1 --limit 50

# Update traffic split
gcloud run services update-traffic dovvybuddy-backend \
  --region us-central1 \
  --to-tags v1.0.0=50

# Rollback
gcloud run services update-traffic dovvybuddy-backend \
  --region us-central1 \
  --to-revisions PREVIOUS_REVISION=100
```

### Production Rollout Checklist

**Phase 0: Pre-Rollout (Week -1)**

- [ ] All previous PRs merged (PR3.2a-PR3.2e)
- [ ] Staging environment deployed and tested
- [ ] Load testing passed (50 concurrent users, P95 <5s)
- [ ] Monitoring configured (Sentry, Cloud Run metrics)
- [ ] Alerting rules created
- [ ] DNS configured (`api.dovvybuddy.com`)
- [ ] SSL certificate provisioned
- [ ] Rollback procedure documented and tested
- [ ] Team briefed on rollout plan

**Phase 1: Initial Deployment (Day 1, 0% traffic)**

- [ ] Deploy to production Cloud Run (--no-traffic)
- [ ] Verify health check passes
- [ ] Run smoke tests against new revision
- [ ] Check logs for errors
- [ ] Verify Sentry capturing events
- [ ] Wait 1 hour, monitor metrics

**Phase 2: Canary Rollout (Day 1, 10% traffic)**

- [ ] Update traffic split: 10% → new revision, 90% → TypeScript (if dual deployment)
- [ ] Monitor for 4-6 hours:
  - [ ] Error rate <1%
  - [ ] Latency P95 <5s
  - [ ] No critical Sentry errors
  - [ ] Cloud Run metrics stable
- [ ] Manual spot checks: Test 10+ user scenarios
- [ ] Rollback trigger: Error rate >5% or latency >10s
- [ ] If healthy, proceed to Phase 3

**Phase 3: 50% Rollout (Day 2)**

- [ ] Update traffic split: 50% → new revision
- [ ] Monitor for 12-24 hours:
  - [ ] Error rate <1%
  - [ ] Latency P95 <5s
  - [ ] No increase in user-reported issues
  - [ ] Database connection pool stable
- [ ] Manual spot checks: Test 20+ user scenarios
- [ ] Rollback trigger: Same as Phase 2
- [ ] If healthy, proceed to Phase 4

**Phase 4: Full Rollout (Day 3-4)**

- [ ] Update traffic split: 100% → new revision
- [ ] Monitor for 24-48 hours:
  - [ ] Error rate <1%
  - [ ] Latency P95 <5s
  - [ ] No critical user-reported issues
  - [ ] All metrics stable
- [ ] Deprecate TypeScript backend (stop serving traffic)
- [ ] Keep TypeScript backend code (for rollback)
- [ ] Rollback trigger: Same as Phase 2

**Phase 5: Cleanup (Week 2)**

- [ ] 1 week stability confirmed (no critical errors)
- [ ] Archive TypeScript backend code:
  - [ ] Create `archive/typescript-backend` branch
  - [ ] Move `src/lib/orchestration/`, `src/lib/agent/`, etc. to archive
  - [ ] Update README with migration notes
  - [ ] Keep Drizzle migrations (historical reference)
- [ ] Update CI/CD (remove TypeScript backend jobs)
- [ ] Update documentation
- [ ] Celebrate migration complete! 🎉

---

## Rollback Plan

### Automatic Rollback (Cloud Run)

**Scenario:** New revision has critical errors

**Procedure:**
```bash
# Revert to previous revision (execution time: <1 minute)
gcloud run services update-traffic dovvybuddy-backend \
  --region us-central1 \
  --to-revisions PREVIOUS_REVISION=100

# Or rollback to specific revision
gcloud run services update-traffic dovvybuddy-backend \
  --region us-central1 \
  --to-revisions dovvybuddy-backend-00005-abc=100
```

**Verification:**
- Check Cloud Run dashboard (traffic shifted)
- Test /api/chat endpoint
- Monitor error rate (should drop)

### Manual Rollback (Frontend)

**Scenario:** Need to revert frontend to call TypeScript backend

**Procedure:**
1. Update Vercel environment variable: `BACKEND_URL=<internal>` (empty or `/api`)
2. Redeploy frontend (automatic on Vercel, <2 minutes)
3. Verify frontend calls TypeScript backend (check network tab)

**Execution time:** <5 minutes

### Database Rollback

**Not needed.** Schema unchanged, data compatible with both backends.

### Rollback Triggers

**Automatic (if monitoring configured):**
- Error rate >5% sustained for 15 minutes
- Latency P95 >10s sustained for 15 minutes

**Manual:**
- Critical user-reported bugs
- Database connection exhaustion
- Unexpected behavior (data corruption, security issue)

---

## Dependencies

### PRs that must be merged

- ✅ **PR3.2a** (Backend Foundation)
- ✅ **PR3.2b** (Core Services)
- ✅ **PR3.2c** (Agent Orchestration)
- ✅ **PR3.2d** (Content Scripts)
- ✅ **PR3.2e** (Frontend Integration)

### External Dependencies

- Google Cloud Platform account with billing enabled
- Cloud Run API enabled
- Container Registry enabled
- DNS access (dovvybuddy.com)
- Sentry account (2 projects: backend, frontend)
- GitHub repository with secrets configured:
  - `GCP_SA_KEY`: Service account key (JSON)
  - `GCP_PROJECT_ID`: GCP project ID
  - `DATABASE_URL_STAGING`: Staging database URL
  - `DATABASE_URL_PRODUCTION`: Production database URL
  - `GEMINI_API_KEY`: Gemini API key
  - `GROQ_API_KEY`: Groq API key
  - `SENTRY_DSN_BACKEND`: Backend Sentry DSN
  - `SENTRY_DSN_FRONTEND`: Frontend Sentry DSN

---

## Risks & Mitigations

### Risk 1: Cold start latency on Cloud Run

**Likelihood:** Medium  
**Impact:** Medium (first request slow, poor UX)

**Mitigation:**
- Configure min instances: 1-2 in production (always warm)
- Optimize Docker image size (<500MB)
- Monitor cold start frequency and duration
- Consider Cloud Run second generation (faster cold starts)

**Acceptance Criteria:**
- Cold starts <3 seconds (if they occur)
- P95 latency <5s (including cold starts)
- Min instances prevent most cold starts

### Risk 2: Traffic split misconfigured (100% to Python too early)

**Likelihood:** Low  
**Impact:** High (widespread issues if Python backend broken)

**Mitigation:**
- Document exact traffic split percentages
- Require manual approval for traffic increases
- Monitor metrics at each stage (4-24 hours)
- Set conservative rollback thresholds

**Acceptance Criteria:**
- Traffic split follows plan (10% → 50% → 100%)
- Monitoring windows respected
- No traffic increase without metric validation

### Risk 3: Database connection pool exhaustion

**Likelihood:** Medium  
**Impact:** High (backend crashes, service unavailable)

**Mitigation:**
- Load test with realistic concurrency (50+ users)
- Configure appropriate pool size (10-20 connections)
- Monitor active connections in Cloud Run
- Set max instances limit (10) to cap connections

**Acceptance Criteria:**
- Connection pool never exhausted during load test
- Active connections monitored
- Graceful degradation if pool full (503 errors, not crashes)

### Risk 4: Cost spike from auto-scaling

**Likelihood:** Medium  
**Impact:** Medium (unexpected bills)

**Mitigation:**
- Set max instances limit (10)
- Monitor costs daily during rollout
- Set budget alerts in GCP ($100/month initial)
- Review cost after first week

**Acceptance Criteria:**
- Monthly cost within budget (<$100 for V1 traffic)
- No unexpected charges
- Cost per request acceptable (<$0.01)

### Risk 5: DNS propagation delay

**Likelihood:** Low  
**Impact:** Low (users can't access api.dovvybuddy.com)

**Mitigation:**
- Update DNS 24-48 hours before cutover
- Test with hosts file override first
- Verify DNS propagation (dig, nslookup)
- Communicate expected downtime (if any)

**Acceptance Criteria:**
- DNS resolves to Cloud Run URL
- SSL certificate valid
- No DNS errors in production

### Risk 6: Monitoring blind spots

**Likelihood:** Medium  
**Impact:** High (miss critical issues during rollout)

**Mitigation:**
- Configure all alerting rules before rollout
- Test alerts (send test events to Sentry)
- Monitor dashboards manually during rollout
- Set up Slack notifications for critical alerts

**Acceptance Criteria:**
- Alerts fire correctly (tested)
- Dashboards show all key metrics
- Manual monitoring schedule followed

---

## Trade-offs

### Trade-off 1: Cloud Run vs Railway/Render

**Chosen:** Cloud Run (Google Cloud)

**Rationale:**
- Better auto-scaling (serverless)
- Google ecosystem integration (Gemini, Vertex AI)
- Production-grade reliability
- Better observability (Cloud Monitoring)

**Trade-off:**
- More complex setup (GCP account, IAM, etc.)
- Cold starts (mitigated with min instances)
- Higher cost for always-on (min instances)

**Decision:** Accept trade-off. Cloud Run better for long-term scaling.

### Trade-off 2: Min Instances (0 vs 1 vs 2)

**Chosen:** 1 instance in production

**Rationale:**
- Balance between cost and performance
- Eliminates most cold starts (<3s first request)
- Cost: ~$30-50/month for 1 instance always-on

**Trade-off:**
- Higher cost vs 0 min instances (serverless)
- Not HA (single instance failure → cold start)

**Decision:** 1 instance for V1, revisit if traffic increases.

### Trade-off 3: Gradual Rollout (10-50-100) vs Big Bang

**Chosen:** Gradual rollout (10% → 50% → 100%)

**Rationale:**
- Lower risk (catch issues early)
- Easier rollback (less user impact)
- Build confidence with monitoring

**Trade-off:**
- Slower rollout (3-4 days vs 1 day)
- Dual backend maintenance during rollout
- More complex traffic management

**Decision:** Accept trade-off. Risk mitigation worth extra time.

### Trade-off 4: Archive TypeScript Backend vs Keep Forever

**Chosen:** Archive after 1 week stability

**Rationale:**
- Clean up codebase (reduce maintenance burden)
- Keep in Git history (rollback if needed)
- Clear signal: migration complete

**Trade-off:**
- Harder rollback after archive (must un-archive)
- Risk if Python backend has long-tail issues

**Decision:** Archive after 1 week (reasonable safety window).

---

## Open Questions

### Q1: What is minimum instance count for production?

**Context:** Balance cost vs cold start latency

**Options:**
- A) 0 instances (serverless, cold starts)
- B) 1 instance (always warm, ~$30-50/month)
- C) 2 instances (higher availability, ~$60-100/month)

**Recommendation:** Option B (1 instance) for V1

**Decision:** Option B ✅

### Q2: Should we implement blue-green deployment?

**Context:** More complex but safer than traffic splitting

**Options:**
- A) Traffic splitting (current plan)
- B) Blue-green (two full environments)

**Recommendation:** Option A (traffic splitting sufficient for V1)

**Decision:** Option A ✅

### Q3: When should we archive TypeScript backend code?

**Context:** Balance between rollback safety and codebase cleanliness

**Options:**
- A) Immediately after 100% cutover
- B) After 1 week stability
- C) After 1 month (very conservative)

**Recommendation:** Option B (1 week)

**Decision:** Option B ✅

### Q4: Should we run both backends in parallel permanently?

**Context:** Some companies keep old and new for fallback

**Options:**
- A) Deprecate TypeScript backend after rollout (planned)
- B) Keep both running permanently (fallback)

**Recommendation:** Option A (Python-only after migration)

**Decision:** Option A ✅

---

## Success Criteria

### Technical Success

- [ ] Docker image builds successfully
- [ ] Staging deployment successful
- [ ] Load testing passed (50 users, P95 <5s, error rate <1%)
- [ ] Production deployment successful (0% traffic initially)
- [ ] Traffic split configured correctly (10% → 50% → 100%)
- [ ] Monitoring dashboards show healthy metrics
- [ ] Alerting rules fire correctly (tested)
- [ ] Rollback tested successfully
- [ ] 100% traffic cutover completed
- [ ] No critical errors for 1 week
- [ ] TypeScript backend archived

### Operational Success

- [ ] DNS configured (`api.dovvybuddy.com` → Cloud Run)
- [ ] SSL certificate valid
- [ ] Sentry capturing errors
- [ ] Logs structured and searchable
- [ ] Deployment runbook followed
- [ ] Rollback procedure documented and tested
- [ ] Cost within budget (<$100/month)

### User Success

- [ ] No user-facing disruptions during rollout
- [ ] Response quality maintained (manual spot checks)
- [ ] Latency acceptable (<5s P95)
- [ ] No increase in user-reported issues
- [ ] Zero data loss

### Team Success

- [ ] Deployment process documented (runbook)
- [ ] Monitoring dashboards accessible
- [ ] Alerting configured (Slack, email)
- [ ] Rollback procedure clear and tested
- [ ] Migration complete (Python-only backend)
- [ ] Lessons learned documented

---

## Next Steps

After PR3.2f is merged and rollout complete:

1. **Monitor production:** Watch metrics for 2-4 weeks, optimize as needed
2. **Cost analysis:** Review Cloud Run costs, optimize if needed (reduce min instances if low traffic)
3. **Performance tuning:** Profile hot paths, optimize if bottlenecks found
4. **Documentation:** Update main README with Python backend architecture
5. **Celebrate!** 🎉 Python migration complete
6. **PR7b:** Implement Telegram bot using Python backend
7. **PR5:** Build new chat UI (now using Python backend)

---

## Related Documentation

- **Parent Epic:** `/docs/plans/PR3.2-Python-Backend-Migration.md`
- **Previous PRs:** PR3.2a-PR3.2e
- **Cloud Run Docs:** https://cloud.google.com/run/docs
- **Sentry FastAPI:** https://docs.sentry.io/platforms/python/guides/fastapi/
- **k6 Load Testing:** https://k6.io/docs/

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2026-01-01 | AI Assistant | Initial draft |

---

**Status:** 🟡 Draft — Ready after PR3.2a-PR3.2e complete

**Estimated Duration:** 2-3 weeks  
**Complexity:** High  
**Risk Level:** Medium-High

---

**END OF PR3.2f PLAN**
