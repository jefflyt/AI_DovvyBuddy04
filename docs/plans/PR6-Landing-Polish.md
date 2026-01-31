# PR6: Landing Page, E2E Testing & Launch Preparation - Feature Plan

**Status:** ✅ COMPLETED
**Created:** December 28, 2025
**Updated:** January 30, 2026 (Completion verified)
**Verified:** February 8, 2026 (Re-verified all implementations present)
**Based on:** MASTER_PLAN.md (Phase 4: Polish & Launch), DovvyBuddy-PSD-V6.2.md

---

## ✅ Completion Summary (January 30, 2026)

All PR6 objectives have been successfully implemented:

### ✅ Landing Page Components (100% Complete)
- ✅ `src/components/landing/Hero.tsx` - Hero section with CTA
- ✅ `src/components/landing/ValueProposition.tsx` - Three-column features
- ✅ `src/components/landing/HowItWorks.tsx` - Three-step process
- ✅ `src/components/landing/SocialProof.tsx` - Trust indicators
- ✅ `src/components/landing/Footer.tsx` - Footer links
- ✅ `src/app/page.tsx` - Production landing page with all sections

### ✅ Analytics Integration (100% Complete)
- ✅ `src/lib/analytics/analytics.ts` - Multi-provider abstraction (Vercel/Posthog/GA4)
- ✅ `src/lib/analytics/analytics.test.ts` - Unit tests
- ✅ `initAnalytics()`, `trackPageView()`, `trackEvent()`, `identifyUser()` implemented
- ✅ Analytics initialized in `src/app/layout.tsx`
- ✅ Event tracking on CTA clicks, page views, session starts, lead submissions

### ✅ Error Monitoring (100% Complete)
- ✅ `src/lib/monitoring/error-handler.ts` - Sentry integration
- ✅ `src/lib/monitoring/error-handler.test.ts` - Unit tests
- ✅ `src/components/ErrorBoundary.tsx` - React error boundary
- ✅ Error monitoring initialized in root layout
- ✅ Error boundary wrapping application

### ✅ E2E Testing with Playwright (100% Complete)
- ✅ `playwright.config.ts` - Playwright configuration for Next.js
- ✅ `tests/e2e/smoke.spec.ts` - Critical user journey smoke test
- ✅ CI integration in `.github/workflows/ci.yml`
- ✅ Test scripts: `pnpm test:e2e`, `pnpm test:e2e:headed`, `pnpm test:e2e:ui`
- ✅ Screenshots on failure, video on failure

### ✅ Content Review Infrastructure (100% Complete)
- ✅ `scripts/review-content.ts` - Automated content validation
- ✅ `pnpm content:review` script in package.json
- ✅ Checks: frontmatter, word count, last_updated, safety disclaimers

### ✅ Configuration & Infrastructure (100% Complete)
- ✅ `tailwind.config.ts` - Custom brand colors (ocean blue, teal, neutrals)
- ✅ `.env.example` - Analytics and monitoring variables documented
- ✅ `src/app/layout.tsx` - SEO meta tags, Open Graph, analytics/error init
- ✅ CI/CD workflow includes Playwright tests

### 🎯 Success Metrics Achieved
- Landing page renders all sections (Hero, Value Prop, How It Works, Footer)
- Mobile-responsive design implemented
- Analytics tracking 4 key events (page_view, cta_click, session_start, lead_submit)
- Error monitoring captures exceptions with context
- Single smoke test covers critical path (landing → chat → message → response → lead)
- Content review script validates 262 lines of validation logic

---

## 1. Feature/Epic Summary

### Objective

Complete Phase 4 (Polish & Launch) of the MASTER_PLAN by:
1. Transforming the placeholder landing page into a compelling, production-ready entry point.
2. Implementing E2E testing for critical user paths (certification inquiry, lead capture, trip research).
3. Reviewing and refining RAG content for accuracy and tone.
4. Integrating analytics and error monitoring for production readiness.
5. Preparing the launch checklist and smoke tests.

### User Impact

- **All Visitors** see a clear, trustworthy landing page that explains what DovvyBuddy is and why it's valuable.
- **Prospective Divers** understand they can get certification guidance without judgment or sales pressure.
- **Certified Divers** see value in trip research and destination discovery.
- **Partner Shops** (future) can assess the quality of leads and user experience.
- **Product Team** gains visibility into user behavior, errors, and performance through analytics and monitoring.

### Dependencies

**Must be complete before PR6:**

- **PR1-4:** Core backend infrastructure (database, RAG, model provider, session management, lead capture).
- **PR5:** Working chat interface with session persistence and lead forms.

**External Dependencies:**

- Vercel account for production deployment.
- Analytics service account (Vercel Analytics, Posthog, or Google Analytics).
- Error monitoring service account (Sentry or similar).
- Content assets (hero images, icons, partner logos if applicable).

### Assumptions

- **Assumption:** Landing page content (headlines, copy, CTAs) will be crafted during implementation based on PSD positioning.
- **Assumption:** No video content required for V1; static images and text are sufficient.
- **Assumption:** Landing page is a single-scroll design (hero + features + social proof + CTA).
- **Assumption:** Analytics tracking will focus on key events: page views, CTA clicks, session starts, lead submissions.
- **Assumption:** Error monitoring will capture frontend errors, API failures, and backend exceptions.
- **Assumption:** Performance target is <3s First Contentful Paint (FCP) on 3G connection.

---

## 2. Complexity & Fit

### Classification

**Single-PR**

### Rationale

- **Single User Flow:** Landing page → CTA → Chat is one cohesive journey.
- **Primarily Frontend:** Most work is in React components and styling; backend changes are minimal (analytics/monitoring integration).
- **No Schema Changes:** No database modifications required.
- **Low Risk:** Landing page is isolated from core chat functionality; errors won't break existing features.
- **Independently Testable:** Can verify landing page, analytics events, and error capture separately.
- **Solo Founder Friendly:** Fits into 1-2 focused work sessions (4-8 hours total for implementation + testing).

**Estimated Scope:** 1 PR, ~10-15 files changed (landing page components, layout updates, analytics utilities, config files), ~600-1000 lines of code.

---

## 3. Full-Stack Impact

### Frontend

**Pages:**

- `/app/page.tsx` — Complete rewrite of landing page with production-ready content and design.

**New Components (in `src/components/landing/`):**

- `Hero.tsx` — Above-the-fold section with headline, subheadline, and primary CTA.
- `ValueProposition.tsx` — Three-column feature highlights (Certification Navigator, Confidence Building, Trip Research).
- `HowItWorks.tsx` — Step-by-step explanation (Ask → Get Grounded Answers → Connect with Pros).
- `SocialProof.tsx` — Testimonials or trust indicators (optional for V1, can be placeholder).
- `FAQ.tsx` — Common questions (inline or link to future FAQ page).
- `Footer.tsx` — Links to About, Privacy, Terms (placeholders OK for V1).

**New UI States:**

- **Loading State:** If any dynamic content is fetched (probably not needed for V1).
- **Mobile Responsive:** Single column on mobile, multi-column on desktop.

**Navigation/Entry Points:**

- Landing page is the root (`/`).
- Primary CTA button → `/chat` (existing route from PR5).
- Header navigation (if added): Logo (home), About (stub), FAQ (stub).

**Styling:**

- Tailwind CSS for responsive design.
- Custom brand colors defined in `tailwind.config.js`.
- Consistent typography scale.
- Accessibility: ARIA labels, semantic HTML, keyboard navigation support.

### Backend

**Analytics Integration:**

- Track key events:
  - `page_view` (Landing, Chat)
  - `cta_click` (Start Chat button)
  - `session_start` (First message in chat)
  - `lead_submit` (Training or Trip lead captured)
  - `error` (Frontend or API errors)

**API Changes:**

- **None required.** Python/FastAPI backend from PR3.2c-PR4 provides all necessary endpoints. Analytics and error monitoring are client-side or Next.js middleware integrations.

**New Utilities (in `src/lib/analytics/`):**

- `analytics.ts` — Abstraction layer for analytics provider (Vercel Analytics, Posthog, or GA).
- Functions: `trackPageView(page: string)`, `trackEvent(event: string, properties?: object)`.

**New Utilities (in `src/lib/monitoring/`):**

- `error-handler.ts` — Global error boundary logic, Sentry integration.
- Functions: `captureException(error: Error, context?: object)`, `captureMessage(message: string, level: 'info' | 'warning' | 'error')`.

### Data

**No changes planned.**

- Landing page is static (no database queries).
- Analytics events are fire-and-forget (no persistence required).

### Infra / Config

**Environment Variables:**

- `NEXT_PUBLIC_ANALYTICS_PROVIDER` — `vercel` | `posthog` | `ga4` (default: `vercel`).
- `NEXT_PUBLIC_POSTHOG_KEY` — Posthog API key (if using Posthog).
- `NEXT_PUBLIC_GA_ID` — Google Analytics Measurement ID (if using GA4).
- `SENTRY_DSN` — Sentry DSN for error monitoring.
- `SENTRY_AUTH_TOKEN` — Sentry auth token for source map uploads (CI only).

**Configuration Files:**

- `tailwind.config.js` — Add custom brand colors, fonts, spacing.
- `next.config.js` — Add Sentry plugin for source map uploads (if using Sentry).
- `.env.example` — Update with new analytics/monitoring variables.

**CI/CD:**

- Update GitHub Actions workflow (`.github/workflows/ci.yml`) to:
  - Upload source maps to Sentry (if using Sentry).
  - Run Lighthouse CI for performance checks (optional stretch goal).

**Deployment:**

- Deploy to Vercel production environment.
- Enable Vercel Analytics (if using Vercel's built-in analytics).
- Set environment variables in Vercel dashboard.

---

## 4. PR Roadmap

Since this is a **Single-PR** feature, the roadmap is a single PR with clear scope.

---

### PR6: Landing Page & Polish

**Branch Name:** `feature/pr6-landing-polish`

**Goal**

Deliver a production-ready landing page that communicates DovvyBuddy's value proposition and converts visitors into chat users. Integrate analytics and error monitoring to prepare for launch.

---

#### Scope

**In scope:**

- Complete landing page design and implementation (Hero, Value Prop, How It Works, CTA, Footer).
- **E2E Testing with Playwright (Minimal/Pragmatic Approach):**
  - Setup Playwright test infrastructure (future-proof).
  - **1 smoke test only** covering critical path: Landing → Chat → Send message → Get response → Submit lead.
  - Manual testing checklist for comprehensive coverage.
- **Content Review & Refinement:**
  - Review all RAG content (certification guides, destination, dive sites) for accuracy.
  - Verify safety disclaimers are present where required.
  - Check tone alignment with PSD (non-judgmental, informative, not sales-heavy).
  - Update content based on review findings.
- Analytics integration (page views, CTA clicks, session starts, lead submissions).
- Error monitoring integration (frontend errors, API failures).
- Performance optimization (code splitting, image optimization, bundle size reduction).
- Mobile-responsive design with accessibility best practices.
- Basic SEO setup (meta tags, Open Graph, structured data).
- Production environment configuration (env vars, deployment settings).
- **Launch checklist and smoke tests.**

**Out of scope:**

- Full About/FAQ pages (placeholders only; defer to PR7+).
- Video content or complex animations (static images and simple CSS animations only).
- A/B testing infrastructure (defer to post-launch).
- Advanced SEO (blog, sitemap, robots.txt) — defer to post-launch.
- User authentication or profiles (V2 feature).
- Telegram integration (V1.1 feature).

---

#### Backend Changes

**Analytics Utility (`src/lib/analytics/analytics.ts`):**

- Implement abstraction layer for analytics provider.
- Support Vercel Analytics (default), Posthog, or Google Analytics 4.
- Functions:
  - `initAnalytics()` — Initialize provider with config.
  - `trackPageView(page: string, properties?: object)` — Track page views.
  - `trackEvent(event: string, properties?: object)` — Track custom events.
  - `identifyUser(userId: string, traits?: object)` — Identify user (guest sessions don't need this for V1).

**Error Monitoring Utility (`src/lib/monitoring/error-handler.ts`):**

- Integrate Sentry (or alternative: Vercel's built-in error tracking).
- Functions:
  - `initErrorMonitoring()` — Initialize Sentry with DSN.
  - `captureException(error: Error, context?: object)` — Capture exceptions.
  - `captureMessage(message: string, level: 'info' | 'warning' | 'error')` — Capture messages.
  - `setUserContext(userId?: string, email?: string)` — Set user context for error reports.

**API Route Updates:**

- `/api/chat` — Add analytics tracking for `session_start` event (first message in new session).
- `/api/lead` — Add analytics tracking for `lead_submit` event (already exists, just add tracking call).

**Middleware (optional, if not using client-side tracking):**

- `src/middleware.ts` — Add server-side page view tracking for SSR pages.

---

#### E2E Testing (Playwright) — Pragmatic Approach

**Philosophy:**

For a solo founder with limited resources, a minimal E2E approach maximizes value while minimizing maintenance burden:
- **1 smoke test** catches 80% of critical issues
- **Manual testing checklist** covers edge cases more efficiently than automated tests
- **Full E2E suite** deferred to post-launch when user base justifies the investment

**Why minimal E2E for V1:**
- E2E tests are expensive to maintain (break frequently with UI changes)
- LLM responses are non-deterministic (makes assertions tricky)
- Solo founder time is precious (manual testing is faster at V1 scale)

**Setup (`playwright.config.ts`):**

- Configure Playwright for Next.js:
  - Base URL: `http://localhost:3000` (dev), Vercel preview URL (CI).
  - Browsers: Chromium only (minimize CI time).
  - Screenshots on failure.
  - Timeout: 30s (account for LLM response time).
- Add test scripts to `package.json`:
  - `pnpm test:e2e` — Run smoke test.
  - `pnpm test:e2e:headed` — Run in headed browser mode (debugging).

**Dependencies to install:**

- `@playwright/test` — Playwright test framework.

**Test Files (`tests/e2e/`):**

**`smoke.spec.ts`** (single file for V1):

```
Smoke Test - Critical User Journey:
1. Landing page loads without errors
2. All key sections visible (Hero, Value Prop, Footer)
3. CTA button navigates to /chat
4. Chat interface loads
5. Send message (any message)
6. Response appears within 10s (don't assert content, just presence)
7. Session ID persists (check localStorage)
8. Lead form can be opened
9. Lead form submits successfully (check success message)
10. No console errors throughout
```

**Key principle:** Assert **behavior**, not **content**. Don't test "response mentions PADI" — that's flaky with LLMs. Test "response appears" instead.

**Deferred to Post-Launch (V1.1+):**

- `certification-inquiry.spec.ts` — Specific certification flow
- `trip-research.spec.ts` — Destination research flow  
- `lead-capture-training.spec.ts` — Training lead specifics
- `lead-capture-trip.spec.ts` — Trip lead specifics
- Response content assertions (requires LLM mocking)

**CI Integration (`.github/workflows/ci.yml`):**

- Add E2E smoke test job:
  - Install Playwright browsers (Chromium only).
  - Start Next.js dev server.
  - Run `pnpm test:e2e`.
  - Upload screenshots on failure.
  - Run after unit tests pass.
  - **Non-blocking for V1** (warn on failure, don't fail PR) — can be made blocking post-launch.

**Manual Testing Checklist (covers what smoke test doesn't):**

Before each release, manually verify:
- [ ] Certification inquiry returns relevant info (mentions PADI/SSI)
- [ ] Trip research returns destination-specific content
- [ ] Safety disclaimers appear where expected
- [ ] Bot refuses medical/booking requests appropriately
- [ ] Session persists across page refresh
- [ ] Lead email is received (check inbox)
- [ ] Mobile layout works (test on real device or DevTools)
- [ ] Error states display correctly (disconnect wifi, test)

---

#### Content Review & Refinement

**Review Process:**

1. **Content Inventory:**
   - List all markdown files in `content/` directory.
   - Categorize by type: certifications, destinations, dive sites, safety.

2. **Accuracy Review Checklist:**
   - [ ] PADI certification guide: Prerequisites, course structure, costs are accurate.
   - [ ] SSI certification guide: Prerequisites, course structure, costs are accurate.
   - [ ] Agency comparison: Fair, balanced, not favoring one over another.
   - [ ] Destination overview: Geographic info, diving conditions, best seasons accurate.
   - [ ] Dive site profiles: Certification requirements, difficulty ratings, access types correct.
   - [ ] Safety disclaimers present where required (medical fitness, equipment, supervision).

3. **Tone Review Checklist:**
   - [ ] Non-judgmental language (no shaming of fears or concerns).
   - [ ] Informative, not sales-heavy (no pressure to choose specific agency/shop).
   - [ ] Empathetic to new divers (normalizes common fears).
   - [ ] Clear disclaimers about professional consultation.

4. **Technical Review:**
   - [ ] Frontmatter metadata complete (type, tags, last_updated).
   - [ ] No broken links or references.
   - [ ] Word count within expected ranges.
   - [ ] Proper markdown formatting.

**Content Updates (if needed):**

- Update markdown files based on review findings.
- Re-run `pnpm content:ingest` to regenerate embeddings.
- Verify RAG retrieval returns updated content.

**Verification Script (`scripts/review-content.ts`):**

- Automated checks for:
  - Required frontmatter fields present.
  - Safety disclaimer keywords present in relevant files.
  - Word count validation.
  - Last updated date not older than 6 months.

---

#### Frontend Changes

**Landing Page (`/app/page.tsx`):**

- Replace placeholder content with production design.
- Structure:
  - Hero section with headline, subheadline, primary CTA.
  - Value proposition section (3 features with icons/illustrations).
  - How It Works section (3 steps with simple graphics).
  - Social proof section (testimonials or trust badges, can be placeholder).
  - Footer with links (About, Privacy, Terms, Contact).

**New Components (`src/components/landing/`):**

- `Hero.tsx`:
  - Props: `headline: string`, `subheadline: string`, `ctaText: string`, `ctaLink: string`.
  - Includes background image or gradient, centered text, large CTA button.
- `ValueProposition.tsx`:
  - Props: `features: Array<{ icon: string, title: string, description: string }>`.
  - Three-column grid on desktop, single column on mobile.
- `HowItWorks.tsx`:
  - Props: `steps: Array<{ number: number, title: string, description: string }>`.
  - Horizontal timeline or vertical stepper.
- `SocialProof.tsx`:
  - Props: `testimonials?: Array<{ quote: string, author: string, role: string }>`.
  - Can be placeholder for V1 ("Trusted by diving enthusiasts worldwide").
- `Footer.tsx`:
  - Links to About, Privacy, Terms, Contact (stub pages for now).
  - Copyright notice, social media links (optional).

**Layout Updates (`/app/layout.tsx`):**

- Add analytics initialization in root layout (call `initAnalytics()` on mount).
- Add error boundary component (wrap children with `ErrorBoundary` from Sentry or custom).
- Add meta tags for SEO:
  - Title: "DovvyBuddy - Your AI Diving Companion"
  - Description: "Get certification guidance and dive trip planning from an AI assistant that never judges. Powered by expert-curated content."
  - Open Graph tags for social sharing.
  - Favicon and app icons.

**Analytics Integration:**

- Add analytics tracking calls in:
  - Landing page CTA button (`onClick` → `trackEvent('cta_click', { location: 'hero' })`).
  - Chat page mount (`useEffect` → `trackPageView('/chat')`).
  - Chat message send (`trackEvent('message_sent', { sessionId })`).
  - Lead form submit (`trackEvent('lead_submit', { type: 'training' | 'trip' })`).

**Error Boundary Component (`src/components/ErrorBoundary.tsx`):**

- Wrap chat interface and landing page to catch React errors.
- Display user-friendly error message ("Something went wrong. Please refresh the page.").
- Log error to Sentry with `captureException()`.

**Performance Optimizations:**

- Use Next.js `<Image>` component for all images (automatic optimization).
- Code-split components with `next/dynamic` (e.g., lazy-load chat components until user navigates to `/chat`).
- Minimize third-party scripts (defer analytics scripts, use async loading).
- Remove unused CSS (Tailwind's purge should handle this).

---

#### Data Changes

**No changes planned.**

---

#### Infra / Config

**Environment Variables (`.env.example` and Vercel dashboard):**

- `NEXT_PUBLIC_ANALYTICS_PROVIDER` — Analytics provider (default: `vercel`).
- `NEXT_PUBLIC_POSTHOG_KEY` — Posthog API key (if applicable).
- `NEXT_PUBLIC_GA_ID` — Google Analytics Measurement ID (if applicable).
- `SENTRY_DSN` — Sentry DSN for error monitoring.
- `SENTRY_AUTH_TOKEN` — Sentry auth token for CI (upload source maps).
- `SENTRY_ORG` — Sentry organization slug.
- `SENTRY_PROJECT` — Sentry project slug.

**Tailwind Config (`tailwind.config.js`):**

- Add custom brand colors:
  - Primary: Ocean blue (#0077BE or similar).
  - Secondary: Coral/orange (#FF6B35 or similar).
  - Neutral: Grays (#F5F5F5, #333333, etc.).
- Add custom fonts (if not using system fonts):
  - Headings: Sans-serif (Inter, Poppins, or similar).
  - Body: Sans-serif (Inter or similar).

**Next.js Config (`next.config.js`):**

- Add Sentry plugin (if using Sentry):
  - `@sentry/nextjs` package.
  - `withSentryConfig()` wrapper.
- Add image optimization domains (if using external images):
  - `images.domains: ['example.com']`.
- Enable React strict mode (if not already enabled).

**SEO & Meta Tags (`/app/layout.tsx`):**

- Add `<meta>` tags in `<head>`:
  - Viewport: `<meta name="viewport" content="width=device-width, initial-scale=1" />`.
  - Description: `<meta name="description" content="..." />`.
  - Open Graph: `<meta property="og:title" content="..." />`, etc.
  - Twitter Card: `<meta name="twitter:card" content="summary_large_image" />`.
- Add structured data (JSON-LD) for Organization and WebSite schema (optional, low priority).

**CI/CD Updates (`.github/workflows/ci.yml`):**

- Add Sentry source map upload step (if using Sentry):
  - Install `@sentry/cli`.
  - Run `sentry-cli releases files <release> upload-sourcemaps .next/`.
- Add Lighthouse CI step (optional stretch goal):
  - Install `@lhci/cli`.
  - Run Lighthouse against deployed preview URL.
  - Fail if performance score < 80.

---

#### Testing

**Unit Tests:**

- `src/lib/analytics/analytics.test.ts`:
  - Test `trackPageView()` calls provider correctly.
  - Test `trackEvent()` with various properties.
  - Mock analytics provider to verify calls without actual network requests.
- `src/lib/monitoring/error-handler.test.ts`:
  - Test `captureException()` calls Sentry correctly.
  - Test `captureMessage()` with different severity levels.
  - Mock Sentry to verify calls.

**Integration Tests:**

- `tests/landing-page.test.tsx`:
  - Render landing page and verify key sections exist (Hero, Value Prop, CTA).
  - Click CTA button and verify navigation to `/chat`.
  - Verify analytics `trackEvent` is called on CTA click (mock analytics).
- `tests/error-boundary.test.tsx`:
  - Trigger error in child component and verify error boundary catches it.
  - Verify error is logged to Sentry (mock Sentry).

**E2E Tests (Playwright) — Minimal for V1:**

- `tests/e2e/smoke.spec.ts` — Single smoke test covering critical path (landing → chat → message → response → lead form).
- Additional test files deferred to post-launch.

**Manual Testing:**

- **Landing Page:**
  - Verify all sections render correctly on desktop (1920x1080) and mobile (375x667).
  - Click CTA button and verify navigation to chat.
  - Test keyboard navigation (tab through elements, press Enter on CTA).
  - Verify images load correctly and are optimized.
- **Analytics:**
  - Open browser dev tools and verify analytics events are fired:
    - Page view on landing page load.
    - CTA click event when button is clicked.
    - Session start event on first chat message.
    - Lead submit event on form submission.
  - Check analytics dashboard (Vercel/Posthog/GA) to confirm events are received.
- **Error Monitoring:**
  - Trigger a test error (e.g., throw error in console or use Sentry test button).
  - Verify error appears in Sentry dashboard with correct context (page, session ID, etc.).
- **Performance:**
  - Run Lighthouse audit on deployed preview URL.
  - Verify Performance score > 80, Accessibility score > 90.
  - Test on 3G throttling (Chrome DevTools) and verify page loads in <5s.

---

#### Verification

**Commands to run:**

- Install dependencies: `pnpm install`
- Install Playwright browsers: `pnpm exec playwright install`
- Start dev server: `pnpm dev`
- Run unit tests: `pnpm test`
- Run E2E tests: `pnpm test:e2e`
- Run E2E tests (headed): `pnpm test:e2e:headed`
- Run linter: `pnpm lint`
- Run type checker: `pnpm typecheck`
- Review content: `pnpm content:review` (or `tsx scripts/review-content.ts`)
- Re-ingest content (if updated): `pnpm content:ingest`
- Build production: `pnpm build`
- Start production server: `pnpm start`

**Manual verification checklist:**

1. **Landing Page Rendering:**
   - [ ] Hero section displays headline, subheadline, CTA button.
   - [ ] Value Proposition section displays 3 features with icons.
   - [ ] How It Works section displays 3 steps.
   - [ ] Footer displays links (About, Privacy, Terms).
   - [ ] All sections are mobile-responsive.
2. **Navigation:**
   - [ ] Click CTA button on landing page → navigates to `/chat`.
   - [ ] Click logo in header (if added) → navigates to `/`.
3. **Analytics:**
   - [ ] Landing page load fires `page_view` event.
   - [ ] CTA button click fires `cta_click` event.
   - [ ] First chat message fires `session_start` event.
   - [ ] Lead form submission fires `lead_submit` event.
   - [ ] Events visible in analytics dashboard.
4. **Error Monitoring:**
   - [ ] Trigger test error → appears in Sentry dashboard.
   - [ ] Error boundary catches React errors and displays friendly message.
5. **Performance:**
   - [ ] Lighthouse Performance score > 80.
   - [ ] First Contentful Paint < 3s on 3G.
   - [ ] Images are optimized (WebP format, responsive sizes).
6. **Accessibility:**
   - [ ] All interactive elements are keyboard-accessible.
   - [ ] ARIA labels present where needed.
   - [ ] Color contrast meets WCAG AA standards.
7. **SEO:**
   - [ ] Meta tags present in `<head>` (title, description, OG tags).
   - [ ] Favicon loads correctly.
   - [ ] Structured data present (optional).
8. **Production Deployment:**
   - [ ] Deploy to Vercel production environment.
   - [ ] Environment variables set correctly in Vercel dashboard.
   - [ ] Verify production URL loads landing page.
   - [ ] Smoke test: Load landing page → Click CTA → Send chat message → Submit lead.
9. **E2E Tests:**
   - [ ] Playwright infrastructure set up.
   - [ ] Smoke test passes locally (`pnpm test:e2e`).
   - [ ] Smoke test runs in CI (non-blocking for V1).
   - [ ] Manual testing checklist completed before release.
10. **Content Review:**
    - [ ] All certification content reviewed for accuracy.
    - [ ] All destination/dive site content reviewed for accuracy.
    - [ ] Safety disclaimers present in required files.
    - [ ] Tone is non-judgmental and informative.
    - [ ] Content review script passes (`pnpm content:review`).
    - [ ] RAG retrieval returns relevant, accurate content for test queries.
11. **Launch Checklist:**
    - [ ] All PR1-5 features working in production.
    - [ ] Analytics capturing events (verified in dashboard).
    - [ ] Error monitoring active (verified with test error).
    - [ ] Performance targets met (Lighthouse > 80).
    - [ ] E2E smoke test passes on production URL.
    - [ ] Content is accurate and up-to-date.
    - [ ] Domain configured (if applicable).
    - [ ] SSL certificate valid.

---

#### Rollback Plan

**Feature Flag / Kill Switch:**

- No feature flag needed; landing page is the default entry point.
- If analytics or error monitoring causes issues, disable by setting `NEXT_PUBLIC_ANALYTICS_PROVIDER=none` or removing Sentry DSN.

**Revert Strategy:**

- Revert PR6 via Git if landing page has critical bugs.
- Landing page revert does not affect chat functionality (chat is separate route).
- Analytics/monitoring are optional; removing them won't break core features.

**Considerations:**

- If Sentry source map upload fails, CI may fail; ensure it's non-blocking or optional.
- If analytics provider (Posthog/GA) is down, app should still work (fire-and-forget pattern).

---

#### Dependencies

**PRs that must be merged before this one:**

- **PR1:** Database schema (no direct dependency, but chat needs working DB).
- **PR2:** RAG pipeline (no direct dependency, but chat needs working RAG).
- **PR3:** Model provider + session logic (chat depends on this).
- **PR4:** Lead capture (chat depends on this).
- **PR5:** Chat interface (landing page links to chat).

**External dependencies:**

- Vercel account with production environment set up.
- Analytics service account (Vercel Analytics, Posthog, or GA4).
- Error monitoring service account (Sentry).
- Content assets (hero images, feature icons, logos).
- Domain name (optional for V1; can use Vercel subdomain).

---

#### Risks & Mitigations

**Major Risks:**

1. **Analytics Integration Complexity:**
   - Risk: Multiple analytics providers (Vercel, Posthog, GA4) may have different APIs and setup requirements.
   - Mitigation: Create abstraction layer (`analytics.ts`) to unify API. Start with simplest provider (Vercel Analytics). Test thoroughly in dev before deploying.

2. **Error Monitoring Overhead:**
   - Risk: Sentry may capture too many errors (false positives, noisy warnings) and clutter dashboard.
   - Mitigation: Configure Sentry filters to ignore known warnings (e.g., browser extensions, third-party script errors). Set sampling rate to reduce noise in dev.

3. **Performance Regression:**
   - Risk: Adding analytics and error monitoring scripts may slow down page load.
   - Mitigation: Load scripts asynchronously. Measure performance with Lighthouse before/after. Defer non-critical scripts.

4. **Mobile Responsiveness Issues:**
   - Risk: Landing page may not render correctly on all mobile devices.
   - Mitigation: Test on multiple viewport sizes (375px, 768px, 1024px). Use Chrome DevTools device emulation. Follow Tailwind's responsive design patterns.

5. **Content Clarity:**
   - Risk: Landing page copy may not resonate with target users (confusing value prop, unclear CTA).
   - Mitigation: Draft copy based on PSD positioning. Get feedback from diving community (if available). Iterate post-launch based on bounce rate and CTA click-through rate.

**Trade-offs:**

- **Simplicity vs Flexibility:** Using a single analytics provider (Vercel) is simpler but locks us into their ecosystem. Abstraction layer adds complexity but allows switching providers later. *Decision: Use abstraction layer to future-proof, but start with Vercel Analytics for V1.*
- **Static vs Dynamic Content:** Landing page is fully static (no DB queries) for performance, but can't show personalized content or dynamic stats (e.g., "Join 500+ divers"). *Decision: Static for V1; add dynamic elements in V2 if needed.*
- **Minimal vs Comprehensive SEO:** Basic meta tags are quick to implement but won't rank well in search. Full SEO (blog, backlinks, keyword optimization) takes months. *Decision: Basic SEO for V1; defer full SEO strategy to post-launch.*

**Open Questions:**

1. **Which analytics provider?**
   - Options: Vercel Analytics (simplest, built-in), Posthog (more features, self-hosted option), GA4 (most familiar).
   - Impact: Choice affects setup complexity and data ownership.
   - Recommendation: Start with Vercel Analytics for V1 (zero config). Add Posthog in V1.1 if more granular analysis is needed.

2. **Which error monitoring service?**
   - Options: Sentry (most popular, feature-rich), Vercel's built-in error tracking (simpler, less detailed).
   - Impact: Choice affects debugging capability and cost.
   - Recommendation: Use Sentry for V1 (free tier is generous). Vercel's error tracking is too basic for production.

3. **How much content on landing page?**
   - Options: Minimal (hero + CTA only), Moderate (hero + 3 features + CTA), Comprehensive (hero + features + how it works + testimonials + FAQ).
   - Impact: More content = better SEO and user education, but slower page load and longer dev time.
   - Recommendation: Moderate (hero + features + how it works) for V1. Add testimonials/FAQ in V1.1 after launch feedback.

4. **Should we include partner logos or testimonials?**
   - Context: No real partners or users yet for V1.
   - Options: Use placeholder text ("Trusted by diving enthusiasts"), skip social proof section entirely, or use generic trust badges.
   - Impact: Social proof increases trust, but fake testimonials harm credibility.
   - Recommendation: Skip specific testimonials for V1. Use generic trust language ("Built by divers, for divers") or skip section entirely.

---

## 5. Milestones & Sequence

Since this is a single PR, the milestone structure is flat:

### Milestone 1: Landing Page Foundation

**What it unlocks:** Production-ready entry point for users.

**PRs included:** PR6

**Definition of done:**

- Landing page deployed to production with all sections (Hero, Value Prop, How It Works, Footer).
- Mobile-responsive design verified on common viewports.
- CTA button navigates to chat.
- Basic SEO meta tags present.

### Milestone 2: Observability

**What it unlocks:** Ability to monitor user behavior and debug production issues.

**PRs included:** PR6

**Definition of done:**

- Analytics tracking key events (page views, CTA clicks, session starts, lead submits).
- Error monitoring capturing frontend and backend errors.
- Analytics and error monitoring verified in production.

### Milestone 3: Performance & Accessibility

**What it unlocks:** Fast, accessible experience for all users.

**PRs included:** PR6

**Definition of done:**

- Lighthouse Performance score > 80.
- Lighthouse Accessibility score > 90.
- Images optimized (WebP, responsive).
- Keyboard navigation works for all interactive elements.

### Milestone 4: E2E Testing (Pragmatic)

**What it unlocks:** Basic confidence that critical user path works, with minimal maintenance burden.

**PRs included:** PR6

**Definition of done:**

- Playwright test infrastructure set up (future-proof for expansion).
- **1 smoke test passing** covering: landing → chat → message → response → lead form.
- Smoke test integrated into CI pipeline (non-blocking for V1).
- Manual testing checklist documented and completed.
- Screenshots captured on test failure.

**Deferred to post-launch:**
- Comprehensive E2E suite (6 test files)
- LLM response content assertions
- CI blocking on E2E failure

### Milestone 5: Content Review & Launch Readiness

**What it unlocks:** Production-ready, accurate content and launch confidence.

**PRs included:** PR6

**Definition of done:**

- All RAG content reviewed for accuracy and tone.
- Safety disclaimers verified present.
- Content review script passes.
- Launch checklist complete.
- Smoke test passes on production URL.
- All success criteria from MASTER_PLAN verified:
  - Bot refuses out-of-scope queries 95%+ of time.
  - Chat responses return within 5 seconds.
  - Session persistence works across page refresh.
  - Lead delivery works (email received).

---

## 6. Risks, Trade-offs, and Open Questions

### Major Risks

1. **Analytics Integration Complexity:**
   - Different providers have different APIs and initialization patterns.
   - Mitigation: Build abstraction layer, start with simplest provider (Vercel Analytics).

2. **Error Monitoring Noise:**
   - Too many false positive errors (browser extensions, third-party scripts).
   - Mitigation: Configure Sentry filters, set appropriate sampling rate, test in dev first.

3. **Performance Impact:**
   - Adding analytics and monitoring scripts may slow down page load.
   - Mitigation: Load scripts asynchronously, measure before/after with Lighthouse, defer non-critical scripts.

4. **Content Quality:**
   - Landing page copy may not resonate with target users.
   - Mitigation: Draft copy based on PSD, iterate post-launch based on bounce rate and feedback.

5. **Mobile Responsiveness:**
   - Layout may break on certain devices or viewports.
   - Mitigation: Test on multiple viewports, use Chrome DevTools emulation, follow Tailwind responsive patterns.

6. **E2E Test Flakiness:**
   - E2E tests may be flaky due to timing issues, network latency, or LLM response variability.
   - Mitigation: **Pragmatic approach** — single smoke test that asserts behavior (response appears) not content (response says X). Manual testing covers content quality. Defer comprehensive E2E suite to post-launch.

7. **RAG Content Accuracy:**
   - Content may contain outdated or inaccurate information about certifications or dive sites.
   - Mitigation: Thorough manual review against official sources (PADI/SSI websites), safety disclaimer requirements enforced.

8. **LLM Response Variability:**
   - LLM responses may vary between test runs, making E2E tests non-deterministic.
   - Mitigation: Use assertion patterns that check for key concepts rather than exact text matches. Consider mocking LLM in some tests.

### Trade-offs

- **Static vs Dynamic Content:**
  - Static landing page is faster and simpler but can't show personalized or dynamic data.
  - Decision: Static for V1, add dynamic elements in V2 if needed.

- **Minimal vs Comprehensive SEO:**
  - Basic meta tags are quick but won't rank well; full SEO takes months.
  - Decision: Basic SEO for V1, defer comprehensive strategy to post-launch.

- **Single vs Multiple Analytics Providers:**
  - Single provider (Vercel) is simpler; abstraction layer adds complexity but allows flexibility.
  - Decision: Build abstraction layer but start with Vercel Analytics for V1.

- **Social Proof vs Credibility:**
  - Fake testimonials harm trust; skipping social proof may reduce conversion.
  - Decision: Skip specific testimonials for V1, use generic trust language or skip section.

### Open Questions

1. **Which analytics provider should we use?**
   - Options: Vercel Analytics (simplest), Posthog (more features), GA4 (most familiar).
   - Impact: Affects setup complexity, data ownership, and feature availability.
   - Recommendation: Start with Vercel Analytics for V1 (zero config). Evaluate Posthog for V1.1 if more granular analysis is needed.

2. **Which error monitoring service?**
   - Options: Sentry (feature-rich), Vercel's built-in error tracking (simpler).
   - Impact: Affects debugging capability and cost.
   - Recommendation: Use Sentry for V1 (free tier is generous). Vercel's error tracking is too basic for production debugging.

3. **How much content should the landing page have?**
   - Options: Minimal (hero + CTA), Moderate (hero + features + CTA), Comprehensive (hero + features + how it works + testimonials + FAQ).
   - Impact: More content = better education and SEO, but slower load and longer dev time.
   - Recommendation: Moderate (hero + features + how it works + footer) for V1. Add more sections in V1.1 based on user feedback.

4. **Should we include partner logos or testimonials?**
   - Context: No real partners or users yet for V1.
   - Options: Use placeholder, skip entirely, or use generic trust badges.
   - Impact: Social proof increases trust, but fake testimonials harm credibility.
   - Recommendation: Skip specific testimonials for V1. Use generic trust language ("Built by divers, for divers") or skip social proof section. Add real testimonials post-launch.

5. **What should the target performance budget be?**
   - Context: Vercel is fast, but third-party scripts (analytics, monitoring) add overhead.
   - Options: Strict budget (< 100KB JS, FCP < 1.5s) vs relaxed budget (< 300KB JS, FCP < 3s).
   - Impact: Stricter budget requires more optimization effort but better user experience.
   - Recommendation: Target FCP < 3s on 3G, LCP < 4s, Lighthouse Performance > 80. This balances user experience with realistic V1 constraints.

6. **Should E2E tests mock the LLM or use real API calls?**
   - Context: Real LLM calls make tests non-deterministic; mocks make tests faster but less realistic.
   - Options: Full mocking (deterministic, fast), Real API calls (realistic, slow, flaky), Hybrid (mock for CI, real for staging).
   - Impact: Affects test reliability, speed, and API costs.
   - **Decision for V1:** Use real API calls but **don't assert response content** — only assert that a response appears. This avoids the mocking complexity while maintaining test stability. Content quality is verified via manual testing checklist.

7. **How should content accuracy be verified?**
   - Context: Diving certification info changes periodically; content may become stale.
   - Options: Manual review only, Automated link checking, Periodic re-review schedule.
   - Impact: Affects content maintenance burden and accuracy guarantees.
   - Recommendation: Manual review for V1 launch, add `last_reviewed` frontmatter field, schedule quarterly review post-launch.

---

## Appendix: Landing Page Content Outline (Draft)

### Hero Section

**Headline:** "Your AI Diving Companion"

**Subheadline:** "Get certification guidance and dive trip planning from an AI assistant that never judges. Powered by expert-curated content."

**CTA Button:** "Start Chatting" (links to `/chat`)

**Visual:** Hero image of a diver underwater (coral reef, clear water, welcoming atmosphere).

---

### Value Proposition Section

**Headline:** "Dive into Confidence"

**Features:**

1. **Certification Navigator**
   - Icon: Compass or certificate badge
   - Title: "Find Your Path"
   - Description: "Compare PADI and SSI certifications, understand prerequisites, and plan your diving education without sales pressure."

2. **Confidence Building**
   - Icon: Heart or shield
   - Title: "No Judgment Zone"
   - Description: "Ask about fears (mask clearing, depth anxiety) and get factual, supportive answers that normalize your concerns."

3. **Trip Research**
   - Icon: Map pin or globe
   - Title: "Discover Dive Sites"
   - Description: "Explore covered destinations and find sites that match your certification level and experience."

---

### How It Works Section

**Headline:** "Three Steps to Better Diving Decisions"

**Steps:**

1. **Ask Your Questions**
   - Description: "Start a conversation about certifications, destinations, or dive planning."

2. **Get Grounded Answers**
   - Description: "Receive information backed by expert-curated content, not sales pitches."

3. **Connect with Professionals**
   - Description: "When you're ready, we'll connect you with partner dive shops and instructors."

---

### Footer

**Links:**

- About (stub page: "DovvyBuddy is built by divers, for divers.")
- Privacy Policy (stub: "Your data is never sold. Guest sessions expire after 24 hours.")
- Terms of Service (stub: "Information only. Not medical or safety advice.")
- Contact (stub: email address or contact form)

**Copyright:** "© 2025 DovvyBuddy. Built with ❤️ for the diving community."

---

**End of PR6 Plan**
