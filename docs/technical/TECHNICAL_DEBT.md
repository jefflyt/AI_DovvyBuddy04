# Technical Debt

**Last Updated:** January 31, 2026

---

## Active Technical Debt

### Test Suite Issues

#### 1. Skipped Session Service Tests
**Location:** `src/lib/session/__tests__/session-service.test.ts`  
**Issue:** Mock setup doesn't properly intercept Drizzle ORM query chains  
**Impact:** 2 tests skipped (97% pass rate)  
**Recommendation:** Replace with integration tests using test database  
**Priority:** Low (covered by integration tests)

#### 2. Excluded Content Ingestion Test
**Location:** `tests/integration/ingest-content.test.ts`  
**Issue:** Module-level DB import throws before `describe.skip` takes effect  
**Impact:** Test excluded from suite  
**Recommendation:** Move DB import inside test functions or use lazy loading  
**Priority:** Low (manual testing confirms functionality)

---

## Resolved Technical Debt

### Model Deprecation (January 2026)
- ✅ **Fixed:** Migrated from `llama-3.1-70b-versatile` (deprecated Jan 1, 2026) to `llama-3.3-70b-versatile`
- ✅ **Action:** Monitor Groq announcements for future deprecations

### Database Schema Migration
- ✅ **Fixed:** Migrated from `vector(1536)` (OpenAI) to `vector(768)` (Gemini embeddings)
- ✅ **Lesson:** Always verify actual database schema matches TypeScript definitions

---

## Best Practices Established

### Mock Complexity vs Integration Tests
**Lesson:** For database-heavy code with complex ORM query chains, integration tests are more maintainable than deep mocks.

### Test Environment Configuration
**Lesson:** Some SDKs (like Groq) need special configuration for test runners. Added `dangerouslyAllowBrowser: true` for Vitest context.

### Centralized Configuration
**Lesson:** Use centralized model configuration to manage provider lifecycles and prevent scattered hardcoded model names.

---

## Future Considerations

### SSE Streaming (Deferred)
**Status:** Not implemented  
**Priority:** Medium  
**Trigger:** Add when responses consistently exceed 5s generation time or user feedback indicates need for real-time UX

### Multi-Agent Orchestration
**Status:** Partially implemented (multi-agent system in place)  
**Future:** Consider ADK/Genkit for more sophisticated agent coordination if needed

---

## Tracking

Track new technical debt as GitHub issues with label `technical-debt` for better visibility and prioritization.
