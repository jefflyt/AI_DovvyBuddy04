# Archived Tests

## Why Archived?

Tests in this directory are **not currently running** but are preserved for future reference or migration.

## Integration Tests (Vitest)

**Location:** `integration-tests-vitest/`  
**Status:** Archived on 2026-01-30  
**Reason:**

- These tests have AbortSignal compatibility issues in Node.js test environment
- They require manual backend server setup (complex, error-prone)
- **E2E tests with Playwright provide better coverage** of the same functionality

**Coverage:**

- 30 integration tests covering API client, session persistence, and lead capture
- All functionality is **already covered by E2E smoke test** in `tests/e2e/smoke.spec.ts`

**Future Considerations:**
If you want to use these tests:

1. Fix AbortSignal mocking issues in Node.js environment
2. Set up automated backend server spawning for tests
3. Or convert to additional Playwright E2E scenarios (recommended)

## When to Unarchive

- You need API-level unit tests (not just browser E2E)
- You fix Node.js fetch/AbortSignal compatibility
- You set up proper test backend infrastructure

---

**Recommendation:** Focus on E2E tests. They're more reliable and test real user flows.
