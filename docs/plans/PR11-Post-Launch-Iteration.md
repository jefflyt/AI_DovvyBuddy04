# PR11: Post-Launch Iteration & Optimization

**Branch Name:** `feature/pr11-post-launch-iteration`  
**Status:** Planned  
**Date:** December 29, 2025  
**Based on:** MASTER_PLAN.md (Phase 4 continuation), PR10a-Production-Launch-Readiness.md

---

## 1. Feature/Epic Summary

### Objective

Establish a continuous improvement cycle for DovvyBuddy based on real user behavior, performance data, and early adopter feedback collected after the initial production launch (PR9). This PR focuses on data-driven refinement of the core user experience, content quality improvements, performance optimization based on actual usage patterns, and implementation of quick wins identified during the soft launch phase.

### User Impact

**Primary Users (Divers):**
- **Prospective New Divers:** Experience improved answer relevance through refined RAG retrieval based on actual query patterns observed in production.
- **OW Divers seeking Advanced Certification:** Benefit from expanded content coverage addressing gaps identified in user conversations.
- **Trip-Planning Divers:** See faster response times through optimized LLM prompt engineering and caching strategies.
- **Mobile Users:** Experience smoother interactions through UI/UX refinements based on real device usage data.

**Secondary Impact:**
- **Partner Shops:** Receive higher-quality leads with better context and qualification signals based on conversation analysis.
- **Product Team:** Gain structured feedback loop with analytics-driven prioritization for V2 features.
- **Content Contributors:** Benefit from clear content gap analysis and update workflows.

### Dependencies

**Upstream (Must be complete):**
- **PR11a:** Production launch with analytics (Posthog/Vercel Analytics), error monitoring (Sentry), and observability infrastructure operational.
- **Soft Launch Period:** Minimum 7-14 days of production traffic with real users to generate meaningful data.
- **Analytics Data:** Session recordings, event tracking, conversion funnel data, performance metrics, error logs.

**External Dependencies:**
- **Analytics Dashboards:** Posthog dashboards configured for key metrics (session duration, message count per session, lead conversion rate, response latency).
- **Error Monitoring:** Sentry configured with sufficient retention for pattern analysis.
- **User Feedback Channel:** Simple feedback mechanism (e.g., thumbs up/down on responses, optional comment field) deployed in PR10a.

### Assumptions

- **Assumption:** Soft launch has generated 50-200+ user sessions with sufficient data to identify patterns.
- **Assumption:** At least 5-10 leads captured, providing insight into conversion quality.
- **Assumption:** Performance baseline established (p50/p95 latency, error rate, bounce rate).
- **Assumption:** Solo founder has capacity to analyze data weekly and prioritize 2-4 high-impact improvements per sprint.
- **Assumption:** Content gaps are identified but don't require major structural changes (additive improvements only).
- **Assumption:** No critical bugs or security issues requiring emergency patches (those would be hotfixes, not part of planned PR11).
- **Assumption:** V2 features (auth, multi-channel, partner dashboard) remain out of scope; PR11 focuses on V1 refinement only.

---

## 2. Complexity & Fit

### Classification: Multi-PR

### Rationale

- **Multiple distinct improvement areas:** Content refinement, RAG optimization, prompt engineering, UI polish, and analytics enhancement represent 5+ independent workstreams.
- **Data dependency:** Requires iterative analysis → hypothesis → implementation → validation cycles across multiple areas simultaneously.
- **Risk management:** Changes to prompts, RAG retrieval, or content need independent testing and rollback capabilities.
- **Incremental value:** Each improvement can be deployed independently, providing continuous value delivery rather than big-bang releases.
- **Solo founder constraint:** Breaking into smaller PRs allows for focused work sessions with clear verification checkpoints.
- **Experimentation:** Some improvements (e.g., prompt variants, retrieval tuning) may require A/B testing or feature flags, which are easier to manage as separate PRs.

### Recommended Number of PRs

**4-6 PRs**, grouped by domain:
1. **PR11a: Content Expansion & Gap Filling** (Data/Content layer)
2. **PR11b: RAG Retrieval Tuning** (Backend/RAG layer)
3. **PR11c: Prompt Engineering & Response Quality** (Backend/LLM layer)
4. **PR11d: UI/UX Refinements** (Frontend layer)
5. **PR11e: Performance Optimization** (Full-stack)
6. **PR11f: Analytics & Feedback Loop** (Observability layer) - Optional if sufficient in PR10a

---

## 3. Full-Stack Impact

### Frontend

**Pages/Components Impacted:**
- `/app/chat/page.tsx` — UI refinements based on user behavior (e.g., improved empty state, better error messaging).
- `MessageBubble.tsx` — Typography, spacing, readability improvements based on mobile usage patterns.
- `ChatInput.tsx` — Potential enhancements (character counter, send-on-enter toggle, better mobile keyboard handling).
- `LeadCaptureForm.tsx` — Field refinements based on conversion funnel drop-off analysis.
- Landing page (`/app/page.tsx`) — Copy/CTA adjustments based on bounce rate and session start analytics.

**New UI States:**
- Enhanced feedback widget (thumbs up/down with optional comment).
- Improved loading states (skeleton screens, progress indicators for long RAG queries).
- Better mobile viewport optimization (touch targets, spacing, safe areas).

**Navigation/Entry Points:**
- Potential "Example Questions" prompt suggestions to guide new users (based on top query patterns).
- Quick links to common certification pathways identified in analytics.

### Backend

**APIs to Add/Modify:**
- `POST /api/feedback` — New endpoint for capturing user feedback on responses (thumbs up/down, optional comment).
- `GET /api/analytics/insights` (Optional) — Internal endpoint for admin dashboard or weekly report generation.
- `POST /api/chat` — Refine prompt construction logic based on observed failure patterns; add caching headers for repeated queries.

**Services/Modules Impacted:**
- `src/lib/rag/retrieval.ts` — Tuning parameters (top-k, similarity threshold, re-ranking logic) based on retrieval quality analysis.
- `src/lib/prompts/` — Refine system prompts, add few-shot examples for common edge cases, improve safety guardrails based on observed misinterpretations.
- `src/lib/model-provider/` — Add response caching for common queries, implement retry logic with exponential backoff if error rate is high.
- `src/lib/session/` — Potential optimization if session lookup is a performance bottleneck.

**Validation/Auth/Error Handling:**
- Enhanced input validation for edge cases discovered in production (e.g., emoji handling, very long messages, special characters).
- More granular error categorization for better Sentry alerting.
- Rate limiting refinements based on observed abuse patterns (if any).

### Data

**Entities/Tables/Fields Involved:**
- **New Table:** `feedback` — Store user feedback on assistant responses.
  - Fields: `id`, `session_id`, `message_id`, `rating` (positive/negative/neutral), `comment` (TEXT, nullable), `created_at`.
- **content_embeddings** — Add new chunks for gap-filled content areas.
- **sessions** — Potentially add metadata fields for analytics (e.g., `user_agent`, `referrer`, `first_message_category`).
- **leads** — Add quality scoring field based on conversation depth/context richness (optional enhancement).

**Migrations/Backfills:**
- Migration to add `feedback` table.
- Migration to add optional metadata columns to `sessions` table (backward-compatible, nullable fields).
- Re-ingestion of updated content into `content_embeddings` (delete old, insert new).

**Compatibility Strategy:**
- All schema changes are additive (new tables, nullable columns) — no breaking changes.
- Content re-ingestion can happen without downtime (upsert logic or versioned embeddings).

### Infra / Config

**Env Vars/Secrets:**
- Potentially add `FEATURE_FLAG_RESPONSE_CACHE=true|false` for testing caching logic.
- `ANALYTICS_WEBHOOK_URL` (optional) for automated weekly reports.

**Feature Flags:**
- `ENABLE_FEEDBACK_WIDGET` — Toggle feedback UI on/off for gradual rollout.
- `ENABLE_RESPONSE_CACHE` — Enable/disable LLM response caching for A/B testing.
- `RAG_TOP_K` — Make retrieval parameter configurable via env var for easy tuning.

**CI/CD:**
- Add performance regression tests (response time benchmarks) to CI pipeline.
- Add content validation checks (linting Markdown, checking for broken references).

---

## 4. PR Roadmap (Multi-PR Plan)

### PR11a: Content Expansion & Gap Filling

**Goal**

Address content gaps identified through user conversation analysis and expand coverage for high-demand topics that currently fall back to generic responses.

**Scope**

**In Scope:**
- Analyze chat logs (anonymized) to identify top 10-15 topics with insufficient RAG retrieval results.
- Write new Markdown content for identified gaps:
  - Expanded certification prerequisite details (medical requirements, age limits, skill prerequisites).
  - Additional destination/dive site content if users are asking about uncovered locations.
  - Safety reference content (buoyancy control, nitrogen narcosis, decompression sickness basics) within information-only guardrails.
  - FAQ-style content for common edge cases ("Can I dive with asthma?", "How long does certification take?").
- Update existing content based on observed user confusion (clarify ambiguous sections, add examples).
- Re-run content ingestion pipeline to update embeddings.

**Out of Scope:**
- Major content restructuring (taxonomy changes).
- Content for destinations beyond initial 1-2 pilot locations.
- User-generated content or community contributions.
- Multilingual content (English only).

**Backend Changes**

None — content-only update.

**Frontend Changes**

None — improved responses appear automatically via updated RAG retrieval.

**Data Changes**

- **Migrations:** None.
- **Content Ingestion:**
  - Run `pnpm content:ingest` with updated Markdown files.
  - Strategy: Delete old embeddings for updated files (by `content_path`), insert new ones.
  - Verify updated embedding count in database.
- **Backward Compatibility:** Seamless — new embeddings are additive or replacements.

**Testing**

- **Unit Tests:** None required (content-only).
- **Integration Tests:**
  - Test retrieval function with queries that previously had poor results; verify improved context.
- **Manual Checks:**
  - Query bot with 5-10 previously-problematic questions; verify improved answers.
  - Spot-check that existing good responses haven't degraded.

**Verification**

Commands:
- `pnpm content:ingest`
- `pnpm test` (run retrieval integration tests)

Manual verification checklist:
1. Run ingestion script, verify no errors.
2. Query database: `SELECT COUNT(*) FROM content_embeddings;` — verify count increased.
3. Test bot with sample gap questions, verify relevant chunks retrieved.
4. Spot-check 3-5 existing good queries to ensure no regression.

**Rollback Plan**

- **Revert Strategy:** 
  - Keep previous content in git history.
  - Re-run ingestion with previous commit's content to restore old embeddings.
  - No feature flag needed (content changes are low-risk).

**Dependencies**

- Soft launch analytics data identifying content gaps.
- Access to anonymized chat logs for gap analysis.

**Risks & Mitigations**

- **Risk:** New content introduces factual errors or safety advice violations.
  - **Mitigation:** Peer review content with dive professional; run safety prompt tests with new content.
- **Risk:** Embeddings for updated content don't improve retrieval quality.
  - **Mitigation:** Test retrieval with sample queries before deploying; tune chunk size if needed.

---

### PR11b: RAG Retrieval Tuning

**Goal**

Optimize RAG retrieval parameters and logic based on observed retrieval quality issues, improving answer relevance and reducing hallucination risk.

**Scope**

**In Scope:**
- Analyze retrieval logs to identify:
  - Queries with low similarity scores (poor retrieval).
  - Queries returning irrelevant chunks (false positives).
  - Queries missing relevant chunks that exist in corpus (false negatives).
- Tune retrieval parameters:
  - Adjust `top_k` (number of chunks returned) — test 3, 5, 7, 10.
  - Adjust similarity threshold (minimum cosine similarity) — test 0.5, 0.6, 0.7.
  - Implement re-ranking logic (e.g., boost chunks from certain content types for specific query patterns).
- Implement query expansion/rewriting for ambiguous queries (e.g., "OW" → "Open Water certification").
- Add retrieval metadata to session logs for debugging (chunk IDs, similarity scores).

**Out of Scope:**
- Switching to a different embedding model (defer to major version).
- Implementing hybrid search (keyword + vector) — defer unless critical gap identified.
- Semantic chunking improvements (keep existing 500-800 token strategy unless proven inadequate).

**Backend Changes**

- **`src/lib/rag/retrieval.ts`:**
  - Add configurable parameters (`topK`, `similarityThreshold`) with env var fallbacks.
  - Implement re-ranking function (optional, if needed).
  - Add query preprocessing (expansion/normalization).
  - Return retrieval metadata (chunk IDs, scores) in response.
- **`/api/chat`:**
  - Log retrieval metadata to structured logs (for analysis).
  - Pass tuned parameters to retrieval function.

**Frontend Changes**

None (backend-only improvement).

**Data Changes**

None — uses existing `content_embeddings` table.

**Infra / Config**

- **Env Vars:**
  - `RAG_TOP_K=5` (default, configurable)
  - `RAG_SIMILARITY_THRESHOLD=0.6` (default, configurable)
- **Feature Flags:** None (tuning params controlled via env vars).

**Testing**

- **Unit Tests:**
  - Test query normalization function with edge cases.
  - Test re-ranking logic (if implemented).
- **Integration Tests:**
  - Golden dataset: 20-30 representative queries with expected "good" chunks.
  - Assert that retrieval returns relevant chunks above threshold.
  - Test retrieval with various `topK` and `threshold` values.
- **Manual Checks:**
  - Test with 10 real user queries from analytics; verify improved relevance.

**Verification**

Commands:
- `pnpm test` (run retrieval integration tests)
- `pnpm dev` (manual testing)

Manual verification checklist:
1. Deploy with `RAG_TOP_K=5, RAG_SIMILARITY_THRESHOLD=0.6`.
2. Test 10 sample queries, review retrieved chunks and similarity scores.
3. Adjust parameters, repeat testing.
4. Compare answer quality before/after tuning with side-by-side tests.

**Rollback Plan**

- **Feature Flag:** Use env vars to revert to previous parameter values (`RAG_TOP_K=3, RAG_SIMILARITY_THRESHOLD=0.5`).
- **Revert Strategy:** Git revert PR11b; redeploy with old parameters.

**Dependencies**

- Retrieval quality analysis from soft launch data.
- Sample queries with known-good expected chunks for testing.

**Risks & Mitigations**

- **Risk:** Increased `topK` adds latency or noise to LLM context.
  - **Mitigation:** Benchmark retrieval latency; monitor LLM response quality with different `topK` values.
- **Risk:** Stricter threshold excludes relevant chunks for edge-case queries.
  - **Mitigation:** A/B test with small cohort; monitor session satisfaction (via feedback widget).

---

### PR11c: Prompt Engineering & Response Quality

**Goal**

Refine LLM system prompts and few-shot examples based on observed response quality issues, reducing hallucinations, improving safety guardrail adherence, and enhancing conversational tone.

**Scope**

**In Scope:**
- Analyze LLM responses for common failure modes:
  - Hallucinations (inventing facts not in RAG context).
  - Safety violations (giving medical/instructor advice).
  - Tone issues (too formal, not reassuring enough, inconsistent personality).
  - Incomplete answers (missing disclaimers, not addressing question fully).
- Refine system prompts (`src/lib/prompts/`):
  - Add explicit "NEVER invent facts" instruction.
  - Strengthen safety guardrails with negative examples.
  - Add few-shot examples for common scenarios (new diver fears, agency comparison, trip planning).
  - Improve conversational tone guidance (friendly, non-judgmental, confidence-building).
- Implement prompt testing framework:
  - Create test suite of 30-50 representative user queries.
  - Assert expected behavior (e.g., refusal for medical questions, grounded answers, proper disclaimers).
- Optimize prompt length for performance (reduce token usage while maintaining quality).

**Out of Scope:**
- Switching LLM models (stay with Groq/Gemini).
- Advanced prompt techniques (Chain-of-Thought, ReAct) — defer to V2 unless critical need identified.
- Dynamic prompt construction based on user profile (defer to post-auth V2).

**Backend Changes**

- **`src/lib/prompts/`:**
  - Update `system-prompt-base.ts` with refined instructions.
  - Update `certification-navigator-prompt.ts` and `trip-research-prompt.ts` with few-shot examples.
  - Add `prompt-test-suite.ts` for automated testing.
- **`/api/chat`:**
  - No changes (uses updated prompts automatically).
- **Testing Infrastructure:**
  - Add prompt testing script (`scripts/test-prompts.ts`) that runs test queries against LLM and validates responses.

**Frontend Changes**

None (backend-only prompt changes).

**Data Changes**

None.

**Infra / Config**

- **Feature Flags (Optional):**
  - `PROMPT_VERSION=v1|v2` — A/B test prompt variants if needed.
- **Env Vars:** None.

**Testing**

- **Prompt Test Suite:**
  - 30-50 test cases covering:
    - Common certification questions (should get grounded answers).
    - Medical/safety questions (should refuse gracefully).
    - Trip planning queries (should use destination data from RAG).
    - Edge cases (ambiguous queries, multi-part questions, follow-ups).
  - Automated assertions:
    - Check for safety refusal keywords in responses to out-of-scope queries.
    - Check for citation/grounding indicators in factual responses.
    - Check for disclaimers in certification pathway answers.
- **Manual Review:**
  - Human review of 20 responses for tone, completeness, accuracy.

**Verification**

Commands:
- `pnpm test:prompts` (new script to run prompt test suite)
- `pnpm test` (existing test suite)

Manual verification checklist:
1. Run prompt test suite, verify 95%+ pass rate.
2. Manually test 10 real user queries from analytics, compare before/after responses.
3. Check for improved tone, reduced hallucinations, better safety adherence.
4. Verify token usage hasn't increased significantly (check LLM API logs).

**Rollback Plan**

- **Feature Flag:** Use `PROMPT_VERSION=v1` to revert to previous prompts if quality degrades.
- **Revert Strategy:** Git revert PR11c; redeploy with old prompts.

**Dependencies**

- Response quality analysis from soft launch data.
- Sample user queries with known failure modes.

**Risks & Mitigations**

- **Risk:** Prompt changes introduce new failure modes (e.g., over-cautious refusals, verbose responses).
  - **Mitigation:** Comprehensive prompt test suite; gradual rollout with monitoring.
- **Risk:** Increased prompt length adds latency or cost.
  - **Mitigation:** Monitor token usage and response latency; optimize prompt length.

---

### PR11d: UI/UX Refinements

**Goal**

Polish the chat interface and landing page based on user behavior analytics, improving usability, mobile experience, and conversion rates.

**Scope**

**In Scope:**
- Analyze session recordings (Posthog) for UX friction points:
  - Interaction delays (slow taps, abandoned inputs).
  - Scroll/navigation patterns (dead zones, confusion points).
  - Mobile-specific issues (tiny touch targets, keyboard overlap, awkward layouts).
- Implement UI improvements:
  - **Chat Interface:**
    - Better mobile keyboard handling (input field stays visible, auto-scroll to latest message).
    - Improved typing indicator and loading states (skeleton screens).
    - Enhanced message readability (font size, line height, contrast).
    - Touch target optimization (larger buttons, better spacing).
    - "Example Questions" prompt suggestions to guide new users (3-5 suggested prompts based on top query patterns).
  - **Lead Capture Form:**
    - Reduce friction based on drop-off analysis (simplify fields, better validation feedback).
    - Add progress indicator for multi-step forms (if applicable).
  - **Landing Page:**
    - Refine copy and CTAs based on bounce rate analysis.
    - Add social proof or trust indicators (testimonials, partner logos) if available.
    - Optimize hero section for mobile viewport.
- Accessibility improvements:
  - Ensure keyboard navigation works smoothly.
  - Add ARIA labels where missing.
  - Test with screen reader.

**Out of Scope:**
- Major redesign or new pages.
- Complex animations or transitions (keep lightweight).
- Dark mode (defer to V2).
- Accessibility audit beyond basic compliance (full WCAG 2.1 AA compliance deferred).

**Backend Changes**

None (frontend-only changes).

**Frontend Changes**

- **`src/components/chat/`:**
  - Update `MessageBubble.tsx` for improved readability (typography, spacing).
  - Update `ChatInput.tsx` for better mobile keyboard handling.
  - Update `MessageList.tsx` for auto-scroll behavior and skeleton loading.
  - Add `ExampleQuestions.tsx` component (shows 3-5 suggested prompts in empty state).
- **`src/components/lead/LeadCaptureForm.tsx`:**
  - Simplify form fields, improve validation feedback.
- **`/app/page.tsx` (Landing Page):**
  - Refine hero copy and CTA button text/placement.
  - Add trust indicators (optional, if content available).
- **`globals.css`:**
  - Adjust base font sizes, line heights, spacing for mobile.
  - Improve touch target sizes (min 44x44px).

**Data Changes**

None.

**Infra / Config**

None.

**Testing**

- **Manual Testing:**
  - Test on 3-5 real mobile devices (iOS, Android, various screen sizes).
  - Test with keyboard navigation (tab through all interactive elements).
  - Test with VoiceOver/TalkBack screen readers.
- **Visual Regression Tests (Optional):**
  - Screenshot tests for key views (landing page, chat interface, lead form).
- **Analytics Validation:**
  - Deploy changes, monitor bounce rate, session duration, lead conversion rate for 7 days.

**Verification**

Commands:
- `pnpm dev` (manual testing)
- `pnpm build` (verify build succeeds)

Manual verification checklist:
1. Test chat interface on iPhone Safari, Android Chrome, desktop (Chrome, Firefox).
2. Verify typing indicator, loading states, auto-scroll work correctly.
3. Verify "Example Questions" appear on empty chat state.
4. Test lead form submission on mobile, verify all fields accessible and validation clear.
5. Test landing page CTA flow on mobile, verify no layout shifts or broken interactions.
6. Tab through all interactive elements, verify keyboard navigation works.
7. Test with screen reader (VoiceOver on iOS), verify core flows are understandable.

**Rollback Plan**

- **Revert Strategy:** Git revert PR10d; redeploy previous UI.
- **Feature Flag (Optional):** Use `ENABLE_NEW_UI=true|false` for gradual rollout if changes are significant.

**Dependencies**

- Session recording analysis from Posthog (minimum 50-100 sessions).
- Analytics data on bounce rate, session duration, lead conversion rate.

**Risks & Mitigations**

- **Risk:** UI changes break existing mobile interactions or introduce new bugs.
  - **Mitigation:** Thorough manual testing on real devices; deploy to staging first.
- **Risk:** Changes don't improve conversion metrics.
  - **Mitigation:** A/B test with small cohort if possible; monitor analytics closely for 7 days post-deploy.

---

### PR11e: Performance Optimization

**Goal**

Reduce response latency, optimize bundle size, and improve perceived performance based on real-world performance metrics from production.

**Scope**

**In Scope:**
- Analyze performance bottlenecks:
  - Identify slow API endpoints (response time p95).
  - Identify slow database queries (session lookup, RAG retrieval).
  - Identify large frontend bundle sizes (JavaScript, CSS).
  - Identify slow LLM responses (RAG + prompt + inference time).
- Backend optimizations:
  - Implement response caching for common queries (LRU cache in memory or Redis).
  - Add database connection pooling if not already configured.
  - Optimize RAG retrieval query (add indexes if missing).
  - Implement streaming responses for LLM (return partial responses as they generate, improving perceived speed).
- Frontend optimizations:
  - Code splitting (lazy load non-critical components).
  - Image optimization (use Next.js Image component, WebP format).
  - Reduce JavaScript bundle size (analyze with webpack-bundle-analyzer, remove unused deps).
  - Improve Lighthouse scores (target: >90 Performance, >90 Accessibility).

**Out of Scope:**
- CDN optimization beyond Vercel defaults (defer unless critical issue).
- Server-side rendering optimizations beyond Next.js defaults (defer to major refactor).
- Database scaling (read replicas, sharding) — defer unless traffic exceeds capacity.

**Backend Changes**

- **`/api/chat`:**
  - Add response caching middleware (check cache before calling LLM).
  - Implement streaming response (SSE or chunked transfer encoding) for LLM output.
- **`src/db/client.ts`:**
  - Configure connection pooling (e.g., `pg.Pool` with max connections).
- **`src/lib/rag/retrieval.ts`:**
  - Add database indexes on `content_embeddings.embedding` (if not already indexed for vector similarity).
  - Optimize query (e.g., limit result set earlier, avoid unnecessary joins).
- **`src/lib/model-provider/`:**
  - Add request timeout and retry logic with circuit breaker (avoid cascading failures).

**Frontend Changes**

- **Code Splitting:**
  - Lazy load `LeadCaptureForm.tsx` and other non-critical components.
  - Use `React.lazy()` and `Suspense` for route-based splitting.
- **`next.config.js`:**
  - Enable `swcMinify` (if not already enabled).
  - Configure image optimization settings.
- **Bundle Analysis:**
  - Add `@next/bundle-analyzer` to dev dependencies.
  - Run analysis, remove unused dependencies (e.g., unused Tailwind classes).

**Data Changes**

- **Migrations:**
  - Add index on `content_embeddings.embedding` (pgvector-specific index: `ivfflat` or `hnsw`).
  - Add index on `sessions.id` (if not already primary key).
  - Add index on `sessions.expires_at` (for cleanup queries).

**Backward Compatibility:** Indexes are additive, no breaking changes.

**Infra / Config**

- **Env Vars:**
  - `ENABLE_RESPONSE_CACHE=true` (toggle caching).
  - `CACHE_TTL_SECONDS=3600` (cache expiration).
- **Feature Flags:** None (caching controlled via env var).
- **CI/CD:**
  - Add Lighthouse CI to PR checks (fail if Performance score <80).

**Testing**

- **Performance Benchmarks:**
  - Measure baseline response times (p50, p95, p99) for `/api/chat` with representative queries.
  - Measure frontend bundle size before optimizations.
  - Run Lighthouse audit before optimizations.
- **Post-Optimization:**
  - Re-measure response times, verify improvement (target: 20-30% reduction in p95).
  - Re-measure bundle size, verify reduction (target: 10-20% smaller).
  - Re-run Lighthouse, verify score improvements.
- **Load Testing (Optional):**
  - Use Artillery or k6 to simulate 50 concurrent users, verify no degradation.

**Verification**

Commands:
- `pnpm build` (verify build succeeds)
- `pnpm analyze` (run bundle analyzer)
- `pnpm lighthouse` (run Lighthouse audit — add script)

Manual verification checklist:
1. Deploy to staging with caching enabled.
2. Test 10 common queries, verify caching works (check response headers, verify cache hits in logs).
3. Test streaming responses (verify partial LLM output appears progressively).
4. Run Lighthouse audit, verify Performance >90, Accessibility >90.
5. Check Vercel Analytics for bundle size, verify reduction.
6. Monitor production for 48 hours, verify no regressions in error rate or latency.

**Rollback Plan**

- **Feature Flag:** Set `ENABLE_RESPONSE_CACHE=false` to disable caching if issues arise.
- **Revert Strategy:** Git revert PR10e; redeploy with old code.
- **Database Indexes:** Indexes can remain (no harm if unused); drop if they cause write performance issues (unlikely).

**Dependencies**

- Performance baseline data from PR9 monitoring (p50/p95 latency, bundle size, Lighthouse scores).
- Production traffic patterns (identify cacheable queries).

**Risks & Mitigations**

- **Risk:** Response caching returns stale data or breaks personalization.
  - **Mitigation:** Cache only for identical queries with no session-specific context; set short TTL (1 hour).
- **Risk:** Streaming responses complicate error handling or break client-side parsing.
  - **Mitigation:** Implement streaming with fallback to full response; test thoroughly on multiple browsers.
- **Risk:** Database indexes slow down writes (inserts/updates).
  - **Mitigation:** Monitor write performance; pgvector indexes are read-optimized and shouldn't significantly impact writes for small corpus.

---

### PR11f: Analytics & Feedback Loop (Optional)

**Goal**

Enhance observability and establish a structured feedback loop for continuous improvement based on user behavior and satisfaction signals.

**Scope**

**In Scope:**
- Implement user feedback widget:
  - Add thumbs up/down buttons on each assistant message.
  - Optional text field for user comments.
  - Store feedback in `feedback` table.
- Create analytics dashboard (internal):
  - Key metrics: session count, avg. messages per session, lead conversion rate, feedback sentiment.
  - Top user queries (aggregate, anonymized).
  - Content gap analysis (queries with low RAG retrieval scores).
  - Error rate and types (from Sentry).
- Automated weekly report:
  - Email or Slack summary of key metrics + actionable insights.
  - Highlight content gaps, prompt failure patterns, performance issues.
- Refinement workflow:
  - Document process for analyzing feedback and prioritizing improvements.
  - Create template for quick-win improvements (content updates, prompt tweaks).

**Out of Scope:**
- Public-facing analytics or user dashboards.
- Advanced BI tools (Tableau, Looker) — use Posthog/Retool for V1.
- Real-time alerting beyond Sentry (defer complex monitoring to V2).

**Backend Changes**

- **`POST /api/feedback`:**
  - Accept: `{ sessionId, messageId, rating, comment? }`.
  - Validate payload, save to `feedback` table.
  - Return: `{ success }`.
- **`GET /api/analytics/insights` (Internal Only):**
  - Aggregate feedback sentiment, top queries, content gaps.
  - Protected by admin auth token (simple bearer token for V1).
- **Automated Report Script:**
  - `scripts/generate-weekly-report.ts` — queries database and Posthog API, generates Markdown report, sends via email (Resend).

**Frontend Changes**

- **`MessageBubble.tsx`:**
  - Add thumbs up/down buttons below each assistant message.
  - On click, call `/api/feedback`, show success toast.
  - Optional: show text input on negative feedback for user comment.
- **Admin Dashboard (Optional):**
  - Simple page (`/app/admin/page.tsx`) showing key metrics from `/api/analytics/insights`.
  - Protected by hardcoded password or API token (basic auth for V1).

**Data Changes**

- **Migration:**
  - Create `feedback` table:
    - `id` UUID PRIMARY KEY
    - `session_id` UUID REFERENCES sessions(id)
    - `message_id` TEXT NOT NULL
    - `rating` TEXT NOT NULL CHECK (rating IN ('positive', 'negative', 'neutral'))
    - `comment` TEXT (nullable)
    - `created_at` TIMESTAMP DEFAULT NOW()
  - Add indexes on `session_id` and `created_at`.
- **Backward Compatibility:** Additive, no breaking changes.

**Infra / Config**

- **Env Vars:**
  - `ADMIN_API_TOKEN` — Simple bearer token for admin endpoints.
  - `WEEKLY_REPORT_EMAIL` — Email address for automated report.
- **Feature Flags:**
  - `ENABLE_FEEDBACK_WIDGET=true` — Toggle feedback UI on/off.

**Testing**

- **Unit Tests:**
  - Test `/api/feedback` validation (invalid session ID, missing rating).
- **Integration Tests:**
  - Test feedback submission end-to-end (UI → API → DB).
  - Test analytics query aggregation logic.
- **Manual Checks:**
  - Submit feedback via UI, verify stored in database.
  - Call `/api/analytics/insights`, verify JSON response with metrics.
  - Run weekly report script, verify email sent with correct data.

**Verification**

Commands:
- `pnpm db:migrate` (apply feedback table migration)
- `pnpm test` (run unit/integration tests)
- `pnpm report:weekly` (new script to generate report)

Manual verification checklist:
1. Deploy with `ENABLE_FEEDBACK_WIDGET=true`.
2. Send a chat message, verify thumbs up/down buttons appear.
3. Click thumbs up, verify success toast and DB entry.
4. Click thumbs down, verify comment field appears, submit comment, verify DB entry.
5. Access `/admin` with API token, verify metrics displayed correctly.
6. Run weekly report script, verify email received with actionable insights.

**Rollback Plan**

- **Feature Flag:** Set `ENABLE_FEEDBACK_WIDGET=false` to hide feedback UI if issues arise.
- **Revert Strategy:** Git revert PR10f; redeploy without feedback features.
- **Database:** Drop `feedback` table if needed (no foreign key dependencies breaking other features).

**Dependencies**

- PR9 analytics infrastructure (Posthog) operational.
- Production traffic (minimum 50 sessions) to generate meaningful insights.

**Risks & Mitigations**

- **Risk:** Low feedback submission rate (users don't engage with widget).
  - **Mitigation:** Make widget unobtrusive but visible; consider incentive (e.g., "Help us improve!").
- **Risk:** Negative feedback is discouraging without actionable insights.
  - **Mitigation:** Focus on patterns in feedback, not individual comments; prioritize high-impact improvements.
- **Risk:** Admin dashboard becomes unmaintained or unused.
  - **Mitigation:** Start with automated weekly report only; build dashboard only if manual review is frequent.

---

## 5. Milestones & Sequence

### Milestone 1: Content & Retrieval Quality (Weeks 1-2)

**Goal:** Improve answer relevance and coverage based on soft launch data.

**PRs Included:**
- **PR11a: Content Expansion & Gap Filling**
- **PR11b: RAG Retrieval Tuning**

**What "Done" Means:**
- Top 10 content gaps addressed with new Markdown content.
- RAG retrieval parameters tuned, golden test dataset passes at 90%+ relevance.
- User queries that previously had poor answers now return relevant, grounded responses.

---

### Milestone 2: Response Quality & User Experience (Weeks 2-3)

**Goal:** Polish LLM outputs and refine UI based on user behavior.

**PRs Included:**
- **PR11c: Prompt Engineering & Response Quality**
- **PR11d: UI/UX Refinements**

**What "Done" Means:**
- Prompt test suite passes at 95%+ (safety, grounding, tone).
- Mobile UX friction points addressed (keyboard handling, touch targets, readability).
- Landing page bounce rate reduced by 10-20% (monitored over 7 days).
- Lead form conversion rate improved or stable (no regression).

---

### Milestone 3: Performance & Observability (Weeks 3-4)

**Goal:** Optimize speed and establish continuous improvement feedback loop.

**PRs Included:**
- **PR11e: Performance Optimization**
- **PR11f: Analytics & Feedback Loop** (Optional)

**What "Done" Means:**
- Chat response latency (p95) reduced by 20-30%.
- Frontend bundle size reduced by 10-20%.
- Lighthouse Performance score >90, Accessibility score >90.
- User feedback widget deployed and collecting data (if PR10f included).
- Automated weekly analytics report generating actionable insights.

---

## 6. Risks, Trade-offs, and Open Questions

### Major Risks

1. **Insufficient Data for Optimization:**
   - **Risk:** Soft launch traffic too low to identify meaningful patterns (e.g., <50 sessions).
   - **Mitigation:** Extend soft launch period to 3-4 weeks if needed; use synthetic test queries to supplement real data; prioritize qualitative user feedback over quantitative metrics initially.

2. **Content Update Doesn't Improve Retrieval:**
   - **Risk:** New content is ingested but doesn't improve RAG results due to poor chunking, off-topic focus, or embedding quality issues.
   - **Mitigation:** Test retrieval with sample queries before deploying; review chunk boundaries manually; tune embedding model parameters if needed (e.g., adjust chunk size).

3. **Prompt Changes Introduce New Failure Modes:**
   - **Risk:** Refined prompts over-correct (e.g., refuse too many in-scope queries, become overly verbose, lose conversational tone).
   - **Mitigation:** Comprehensive prompt test suite with before/after comparison; A/B test with small cohort if feasible; monitor feedback sentiment closely for 7 days post-deploy.

4. **Performance Optimizations Break Functionality:**
   - **Risk:** Caching returns stale data; streaming responses break on certain browsers; database indexes slow down writes.
   - **Mitigation:** Feature flags for caching/streaming; thorough cross-browser testing; monitor write latency and error rates closely; rollback plan ready.

5. **Solo Founder Bandwidth:**
   - **Risk:** 4-6 PRs may be too much to implement, test, and deploy within a reasonable timeframe (4-6 weeks).
   - **Mitigation:** Prioritize PRs by impact (start with PR10a/b/c, defer PR10f if time-constrained); timebox each PR to 1 week; accept "good enough" over "perfect" for V1 iteration.

### Trade-offs

1. **Breadth vs. Depth of Improvements:**
   - **Trade-off:** Covering multiple areas (content, retrieval, prompts, UI, performance) vs. deep optimization in one area.
   - **Decision:** Favor breadth for PR10 — address multiple observed pain points incrementally rather than over-engineering one area. Deep optimization (e.g., advanced RAG techniques, LLM fine-tuning) deferred to V2.

2. **Manual Analysis vs. Automated Tools:**
   - **Trade-off:** Time-intensive manual log/session analysis vs. investing in automated analytics dashboards.
   - **Decision:** Start with manual analysis for PR10a-c (faster to act on); invest in PR10f (analytics dashboard) only if feedback loop proves valuable. Solo founder time is precious — avoid premature tooling.

3. **A/B Testing vs. All-at-Once Deployment:**
   - **Trade-off:** Rigorous A/B testing for each change vs. deploying improvements quickly and monitoring overall metrics.
   - **Decision:** Deploy all-at-once for PR10 (simpler for solo founder); use feature flags for riskier changes (caching, streaming); monitor aggregate metrics (response quality, lead conversion) for regression. A/B testing infrastructure deferred to V2 when traffic scales.

4. **Content Scope vs. Quality:**
   - **Trade-off:** Expanding content coverage broadly (more destinations, more topics) vs. refining existing content deeply.
   - **Decision:** For PR10a, focus on depth over breadth — fill gaps in existing 1 destination + certification topics rather than adding new destinations. Quality > quantity for V1 trust-building.

### Open Questions

1. **What is "good enough" retrieval quality?**
   - **Question:** What threshold of retrieval accuracy (e.g., "relevant chunk in top-5 results") should PR10b target?
   - **Impact:** Determines how much time to invest in RAG tuning vs. moving on.
   - **Recommendation:** Target 80-90% relevance for golden test dataset (20-30 queries). If already above 75%, deprioritize PR10b in favor of prompt/content work.

2. **Should PR10f be included in initial scope?**
   - **Question:** Is feedback widget + analytics dashboard critical for PR10, or can it be deferred to PR11 (ongoing ops)?
   - **Impact:** Determines PR10 timeline (4 weeks vs. 6 weeks).
   - **Recommendation:** Include minimal version (feedback widget + simple metrics query) in PR10f; defer automated reports and admin dashboard to post-PR10 if time-constrained. Feedback widget is high-value (qualitative data for future iterations).

3. **Which performance optimization has highest ROI?**
   - **Question:** Should PR10e prioritize backend (response caching, DB optimization) or frontend (bundle size, code splitting)?
   - **Impact:** Determines where to focus engineering effort if time is limited.
   - **Recommendation:** Analyze PR9 metrics first. If response latency p95 >7s, prioritize backend caching. If bundle size >500KB or Lighthouse Performance <80, prioritize frontend optimization. If both are acceptable, defer PR10e entirely and focus on content/prompt quality (PR10a-c).

4. **How to handle multi-turn conversation context in prompt optimization?**
   - **Question:** PR10c focuses on single-turn prompts. Should we optimize for multi-turn conversations (follow-up questions, context retention)?
   - **Impact:** Prompt design complexity; testing scope.
   - **Recommendation:** Analyze session data — if avg. session length is <3 messages, optimize for single-turn. If >5 messages, add few-shot examples for follow-up handling in PR10c.

5. **Should content updates be versioned or replaced in-place?**
   - **Question:** Should old content embeddings be preserved (versioned) or overwritten when updating content in PR10a?
   - **Impact:** Database storage, rollback strategy, content A/B testing.
   - **Recommendation:** For PR10, replace in-place (delete old embeddings by `content_path`, insert new). Version control via git history is sufficient. Implement versioned embeddings only if A/B testing content becomes a priority in V2.

---

## 7. Summary

**PR10: Post-Launch Iteration & Optimization** is a multi-PR epic (4-6 PRs) focused on data-driven refinement of DovvyBuddy V1 based on soft launch insights. The roadmap balances content quality, technical performance, and user experience improvements across the full stack, with each PR independently deployable and testable.

### Priority Order

The solo founder should prioritize PRs by impact:

1. **PR10a (Content)** — Highest impact on answer quality; lowest technical risk.
2. **PR10c (Prompts)** — High impact on response quality; moderate effort.
3. **PR10b (RAG)** — Medium impact; dependent on observed retrieval issues.
4. **PR10d (UI/UX)** — Medium impact; improves conversion and retention.
5. **PR10e (Performance)** — Depends on baseline metrics; defer if acceptable.
6. **PR10f (Analytics)** — Optional; high value for long-term iteration.

### Recommended Timeline

- **Week 1:** PR10a (Content Expansion)
- **Week 2:** PR10b (RAG Tuning) + PR10c (Prompt Engineering) — can be parallelized if founder is comfortable with both areas
- **Week 3:** PR10d (UI/UX Refinements)
- **Week 4:** PR10e (Performance Optimization) and/or PR10f (Analytics & Feedback) — prioritize based on Week 1-3 learnings

### Success Criteria for PR10 Epic

- Answer relevance improved (qualitative assessment: 80%+ of test queries return grounded, helpful responses).
- User satisfaction signals positive (feedback widget sentiment >60% positive, or session duration increases).
- Performance targets met (p95 response time <5s, Lighthouse Performance >90).
- Content gaps addressed (top 10 missing topics covered).
- Continuous improvement process established (weekly analytics review, clear backlog of next improvements).
