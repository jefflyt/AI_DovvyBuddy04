# PR9: User Authentication & Profiles (V2 Foundation)

**Branch Name:** `feature/pr9-user-auth-profiles`  
**Status:** Planned  
**Date:** December 29, 2025  
**Updated:** January 8, 2026 (Backend clarification)  
**Based on:** MASTER_PLAN.md (V2 Roadmap), DovvyBuddy-PSD-V6.2.md (V2 profiles + log)

> **✅ BACKEND NOTE:** Auth implementation will use Python/FastAPI backend with appropriate auth library (e.g., FastAPI-Users, Python-JOSE for JWT). Frontend uses NextAuth.js for session management. Plans below reference TypeScript paths for frontend components only.

---

## 1. Feature/Epic Summary

### Objective

Implement user authentication and persistent profiles as the foundation for V2 features. This transitions DovvyBuddy from guest-only ephemeral sessions to authenticated users with cross-device conversation history, saved preferences, and persistent diver profiles. This PR establishes the infrastructure for future V2 features (dive logs, personalization, notification preferences, etc.) while maintaining backward compatibility with guest sessions.

### User Impact

**Primary Users (Divers):**

- **Returning users** can create accounts and access conversation history across devices (web and Telegram).
- **Privacy-conscious users** can still use guest mode (no account required).
- **Registered users** build a persistent diver profile (certification, experience, preferences) that improves recommendations over time.
- **Multi-device users** seamlessly continue conversations from phone to desktop.

**Secondary Impact:**

- **Partner Shops:** Richer lead context from authenticated users (verified email, consistent profile).
- **Product Team:** User retention metrics, cohort analysis, and personalization foundation.
- **Future Features:** Unlocks dive log storage, trip planning history, species ID history, personalized recommendations.

### Dependencies

**Upstream (Must be complete):**

- **PR1-7:** Full web V1 functionality (database, RAG, sessions, lead capture, landing page, E2E testing).
- **PR8a-8c:** Telegram integration (optional but recommended to ensure auth works cross-channel).

**External Dependencies:**

- **Auth Provider:** NextAuth.js (self-hosted, migrate to Clerk if needed for scaling).
- **Email Service:** Resend API (already integrated for leads) for verification emails.
- **Database:** Postgres instance (existing) for user/profile tables.

### Assumptions

- **Assumption:** Use **NextAuth.js** for authentication (email/password, magic links) for self-hosted auth with full control.
  - Alternative: Migrate to Clerk later if scaling/OAuth complexity requires managed service.
- **Assumption:** Guest sessions remain fully functional (no forced signup).
- **Assumption:** User profiles store diver-specific data (certification, dive count, preferences) separate from auth provider's user record.
- **Assumption:** Conversation history migrates from session-based (24h ephemeral) to user-linked (persistent, retrievable).
- **Assumption:** Telegram users can link their Telegram account to a web account (via magic link or OAuth flow).
- **Assumption:** Privacy-first: Users can delete accounts and all associated data (GDPR-ready delete flow).
- **Assumption:** No social login (Google, Facebook) in V2.0; can be added in V2.1 if demand exists.
- **Assumption:** Email verification required for registration (prevents spam accounts).
- **Assumption:** Users can toggle between guest mode and logged-in mode easily.

---

## 2. Complexity & Fit

### Classification

**Multi-PR** (3-4 PRs recommended)

### Rationale

**Why Multi-PR:**

- **Multiple system layers affected:** Auth provider integration, database schema changes, API middleware, UI updates, session migration logic, Telegram linking.
- **Risk of breaking existing functionality:** Guest sessions, lead capture, chat flow must continue to work.
- **Migration complexity:** Existing guest sessions need safe handling (discard vs. optional account creation with history import).
- **Testing surface:** Auth flows, session persistence, cross-device sync, privacy controls, Telegram linking all need separate validation.
- **Deployment strategy:** Feature flags required to toggle authenticated features during rollout.

**Recommended PR Count:** 3 PRs

1. **PR9a:** Auth infrastructure + User/Profile schema (backend-only, no UI changes).
2. **PR9b:** Web UI integration (signup, login, profile pages, session migration).
3. **PR9c:** Telegram account linking + cross-channel session sync.

Alternative: If Telegram is not yet live, defer PR9c and combine PR9a+9b into a single larger PR (acceptable if solo founder can handle larger testing surface).

**Estimated Complexity:**

- Backend: Medium-High (auth middleware, session migration, profile CRUD).
- Frontend: Medium (auth UI, protected routes, profile management).
- Data: Medium (user/profile tables, session linking, migration logic).
- Infra: Medium (NextAuth.js configuration, email verification via Resend).

---

## 3. Full-Stack Impact

### Frontend

**Pages/Components Impacted:**

- **New Pages:**
  - `/app/auth/signin/page.tsx` — Sign-in page (email/password or magic link).
  - `/app/auth/signup/page.tsx` — Sign-up page with email verification.
  - `/app/auth/verify/page.tsx` — Email verification confirmation.
  - `/app/profile/page.tsx` — User profile management (view/edit diver profile).
  - `/app/settings/page.tsx` — Account settings (email, password, delete account).
- **Existing Pages Modified:**
  - `/app/page.tsx` (Landing) — Add "Sign In" / "Sign Up" buttons to header.
  - `/app/chat/page.tsx` — Add user avatar/menu; detect logged-in state; load history from DB.
  - `/app/layout.tsx` — Add auth context provider; show/hide nav based on auth state.

**Components to Add:**

- `src/components/auth/SignInForm.tsx` — Email/password or magic link form.
- `src/components/auth/SignUpForm.tsx` — Registration form with email, password, optional profile fields.
- `src/components/auth/UserMenu.tsx` — Dropdown with "Profile," "Settings," "Sign Out."
- `src/components/profile/DiverProfileForm.tsx` — Form to edit certification, dive count, preferences.
- `src/components/profile/ConversationHistoryList.tsx` — List past conversations with load/resume buttons.

**New UI States:**

- **Guest mode vs. Logged-in mode:** Header shows different CTAs; chat UI shows/hides history button.
- **Profile completion prompt:** After signup, prompt user to complete diver profile (optional, dismissible).
- **Session migration prompt:** When guest user signs up, offer to import current conversation history.

**Navigation/Entry Points:**

- Header: "Sign In" / "Sign Up" buttons (guest) → User avatar + dropdown (authenticated).
- Profile page: Access via user menu.
- Chat page: "View History" button (authenticated only).

### Backend

**APIs to Add:**

- **POST /api/auth/signup** — Create user account, send verification email.
- **POST /api/auth/signin** — Authenticate user, return session token (or handled by Clerk).
- **POST /api/auth/verify-email** — Confirm email verification token.
- **GET /api/auth/me** — Get current user info and profile.
- **POST /api/auth/signout** — Invalidate session.
- **GET /api/profile** — Retrieve user's diver profile.
- **PATCH /api/profile** — Update diver profile fields.
- **DELETE /api/profile** — Delete account and all associated data (GDPR-ready).
- **GET /api/conversations** — List user's conversation history (paginated).
- **GET /api/conversations/:id** — Retrieve specific conversation thread.
- **POST /api/conversations/:id/resume** — Resume conversation (load into active session).

**APIs to Modify:**

- **POST /api/chat** — Accept optional `userId` (from auth token); link session to user; persist messages to DB.
- **POST /api/session/new** — Support both guest and authenticated session creation.
- **POST /api/lead** — Include `userId` if authenticated (richer lead context).

**Services/Modules to Add:**

- `src/lib/auth/clerk-client.ts` — Clerk SDK initialization and helpers.
- `src/lib/auth/middleware.ts` — Auth middleware to protect routes; extract user from token.
- `src/lib/auth/session-migration.ts` — Logic to migrate guest session to user account.
- `src/lib/user/user-service.ts` — CRUD for user profiles (get, update, delete).
- `src/lib/conversation/conversation-service.ts` — CRUD for conversation history (list, get, resume, archive).

**Auth/Validation/Error Handling:**

- **Middleware:** Protect `/api/profile`, `/api/conversations`, and other user-specific endpoints with auth middleware.
- **Validation:** Email format, password strength (min 8 chars, uppercase, number), required profile fields.
- **Error Handling:** 401 Unauthorized for missing/invalid token; 403 Forbidden for accessing other users' data.
- **Rate Limiting:** Signup/signin endpoints limited to prevent abuse (e.g., 5 attempts per IP per 10 minutes).

### Data

**Entities/Tables Involved:**

**New Tables:**

1. **users**
   - `id` (UUID, primary key)
   - `email` (VARCHAR, unique, not null)
   - `email_verified` (BOOLEAN, default false)
   - `password_hash` (VARCHAR, nullable) — Hashed password for email/password auth (bcrypt).
   - `created_at` (TIMESTAMP)
   - `updated_at` (TIMESTAMP)

2. **diver_profiles**
   - `id` (UUID, primary key)
   - `user_id` (UUID, foreign key → users.id, unique)
   - `certification_agency` (VARCHAR, nullable) — "PADI", "SSI", etc.
   - `certification_level` (VARCHAR, nullable) — "Open Water", "Advanced Open Water", etc.
   - `logged_dives` (INTEGER, nullable)
   - `comfort_level` (VARCHAR, nullable) — "Beginner", "Intermediate", "Advanced"
   - `preferences` (JSONB, nullable) — Destination interests, dive types, etc.
   - `created_at` (TIMESTAMP)
   - `updated_at` (TIMESTAMP)

3. **conversations**
   - `id` (UUID, primary key)
   - `user_id` (UUID, foreign key → users.id, nullable) — NULL for guest sessions.
   - `session_id` (UUID, foreign key → sessions.id, unique) — Link to session table.
   - `title` (VARCHAR, nullable) — Auto-generated or user-set title.
   - `channel_type` (VARCHAR) — "web" or "telegram"
   - `is_archived` (BOOLEAN, default false)
   - `created_at` (TIMESTAMP)
   - `updated_at` (TIMESTAMP)
   - `last_message_at` (TIMESTAMP, nullable)

**Modified Tables:**

4. **sessions** (existing table, add fields)
   - Add `user_id` (UUID, foreign key → users.id, nullable) — Link session to user if authenticated.
   - Existing fields: `id`, `diver_profile` (JSONB), `conversation_history` (JSONB), `created_at`, `expires_at`.

5. **leads** (existing table, add field)
   - Add `user_id` (UUID, foreign key → users.id, nullable) — Link lead to user if authenticated.

**Migrations:**

- **Migration 1:** Create `users` table.
- **Migration 2:** Create `diver_profiles` table.
- **Migration 3:** Create `conversations` table.
- **Migration 4:** Add `user_id` column to `sessions` table (nullable, indexed).
- **Migration 5:** Add `user_id` column to `leads` table (nullable, indexed).

**Data Migration/Backfill:**

- **Guest sessions:** No migration required (remain guest sessions; expire after 24h as designed).
- **Existing leads:** `user_id` remains NULL (no retroactive linking).

**Backward Compatibility:**

- **Guest sessions:** Sessions with `user_id = NULL` continue to work as before (24h expiry).
- **Authenticated sessions:** Sessions with `user_id` set do not expire (or have extended expiry, e.g., 30 days of inactivity).

### Infra / Config

**Environment Variables:**

- `NEXTAUTH_SECRET` — Random 32+ char string for JWT signing.
- `NEXTAUTH_URL` — Full URL of the app (e.g., `http://localhost:3000` or `https://dovvybuddy.com`).
- `AUTH_PROVIDER` — "nextauth" (for future flexibility if migrating to Clerk).
- `SESSION_MAX_AGE_GUEST` — Guest session timeout (default: 86400 seconds = 24h).
- `SESSION_MAX_AGE_AUTHENTICATED` — Authenticated session timeout (default: 2592000 seconds = 30 days).
- `REQUIRE_EMAIL_VERIFICATION` — Boolean flag (default: true).

**Feature Flags:**

- `FEATURE_USER_AUTH_ENABLED` — Toggle authentication features on/off (default: false until ready).
- `FEATURE_GUEST_SESSION_MIGRATION` — Toggle guest-to-user session import (default: true).

**CI/CD Considerations:**

- Add Clerk API keys to CI secrets for integration tests.
- Update E2E tests to handle both guest and authenticated flows.
- Add database migration step to deployment pipeline.

---

## 4. PR Roadmap (Multi-PR Plan)

### PR9a: Auth Infrastructure & User/Profile Schema

**Goal**

Establish the foundational authentication system and database schema for users and profiles without changing the UI. This PR is backend-only and can be deployed behind a feature flag.

**Scope**

**In Scope:**

- Install and configure NextAuth.js with Credentials provider (email/password).
- Create database migrations for `users`, `diver_profiles`, `conversations` tables.
- Add `user_id` columns to `sessions` and `leads` tables.
- Implement auth middleware to protect API routes.
- Implement user and profile CRUD services.
- Create `/api/auth/*` endpoints (signup, signin, verify-email, signout, me).
- Create `/api/profile` endpoints (GET, PATCH, DELETE).
- Create `/api/conversations` endpoints (list, get, resume).
- Modify `/api/chat` to accept and handle authenticated users (link session to `user_id`).
- Add feature flag `FEATURE_USER_AUTH_ENABLED` (default: false).
- Unit and integration tests for auth services and endpoints.

**Out of Scope:**

- Any UI changes (landing, chat, profile pages).
- Telegram account linking.
- Guest session migration UI (defer to PR9b).
- Email verification flow UI (defer to PR9b).

**Backend Changes**

**New Modules:**

- `src/lib/auth/nextauth-config.ts` — NextAuth.js configuration with Credentials provider.
  - Configure email/password authentication.
  - Configure JWT session strategy.
  - Configure email verification callbacks.
- `src/lib/auth/middleware.ts` — Next.js middleware for route protection.
  - `requireAuth` — Middleware to protect routes; extract user ID from token, attach to request.
  - `optionalAuth` — Middleware to optionally extract user ID (for endpoints that support both guest and authenticated users).
- `src/lib/auth/session-migration.ts` — Logic for migrating guest sessions.
  - `migrateGuestSessionToUser(sessionId: string, userId: string)` — Link session to user, convert to persistent.
- `src/lib/user/user-service.ts` — User CRUD.
  - `createUser(data: { email, clerkUserId?, emailVerified })` — Create user record.
  - `getUserById(userId: string)` — Retrieve user by ID.
  - `getUserByEmail(email: string)` — Retrieve user by email.
  - `deleteUser(userId: string)` — GDPR-compliant delete (cascade to profiles, conversations, sessions).
- `src/lib/user/profile-service.ts` — Diver profile CRUD.
  - `createProfile(userId: string, data: DiverProfileInput)` — Create profile.
  - `getProfile(userId: string)` — Retrieve profile.
  - `updateProfile(userId: string, data: Partial<DiverProfileInput>)` — Update profile fields.
  - `deleteProfile(userId: string)` — Delete profile (part of user deletion cascade).
- `src/lib/conversation/conversation-service.ts` — Conversation history CRUD.
  - `listConversations(userId: string, { limit, offset, includeArchived })` — Paginated list.
  - `getConversation(conversationId: string, userId: string)` — Retrieve full thread.
  - `resumeConversation(conversationId: string, userId: string)` — Load into active session.
  - `archiveConversation(conversationId: string, userId: string)` — Mark as archived.
  - `deleteConversation(conversationId: string, userId: string)` — Hard delete.

**New API Endpoints:**

- **POST /api/auth/signup**
  - Body: `{ email, password }`
  - Actions: Hash password with bcrypt, create user record in DB, send verification email via Resend.
  - Response: `{ success: true, userId, message: "Verification email sent" }`
- **POST /api/auth/signin**
  - Note: Handled by NextAuth.js `/api/auth/[...nextauth]` route.
  - Uses Credentials provider to verify email/password against DB.
  - Creates JWT session on success.
- **POST /api/auth/verify-email**
  - Body: `{ token }` (email verification token).
  - Actions: Verify token with Clerk, update `email_verified` in DB.
  - Response: `{ success: true }`
- **GET /api/auth/me** (protected)
  - Actions: Extract user ID from auth token, retrieve user + profile.
  - Response: `{ user: { id, email, emailVerified }, profile: { ... } }`
- **POST /api/auth/signout**
  - Actions: Invalidate session token (handled by Clerk or clear cookie).
  - Response: `{ success: true }`
- **GET /api/profile** (protected)
  - Actions: Retrieve diver profile for authenticated user.
  - Response: `{ profile: { certificationAgency, certificationLevel, loggedDives, ... } }`
- **PATCH /api/profile** (protected)
  - Body: `{ certificationAgency?, certificationLevel?, loggedDives?, comfortLevel?, preferences? }`
  - Actions: Update profile fields.
  - Response: `{ success: true, profile: { ... } }`
- **DELETE /api/profile** (protected)
  - Actions: Delete user account, cascade to profiles, conversations, sessions, leads (anonymize or delete based on GDPR rules).
  - Response: `{ success: true }`
- **GET /api/conversations** (protected)
  - Query: `?limit=20&offset=0&includeArchived=false`
  - Actions: List user's conversations (paginated).
  - Response: `{ conversations: [ { id, title, channelType, lastMessageAt, ... } ], total, hasMore }`
- **GET /api/conversations/:id** (protected)
  - Actions: Retrieve full conversation thread (messages).
  - Response: `{ conversation: { id, messages: [ ... ], ... } }`
- **POST /api/conversations/:id/resume** (protected)
  - Actions: Load conversation into active session (create new session linked to conversation).
  - Response: `{ sessionId, conversation: { ... } }`

**Modified API Endpoints:**

- **POST /api/chat**
  - Before: Only accepts `{ sessionId?, message }`.
  - After: Optionally extract `userId` from auth token (via `optionalAuth` middleware); if present, link session to user.
  - Changes:
    - If `userId` present and session exists: Update `sessions.user_id`.
    - If `userId` present and new session: Create session with `user_id` set; do not set `expires_at` (or set long expiry).
    - If `userId` absent: Behavior unchanged (guest session, 24h expiry).
- **POST /api/session/new**
  - Before: Always creates guest session.
  - After: Accept optional `userId` (from auth token); create authenticated session if present.
- **POST /api/lead**
  - Before: Saves lead with session data.
  - After: If `userId` present (from auth token), include in lead record.

**Data Changes**

**Migrations:**

- **001_create_users_table.sql**
  - Create `users` table with `id`, `email`, `email_verified`, `password_hash`, `created_at`, `updated_at`.
  - Add unique constraint on `email`.
- **002_create_diver_profiles_table.sql**
  - Create `diver_profiles` table with `id`, `user_id` (FK), `certification_agency`, `certification_level`, `logged_dives`, `comfort_level`, `preferences` (JSONB), `created_at`, `updated_at`.
  - Add unique constraint on `user_id` (one profile per user).
- **003_create_conversations_table.sql**
  - Create `conversations` table with `id`, `user_id` (FK, nullable), `session_id` (FK, unique), `title`, `channel_type`, `is_archived`, `created_at`, `updated_at`, `last_message_at`.
  - Add index on `user_id`, `last_message_at` (for efficient conversation listing).
- **004_add_user_id_to_sessions.sql**
  - Add `user_id` (UUID, nullable, FK → users.id) to `sessions` table.
  - Add index on `user_id`.
- **005_add_user_id_to_leads.sql**
  - Add `user_id` (UUID, nullable, FK → users.id) to `leads` table.
  - Add index on `user_id`.

**Backward Compatibility:**

- All new columns are nullable (existing rows unaffected).
- Guest sessions continue to work (`user_id = NULL`).

**Infra / Config**

**Environment Variables:**

- `NEXTAUTH_SECRET` — Required (32+ char random string).
- `NEXTAUTH_URL` — Required (app URL).
- `FEATURE_USER_AUTH_ENABLED` — Boolean (default: false).

**Testing**

**Unit Tests:**

- `src/lib/auth/nextauth-config.test.ts` — Test NextAuth.js configuration and Credentials provider.
- `src/lib/user/user-service.test.ts` — Test user CRUD (create, get, delete).
- `src/lib/user/profile-service.test.ts` — Test profile CRUD.
- `src/lib/conversation/conversation-service.test.ts` — Test conversation list, get, resume, archive, delete.
- `src/lib/auth/middleware.test.ts` — Test `requireAuth` and `optionalAuth` middleware.

**Integration Tests:**

- **POST /api/auth/signup** — Create user, verify password hashed in DB, verify verification email sent (mock Resend).
- **POST /api/auth/[...nextauth]** — Authenticate with valid credentials via NextAuth.js, verify JWT session created.
- **GET /api/auth/me** — Verify user and profile returned for authenticated request.
- **GET /api/profile** — Verify profile retrieval for authenticated user.
- **PATCH /api/profile** — Verify profile update.
- **DELETE /api/profile** — Verify cascade delete of user, profile, sessions, conversations.
- **GET /api/conversations** — Verify pagination and filtering.
- **POST /api/chat (authenticated)** — Verify session linked to user, messages saved to conversation.
- **POST /api/chat (guest)** — Verify guest flow still works (no regression).

**Verification**

**Commands:**

- Install: `pnpm install`
- DB Migrate: `pnpm db:migrate` (run new migrations)
- Dev: `pnpm dev`
- Test: `pnpm test` (unit + integration tests)
- Typecheck: `pnpm typecheck`
- Lint: `pnpm lint`
- Build: `pnpm build`

**Manual Verification:**

1. Set `FEATURE_USER_AUTH_ENABLED=false` in `.env`.
2. Start dev server: `pnpm dev`.
3. Verify existing guest chat flow still works (no UI changes, no breakage).
4. Set `FEATURE_USER_AUTH_ENABLED=true`.
5. Curl signup: `curl -X POST http://localhost:3000/api/auth/signup -d '{"email":"test@example.com","password":"Test1234"}'`.
6. Verify user created in DB: `SELECT * FROM users WHERE email='test@example.com';`.
7. Sign in via NextAuth.js: Visit `http://localhost:3000/api/auth/signin` or use the signin page.
8. Verify JWT session cookie set (`next-auth.session-token`).
9. Curl `/api/auth/me` with token: Verify user + profile returned.
10. Curl `/api/profile` PATCH: Update profile fields, verify in DB.
11. Curl `/api/chat` with auth token: Send message, verify session linked to user in DB.

**Rollback Plan**

**Feature Flag:**

- Set `FEATURE_USER_AUTH_ENABLED=false` to disable all new endpoints and auth logic.
- Guest sessions continue to work unchanged.

**Revert Strategy:**

- Revert PR: Drop new tables (`users`, `diver_profiles`, `conversations`) and new columns (`user_id` in `sessions`, `leads`).
- No data loss for guest sessions or existing leads.

**Dependencies**

**Upstream:**

- PR1-6 complete (database, RAG, sessions, lead capture, landing page, E2E testing).

**External:**

- NextAuth.js configuration (no external account needed).
- Resend API for email verification (already integrated).

**Risks & Mitigations**

| Risk                           | Impact                                | Mitigation                                                                                                                                  |
| ------------------------------ | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Email delivery failure         | Users cannot verify email             | 1. Implement retry logic for Resend API<br>2. Provide "resend verification" button<br>3. Log failures for monitoring                        |
| Database migration failure     | New tables not created, deploy fails  | 1. Test migrations thoroughly in staging<br>2. Implement rollback script<br>3. Use feature flag to disable features if migration incomplete |
| Guest session breakage         | Existing users lose functionality     | 1. Comprehensive regression testing of guest flows<br>2. Feature flag to disable auth features<br>3. Maintain parallel guest code paths     |
| Data privacy / GDPR compliance | Legal risk if user data not deletable | 1. Implement cascade delete for user account deletion<br>2. Add data export endpoint (future)<br>3. Clear privacy policy                    |
| Auth middleware performance    | Increased latency on API routes       | 1. Cache user lookups (in-memory or Redis)<br>2. Monitor P95 latency<br>3. Optimize DB queries (indexes on `user_id`)                       |

---

### PR9b: Web UI Integration & Guest Session Migration

**Goal**

Integrate authentication UI into the web interface, allow users to sign up/sign in, manage profiles, and optionally migrate guest sessions to authenticated accounts. This PR makes authentication visible and usable to end users.

**Scope**

**In Scope:**

- Build authentication UI pages (sign-in, sign-up, email verification, profile, settings).
- Update landing page header with auth buttons (Sign In / Sign Up) for guests, user menu for authenticated users.
- Update chat page to detect auth state and show history button for authenticated users.
- Implement guest session migration prompt (offer to import current conversation on signup).
- Add profile completion prompt after signup (optional, dismissible).
- Build profile management page (view/edit diver profile).
- Build settings page (change email, password, delete account).
- Build conversation history UI (list past conversations, resume/archive/delete).
- Update `/api/chat` client-side logic to include auth token in requests.
- Mobile-responsive UI for all new pages.
- E2E smoke test for signup → signin → profile update → chat → history.

**Out of Scope:**

- Telegram account linking (defer to PR9c).
- Password reset flow (use Clerk's built-in flow or defer to V2.1).
- Social login (Google, Facebook) — defer to V2.1.
- Multi-factor authentication (MFA) — defer to V2.1.
- Profile photo upload — defer to V2.1.

**Frontend Changes**

**New Pages:**

- `/app/auth/signin/page.tsx` — Sign-in page with email/password (NextAuth.js Credentials provider).
- `/app/auth/signup/page.tsx` — Sign-up page with email, password, optional profile fields (name, agency, level).
- `/app/auth/verify/page.tsx` — Email verification confirmation (show success message, redirect to chat).
- `/app/profile/page.tsx` — User profile management (view/edit certification, dive count, preferences).
- `/app/settings/page.tsx` — Account settings (email, password, delete account).
- `/app/history/page.tsx` — Conversation history list with load/resume/archive/delete buttons.

**Modified Pages:**

- `/app/page.tsx` (Landing)
  - Add "Sign In" / "Sign Up" buttons to header for guests.
  - Show user avatar + dropdown menu for authenticated users (Profile, History, Settings, Sign Out).
- `/app/chat/page.tsx`
  - Detect auth state (use Clerk's `useUser()` hook or custom context).
  - If authenticated: Show "View History" button, load session from DB if resuming.
  - If guest: Show existing behavior (no history button).
  - On message send: Include auth token in `/api/chat` request if authenticated.
- `/app/layout.tsx`
  - Wrap app in NextAuth.js `<SessionProvider>` for client-side session access.
  - Show navigation based on auth state (header buttons change).

**New Components:**

- `src/components/auth/SignInForm.tsx` — Email/password form or magic link (use Clerk's `<SignIn />` component or custom form).
- `src/components/auth/SignUpForm.tsx` — Registration form (use Clerk's `<SignUp />` component or custom).
- `src/components/auth/UserMenu.tsx` — Dropdown menu with avatar, username, Profile/History/Settings/Sign Out links.
- `src/components/profile/DiverProfileForm.tsx` — Form to edit certification agency, level, dive count, preferences.
- `src/components/profile/ProfileCompletionPrompt.tsx` — Banner prompting user to complete profile after signup (dismissible).
- `src/components/profile/ConversationHistoryList.tsx` — List of past conversations with metadata (title, date, channel, message count).
- `src/components/profile/ConversationCard.tsx` — Individual conversation card with Resume/Archive/Delete buttons.
- `src/components/chat/GuestSessionMigrationPrompt.tsx` — Banner offering to import current conversation on signup (show after signup if guest session active).

**UI States:**

- **Guest mode:** Header shows "Sign In" / "Sign Up"; chat has no history button.
- **Authenticated mode:** Header shows user avatar + menu; chat has "View History" button.
- **Profile incomplete:** After signup, show profile completion prompt (optional, dismissible).
- **Session migration:** After signup, if guest session active, show migration prompt (Import / Start Fresh).
- **Email unverified:** Show banner in app until email verified.

**Backend Changes**

**No new endpoints** (all implemented in PR9a).

**Modified Behavior:**

- `/api/chat` now receives auth token from client (sent in `Authorization` header).

**Data Changes**

**No new migrations** (all schema in PR9a).

**Session Migration Logic:**

- When user signs up and has active guest session:
  - Call `/api/auth/migrate-session` (new endpoint to add in PR9b) with `sessionId` and `userId`.
  - Backend links session to user (`sessions.user_id = userId`), removes `expires_at` (or extends to 30 days).
  - Create `conversations` record linked to session and user.

**Infra / Config**

**Environment Variables:**

- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` — Required for client-side Clerk SDK.

**Feature Flag:**

- `FEATURE_USER_AUTH_ENABLED` — Set to `true` to enable UI.

**Testing**

**Unit Tests:**

- `src/components/auth/SignInForm.test.tsx` — Test form validation, submission.
- `src/components/auth/SignUpForm.test.tsx` — Test validation, submission, error handling.
- `src/components/profile/DiverProfileForm.test.tsx` — Test profile field updates.
- `src/components/profile/ConversationHistoryList.test.tsx` — Test list rendering, resume/archive/delete actions.

**Integration Tests:**

- **Sign-up flow:** Fill form → Submit → Verify email sent → Confirm email → Redirect to chat.
- **Sign-in flow:** Fill form → Submit → Redirect to chat → Verify user state.
- **Profile update:** Edit profile fields → Save → Verify updated in DB.
- **Guest session migration:** Start chat as guest → Sign up → Accept migration prompt → Verify session linked to user.
- **Conversation history:** Create multiple conversations → View history → Resume conversation → Verify loaded into chat.

**E2E Tests:**

- **Smoke test (authenticated flow):**
  1. Navigate to landing page.
  2. Click "Sign Up".
  3. Fill email, password, submit.
  4. Verify redirect to chat (or email verification page).
  5. Click "View History" (should be empty).
  6. Send message in chat.
  7. Navigate to history page.
  8. Verify conversation appears in list.
  9. Click "Resume".
  10. Verify conversation loaded in chat.
  11. Navigate to profile page.
  12. Update certification level.
  13. Verify saved (check DB or re-fetch profile).
  14. Sign out.
  15. Verify redirected to landing.

**Verification**

**Commands:**

- Install: `pnpm install`
- Dev: `pnpm dev`
- Test: `pnpm test`
- E2E: `pnpm test:e2e` (Playwright)
- Typecheck: `pnpm typecheck`
- Lint: `pnpm lint`
- Build: `pnpm build`

**Manual Verification:**

1. Set `FEATURE_USER_AUTH_ENABLED=true` in `.env`.
2. Start dev server: `pnpm dev`.
3. Navigate to `http://localhost:3000`.
4. Verify header shows "Sign In" / "Sign Up" buttons.
5. Click "Sign Up".
6. Fill form, submit.
7. Verify email verification sent (check Resend logs or test email).
8. Confirm email (click link in email or manually verify token).
9. Verify redirected to chat page.
10. Verify profile completion prompt appears (optional, dismiss or complete).
11. Send message in chat.
12. Verify message saved (check DB: `SELECT * FROM sessions WHERE user_id IS NOT NULL;`).
13. Click "View History".
14. Verify conversation listed.
15. Click "Resume".
16. Verify conversation loaded.
17. Navigate to profile page.
18. Edit certification level, save.
19. Verify updated in DB: `SELECT * FROM diver_profiles;`.
20. Navigate to settings page.
21. Test delete account (on test account only).
22. Verify cascade delete (user, profile, sessions, conversations deleted).

**Guest Regression Testing:**

1. Open incognito window.
2. Navigate to `http://localhost:3000`.
3. Click "Start Chatting" (or equivalent guest CTA).
4. Send message as guest.
5. Verify guest session works unchanged (24h expiry, no history button).
6. Refresh page.
7. Verify session persists (localStorage or cookie).
8. Close tab, reopen.
9. Verify session expired after 24h (manual wait or adjust timeout for testing).

**Rollback Plan**

**Feature Flag:**

- Set `FEATURE_USER_AUTH_ENABLED=false` to hide all auth UI.
- Landing page shows original guest-only CTAs.
- Chat page works in guest mode only.

**Revert Strategy:**

- Revert PR: Remove auth UI pages and components.
- Guest sessions continue to work.
- Database schema from PR9a remains (no rollback needed unless dropping feature entirely).

**Dependencies**

**Upstream:**

- PR9a complete (auth backend, user/profile schema).

**External:**

- Clerk account and publishable key.

**Risks & Mitigations**

| Risk                                          | Impact                           | Mitigation                                                                                                                                      |
| --------------------------------------------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Email verification not received               | Users cannot complete signup     | 1. Resend verification email button<br>2. Check spam folder prompt<br>3. Support email for manual verification                                  |
| Guest session migration fails                 | User loses current conversation  | 1. Test migration logic thoroughly<br>2. Provide "Skip" option (start fresh)<br>3. Log migration failures for debugging                         |
| Profile form UX confusing                     | Users abandon profile completion | 1. Make profile fields optional<br>2. Clear help text and examples<br>3. Progress indicator if multi-step                                       |
| History page performance (many conversations) | Slow load, poor UX               | 1. Paginate conversation list (20 per page)<br>2. Add loading state<br>3. Optimize DB query (index on `user_id`, `last_message_at`)             |
| Auth token expiry mid-conversation            | User kicked out unexpectedly     | 1. Implement token refresh logic (Clerk handles automatically)<br>2. Graceful error handling (prompt re-login)<br>3. Save draft message locally |

---

### PR9c: Telegram Account Linking & Cross-Channel Session Sync

**Goal**

Enable Telegram users to link their Telegram account to a DovvyBuddy web account, allowing conversation history and profile data to sync across channels (web and Telegram). This completes the multi-channel authenticated experience.

**Scope**

**In Scope:**

- Implement Telegram account linking flow (magic link sent via Telegram bot).
- Add `telegram_user_id` field to `users` table.
- Modify Telegram bot to detect linked vs. unlinked users.
- Sync diver profile from web to Telegram (use same profile for recommendations).
- Allow Telegram users to access conversation history started on web (and vice versa).
- Add "Link Account" command in Telegram bot.
- Add "Linked Accounts" section in web settings page (show Telegram username if linked).
- Support unlinking Telegram account from web settings.

**Out of Scope:**

- WhatsApp or other messaging platforms (defer to V2.2+).
- Telegram group chat support (1-on-1 chats only, as in PR8b).
- Telegram-specific features (voice messages, location sharing) — defer to V2.2+.
- Cross-device session sync within Telegram (Telegram bot is stateless; relies on DB session).

**Backend Changes**

**New Endpoints:**

- **POST /api/auth/link-telegram** (protected)
  - Body: `{ telegramUserId, telegramUsername }`
  - Actions: Link `telegram_user_id` to authenticated user; verify uniqueness (one Telegram account per user).
  - Response: `{ success: true }`
- **POST /api/auth/unlink-telegram** (protected)
  - Actions: Remove `telegram_user_id` from user record.
  - Response: `{ success: true }`
- **GET /api/auth/telegram-link-status** (protected)
  - Response: `{ isLinked: true/false, telegramUsername: "..." }`

**Modified Endpoints:**

- **POST /api/telegram/webhook** (from PR8b)
  - Before: Creates guest session for each Telegram user.
  - After: Check if `telegram_user_id` is linked to a user account; if yes, use user's session and profile.

**New Modules:**

- `src/lib/auth/telegram-link-service.ts`
  - `generateTelegramLinkToken(userId: string)` — Generate one-time token for linking.
  - `verifyTelegramLinkToken(token: string)` — Verify token, return user ID.
  - `linkTelegramAccount(userId: string, telegramUserId: string, telegramUsername: string)` — Update user record.
  - `unlinkTelegramAccount(userId: string)` — Remove Telegram link.
  - `getUserByTelegramId(telegramUserId: string)` — Look up user by Telegram ID.

**Telegram Bot Changes:**

- **New Commands:**
  - `/link` — Initiates account linking flow.
    - Bot sends magic link: "Click here to link your Telegram account: https://dovvybuddy.com/auth/link-telegram?token=..."
    - User clicks link, redirects to web app, authenticates (or signs in), confirms linking.
  - `/unlink` — Unlinks Telegram account (requires confirmation).
  - `/profile` — Shows current diver profile (if linked); prompts to link if unlinked.

**Linking Flow:**

1. User types `/link` in Telegram bot.
2. Bot generates one-time link token, sends magic link to user.
3. User clicks link, opens web browser.
4. Web app detects link token, prompts user to sign in (if not already).
5. After sign-in, web app confirms linking: "Link this Telegram account (@username) to your DovvyBuddy account?"
6. User confirms.
7. Web app calls `/api/auth/link-telegram` with user ID and Telegram user ID.
8. Bot receives webhook confirmation (or user returns to Telegram and types `/profile` to verify).

**Frontend Changes**

**New Pages:**

- `/app/auth/link-telegram/page.tsx` — Landing page for Telegram link token; prompts sign-in, shows confirmation UI.

**Modified Pages:**

- `/app/settings/page.tsx` — Add "Linked Accounts" section.
  - If Telegram linked: Show username, "Unlink" button.
  - If Telegram not linked: Show "Link Telegram Account" instructions (direct user to Telegram bot to type `/link`).

**Data Changes**

**Migration:**

- **006_add_telegram_user_id_to_users.sql**
  - Add `telegram_user_id` (VARCHAR, nullable, unique) to `users` table.
  - Add `telegram_username` (VARCHAR, nullable) to `users` table.

**Backward Compatibility:**

- Existing users have `telegram_user_id = NULL` (not linked).
- Telegram users without linked accounts continue to use guest sessions (PR8b behavior).

**Infra / Config**

**Environment Variables:**

- No new env vars (uses existing Telegram bot token from PR8b).

**Testing**

**Unit Tests:**

- `src/lib/auth/telegram-link-service.test.ts` — Test token generation, verification, linking, unlinking.

**Integration Tests:**

- **Telegram linking flow:**
  1. User types `/link` in Telegram bot.
  2. Bot generates token, sends magic link.
  3. Simulate clicking link (call `/app/auth/link-telegram?token=...`).
  4. Authenticate user.
  5. Confirm linking.
  6. Verify `telegram_user_id` set in `users` table.
- **Cross-channel session sync:**
  1. User starts conversation on web (authenticated).
  2. User opens Telegram bot.
  3. Bot detects linked account, loads user's profile and session.
  4. User sends message in Telegram.
  5. Verify message appended to same conversation (check `conversations` table).
  6. User returns to web, checks history.
  7. Verify Telegram message appears in conversation thread.

**E2E Tests:**

- **Telegram linking smoke test:**
  1. User signs in on web.
  2. Navigate to settings page.
  3. Verify "Link Telegram Account" instructions shown.
  4. Simulate `/link` command in Telegram (mock bot response).
  5. Click magic link (open in browser).
  6. Verify redirect to web, sign-in prompt (if needed).
  7. Confirm linking.
  8. Verify settings page shows linked Telegram username.
  9. Unlink Telegram account.
  10. Verify `telegram_user_id` removed from DB.

**Verification**

**Commands:**

- Install: `pnpm install`
- Dev: `pnpm dev`
- Test: `pnpm test`
- Typecheck: `pnpm typecheck`
- Lint: `pnpm lint`
- Build: `pnpm build`

**Manual Verification:**

1. Deploy Telegram bot (from PR8b) and web app (with PR9a+9b).
2. Sign in to web app as test user.
3. Navigate to settings page.
4. Note "Link Telegram Account" instructions.
5. Open Telegram, start chat with bot.
6. Type `/link`.
7. Bot sends magic link.
8. Click link (opens browser).
9. Verify web app prompts to confirm linking.
10. Confirm.
11. Verify settings page now shows linked Telegram username.
12. Send message in Telegram bot.
13. Check web app conversation history.
14. Verify Telegram message appears.
15. Send message in web app.
16. Check Telegram bot (send another message or query).
17. Verify bot has context from web conversation.
18. Unlink Telegram account from web settings.
19. Verify unlink confirmation.
20. Check DB: `SELECT telegram_user_id FROM users WHERE id='...';` (should be NULL).

**Rollback Plan**

**Feature Flag:**

- Add `FEATURE_TELEGRAM_LINKING_ENABLED` (default: false until stable).
- If disabled, Telegram bot continues to use guest sessions (PR8b behavior).

**Revert Strategy:**

- Revert PR: Remove linking logic, drop `telegram_user_id` column.
- Telegram users continue to work in guest mode.

**Dependencies**

**Upstream:**

- PR9a complete (auth backend).
- PR9b complete (web UI).
- PR8b complete (Telegram bot with guest sessions).

**External:**

- Telegram bot deployed and accessible.

**Risks & Mitigations**

| Risk                                  | Impact                                   | Mitigation                                                                                                                             |
| ------------------------------------- | ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| User links multiple Telegram accounts | Confusion, data integrity issues         | 1. Enforce unique constraint on `telegram_user_id`<br>2. Allow one Telegram account per user<br>3. Show clear error if already linked  |
| Telegram user forgets they linked     | Unexpected behavior (profile pre-filled) | 1. Show linking status in `/profile` command<br>2. Clear unlink instructions<br>3. Privacy-first messaging                             |
| Magic link token expires              | User cannot complete linking             | 1. Set short expiry (10 minutes)<br>2. Regenerate token on retry (`/link` again)<br>3. Clear error message                             |
| Cross-channel session race condition  | Message order inconsistency              | 1. Use timestamps to order messages<br>2. Add optimistic locking on session updates<br>3. Accept eventual consistency (rare edge case) |
| Telegram bot downtime                 | Web users cannot link                    | 1. Graceful error handling in web UI<br>2. Allow retry<br>3. Monitor bot uptime                                                        |

---

## 5. Milestones & Sequence

### Milestone 1: Auth Foundation (PR8a)

**Goal:** Backend authentication infrastructure ready, no UI changes, feature-flagged off.

**Unlocks:**

- User account creation and management (backend-only).
- Profile data model established.
- Conversation history persistence ready.

**PRs Included:**

- PR8a

**Definition of Done:**

- All PR8a tests pass (unit + integration).
- Migrations run successfully on staging DB.
- Feature flag `FEATURE_USER_AUTH_ENABLED=false` allows guest sessions to work unchanged.
- Manual verification of auth endpoints via Curl.

---

### Milestone 2: Authenticated Web Experience (PR8b)

**Goal:** Web users can sign up, sign in, manage profiles, and access conversation history.

**Unlocks:**

- Cross-device conversation continuity for web users.
- Persistent diver profiles for better recommendations.
- Foundation for personalization and dive logs (V2.1+).

**PRs Included:**

- PR8b

**Definition of Done:**

- All PR8b tests pass (unit + integration + E2E smoke test).
- Feature flag `FEATURE_USER_AUTH_ENABLED=true` enables full auth UI.
- Guest sessions still work (regression tests pass).
- Profile completion and session migration flows verified manually.

---

### Milestone 3: Cross-Channel Authentication (PR8c)

**Goal:** Telegram users can link accounts and access same profile/history across web and Telegram.

**Unlocks:**

- Seamless multi-channel experience.
- Single source of truth for diver profile.
- Foundation for future channels (WhatsApp, SMS, etc.).

**PRs Included:**

- PR8c

**Definition of Done:**

- All PR8c tests pass.
- Telegram linking flow verified end-to-end (manual testing with live bot).
- Cross-channel session sync verified (message sent on web appears in Telegram conversation, and vice versa).
- Unlinking flow verified.

---

## 6. Risks, Trade-offs, and Open Questions

### Major Risks

**Risk 1: Auth Provider Lock-In (Clerk)**

- **Impact:** If Clerk changes pricing or features, migration to another provider is costly.
- **Mitigation:**
  - Abstract auth logic behind `ModelProvider`-style interface (e.g., `AuthProvider`).
  - Keep user data in own DB (Clerk is only for auth tokens, not primary user storage).
  - Evaluate NextAuth.js as fallback (more complex but self-hosted).

**Risk 2: Guest Session Migration Complexity**

- **Impact:** Users lose conversation history if migration fails.
- **Mitigation:**
  - Make migration optional (offer "Skip" button).
  - Test migration flow thoroughly with different session states (active, expired, empty).
  - Log migration failures for debugging.

**Risk 3: Email Deliverability**

- **Impact:** Verification emails not received, users cannot complete signup.
- **Mitigation:**
  - Use Resend with proper domain authentication (SPF, DKIM, DMARC).
  - Add "Resend Email" button on verification page.
  - Provide fallback (support email for manual verification).

**Risk 4: Cross-Channel Session Sync Race Conditions**

- **Impact:** Message order inconsistency if user sends messages on web and Telegram simultaneously.
- **Mitigation:**
  - Use message timestamps to order messages.
  - Accept eventual consistency (rare edge case, low user impact).
  - Add optimistic locking on session updates if issue occurs frequently.

**Risk 5: Telegram Linking Security**

- **Impact:** Attacker could link victim's Telegram account if they intercept magic link token.
- **Mitigation:**
  - Use short-lived tokens (10 minutes expiry).
  - Tokens are one-time use (invalidated after linking).
  - Require sign-in on web (cannot link without authenticating).
  - Show clear confirmation UI ("Link @username to your account?").

**Risk 6: Database Migration Failure**

- **Impact:** Deployment fails, users cannot access app.
- **Mitigation:**
  - Test migrations in staging environment.
  - Implement rollback scripts for each migration.
  - Use feature flag to disable auth features if migration incomplete.
  - Monitor migration status in CI/CD pipeline.

### Trade-offs

**Trade-off 1: Clerk vs. NextAuth.js**

- **Decision:** Use Clerk for V2.0.
- **Rationale:** Clerk reduces auth infrastructure work (email verification, token management, session handling) for solo founder. NextAuth.js is more flexible but requires more setup and maintenance.
- **Deferred:** Evaluate self-hosted auth (NextAuth.js or custom) in V2.2+ if Clerk pricing becomes issue.

**Trade-off 2: Persistent Sessions for Authenticated Users vs. Fixed Expiry**

- **Decision:** Authenticated sessions expire after 30 days of inactivity (vs. 24h for guests).
- **Rationale:** Balances convenience (users stay logged in) with security (inactive sessions expire).
- **Alternative:** Never expire authenticated sessions (requires explicit sign-out) — rejected due to security concerns (shared devices).

**Trade-off 3: Optional vs. Required Profile Completion**

- **Decision:** Profile completion is optional (dismissible prompt after signup).
- **Rationale:** Reduces signup friction; users can complete profile later when needed (e.g., before submitting trip lead).
- **Alternative:** Require profile completion before using chat — rejected due to high friction (users may abandon signup).

**Trade-off 4: Email Verification Required vs. Optional**

- **Decision:** Email verification required for registration.
- **Rationale:** Prevents spam accounts and ensures lead emails are deliverable.
- **Alternative:** Allow unverified accounts with limited features (e.g., no lead submission) — deferred to V2.1 if signup friction is high.

**Trade-off 5: Single PR vs. Multi-PR**

- **Decision:** Split into 3 PRs (PR9a, PR9b, PR9c).
- **Rationale:** Reduces risk; allows incremental testing and deployment; backend can be merged and tested independently before exposing UI.
- **Alternative:** Single large PR — rejected due to high risk of breaking changes and large testing surface.

**Trade-off 6: Guest Session Persistence After Signup**

- **Decision:** Offer optional migration (import current conversation).
- **Rationale:** Balances user convenience (don't lose active conversation) with simplicity (migration can fail, adds complexity).
- **Alternative:** Always discard guest session on signup — rejected due to poor UX (user loses active conversation).

### Open Questions

**Q1: Should we support password reset in PR8b, or rely on Clerk's built-in flow?**

- **Context:** Clerk provides password reset via email automatically.
- **Decision:** Use Clerk's built-in flow for V2.0; consider custom UI in V2.1 if branding consistency is critical.
- **Impact:** If Clerk flow is used, users are redirected to Clerk-hosted page (different branding).

**Q2: Should authenticated sessions have a maximum lifetime (e.g., 90 days absolute expiry), or only inactivity-based expiry?**

- **Context:** Inactivity-based expiry (30 days) means active users stay logged in indefinitely.
- **Decision:** Start with inactivity-based only; add absolute expiry in V2.1 if security review recommends it.
- **Impact:** Long-lived sessions may pose security risk on shared devices; can be mitigated by explicit sign-out.

**Q3: Should we allow users to have multiple active sessions (e.g., phone + desktop)?**

- **Context:** Clerk supports multiple sessions by default.
- **Decision:** Allow multiple sessions for V2.0 (better UX); add "Active Sessions" management in settings page in V2.1 if needed.
- **Impact:** Users can sign out from specific devices; requires session management UI.

**Q4: Should Telegram users be required to link accounts to use advanced features (e.g., lead capture), or can they remain unlinked?**

- **Context:** Unlinked Telegram users use guest sessions (24h expiry, no history).
- **Decision:** Allow unlinked usage for V2.0 (same as PR8b); prompt to link when submitting lead (optional).
- **Impact:** Some Telegram users may never link (acceptable; reduces friction).

**Q5: Should we implement account deletion as soft delete (mark inactive) or hard delete (remove from DB)?**

- **Context:** GDPR requires user data deletion on request; soft delete allows rollback.
- **Decision:** Hard delete for V2.0 (GDPR compliance); cascade delete to profiles, sessions, conversations, leads (anonymize leads if associated with deleted user).
- **Impact:** No rollback after deletion; users must re-register if they change their mind.

**Q6: Should we track user analytics events (signup, signin, profile update) in this PR, or defer to separate analytics PR?**

- **Context:** Analytics already integrated in PR6 (landing page, lead capture).
- **Decision:** Add key auth events (signup, signin, signout, profile_update) in PR8b; use existing analytics service.
- **Impact:** No additional complexity; enables user funnel analysis.

---

## Summary

PR8 establishes the foundation for DovvyBuddy V2 by implementing user authentication and persistent profiles. This multi-PR effort transitions the platform from guest-only sessions to authenticated users with cross-device conversation history, saved preferences, and richer lead context.

**Key Deliverables:**

- **PR9a:** Backend auth infrastructure (Clerk integration, user/profile schema, API endpoints).
- **PR9b:** Web UI for signup, signin, profile management, conversation history, and guest session migration.
- **PR9c:** Telegram account linking and cross-channel session sync.

**Success Criteria:**

- Users can create accounts and access conversation history across devices.
- Guest sessions continue to work unchanged (backward compatibility).
- Telegram users can link accounts and access same profile/history across web and Telegram.
- All auth flows are secure, tested, and GDPR-compliant (account deletion).
- Feature-flagged for safe incremental rollout.

**Next Steps After PR8:**

- **PR9:** Dive log storage and management (V2 core feature).
- **PR10:** Trip planning history and itinerary generation.
- **PR11:** Personalized recommendations based on dive history.
- **PR12:** Species identification (photo recognition) — V2.1 feature.
