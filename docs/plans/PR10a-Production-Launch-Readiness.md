# PR10a: Production Launch Readiness (Polish & Observability)

**Branch Name:** `feature/pr10a-production-launch`  
**Status:** Planned  
**Date:** December 29, 2025  
**Based on:** MASTER_PLAN.md (Phase 4), DovvyBuddy-PSD-V6.2.md

---

## 1. Feature/Epic Summary

### Objective

Transform DovvyBuddy from a feature-complete web application into a production-ready, observable, and polished product ready for public launch. This epic focuses on operational excellence, user experience refinement, performance optimization, comprehensive testing, and real-time monitoring—ensuring the application is stable, fast, and maintainable under real-world usage.

### User Impact

**Primary Users (Divers):**
- **All Users:** Experience faster response times (<5s chat responses) and polished, professional UI/UX.
- **Mobile Users:** Benefit from optimized bundle sizes and responsive design refinements.
- **First-Time Visitors:** See clear value proposition with improved landing page content and CTAs.
- **Returning Users:** Notice improved reliability and graceful error handling.

**Secondary Impact:**
- **Partner Shops:** Confidence that lead delivery is reliable and monitored (delivery tracking + alerts).
- **Product Team:** Real-time visibility into user behavior, technical health, and business metrics (session starts, lead conversions, error rates, response latency).
- **Operations:** Proactive error detection and debugging capabilities via structured logging and error monitoring.

### Dependencies

**Upstream (Must be complete):**
- **PR1-PR6:** Full V1 functionality (database, RAG, model provider, lead capture, chat interface, landing page).
- **PR7a-PR7c (Optional):** Telegram integration (if completed, include in testing scope).
- **PR9a-PR9c (Optional):** User authentication (if completed, include in testing scope and analytics events).

**External Dependencies:**
- **Analytics Provider:** Posthog (preferred) or Vercel Analytics (fallback) for event tracking.
- **Error Monitoring:** Sentry.io for error tracking, alerting, and performance monitoring.
- **Database:** Production Postgres instance (Neon/Supabase) with connection pooling and read replicas (if needed).
- **CDN/Hosting:** Vercel production environment with appropriate tier for expected traffic.

### Assumptions

- **Assumption:** V1 core features (chat, RAG, lead capture) are functionally complete and tested at feature level.
- **Assumption:** Content corpus (certification guides, 1 destination, 5-10 sites) is curated and ready for production ingestion.
- **Assumption:** Performance targets: <5s chat response time (p95), <3s landing page load (LCP), <100ms API response (non-LLM endpoints).
- **Assumption:** Traffic estimates: 10-100 sessions/day initially, scaling to 500/day within 3 months.
- **Assumption:** Manual smoke testing checklist is acceptable for V1 launch; full automated E2E suite deferred to post-launch optimization.
- **Assumption:** Production environment variables (API keys, database URLs, secrets) are managed via Vercel dashboard or secure vault.
- **Assumption:** Launch strategy is phased: soft launch (limited audience) → monitoring period → public announcement.
- **Assumption:** Rollback plan exists: Vercel allows instant rollback to previous deployment; database migrations are backward-compatible.

---

## 2. Complexity & Fit

### Classification

**Multi-PR** (3 PRs recommended)

### Rationale

**Why Multi-PR:**
- **Multiple independent workstreams:** Observability (analytics + monitoring), performance optimization (frontend + backend), and E2E testing/content review each have different testing needs and can be developed in parallel.
- **Risk isolation:** Performance optimizations (bundle splitting, caching) carry risk of breaking existing behavior; separate PR allows focused testing.
- **Deployment sequencing:** Analytics/monitoring should go live first to capture data during performance optimization and testing phases.
- **Solo founder efficiency:** Breaking into smaller PRs allows progress checkpoints and reduces cognitive load for comprehensive testing.
- **Rollback granularity:** If analytics integration has issues, can roll back without losing performance improvements.

**Recommended PR Count:** 3 PRs
1. **PR10a:** Observability & Monitoring (Analytics + Error Tracking + Logging)
2. **PR10b:** Performance Optimization & Content Polish (Bundle size, Caching, Content review, UI refinements)
3. **PR10c:** E2E Testing & Launch Checklist (Playwright smoke tests, Manual checklist, Production deployment validation)

**Estimated Complexity:**
- Backend: Medium (Logging infrastructure, error handling improvements, performance profiling)
- Frontend: Medium (Analytics instrumentation, bundle optimization, UI polish)
- Data: Low (Content review and refinement, no schema changes)
- Infra: Medium-High (Production environment setup, monitoring dashboards, alerting rules)

---

## 3. Full-Stack Impact

### Frontend

**Pages/Components Impacted:**
- **All Existing Pages:** Add analytics event tracking (page views, interactions).
- `/app/page.tsx` (Landing):
  - Content refinement (headline, value proposition, social proof, CTAs).
  - Performance optimization (image lazy loading, font optimization).
  - Analytics: Track CTA clicks ("Start Chat"), scroll depth.
- `/app/chat/page.tsx`:
  - UI polish (loading states, error messages, empty states).
  - Analytics: Track message sent, response received, lead form opened, lead submitted.
  - Performance: Optimize re-renders, debounce input.
- **Error Boundaries:**
  - Add React Error Boundaries to gracefully handle component failures.
  - Log errors to Sentry with component stack traces.

**New UI States Required:**
- **Global Error State:** Friendly fallback UI when critical errors occur (with retry and "Report Issue" options).
- **Performance Budget Warnings:** Alerts during development if bundle size exceeds thresholds.

**Navigation/Entry Points:**
- No new navigation; existing routes remain unchanged.
- Add footer with links: About, FAQ, Privacy Policy, Terms of Service (pages created as static content).

### Backend

**APIs to Add/Modify:**
- **Existing `/api/chat` (Modify):**
  - Add structured logging for every request (session ID, message length, RAG retrieval time, LLM call time, total response time).
  - Add Sentry breadcrumbs for debugging failed requests.
  - Add performance monitoring (trace LLM call duration, DB query duration).
- **Existing `/api/lead` (Modify):**
  - Add delivery confirmation tracking (log email send success/failure).
  - Add Sentry error capture for failed lead deliveries with alerting.
- **New `/api/health` (Add):**
  - Health check endpoint for uptime monitoring (checks DB connection, external API availability).
  - Returns: `{ status: 'ok' | 'degraded' | 'down', checks: { db, llm, email } }`.
- **New `/api/metrics` (Add, Internal Only):**
  - Expose key metrics for dashboards (session count, lead count, error rate, avg response time).
  - Protected by internal API key (not publicly accessible).

**Services/Modules Impacted:**
- **Logging Service (New `src/lib/logging/`):**
  - Structured logger using Pino or Winston.
  - Log levels: ERROR, WARN, INFO, DEBUG.
  - Contextual logging (attach session ID, user ID if authenticated, request ID).
- **Error Handling Middleware:**
  - Centralized error handler for API routes (consistent error responses, Sentry integration).
- **Performance Monitoring:**
  - Instrument key code paths with timing metrics (RAG retrieval, LLM calls, DB queries).

**Validation/Auth/Error-Handling Concerns:**
- Ensure all API endpoints have proper error handling and return structured JSON errors.
- Add rate limiting to prevent abuse (use Vercel rate limiting or Upstash Redis).
- Validate environment variables at startup (fail fast if critical vars missing).

### Data

**No Schema Changes.**

**Data Operations:**
- **Content Review & Refinement:**
  - Audit all markdown content in `content/` for accuracy, tone, and completeness.
  - Ensure safety disclaimers are present in all relevant content.
  - Verify certification pathway content is up-to-date with PADI/SSI 2025 standards.
- **Content Ingestion (Re-run):**
  - Re-run `pnpm content:ingest` with final polished content to production database.
  - Verify vector embeddings are correctly stored and retrievable.
- **Seed Data Validation:**
  - Verify seed data (destinations, dive sites, partner shops) matches production requirements.
  - Ensure all partner shop contact information is accurate.

**Migrations/Backfills:**
- None required (observability tables can be added in future if needed for analytics storage).

**Compatibility Strategy:**
- N/A (no breaking data changes).

### Infra / Config

**Environment Variables (Add to `.env.example` and Production):**
- `SENTRY_DSN` — Sentry project DSN for error tracking.
- `SENTRY_AUTH_TOKEN` — Token for uploading source maps (optional, improves error debugging).
- `POSTHOG_API_KEY` — Posthog project API key for analytics (if using Posthog).
- `POSTHOG_HOST` — Posthog instance URL (default: https://app.posthog.com).
- `INTERNAL_METRICS_API_KEY` — Secret key for accessing `/api/metrics` endpoint.
- `NODE_ENV` — Set to `production` in production environment.
- `VERCEL_ENV` — Auto-set by Vercel (production/preview/development).
- `ENABLE_ANALYTICS` — Feature flag to toggle analytics (true/false, default: true in production).

**Feature Flags:**
- `ENABLE_ANALYTICS` — Control analytics event tracking (enable in production, disable in dev for testing).
- `ENABLE_E2E_MODE` — Mock external services for E2E tests (LLM, email).

**CI/CD Additions:**
- **Production Deployment Workflow:**
  - Add GitHub Actions workflow for production deployments (already handled by Vercel, but add smoke test step post-deploy).
- **Performance Budgets:**
  - Add Lighthouse CI to fail builds if performance thresholds not met (LCP >3s, FCP >1.8s, TTI >3.5s).
- **Bundle Size Monitoring:**
  - Add bundle size checks in CI (fail if JavaScript bundle exceeds 500KB gzipped).

**Monitoring Dashboards:**
- **Sentry Dashboard:** Error rates, performance metrics, release tracking.
- **Posthog Dashboard:** User behavior funnels (Landing → Chat → Lead), session duration, feature usage.
- **Vercel Analytics:** Core Web Vitals (LCP, FID, CLS), page load times, traffic sources.

**Alerting Rules:**
- **Sentry Alerts:**
  - Critical: Error rate >5% over 5 minutes → notify via email/Slack.
  - Warning: New error type introduced → notify.
  - Warning: Lead delivery failure → immediate notification.
- **Uptime Monitoring (UptimeRobot or Vercel):**
  - Ping `/api/health` every 5 minutes.
  - Alert if down for >2 consecutive checks.

---

## 4. PR Roadmap (Multi-PR Plan)

### PR10a: Observability & Monitoring Infrastructure

#### Goal

Establish real-time visibility into application health, user behavior, and business metrics to enable data-driven decisions and proactive incident response post-launch.

#### Scope

**In scope:**
- Install and configure Sentry for error tracking and performance monitoring.
- Install and configure Posthog for product analytics and event tracking.
- Implement structured logging service (`src/lib/logging/`).
- Instrument key user events (page views, chat interactions, lead submissions).
- Create `/api/health` endpoint for uptime monitoring.
- Create `/api/metrics` endpoint for internal dashboards (protected).
- Set up Sentry dashboard with key metrics (error rate, performance, releases).
- Set up Posthog dashboard with user funnels (Landing → Chat → Lead).
- Configure alerting rules for critical errors and lead delivery failures.
- Add logging to all API routes (request/response, timing, errors).
- Document monitoring strategy and dashboard locations in `docs/references/MONITORING.md`.

**Out of scope:**
- Performance optimizations (handled in PR9b).
- E2E testing (handled in PR9c).
- UI/UX polish (handled in PR9b).
- Content review (handled in PR9b).

#### Backend Changes

**APIs to Modify:**
- `POST /api/chat` — Add structured logging, Sentry breadcrumbs, performance traces.
- `POST /api/lead` — Add lead delivery tracking, Sentry error capture.
- `POST /api/session/new` — Add session creation logging.
- All API routes — Wrap with error handling middleware that logs to Sentry.

**APIs to Add:**
- `GET /api/health` — Health check (DB + LLM + Email connectivity).
- `GET /api/metrics` — Internal metrics endpoint (protected by API key).

**New Services/Modules:**
- `src/lib/logging/logger.ts` — Structured logger (Pino) with contextual fields.
- `src/lib/logging/middleware.ts` — Request logging middleware for API routes.
- `src/lib/monitoring/sentry.ts` — Sentry initialization and error capture utilities.
- `src/lib/monitoring/analytics.ts` — Posthog event tracking wrapper.

**Error Handling:**
- Create centralized error handler middleware (`src/lib/errors/handler.ts`).
- Define error types with appropriate HTTP codes and user-facing messages.
- Capture all errors in Sentry with full context (session ID, stack trace).

#### Frontend Changes

**Components to Create:**
- `src/components/ErrorBoundary.tsx` — React Error Boundary with Sentry integration.

**Instrumentation (All existing pages):**
- `/app/page.tsx` (Landing):
  - Track: Page view, "Start Chat" CTA click.
- `/app/chat/page.tsx`:
  - Track: Message sent, Response received, Lead form opened, Lead form submitted, Session created, Error displayed.
- Add Posthog `<PostHogProvider>` to `app/layout.tsx`.
- Capture user properties: Session ID, Is authenticated (if PR9 complete).

**Error Boundaries:**
- Wrap `app/layout.tsx` with top-level ErrorBoundary.
- Wrap `/app/chat/page.tsx` with chat-specific ErrorBoundary (allows retry without full page reload).

#### Data Changes

**No schema changes.**

**Logging Output:**
- Logs written to stdout (captured by Vercel).
- Structured JSON format for easy parsing.
- Include: timestamp, level, message, context (sessionId, userId, requestId).

#### Infra / Config

**Environment Variables:**
- `SENTRY_DSN` (required in production)
- `SENTRY_AUTH_TOKEN` (optional, for source maps)
- `POSTHOG_API_KEY` (required in production)
- `POSTHOG_HOST` (default: https://app.posthog.com)
- `INTERNAL_METRICS_API_KEY` (generate secure random string)
- `ENABLE_ANALYTICS` (feature flag, default: true)

**Sentry Setup:**
- Create Sentry project (Next.js platform).
- Configure source maps upload (via Sentry Webpack plugin).
- Set up release tracking (tag releases with git commit SHA).
- Configure breadcrumbs for user actions.

**Posthog Setup:**
- Create Posthog project.
- Define key events:
  - `page_view` (page, referrer)
  - `chat_message_sent` (sessionId, messageLength)
  - `chat_response_received` (sessionId, responseTime, ragRetrievalTime, llmCallTime)
  - `lead_form_opened` (sessionId, leadType)
  - `lead_submitted` (sessionId, leadType, leadId)
  - `error_occurred` (errorType, errorMessage, page)
- Create funnel: Landing → Chat → Lead Submit.

**Alerting:**
- Sentry: Email/Slack alert for error rate >5% over 5 minutes.
- Sentry: Email alert for lead delivery failure (any occurrence).
- UptimeRobot: Monitor `/api/health` every 5 minutes, alert if down.

#### Testing

**Unit Tests:**
- Logger utility formats messages correctly.
- Error handler middleware returns proper error responses.
- Analytics wrapper calls Posthog API correctly (mocked).

**Integration Tests:**
- `/api/health` returns correct status when DB is reachable.
- `/api/metrics` requires API key authentication.
- Error in `/api/chat` is captured by Sentry (verify Sentry.captureException called).

**Manual Verification:**
- Trigger error in dev environment, verify it appears in Sentry dashboard.
- Send test message in chat, verify events appear in Posthog dashboard.
- Check `/api/health` endpoint returns expected JSON.
- Check `/api/metrics` endpoint (with valid API key) returns metrics.

#### Verification

**Commands:**
- Install: `pnpm install`
- Dev: `pnpm dev`
- Test: `pnpm test` (unit tests pass)
- Lint: `pnpm lint` (no errors)
- Typecheck: `pnpm typecheck` (no errors)
- Build: `pnpm build` (successful build)

**Manual Checklist:**
- [ ] Sentry project created and DSN added to `.env`.
- [ ] Posthog project created and API key added to `.env`.
- [ ] Start dev server, navigate to landing page, verify page view event in Posthog.
- [ ] Send chat message, verify `chat_message_sent` and `chat_response_received` events in Posthog.
- [ ] Submit lead form, verify `lead_submitted` event in Posthog.
- [ ] Trigger an error (e.g., invalid API key for LLM), verify error appears in Sentry.
- [ ] Check Sentry breadcrumbs include user actions before error.
- [ ] Visit `/api/health`, verify returns `{ status: 'ok', checks: {...} }`.
- [ ] Visit `/api/metrics` without API key, verify 401 Unauthorized.
- [ ] Visit `/api/metrics` with valid API key, verify returns metrics JSON.
- [ ] Review Sentry dashboard: Releases, error rate chart, performance metrics visible.
- [ ] Review Posthog dashboard: Funnel created (Landing → Chat → Lead).
- [ ] Test alerting: Manually trigger high error rate (script or load test), verify Sentry alert received.

#### Rollback Plan

**Feature Flag:**
- Set `ENABLE_ANALYTICS=false` to disable analytics event tracking if causing issues.

**Revert Strategy:**
- Logging and error handling are additive; reverting PR removes observability but does not break existing features.
- If Sentry causes performance issues (unlikely), remove Sentry middleware from API routes.
- No data migrations involved; safe to revert.

#### Dependencies

**Upstream:**
- PR1-PR6 (core functionality must exist to instrument).

**External:**
- Sentry account and project created.
- Posthog account and project created.

#### Risks & Mitigations

**Risk: Analytics/monitoring libraries increase bundle size significantly.**
- Mitigation: Use dynamic imports for analytics libraries (client-side only). Measure bundle size in CI.

**Risk: Sentry captures sensitive data (user messages, PII).**
- Mitigation: Configure Sentry `beforeSend` hook to scrub sensitive fields (message content, email). Log only metadata.

**Risk: Logging volume causes performance issues or cost spikes.**
- Mitigation: Use appropriate log levels (INFO in prod, DEBUG only when troubleshooting). Sample verbose logs if needed.

---

### PR10b: Performance Optimization & Content Polish

#### Goal

Optimize application performance to meet production targets (<5s chat response, <3s landing page load) and refine content and UI for a polished, professional user experience.

#### Scope

**In scope:**
- **Performance Optimization:**
  - Frontend: Bundle size reduction, code splitting, image optimization, font optimization, lazy loading.
  - Backend: Database query optimization, caching strategy (session cache, RAG results cache).
  - LLM: Prompt optimization to reduce token usage and response time.
- **Content Review & Refinement:**
  - Audit and polish all markdown content in `content/` directory.
  - Review and update landing page copy (headline, value proposition, CTAs).
  - Verify all safety disclaimers are present and clear.
- **UI/UX Polish:**
  - Refine loading states, error messages, empty states.
  - Improve mobile responsiveness (test on multiple screen sizes).
  - Add micro-interactions (button hover states, smooth transitions).
  - Add footer with legal/info pages (About, FAQ, Privacy Policy, Terms of Service).
- **SEO Basics:**
  - Add meta tags (title, description, og:image) to all pages.
  - Generate sitemap.xml and robots.txt.
  - Ensure semantic HTML and accessibility (ARIA labels, alt text).

**Out of scope:**
- Observability infrastructure (handled in PR9a).
- E2E testing (handled in PR9c).
- New features or functionality changes.

#### Backend Changes

**Performance Optimizations:**
- **Database Query Optimization:**
  - Review and optimize Drizzle queries (add indexes if missing).
  - Implement connection pooling (verify Neon/Supabase pooler is enabled).
  - Add query result caching for RAG retrieval (cache vector search results by query hash, TTL 1 hour).
- **Session Caching:**
  - Implement in-memory session cache (Map or LRU cache) to reduce DB reads.
  - Fallback to DB if cache miss.
  - Cache TTL: 15 minutes.
- **Prompt Optimization:**
  - Review system prompts to reduce token count without losing quality.
  - Test prompt variations for conciseness and response time.

**APIs to Modify:**
- `/api/chat` — Add session caching, RAG result caching, optimize DB queries.
- `/api/session/:id` — Add session cache lookup.

**New Utilities:**
- `src/lib/cache/session-cache.ts` — In-memory session cache (Map with TTL).
- `src/lib/cache/rag-cache.ts` — RAG result cache (Map with query hash as key).

#### Frontend Changes

**Performance Optimizations:**
- **Bundle Size Reduction:**
  - Analyze bundle with `@next/bundle-analyzer`.
  - Identify and remove unused dependencies.
  - Use dynamic imports for heavy libraries (e.g., markdown renderer, date picker).
  - Split vendor chunks (React, Next.js, UI libraries).
  - Target: <500KB gzipped total JavaScript.
- **Code Splitting:**
  - Lazy load chat components (only load when user navigates to `/chat`).
  - Use `next/dynamic` for heavy components.
- **Image Optimization:**
  - Convert images to WebP format.
  - Use `next/image` component for automatic optimization.
  - Add explicit width/height to prevent layout shift (CLS).
  - Lazy load below-the-fold images.
- **Font Optimization:**
  - Use `next/font` for local font hosting (reduce external requests).
  - Preload critical fonts.
  - Use `font-display: swap` to prevent invisible text.

**UI/UX Polish:**
- `/app/page.tsx` (Landing):
  - Refine headline and value proposition copy (A/B test variants documented in comments).
  - Add social proof section (partner logos, testimonials if available).
  - Improve CTA button design (color, size, copy).
  - Add hero image or illustration (optimized).
- `/app/chat/page.tsx`:
  - Improve loading state UI (skeleton loaders instead of spinners).
  - Refine error messages (friendly, actionable, with retry button).
  - Add empty state UI (prompt suggestions when conversation starts).
  - Improve message bubble design (spacing, typography, contrast).
  - Add smooth scroll to latest message.
  - Add typing indicator animation.
- **Mobile Responsiveness:**
  - Test on viewport sizes: 320px, 375px, 414px, 768px.
  - Fix any layout issues (horizontal scroll, overlapping elements).
  - Ensure touch targets are ≥44px.
  - Test form inputs on mobile keyboards.
- **Micro-Interactions:**
  - Add button hover/focus states.
  - Add smooth transitions (fade in/out, slide up).
  - Add subtle animation to loading states.

**New Pages:**
- `/app/about/page.tsx` — Static page: About DovvyBuddy.
- `/app/faq/page.tsx` — Static page: Frequently Asked Questions.
- `/app/privacy/page.tsx` — Static page: Privacy Policy.
- `/app/terms/page.tsx` — Static page: Terms of Service.

**Footer Component:**
- `src/components/Footer.tsx` — Links to About, FAQ, Privacy, Terms, Contact.

**SEO:**
- Update `app/layout.tsx` metadata (global title, description).
- Add page-specific metadata to each route.
- Add Open Graph tags for social sharing.
- Generate `sitemap.xml` (use Next.js sitemap generation).
- Add `robots.txt` (allow all).

#### Data Changes

**Content Review & Refinement:**
- Audit `content/certifications/padi/open-water.md` for accuracy, tone, clarity.
- Audit `content/certifications/ssi/open-water.md` for consistency with PADI content.
- Audit `content/destinations/[destination]/overview.md` for completeness.
- Audit `content/destinations/[destination]/sites/[site].md` (5-10 sites) for accuracy.
- Ensure all content includes:
  - Clear safety disclaimers where appropriate.
  - "Verify with instructor/agency" prompts for prerequisites.
  - Consistent tone (friendly, non-judgmental, informative).
- Update `content/safety/general-safety.md` with final reviewed content.

**Re-run Content Ingestion:**
- After content updates, run `pnpm content:ingest` to regenerate embeddings.
- Verify embeddings stored in `content_embeddings` table.
- Test RAG retrieval with sample queries to ensure quality.

#### Infra / Config

**Performance Budgets (CI):**
- Add Lighthouse CI configuration (`.lighthouserc.json`).
- Thresholds:
  - LCP: <3s
  - FCP: <1.8s
  - TTI: <3.5s
  - CLS: <0.1
  - TBT: <300ms
- Fail CI build if thresholds not met.

**Bundle Size Limits (CI):**
- Add bundle size check (use `size-limit` or `next-bundle-analyzer`).
- Fail CI if JavaScript bundle >500KB gzipped.

**Caching Strategy:**
- No CDN-level caching changes (Vercel handles static assets).
- API route caching: No caching for `/api/chat` (dynamic). Cache `/api/health` (1 minute).

#### Testing

**Performance Testing:**
- Run Lighthouse on landing page (desktop + mobile).
- Verify LCP <3s, FCP <1.8s, CLS <0.1.
- Run bundle analyzer, verify total bundle <500KB gzipped.
- Load test `/api/chat` endpoint (simulate 10 concurrent users), verify response time <5s (p95).

**Unit Tests:**
- Session cache: Test cache hit/miss, TTL expiration.
- RAG cache: Test cache key generation, cache hit/miss.

**Manual Testing:**
- **Content Review:** Read through all content files, verify accuracy and tone.
- **Landing Page:** Test on desktop (Chrome, Safari, Firefox) and mobile (iOS Safari, Chrome Android).
  - Verify headline is clear and compelling.
  - Verify CTA button is prominent and functional.
  - Verify images load quickly and are optimized.
  - Check Core Web Vitals in DevTools.
- **Chat Interface:** Test on desktop and mobile.
  - Send multiple messages, verify smooth scrolling.
  - Trigger error (disconnect network), verify error message is friendly and has retry button.
  - Test loading states (slow network simulation).
  - Verify empty state appears when conversation starts.
  - Check mobile responsiveness (keyboard doesn't overlap input, touch targets adequate).
- **Footer Links:** Click each footer link, verify pages load correctly.
- **SEO:** View page source, verify meta tags present. Test social share preview (Facebook debugger, Twitter card validator).

#### Verification

**Commands:**
- Install: `pnpm install`
- Dev: `pnpm dev`
- Test: `pnpm test` (unit tests pass)
- Lint: `pnpm lint` (no errors)
- Typecheck: `pnpm typecheck` (no errors)
- Build: `pnpm build` (successful build, check output for warnings)
- Analyze bundle: `pnpm analyze` (requires bundle analyzer setup)
- Lighthouse: `pnpm lighthouse` (requires Lighthouse CI setup)
- Content ingest: `pnpm content:ingest` (after content updates)

**Manual Checklist:**
- [ ] Run Lighthouse on landing page (desktop), verify LCP <3s.
- [ ] Run Lighthouse on landing page (mobile), verify LCP <3s.
- [ ] Check bundle size (from build output or analyzer), verify <500KB gzipped.
- [ ] Load landing page on slow 3G network (DevTools throttling), verify usable within 5s.
- [ ] Test chat interface on iPhone SE screen size (375x667), verify responsive.
- [ ] Test chat interface on iPad (768x1024), verify responsive.
- [ ] Send 5 messages in quick succession, verify no performance degradation.
- [ ] Trigger error in chat, verify error message is friendly and actionable.
- [ ] Read all content files in `content/`, verify accuracy, tone, and safety disclaimers.
- [ ] Test footer links, verify all pages load and display correctly.
- [ ] View page source for landing page, verify meta tags (title, description, og:image).
- [ ] Test social share preview (paste URL into Facebook, Twitter), verify preview displays correctly.
- [ ] Check `sitemap.xml` and `robots.txt` are accessible.
- [ ] Review Vercel deployment logs for any performance warnings.

#### Rollback Plan

**Revert Strategy:**
- Performance optimizations are largely additive (caching, bundle optimization). Reverting PR removes optimizations but does not break functionality.
- If caching causes stale data issues, disable cache by setting TTL to 0 or removing cache lookups.
- If bundle splitting causes loading issues, revert dynamic imports.
- Content updates can be reverted by re-running `pnpm content:ingest` with previous content version.

**Feature Flag:**
- `ENABLE_SESSION_CACHE` — Toggle session caching on/off (default: true).
- `ENABLE_RAG_CACHE` — Toggle RAG result caching on/off (default: true).

#### Dependencies

**Upstream:**
- PR9a (observability) — Helpful for monitoring performance metrics but not strictly required.

**External:**
- None (all optimizations are internal).

#### Risks & Mitigations

**Risk: Aggressive caching causes stale data issues (e.g., session state out of sync).**
- Mitigation: Use short TTLs (session cache 15 min, RAG cache 1 hour). Add cache invalidation on session update.

**Risk: Bundle splitting breaks lazy-loaded components (load errors).**
- Mitigation: Test all lazy-loaded components thoroughly. Add error boundaries to handle load failures gracefully.

**Risk: Image optimization degrades visual quality.**
- Mitigation: Use Next.js Image component with appropriate quality settings (75-85). Review images visually before deploy.

**Risk: Content updates introduce factual errors.**
- Mitigation: Peer review (if possible) or careful solo review. Test RAG retrieval with known queries. Consider adding content validation checks (e.g., no broken links).

---

### PR10c: E2E Testing & Production Launch Checklist

#### Goal

Validate end-to-end user flows with automated smoke tests and comprehensive manual testing to ensure production readiness. Establish a repeatable launch checklist for future releases.

#### Scope

**In scope:**
- **E2E Testing (Playwright):**
  - Single smoke test covering critical path: Landing → Chat → Message → Response → Lead Form → Submit.
  - Test runs in CI (non-blocking for V1, made blocking post-launch).
  - Mock external services (LLM, email) for deterministic tests.
- **Manual Testing Checklist:**
  - Comprehensive checklist covering all user flows, edge cases, and error scenarios.
  - Mobile testing on real devices (iOS + Android).
  - Cross-browser testing (Chrome, Safari, Firefox, Edge).
  - Accessibility testing (keyboard navigation, screen reader).
- **Production Environment Setup:**
  - Verify all environment variables set in Vercel dashboard.
  - Configure custom domain (if applicable).
  - Set up production database (Neon/Supabase) with backups enabled.
  - Run database migrations and content ingestion in production.
- **Launch Checklist:**
  - Pre-launch validation steps.
  - Smoke tests post-deployment.
  - Rollback procedure documentation.
  - Monitoring and alerting validation.
- **Documentation:**
  - Update README with production deployment instructions.
  - Document launch runbook in `docs/references/LAUNCH_RUNBOOK.md`.
  - Document rollback procedure in `docs/references/ROLLBACK.md`.

**Out of scope:**
- Comprehensive E2E suite (deferred to post-launch).
- Load testing (basic load test only; full performance testing deferred).
- Penetration testing / security audit (deferred to V2).

#### Backend Changes

**APIs to Modify:**
- Add `E2E_MODE` environment variable check in relevant services.
- When `E2E_MODE=true`:
  - Mock LLM responses (return canned response for test queries).
  - Mock email delivery (log instead of sending).
  - Use in-memory session storage (no DB writes).

**New Utilities:**
- `src/lib/testing/mocks.ts` — Mock implementations for E2E tests (LLM, email).
- `src/lib/testing/fixtures.ts` — Test data fixtures (sample messages, leads).

#### Frontend Changes

**Test Utilities:**
- `tests/e2e/helpers.ts` — Playwright helper functions (login, start chat, send message).
- `tests/e2e/fixtures.ts` — Page object models for common elements.

**No UI changes.**

#### Data Changes

**No schema changes.**

**Production Database Setup:**
- Create production Postgres instance (Neon/Supabase).
- Enable automated backups (daily).
- Configure connection pooling.
- Run migrations: `pnpm db:migrate` (in production).
- Run seed script: `pnpm db:seed` (in production).
- Run content ingestion: `pnpm content:ingest` (in production).

#### Infra / Config

**E2E Testing Setup:**
- Install Playwright: `pnpm add -D @playwright/test`.
- Create `playwright.config.ts`:
  - Base URL: `http://localhost:3000` (dev) or production URL.
  - Browsers: Chromium, Firefox, WebKit (run on Chromium only in CI for speed).
  - Retry: 2 (for flaky tests).
  - Video: on-failure (for debugging).
- Add E2E test script to `package.json`: `"test:e2e": "playwright test"`.
- Add E2E to CI workflow (run after build, non-blocking initially).

**Production Environment Variables (Verify in Vercel):**
- `DATABASE_URL` (production Postgres connection string)
- `LLM_PROVIDER=gemini`
- `GEMINI_API_KEY` (production key)
- `RESEND_API_KEY` (production key)
- `LEAD_EMAIL_TO` (production email)
- `SESSION_SECRET` (secure random string)
- `SENTRY_DSN` (from PR10a)
- `POSTHOG_API_KEY` (from PR10a)
- `NODE_ENV=production`
- `ENABLE_ANALYTICS=true`
- `ENABLE_SESSION_CACHE=true` (from PR10b)
- `ENABLE_RAG_CACHE=true` (from PR10b)

**Custom Domain (Optional):**
- Configure custom domain in Vercel dashboard.
- Set up DNS records (CNAME or A record).
- Verify SSL certificate provisioned.

#### Testing

**E2E Smoke Test (`tests/e2e/smoke.spec.ts`):**
```
Test: Critical Path Smoke Test
1. Navigate to landing page.
2. Verify landing page loads (check for headline text).
3. Click "Start Chat" CTA.
4. Verify redirected to /chat.
5. Type message: "What is Open Water certification?"
6. Click send button.
7. Wait for response to appear (timeout: 10s).
8. Verify response contains expected keywords (e.g., "certification", "PADI", "SSI").
9. Click lead capture button (or type "I want to sign up").
10. Verify lead form appears.
11. Fill form: name, email.
12. Submit form.
13. Verify success message appears.
```

**E2E Test Configuration:**
- Use `E2E_MODE=true` env var to enable mocks.
- Mock LLM response for "What is Open Water certification?" to return canned response.
- Mock email delivery to log instead of sending.

**Manual Testing Checklist (`docs/references/MANUAL_TEST_CHECKLIST.md`):**

**Functional Tests:**
- [ ] Landing page loads correctly (desktop + mobile).
- [ ] "Start Chat" CTA navigates to /chat.
- [ ] Chat interface loads correctly.
- [ ] Send message, verify response appears within 5s.
- [ ] Send follow-up message, verify conversation history maintained.
- [ ] Click "New Chat" button, verify session resets.
- [ ] Refresh page during chat, verify session persists.
- [ ] Trigger lead capture flow (training), verify form appears.
- [ ] Submit lead form with valid data, verify success message.
- [ ] Submit lead form with invalid data (missing email), verify validation error.
- [ ] Verify lead delivery email received (check production email inbox).
- [ ] Test out-of-scope query (e.g., "Book me a flight"), verify refusal message.
- [ ] Test medical query, verify safety disclaimer and refusal.
- [ ] Test uncovered destination query, verify "not covered" response.

**Error Handling:**
- [ ] Disconnect network, send message, verify error message appears.
- [ ] Reconnect network, click retry, verify request succeeds.
- [ ] Trigger invalid LLM API key (temporarily change env var), verify graceful error.
- [ ] Trigger database connection failure (disconnect DB), verify /api/health returns degraded status.

**Performance:**
- [ ] Measure landing page load time (Lighthouse or DevTools), verify LCP <3s.
- [ ] Measure chat response time (send message, time to response), verify <5s (p95).
- [ ] Test under slow 3G network (DevTools throttling), verify usable.

**Mobile & Responsive:**
- [ ] Test on iPhone (Safari iOS): Landing, Chat, Lead form.
- [ ] Test on Android (Chrome): Landing, Chat, Lead form.
- [ ] Test on tablet (iPad): Landing, Chat, Lead form.
- [ ] Verify keyboard doesn't overlap input on mobile.
- [ ] Verify touch targets are adequate (buttons, links).

**Cross-Browser:**
- [ ] Test on Chrome (desktop).
- [ ] Test on Safari (desktop).
- [ ] Test on Firefox (desktop).
- [ ] Test on Edge (desktop).

**Accessibility:**
- [ ] Navigate landing page with keyboard only (Tab, Enter), verify all interactive elements accessible.
- [ ] Navigate chat interface with keyboard only.
- [ ] Test with screen reader (VoiceOver on Mac, NVDA on Windows), verify elements announced correctly.
- [ ] Check color contrast (WCAG AA), verify text readable.
- [ ] Verify all images have alt text.
- [ ] Verify form inputs have labels.

**Analytics & Monitoring:**
- [ ] Send test message, verify events appear in Posthog dashboard.
- [ ] Submit test lead, verify lead_submitted event in Posthog.
- [ ] Trigger test error, verify error appears in Sentry dashboard.
- [ ] Check Sentry breadcrumbs include user actions before error.
- [ ] Verify /api/health endpoint returns ok status.

**Content Quality:**
- [ ] Ask certification question, verify response is accurate and grounded.
- [ ] Ask destination question (covered destination), verify response includes relevant sites.
- [ ] Ask destination question (uncovered destination), verify refusal.
- [ ] Verify safety disclaimers appear in relevant responses.
- [ ] Verify "verify with instructor" prompts appear for prerequisites.

#### Verification

**Commands:**
- Install: `pnpm install`
- Dev: `pnpm dev`
- Test (unit): `pnpm test`
- Test (E2E): `pnpm test:e2e`
- Lint: `pnpm lint`
- Typecheck: `pnpm typecheck`
- Build: `pnpm build`
- DB migrate (prod): `pnpm db:migrate` (with production DATABASE_URL)
- DB seed (prod): `pnpm db:seed` (with production DATABASE_URL)
- Content ingest (prod): `pnpm content:ingest` (with production DATABASE_URL)

**Deployment Verification (Post-Deploy to Production):**
- [ ] Visit production URL, verify landing page loads.
- [ ] Check browser console for errors (should be none).
- [ ] Check Vercel deployment logs for errors (should be none).
- [ ] Run E2E smoke test against production: `pnpm test:e2e --url=https://dovvybuddy.com`.
- [ ] Manually test critical path on production (Landing → Chat → Message → Lead Submit).
- [ ] Check Posthog dashboard for new session events (from your test session).
- [ ] Check Sentry dashboard (should have no new errors from production).
- [ ] Verify /api/health returns ok status.
- [ ] Verify lead delivery email received (from production test lead submission).

**Launch Checklist (`docs/references/LAUNCH_RUNBOOK.md`):**

**Pre-Launch (1 week before):**
- [ ] PR9a (Observability) merged and deployed to production.
- [ ] PR9b (Performance & Polish) merged and deployed to production.
- [ ] All environment variables set in Vercel production environment.
- [ ] Production database created, migrations run, seed data loaded.
- [ ] Content ingestion completed in production.
- [ ] Sentry project configured, alerts tested.
- [ ] Posthog project configured, funnels created.
- [ ] Uptime monitoring configured (UptimeRobot or Vercel).
- [ ] Custom domain configured (if applicable) and SSL verified.
- [ ] Manual testing checklist completed (100% pass rate).
- [ ] E2E smoke test passing in CI.

**Launch Day (Soft Launch):**
- [ ] Deploy final version to production (merge PR9c).
- [ ] Run post-deploy verification (smoke test, manual test critical path).
- [ ] Verify monitoring dashboards operational (Sentry, Posthog, Vercel).
- [ ] Send test lead, verify delivery to partner email.
- [ ] Share URL with limited audience (friends, beta testers, partner shop staff).
- [ ] Monitor Sentry for errors (check every 2 hours for first 24 hours).
- [ ] Monitor Posthog for user behavior (session starts, lead submissions).
- [ ] Monitor Vercel analytics for traffic and performance.

**Post-Launch (1 week after):**
- [ ] Review metrics: Sessions, leads, error rate, response time.
- [ ] Gather user feedback from beta testers.
- [ ] Identify and prioritize bugs/issues.
- [ ] Plan next iteration (bug fixes, content updates, feature enhancements).
- [ ] Make E2E tests blocking in CI (if smoke test is stable).
- [ ] Write post-mortem or launch reflection (what went well, what to improve).

**Rollback Procedure (`docs/references/ROLLBACK.md`):**

**Scenario 1: Critical bug in latest deployment**
1. In Vercel dashboard, go to Deployments.
2. Find the previous stable deployment.
3. Click "..." menu → "Promote to Production".
4. Verify rollback successful (visit production URL, test critical path).
5. Notify team/users of rollback.
6. Investigate and fix bug in separate hotfix branch.

**Scenario 2: Database migration failure**
1. If migration failed mid-apply, check DB state (which migrations applied).
2. If possible, roll forward (apply remaining migrations).
3. If rollback needed:
   - Restore database from pre-migration backup (if available).
   - OR manually revert migration changes (DROP TABLE, DROP COLUMN, etc.).
4. Test database integrity.
5. Redeploy application with reverted migration.

**Scenario 3: Performance degradation**
1. Identify source (Sentry performance traces, Vercel logs).
2. If caused by caching issue: Set `ENABLE_SESSION_CACHE=false` and `ENABLE_RAG_CACHE=false` in Vercel env vars.
3. Redeploy (Vercel auto-redeploys on env var change).
4. Monitor performance metrics.
5. If issue persists, rollback deployment (Scenario 1).

#### Rollback Plan

**Feature Flag:**
- `E2E_MODE` — Toggle E2E mocks on/off (only for testing).

**Revert Strategy:**
- E2E tests are non-breaking (CI non-blocking initially). Reverting PR removes tests but does not affect production functionality.
- If E2E tests are flaky, disable in CI temporarily while stabilizing.
- Production environment setup and launch checklist are documentation only; no code changes to revert.

#### Dependencies

**Upstream:**
- PR9a (Observability) — Required for monitoring production.
- PR9b (Performance & Polish) — Required for production-ready performance and UX.
- PR1-PR6 (Core functionality) — Required for E2E tests to have features to test.

**External:**
- Production Postgres instance (Neon/Supabase).
- Production Vercel account with appropriate tier.
- Custom domain (optional).
- Email access for lead delivery testing.

#### Risks & Mitigations

**Risk: E2E tests are flaky (false failures in CI).**
- Mitigation: Use Playwright retry mechanism (2 retries). Make tests deterministic (use mocks). Keep E2E non-blocking in CI initially.

**Risk: Production deployment fails due to missing environment variable.**
- Mitigation: Document all required env vars in `.env.example`. Add startup validation that checks for required vars and fails fast with clear error message.

**Risk: Database migration fails in production.**
- Mitigation: Test migrations thoroughly in staging environment first. Use backward-compatible migrations. Have backup/restore procedure documented and tested.

**Risk: Content ingestion fails in production (API rate limit, network issue).**
- Mitigation: Run content ingestion during low-traffic window. Implement retry logic with exponential backoff. Monitor ingestion job for failures.

**Risk: High traffic on launch day overwhelms infrastructure.**
- Mitigation: Soft launch to limited audience first. Monitor traffic and scale Vercel plan if needed. Use rate limiting to prevent abuse.

---

## 5. Milestones & Sequence

### Milestone 1: Observability Foundation (PR9a)

**What it unlocks:** Real-time visibility into production health, enabling data-driven decisions and proactive incident response.

**PRs Included:**
- PR10a: Observability & Monitoring Infrastructure

**Definition of Done:**
- Sentry dashboard shows error rates, performance metrics, and release tracking.
- Posthog dashboard shows user funnels (Landing → Chat → Lead).
- Alerts configured and tested (error rate spike, lead delivery failure).
- `/api/health` endpoint operational and monitored.
- All API routes have structured logging.
- Documentation: `docs/references/MONITORING.md` created.

### Milestone 2: Production-Ready Performance & UX (PR9b)

**What it unlocks:** Fast, polished user experience meeting production performance targets, with refined content and professional UI.

**PRs Included:**
- PR10b: Performance Optimization & Content Polish

**Definition of Done:**
- Landing page LCP <3s (desktop and mobile).
- Chat response time <5s (p95).
- Bundle size <500KB gzipped.
- All content reviewed, polished, and re-ingested.
- Landing page copy refined (headline, CTAs, value prop).
- Mobile responsiveness verified on real devices.
- Footer with legal pages added (About, FAQ, Privacy, Terms).
- SEO basics implemented (meta tags, sitemap, robots.txt).
- Performance budgets enforced in CI (Lighthouse, bundle size).

### Milestone 3: Launch-Ready Validation (PR9c)

**What it unlocks:** Confidence in production deployment through automated smoke tests, comprehensive manual testing, and repeatable launch procedures.

**PRs Included:**
- PR10c: E2E Testing & Production Launch Checklist

**Definition of Done:**
- E2E smoke test passing in CI (critical path: Landing → Chat → Lead).
- Manual testing checklist completed (100% pass rate).
- Production environment configured (all env vars set, DB migrated, content ingested).
- Custom domain configured (if applicable).
- Launch runbook documented (`docs/references/LAUNCH_RUNBOOK.md`).
- Rollback procedure documented (`docs/references/ROLLBACK.md`).
- Soft launch completed with limited audience, metrics validated.
- Monitoring dashboards operational and showing expected data.

### Milestone 4: Public Launch

**What it unlocks:** DovvyBuddy is live and accessible to the public, ready to serve divers and generate leads for partner shops.

**No PRs (Operational Milestone):**
- Execute launch checklist from PR9c.
- Announce to broader audience (social media, email, partner shops).
- Monitor metrics for first week (sessions, leads, errors, performance).
- Gather user feedback.
- Plan next iteration based on data and feedback.

**Definition of Done:**
- Public URL accessible and performing well.
- No critical bugs or errors in production.
- Lead delivery confirmed operational (partner shops receiving leads).
- Monitoring dashboards showing healthy metrics (low error rate, target performance met).
- User feedback collected and prioritized for next release.

---

## 6. Risks, Trade-offs, and Open Questions

### Major Risks

**Technical Risks:**

1. **Risk: LLM API rate limits or cost spikes under production load.**
   - **Likelihood:** Medium (depends on launch traffic).
   - **Impact:** High (chat feature unavailable or expensive).
   - **Mitigation:**
     - Implement request rate limiting on `/api/chat` (max 10 requests/minute per session).
     - Set up billing alerts in Gemini/Groq console.
     - Monitor LLM API usage in Sentry performance traces.
     - Have fallback model provider ready (switch from Groq to Gemini or vice versa via env var).

2. **Risk: Database connection pool exhaustion under high concurrent load.**
   - **Likelihood:** Medium (if launch traffic exceeds estimates).
   - **Impact:** High (API requests fail, users can't chat).
   - **Mitigation:**
     - Use Neon/Supabase connection pooler (PgBouncer).
     - Monitor database connection count in Sentry/logs.
     - Configure connection pool size appropriately (start with 10, scale as needed).
     - Implement retry logic for transient DB connection failures.

3. **Risk: Sentry/Posthog outage or misconfiguration causes monitoring blind spots.**
   - **Likelihood:** Low (SaaS providers have high uptime).
   - **Impact:** Medium (loss of observability, but app still functions).
   - **Mitigation:**
     - Wrap Sentry/Posthog calls in try-catch (don't let monitoring failures break app).
     - Test monitoring integration thoroughly in dev/staging.
     - Have backup monitoring (Vercel logs, basic uptime check).

4. **Risk: Content ingestion fails in production (embeddings API rate limit, network issue).**
   - **Likelihood:** Low (one-time operation, can retry).
   - **Impact:** High (RAG retrieval returns no results).
   - **Mitigation:**
     - Run content ingestion during off-peak hours.
     - Implement retry logic with exponential backoff.
     - Manually verify embeddings count in DB after ingestion.
     - Have rollback plan (re-run ingestion from backup content).

5. **Risk: E2E tests are flaky, causing CI failures and blocking deployments.**
   - **Likelihood:** Medium (E2E tests inherently flaky).
   - **Impact:** Medium (slows down deployment velocity).
   - **Mitigation:**
     - Keep E2E tests non-blocking in CI for initial launch.
     - Use Playwright retry mechanism (2-3 retries).
     - Make tests deterministic (use mocks, avoid time-based assertions).
     - Gradually stabilize tests, then make blocking post-launch.

**Product Risks:**

6. **Risk: Launch traffic is higher than expected, causing performance degradation or downtime.**
   - **Likelihood:** Low-Medium (depends on launch strategy).
   - **Impact:** High (poor user experience, reputation damage).
   - **Mitigation:**
     - Soft launch to limited audience first (monitor metrics for 1 week).
     - Use Vercel auto-scaling (serverless scales automatically).
     - Monitor performance metrics (response time, error rate) closely during launch.
     - Have Vercel plan upgrade ready if needed (can scale tier in minutes).
     - Implement graceful degradation (if LLM slow, show loading message; if down, show maintenance page).

7. **Risk: Content quality issues (inaccurate info, poor tone) damage trust.**
   - **Likelihood:** Medium (manual content review is fallible).
   - **Impact:** High (users abandon, poor word-of-mouth).
   - **Mitigation:**
     - Thorough content review by founder + subject matter expert (if available).
     - Test RAG retrieval with diverse queries during manual testing.
     - Collect user feedback early (soft launch audience).
     - Plan rapid content update cycle (update content → re-ingest → redeploy).

8. **Risk: Lead quality is poor (spam, incomplete context), partner shops complain.**
   - **Likelihood:** Low-Medium (depends on UI/UX of lead form).
   - **Impact:** High (partner dissatisfaction, revenue risk).
   - **Mitigation:**
     - Validate lead form inputs (email format, required fields).
     - Implement basic spam detection (rate limiting, honeypot field).
     - Monitor lead submissions in Posthog (check for suspicious patterns).
     - Collect partner feedback after first leads delivered.
     - Iterate on lead form based on feedback.

### Trade-offs

**Trade-off 1: E2E Test Coverage vs. Solo Founder Time**
- **Decision:** Single smoke test (critical path) instead of comprehensive E2E suite.
- **Rationale:** Comprehensive E2E suite is time-intensive to build and maintain. Solo founder resources require prioritization. Single smoke test catches critical regressions while manual checklist covers edge cases.
- **Consequence:** Some edge cases may slip through (mitigated by thorough manual testing and monitoring in production).

**Trade-off 2: Posthog vs. Vercel Analytics**
- **Decision:** Posthog (self-hosted or cloud) for product analytics.
- **Rationale:** Posthog provides more detailed event tracking, funnels, and user segmentation compared to Vercel Analytics (which focuses on Core Web Vitals and traffic sources).
- **Consequence:** Requires additional integration effort and potential cost. If budget is constrained, can fall back to Vercel Analytics initially and migrate to Posthog later.

**Trade-off 3: In-Memory Caching vs. Redis**
- **Decision:** In-memory caching (Map with TTL) for session and RAG results.
- **Rationale:** Simpler implementation, no external dependency, sufficient for V1 traffic estimates. Redis adds cost and complexity.
- **Consequence:** Cache is not shared across serverless function instances (each instance has its own cache). Cache is lost on function cold start. Acceptable for V1; migrate to Redis if traffic scales and cache hit rate is important.

**Trade-off 4: Manual Content Review vs. Automated Validation**
- **Decision:** Manual content review (founder reads all content files).
- **Rationale:** Content corpus is small (~10-15 markdown files). Automated validation (fact-checking, tone analysis) is complex and time-consuming to implement.
- **Consequence:** Manual review is slower and fallible. Mitigated by thorough checklist and testing RAG retrieval quality. Consider automated validation in V2 if content corpus grows significantly.

**Trade-off 5: Soft Launch vs. Big Bang Launch**
- **Decision:** Soft launch to limited audience (beta testers, partner shop staff, small social media post).
- **Rationale:** Reduces risk of launch day disasters (high traffic, unexpected bugs). Allows validation of monitoring, lead delivery, and performance under real-world conditions before broader announcement.
- **Consequence:** Slower user acquisition initially. Acceptable for V1; prioritizes stability over growth velocity.

### Open Questions

**Q1: Which destination should be the initial launch destination?**
- **Impact on Plan:** Content scope (destination overview, site guides). Partner shop selection.
- **Resolution Needed Before:** PR9b (content review).
- **Decision Criteria:** Choose destination with:
  - Existing partner shop relationship (for lead delivery validation).
  - High diver interest and search volume.
  - Diverse site difficulty range (beginner to advanced).
  - Available content sources (dive site info, safety notes, logistics).
- **Proposed Decision:** Defer to founder to select based on partner availability and market research. Suggested options: Cozumel (Mexico), Koh Tao (Thailand), Bonaire (Caribbean).

**Q2: Should analytics use Posthog self-hosted or Posthog Cloud?**
- **Impact on Plan:** Infra setup (self-hosted requires additional deployment) and cost.
- **Resolution Needed Before:** PR9a (observability).
- **Decision Criteria:**
  - Posthog Cloud: Easier setup, managed service, pay-per-event pricing (~$0.00025/event after free tier).
  - Posthog Self-Hosted: Free (compute cost only), more control, requires deployment/maintenance.
- **Proposed Decision:** Use Posthog Cloud for V1 (simpler, faster setup). Migrate to self-hosted if cost becomes significant (>$100/month) or data privacy requirements demand it.

**Q3: Should we implement rate limiting at Vercel level or application level?**
- **Impact on Plan:** Implementation approach (Vercel config vs. middleware code).
- **Resolution Needed Before:** PR9b (performance optimization).
- **Decision Criteria:**
  - Vercel level: Built-in protection, no code changes, limited customization.
  - Application level: Full control, custom rules (per-session, per-IP), requires implementation.
- **Proposed Decision:** Start with Vercel rate limiting (simpler). Add custom application-level rate limiting if Vercel limits are insufficient or too coarse.

**Q4: What is the rollout timeline for PR9a, PR9b, PR9c?**
- **Impact on Plan:** Testing schedule, deployment sequence.
- **Resolution Needed Before:** Starting work on PR9.
- **Proposed Timeline:**
  - **PR9a (Observability):** Week 1-2 (highest priority, needed to monitor subsequent PRs).
  - **PR9b (Performance & Polish):** Week 2-3 (can start in parallel with PR9a, but benefits from having observability in place).
  - **PR9c (E2E & Launch):** Week 3-4 (requires PR9a and PR9b complete).
  - **Public Launch:** Week 5 (after 1 week of soft launch monitoring).
- **Total Duration:** ~5 weeks from start to public launch.

**Q5: Should we use a staging environment separate from production?**
- **Impact on Plan:** Infra setup (additional Vercel project, additional database).
- **Resolution Needed Before:** PR9c (production deployment).
- **Decision Criteria:**
  - Staging environment: Allows testing production-like conditions without risking live site. Doubles hosting cost.
  - No staging: Simpler, lower cost. Rely on local dev + Vercel preview deployments.
- **Proposed Decision:** Use Vercel preview deployments (automatic per-branch) as "staging." Each PR gets a preview URL for testing. No separate staging environment for V1 (cost optimization). Consider adding staging if V2 introduces complex multi-service architecture.

---

## Summary

PR9 (Production Launch Readiness) is a critical epic that transforms DovvyBuddy from a feature-complete application into a production-ready product. By breaking the work into three focused PRs (Observability, Performance & Polish, E2E Testing & Launch), we ensure each component is thoroughly tested and validated before public launch. The comprehensive monitoring, performance optimization, and testing infrastructure established in PR9 will pay dividends throughout the product lifecycle, enabling rapid iteration and confident deployments.

**Key Success Metrics:**
- Error rate <1% (measured in Sentry).
- Chat response time <5s (p95, measured in Sentry/Posthog).
- Landing page LCP <3s (measured in Lighthouse/Vercel Analytics).
- Lead delivery success rate >99% (monitored in logs/Sentry).
- Session-to-lead conversion rate >5% (measured in Posthog funnel).

**Next Steps After PR9:**
- Monitor production metrics for 1-2 weeks.
- Gather user feedback from soft launch audience.
- Prioritize bugs and iterate (PR10: Post-Launch Fixes & Improvements).
- Plan V2 features (User Auth, Dive Logs, Multi-Destination, etc.).
