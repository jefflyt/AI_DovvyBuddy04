# PR5-PR8 Plans Updated for Python Backend

**Date:** January 8, 2026  
**Author:** GitHub Copilot (AI Assistant)  
**Purpose:** Document updates to feature plans (PR5-PR8) to reflect Python/FastAPI backend architecture

---

## Summary

Updated all future feature plans (PR5 onwards) to reflect that the backend has been fully migrated to Python/FastAPI (completed in PR3.2a-PR3.2e). Original plans referenced TypeScript/Next.js API routes which are no longer applicable.

---

## Plans Updated

### ✅ PR5: Chat Interface & Integration

**File:** `docs/plans/PR5-Chat-Interface.md`

**Changes:**
- Updated Backend section to note that Python/FastAPI endpoints already exist (from PR3.2c)
- Clarified that `POST /api/chat` and `POST /api/leads` are fully implemented
- Removed references to Next.js API route modifications
- Noted that rate limiting and cookie handling are optional future enhancements
- Updated deployment considerations to reference Python backend

**Key Message:** No backend changes needed for PR5 - all endpoints already exist

---

### ✅ PR6: Landing Polish & E2E Testing

**File:** `docs/plans/PR6-Landing-Polish.md`

**Changes:**
- Updated API Changes section to clarify Python/FastAPI backend provides all endpoints
- No structural changes needed (plan is primarily frontend-focused)

**Key Message:** Minimal impact - plan is frontend/analytics focused

---

### ✅ PR6.1: MVP Production Deployment

**File:** `docs/plans/PR6.1-MVP-Production-Deployment.md`

**Changes:**
- Added architecture note confirming plan is already Python/FastAPI-first
- No changes needed - plan was written correctly for Python deployment

**Key Message:** Already correct - no updates needed beyond confirmation note

---

### ✅ PR7a: Agent Service Extraction

**File:** `docs/plans/PR7a-Agent-Service-Extraction.md`

**Changes:**
- **Marked entire PR as OBSOLETE**
- Added prominent warning that this PR is no longer needed
- Explained that Python backend (PR3.2c) already provides standalone agent service
- Documented that no extraction is required
- Added note to skip to PR7b instead

**Key Message:** This PR is no longer applicable - agent service already exists in Python

---

### ✅ PR7b: Telegram Bot Adapter

**File:** `docs/plans/PR7b-Telegram-Bot-Adapter.md`

**Changes:**
- Added architecture update noting PR7a is obsolete
- Updated dependencies to reference Python backend from PR3.2c
- Removed references to extracting from Next.js
- Updated assumptions to use Python Telegram bot (`python-telegram-bot` library)
- Changed backend implementation approach to recommend separate Python service
- Updated service structure to show Python files instead of TypeScript
- Clarified integration with existing FastAPI backend via HTTP

**Key Message:** Telegram bot will be Python-based, integrating with existing FastAPI backend

---

### ✅ PR8: User Authentication & Profiles

**File:** `docs/plans/PR8-User-Auth-Profiles.md`

**Changes:**
- Added backend clarification note
- Specified that auth will use Python/FastAPI with appropriate libraries (FastAPI-Users, Python-JOSE)
- Noted that frontend uses NextAuth.js for session management
- Clarified that plan references are for frontend components only

**Key Message:** Auth backend will be Python/FastAPI, frontend uses NextAuth.js

---

### ✅ PR8a: Auth Infrastructure

**File:** `docs/plans/PR8a-Auth-Infrastructure.md`

**Changes:**
- Added backend clarification note
- Specified Python auth libraries (FastAPI-Users, Python-JOSE, Authlib)
- Noted that database migrations will use Alembic (not Drizzle)
- Clarified that implementation will use SQLAlchemy (not Drizzle ORM)

**Key Message:** Auth infrastructure will be Python-based with Alembic migrations

---

### ✅ PR8b: Web UI Auth Integration

**File:** `docs/plans/PR8b-Web-UI-Auth-Integration.md`

**Changes:**
- Added backend clarification note
- Specified that frontend integrates with Python/FastAPI auth endpoints
- Noted that API calls go to FastAPI backend at `/api/auth/*`
- Clarified plan focuses on React/Next.js frontend components

**Key Message:** Frontend integration with Python backend via FastAPI endpoints

---

### ✅ PR8c: Telegram Account Linking

**File:** `docs/plans/PR8c-Telegram-Account-Linking.md`

**Changes:**
- Added backend clarification note
- Specified Python implementation for account linking
- Noted integration with Python Telegram bot

**Key Message:** Account linking implemented in Python/FastAPI

---

## Migration Context

### What Happened

Between December 2025 and January 2026, the project underwent a **complete backend migration from TypeScript/Next.js to Python/FastAPI** (PR3.2a through PR3.2e). This migration was successful and is now complete.

**Key milestones:**
- **PR3.2a:** Backend foundation (database, config)
- **PR3.2b:** Core services (RAG, embeddings, LLM)
- **PR3.2c:** Agent orchestration (multi-agent system)
- **PR3.2d:** Content ingestion scripts
- **PR3.2e:** Frontend integration
- **PR4:** Lead capture (implemented in Python)

### Why Plans Needed Updates

Original feature plans (PR5-PR8) were written in December 2025 **before** the Python migration decision. They assumed a TypeScript/Next.js backend architecture that no longer exists. These updates ensure future implementation follows the actual architecture.

### What Stays the Same

- **Frontend:** Still Next.js/React/TypeScript
- **Database:** Still PostgreSQL with pgvector
- **Deployment:** Still Vercel (frontend) + Cloud Run (backend)
- **Feature scope:** No functionality changes, only implementation approach

### What Changed

- **Backend language:** TypeScript → Python
- **Backend framework:** Next.js API routes → FastAPI
- **ORM:** Drizzle → SQLAlchemy
- **Migrations:** Drizzle-kit → Alembic
- **Validation:** Zod → Pydantic
- **Agent location:** No extraction needed (already standalone Python service)

---

## Implementation Guidance

### For PR5 (Chat Interface)

- Focus on **frontend components only**
- Integrate with existing Python endpoints:
  - `POST /api/chat` (from PR3.2c)
  - `POST /api/leads` (from PR4)
- No backend changes required
- Test against Python backend running on port 8000

### For PR6-6.1 (Polish & Deploy)

- Frontend and DevOps focus
- Python backend already deployment-ready
- No architectural concerns

### For PR7a (Agent Service)

- **Skip this PR entirely**
- Python backend already provides agent service
- Proceed directly to PR7b

### For PR7b (Telegram Bot)

- Implement in **Python** using `python-telegram-bot` library
- Create separate service or integrate into FastAPI app
- Integrate with existing Python backend via HTTP

### For PR8 (Auth & Profiles)

- Backend: Use Python auth libraries
  - FastAPI-Users (full-featured)
  - Python-JOSE (JWT handling)
  - Authlib (OAuth if needed later)
- Frontend: NextAuth.js for session management
- Migrations: Alembic (Python)
- Database: SQLAlchemy models

---

## File Organization Updates

As part of this review, also corrected file organization per Global Instructions:

### Files Moved

1. **PR4_IMPLEMENTATION.md** → `docs/project-management/PR4-Implementation-Guide.md`
   - Implementation guide belongs in project-management folder

2. **README_SERVICES.md** → `src/backend/docs/SERVICES.md`
   - Backend-specific documentation belongs in backend docs

3. **LEAD_CAPTURE_SETUP.md** → `docs/technical/LEAD_CAPTURE_SETUP.md`
   - Technical documentation belongs in technical folder

4. **Removed:** Empty `docs/setup/` folder (no longer needed)

### Reference Updates

- Updated internal documentation references to reflect new file locations
- All links now point to correct paths

---

## Verification

All plan updates have been reviewed to ensure:

- ✅ No breaking changes to feature scope
- ✅ Architecture accurately reflects Python backend
- ✅ Frontend integration paths are clear
- ✅ Implementation guidance is actionable
- ✅ Obsolete plans are clearly marked
- ✅ Dependencies are correctly stated

---

## Next Steps

### Immediate
- Review updated plans before starting PR5 implementation
- Ensure Python backend (PR3.2c-PR4) is fully operational
- Test all endpoints referenced in PR5 plan

### Future
- When implementing PR7b, use Python Telegram bot approach
- When implementing PR8, use Python auth libraries (not NextAuth.js for backend)
- Skip PR7a entirely (obsolete)

---

## Questions?

If there are any questions about the updated plans or the Python migration:

1. Review `docs/plans/PR3.2a-Backend-Foundation.md` for migration rationale
2. Check `docs/project-management/PR3.2*-Implementation-Summary.md` files for what was built
3. See `docs/decisions/0006-python-backend-migration.md` for architectural decision

---

**Status:** ✅ All future plans (PR5-PR8) updated for Python backend  
**Last Updated:** January 8, 2026  
**Confidence:** High - All references verified and corrected
