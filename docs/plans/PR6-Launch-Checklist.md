# PR6 Launch Checklist

## Pre-Deployment Verification

### Code Quality
- [ ] All unit tests passing (`pnpm test`)
- [ ] Type checking passes (`pnpm typecheck`)
- [ ] Linting passes (`pnpm lint`)
- [ ] Format check passes (`pnpm format`)
- [ ] Production build succeeds (`pnpm build`)
- [ ] E2E smoke test passes (`pnpm test:e2e`)
- [ ] Content review passes (`pnpm content:review`)

### Landing Page
- [ ] Landing page loads without errors
- [ ] Hero section displays correctly (headline, subheadline, CTA)
- [ ] Value proposition section displays 3 features
- [ ] How It Works section displays 3 steps
- [ ] Social proof section displays
- [ ] Footer displays with all links
- [ ] Mobile responsive (test on 375px, 768px, 1024px viewports)
- [ ] CTA button navigates to `/chat`
- [ ] All images load correctly
- [ ] No console errors on page load

### Analytics Integration
- [ ] Analytics provider configured (NEXT_PUBLIC_ANALYTICS_PROVIDER)
- [ ] Vercel Analytics installed (@vercel/analytics)
- [ ] Page view tracking verified in browser DevTools
- [ ] CTA click event fires (check Network tab)
- [ ] Session start event fires on first chat message
- [ ] Lead submit event fires on lead form submission
- [ ] Analytics dashboard shows events (verify in production)

### Error Monitoring
- [ ] Sentry DSN configured (SENTRY_DSN)
- [ ] Sentry initialization verified (check browser console)
- [ ] Test error captured in Sentry dashboard
- [ ] Error boundary catches React errors
- [ ] Error boundary displays user-friendly message
- [ ] Source maps uploaded to Sentry (production only)

### Performance
- [ ] Lighthouse Performance score > 80
- [ ] Lighthouse Accessibility score > 90
- [ ] First Contentful Paint < 2s
- [ ] Largest Contentful Paint < 2.5s
- [ ] Cumulative Layout Shift < 0.1
- [ ] Images optimized (WebP format)
- [ ] Bundle size reasonable (< 300KB initial load)
- [ ] Page loads in < 3s on 3G throttling

### SEO
- [ ] Meta title present and descriptive
- [ ] Meta description present and compelling
- [ ] Meta keywords present
- [ ] Open Graph tags present (og:title, og:description, og:image)
- [ ] Twitter Card tags present
- [ ] Favicon present
- [ ] Apple touch icon present
- [ ] robots.txt allows indexing (if desired)

### Accessibility
- [ ] All interactive elements keyboard-accessible
- [ ] Focus indicators visible
- [ ] ARIA labels present where needed
- [ ] Semantic HTML used (header, main, section, footer)
- [ ] Color contrast meets WCAG AA standards
- [ ] Images have alt text
- [ ] Headings follow logical hierarchy (h1 → h2 → h3)

### Content Review
- [ ] All certification content reviewed for accuracy
- [ ] All destination content reviewed
- [ ] All dive site content reviewed
- [ ] Safety disclaimers present where required
- [ ] Tone is non-judgmental and supportive
- [ ] No broken internal links
- [ ] Content review script passes (`pnpm content:review`)

### Integration Testing
- [ ] Landing page → Chat navigation works
- [ ] Chat interface loads correctly
- [ ] User can send a message
- [ ] AI response appears within 30s
- [ ] Session ID persists in localStorage
- [ ] Session persists across page refresh
- [ ] Lead form can be opened
- [ ] Lead form fields are present and functional
- [ ] Lead form validation works
- [ ] Lead form submission succeeds
- [ ] Lead email received in inbox

### E2E Testing
- [ ] Playwright installed (`pnpm exec playwright install`)
- [ ] Smoke test passes (`pnpm test:e2e`)
- [ ] Screenshots captured on failure
- [ ] Test results uploaded to CI artifacts
- [ ] Manual testing checklist completed (see tests/e2e/README.md)

---

## Deployment

### Environment Variables (Vercel Dashboard)
- [ ] `NEXT_PUBLIC_APP_URL` set to production URL
- [ ] `BACKEND_URL` set to Python backend URL
- [ ] `NEXT_PUBLIC_ANALYTICS_PROVIDER` set to `vercel`
- [ ] `SENTRY_DSN` set (if using Sentry)
- [ ] `SENTRY_AUTH_TOKEN` set (for source map uploads)
- [ ] `SENTRY_ORG` set
- [ ] `SENTRY_PROJECT` set
- [ ] All other required env vars from `.env.example` set

### Vercel Settings
- [ ] Production domain configured
- [ ] SSL certificate valid
- [ ] Vercel Analytics enabled
- [ ] Auto-deployment enabled for `main` branch
- [ ] Preview deployments enabled for PRs
- [ ] Environment variables set correctly
- [ ] Build command: `pnpm build`
- [ ] Output directory: `.next`
- [ ] Install command: `pnpm install`

### Deployment Steps
1. [ ] Merge PR6 to `main` branch
2. [ ] Verify CI passes on `main`
3. [ ] Wait for Vercel auto-deployment
4. [ ] Check deployment logs for errors
5. [ ] Verify production URL loads correctly
6. [ ] Run smoke test on production URL

---

## Post-Deployment Verification

### Production Smoke Test
- [ ] Visit production URL
- [ ] Landing page loads without errors
- [ ] Click CTA button → navigates to chat
- [ ] Send test message → receive response
- [ ] Open lead form → fill and submit
- [ ] Verify lead email received
- [ ] Check Sentry dashboard for any errors
- [ ] Check Vercel Analytics for events
- [ ] Test on mobile device (real device, not emulator)

### Monitoring Setup
- [ ] Sentry alerts configured (email/Slack)
- [ ] Vercel deployment notifications enabled
- [ ] Analytics dashboard accessible
- [ ] Error monitoring dashboard accessible
- [ ] Health check endpoint working (if implemented)

### Performance Verification
- [ ] Run Lighthouse on production URL
- [ ] Performance score > 80
- [ ] Accessibility score > 90
- [ ] Best Practices score > 90
- [ ] SEO score > 90

### Final Checks
- [ ] All PR1-5 features still working
- [ ] No regressions in chat functionality
- [ ] No regressions in lead capture
- [ ] No regressions in session management
- [ ] Production logs show no critical errors
- [ ] 404 page works correctly
- [ ] 500 error page works correctly (test by throwing error)

---

## Rollback Plan

If critical issues are found post-deployment:

1. **Immediate Rollback:**
   - [ ] Revert PR6 in Git: `git revert <commit-hash>`
   - [ ] Push to `main`: `git push origin main`
   - [ ] Wait for Vercel auto-deployment
   - [ ] Verify rollback successful

2. **Disable Analytics/Monitoring (if causing issues):**
   - [ ] Set `NEXT_PUBLIC_ANALYTICS_PROVIDER=none` in Vercel
   - [ ] Remove `SENTRY_DSN` from Vercel
   - [ ] Redeploy

3. **Partial Feature Disable:**
   - Landing page cannot be disabled (it's the entry point)
   - Analytics can be disabled via env var
   - Error monitoring can be disabled via env var

---

## Launch Communication

### Internal
- [ ] Update project documentation
- [ ] Update CHANGELOG.md
- [ ] Create implementation summary in `/docs/project-management/`
- [ ] Archive manual testing checklist results

### External (if applicable)
- [ ] Announce launch to beta users
- [ ] Share production URL with stakeholders
- [ ] Update any external documentation

---

## Post-Launch Iteration

### Week 1 Tasks
- [ ] Monitor Sentry for errors (daily)
- [ ] Review Vercel Analytics data (daily)
- [ ] Check lead submission rate
- [ ] Gather user feedback
- [ ] Identify top issues/bugs

### Week 2-4 Tasks
- [ ] Address top priority issues
- [ ] Optimize performance based on real data
- [ ] Refine content based on user queries
- [ ] Consider expanding E2E test suite
- [ ] Plan V1.1 features

---

**Checklist Completed By:** _________________  
**Date:** _________________  
**Production URL:** https://dovvybuddy.com  
**Deployment Time:** _________________  
**Rollback Plan Tested:** Yes / No
