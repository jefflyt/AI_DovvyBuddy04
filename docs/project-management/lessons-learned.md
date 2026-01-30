# Lessons Learned

**Last Updated:** January 31, 2026

---

## Python Backend Migration (PR3.2)

### Database Schema Evolution
**Challenge:** Initial schema used `vector(1536)` for OpenAI embeddings, but we switched to Gemini  
**Solution:** Migrated to `vector(768)` using `drizzle-kit push`  
**Lesson:** Always verify actual database schema matches code definitions. Don't assume migrations are correct.

### Model Lifecycle Management
**Challenge:** Groq deprecated `llama-3.1-70b-versatile` on January 1, 2026 without much notice  
**Solution:** Updated to `llama-3.3-70b-versatile` across entire codebase  
**Lesson:** 
- Track model deprecation timelines proactively
- Use centralized configuration for model names
- Subscribe to provider announcements

### Test Environment Configuration
**Challenge:** Groq SDK blocks browser-like environments, including Vitest test runner  
**Solution:** Added `dangerouslyAllowBrowser: true` flag in test context  
**Lesson:** SDKs may need special configuration for test runners. Check error messages carefully.

### Mock Complexity vs Integration Tests
**Challenge:** Complex ORM query chains (Drizzle) are extremely difficult to mock properly  
**Solution:** Documented as technical debt, recommended integration tests instead  
**Lesson:** For database-heavy code, integration tests with real database may be more maintainable than elaborate mocks. Consider test database setup cost vs mock complexity.

---

## Codebase Refactoring (January 31, 2026)

### Directory Structure Matters
**Challenge:** Backend nested under `src/backend/` created confusion about boundaries  
**Solution:** Moved to root-level `/backend/`, frontend stays in `/src/`  
**Lesson:** Follow industry conventions:
- Next.js expects frontend in root or `src/`
- Backend services belong at root in monorepos
- Clear separation prevents "where does this belong?" questions

### Batch Updates with sed
**Challenge:** 60+ documentation files referencing old `src/backend/` path  
**Solution:** Used `find` + `sed` for batch replacement  
**Lesson:** For mechanical text replacements across many files, shell tools are more efficient than manual updates. But verify with grep first!

### Framework Constraints
**Challenge:** Tried moving Next.js frontend to `/frontend/`, build broke  
**Solution:** Keep Next.js in `src/` per framework requirements  
**Lesson:** Some frameworks have strict conventions. Check documentation before restructuring.

### Git History Preservation
**Challenge:** Moving files could lose git history  
**Solution:** Git automatically detected moves as renames (R flag)  
**Lesson:** Git is smart about detecting file moves. Use `git mv` or let Git auto-detect.

---

## RAG Implementation (December 2025 - January 2026)

### Retrieval-Augmented Facts (RAF) Enforcement
**Challenge:** Preventing LLM hallucinations in safety-critical diving domain  
**Solution:** Implemented citation tracking, NO_DATA signals, agent-level grounding  
**Lesson:**
- Citations must be tracked at retrieval layer
- Agents should refuse to answer without sources
- Confidence scoring helps surface when answers are uncertain

### Content Chunking Strategy
**Challenge:** Finding optimal chunk size for diving content  
**Solution:** ~650 tokens per chunk, topK=5, minSimilarity=0.7  
**Lesson:** Start with these defaults and tune based on retrieval quality metrics

### Vector Dimension Choice
**Challenge:** OpenAI (1536) vs Gemini (768) embeddings  
**Solution:** Switched to Gemini for cost-effectiveness  
**Lesson:** Smaller dimensions (768) work fine for most use cases and reduce storage costs

---

## Development Workflow

### Documentation Proliferation
**Challenge:** Too many status documents (NEXT_STEPS.md, various summaries)  
**Solution:** Consolidated into specific locations (technical/, project-management/, plans/)  
**Lesson:**
- Status updates → git history or project-management/
- Reference commands → README or developer-workflow
- Technical debt → dedicated file or GitHub issues
- Avoid "catch-all" documents that grow indefinitely

### Testing Philosophy
**Achievement:** 97% test pass rate (66/68 tests)  
**Lesson:**
- Write tests as you build, not after
- Integration tests valuable for complex interactions
- Skip tests are OK if documented with reason
- 100% pass rate less important than test maintainability

---

## Next Focus Areas

Based on lessons learned:
1. Set up GitHub issues for technical debt tracking
2. Subscribe to LLM provider announcements (Groq, Google)
3. Establish regular dependency update cadence
4. Create integration test database setup
5. Document performance baselines for regression detection
