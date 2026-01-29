# E2E Testing - Pragmatic Approach for V1

## Philosophy

For a solo founder with limited resources, we take a minimal E2E approach:
- **1 smoke test** catches 80% of critical issues
- **Manual testing checklist** covers edge cases more efficiently than automated tests
- **Full E2E suite** deferred to post-launch when user base justifies the investment

## Why Minimal E2E for V1?

- E2E tests are expensive to maintain (break frequently with UI changes)
- LLM responses are non-deterministic (makes content assertions tricky)
- Solo founder time is precious (manual testing is faster at V1 scale)

## Running Tests

```bash
# Run smoke test (headless)
pnpm test:e2e

# Run with browser visible (for debugging)
pnpm test:e2e:headed

# Run with UI mode (interactive debugging)
pnpm test:e2e:ui
```

## What the Smoke Test Covers

The single smoke test (`smoke.spec.ts`) covers the critical user journey:

1. ✅ Landing page loads without errors
2. ✅ All key sections visible (Hero, Value Prop, Footer)
3. ✅ CTA button navigates to /chat
4. ✅ Chat interface loads
5. ✅ Send message (any message)
6. ✅ Response appears within 30s (don't assert content, just presence)
7. ✅ Session ID persists (check localStorage)
8. ✅ Lead form can be opened
9. ✅ Lead form fields are present and functional
10. ✅ No console errors throughout

**Key principle:** Assert **behavior**, not **content**. Don't test "response mentions PADI" — that's flaky with LLMs. Test "response appears" instead.

## Manual Testing Checklist

Before each release, manually verify the following:

### Content Quality
- [ ] Certification inquiry returns relevant info (mentions PADI/SSI)
- [ ] Trip research returns destination-specific content
- [ ] Safety disclaimers appear where expected
- [ ] Bot refuses medical/booking requests appropriately

### User Experience
- [ ] Session persists across page refresh
- [ ] Lead email is received (check inbox)
- [ ] Mobile layout works (test on real device or DevTools)
- [ ] Error states display correctly (disconnect wifi, test)

### Performance
- [ ] Page load < 3s on 3G (Chrome DevTools throttling)
- [ ] Images load and are optimized
- [ ] No layout shift (CLS < 0.1)

### Analytics & Monitoring
- [ ] Page view events fire (check analytics dashboard)
- [ ] CTA click events fire
- [ ] Session start events fire
- [ ] Lead submit events fire
- [ ] Test error logged to Sentry

## Deferred to Post-Launch (V1.1+)

The following test files are **not** implemented in V1:

- `certification-inquiry.spec.ts` — Specific certification flow assertions
- `trip-research.spec.ts` — Destination research flow
- `lead-capture-training.spec.ts` — Training lead specifics
- `lead-capture-trip.spec.ts` — Trip lead specifics
- Response content assertions (requires LLM mocking or snapshot testing)

**Rationale:** These tests provide diminishing returns at V1 scale. They're valuable when:
- Team size > 1 (CI catches regressions from parallel work)
- Deploy frequency > 1/week (regression risk is higher)
- User base > 100 active users (cost of manual testing exceeds automation cost)

## CI Integration

The smoke test runs on every PR but is **non-blocking** for V1:
- Failures generate warnings, not PR blocks
- Screenshots/videos captured on failure for debugging
- Can be made blocking post-launch when stability improves

## Tips for Debugging

1. **Use headed mode** to see what's happening:
   ```bash
   pnpm test:e2e:headed
   ```

2. **Use UI mode** for interactive debugging:
   ```bash
   pnpm test:e2e:ui
   ```

3. **Check screenshots** in `test-results/` after failures

4. **Check videos** in `test-results/` for replay of failed tests

5. **Increase timeouts** if LLM responses are slow:
   ```typescript
   await expect(responseContainer).toBeVisible({ timeout: 60000 }) // 60s
   ```

## Future Expansion

When ready to expand E2E coverage (post-launch), consider:

1. **Certification flow tests** - Test specific certification queries
2. **Destination research tests** - Test destination-specific queries
3. **Lead capture variants** - Test training vs trip lead flows
4. **Error scenarios** - Test network failures, API errors, etc.
5. **Mobile-specific tests** - Test touch interactions, viewport sizes
6. **Cross-browser tests** - Enable Firefox, Safari in `playwright.config.ts`

Add new test files to `tests/e2e/` and follow the same principle: **assert behavior, not content**.
