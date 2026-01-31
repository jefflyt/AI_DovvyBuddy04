# PR9a: Auth Infrastructure & User/Profile Schema

**Branch Name:** `feature/pr9a-auth-infrastructure`  
**Status:** Planned  
**Date:** December 29, 2025  
**Updated:** January 8, 2026 (Backend clarification)  
**Based on:** PR9-User-Auth-Profiles.md, MASTER_PLAN.md (V2 Roadmap)

> **✅ BACKEND NOTE:** Auth implementation will use Python/FastAPI backend with appropriate auth library (e.g., FastAPI-Users, Python-JOSE for JWT, or Authlib). Frontend uses NextAuth.js for session management and token handling. Database migrations will use Alembic (Python). Original plan references may mention Next.js/Drizzle but implementation will be Python/SQLAlchemy.

---

## 1. Feature/Epic Summary

### Objective

Establish the foundational authentication system and database schema for users and profiles without changing the UI. This PR implements all backend infrastructure needed for user authentication, including NextAuth.js configuration, database tables, auth middleware, and API endpoints. The entire feature is hidden behind a feature flag and can be deployed to production without affecting existing guest users.

### User Impact

**End Users:**
- **No visible changes** — All authentication features are backend-only and feature-flagged off.
- **Guest sessions continue to work identically** — No disruption to existing user flows.

**Internal/Architecture:**
- Authentication infrastructure ready for PR9b (UI integration).
- Database schema supports user accounts, profiles, and persistent conversations.
- API endpoints ready for client integration.
- Foundation for cross-device history and personalization.

### Dependencies

**Upstream (Must be complete):**
- **PR1:** Database schema and migrations (Postgres with Drizzle ORM).
- **PR2:** RAG pipeline (not directly used but part of complete stack).
- **PR3:** Model provider and session logic.
- **PR4:** Lead capture (will be extended to include user_id).
- **PR5:** Chat interface (will call new auth-aware endpoints in PR9b).
- **PR6:** Landing page and E2E testing.

**Optional (Recommended):**
- **PR9a-8c:** Telegram integration (if complete, PR9c can link Telegram accounts; if not, PR9c can be deferred).

**External Dependencies:**
- **NextAuth.js:** Self-hosted auth solution (no external account needed).
- **Resend API:** Already integrated in PR4 for lead emails; will use for verification emails.
- **Postgres Database:** Existing instance with migrations support (Neon or Supabase).

### Assumptions

- **Assumption:** NextAuth.js is the chosen auth provider (self-hosted, full control, no external dependencies).
  - Alternative: Migrate to Clerk later if scaling/OAuth complexity requires managed service.
- **Assumption:** Email/password authentication is primary method via Credentials provider.
- **Assumption:** Email verification is required (prevents spam, ensures deliverable lead emails).
- **Assumption:** Guest sessions remain fully functional with no forced signup (backward compatibility).
- **Assumption:** User profiles are stored in app's Postgres database, not Clerk's user metadata (data portability).
- **Assumption:** Session expiry for authenticated users is 30 days of inactivity (vs. 24h for guests).
- **Assumption:** API endpoints return 401 Unauthorized if auth token missing/invalid (no automatic redirect to login).
- **Assumption:** Postgres foreign keys cascade delete (user deletion removes profiles, sessions, conversations, leads).
- **Assumption:** No social login (Google, Facebook) in PR9a (can add in PR9b or V2.1).
- **Assumption:** Feature flag `FEATURE_USER_AUTH_ENABLED` defaults to `false` (must be explicitly enabled).

---

## 2. Complexity & Fit

### Classification

**Single-PR** (Backend-only, well-defined scope)

### Rationale

**Why Single-PR:**
- **Backend-only:** No frontend changes, minimal risk of UI breakage.
- **Well-defined scope:** Database schema, auth middleware, API endpoints, services.
- **Feature-flagged:** Can be deployed to production safely (no user-facing changes).
- **Testable independently:** Unit and integration tests verify all endpoints work.
- **No migration risk:** New tables and columns are additive (nullable), don't affect existing data.
- **Clear verification:** Curl commands validate all endpoints.

**Estimated Effort:**
- **Backend:** Medium (auth middleware, NextAuth.js configuration, CRUD services, API endpoints).
- **Data:** Low-Medium (5 migrations: 3 new tables, 2 column additions).
- **Testing:** Medium (unit tests for services, integration tests for endpoints).
- **Infra:** Low (add NextAuth.js env vars to .env.example and deployment config).

**Estimated Time:** 2-4 days for solo founder (depends on NextAuth.js familiarity).

---

## 3. Full-Stack Impact

### Frontend

**No changes** — This PR is backend-only. PR9b will add UI.

### Backend

**APIs to Add:**

1. **POST /api/auth/signup**
   - Accept: `{ email: string, password: string }`
   - Actions: 
     - Hash password with bcrypt.
     - Create user record in local DB with `email_verified = false`.
     - Generate email verification token (JWT, 24h expiry).
     - Send verification email via Resend API.
   - Response: `{ success: true, userId: string, message: "Verification email sent" }`
   - Errors: 
     - 400: Invalid email or password format.
     - 409: Email already registered.
     - 500: Database error or email delivery failure.

2. **POST /api/auth/[...nextauth]/route.ts** (NextAuth.js handler)
   - Handles: Signin, signout, session management, CSRF protection.
   - Credentials Provider:
     - Validate email/password against DB (bcrypt.compare).
     - Check `email_verified = true` before allowing signin.
     - Return user object on success.
   - JWT Strategy: Session stored as signed JWT in HTTP-only cookie.
   - Errors:
     - 401: Invalid credentials (handled by NextAuth.js).
     - Email not verified: Return error in authorize callback.

3. **POST /api/auth/verify-email**
   - Accept: `{ token: string }` (JWT verification token, signed with NEXTAUTH_SECRET).
   - Actions:
     - Verify JWT signature and expiry.
     - Extract user ID from token payload.
     - Update `email_verified = true` in DB.
   - Response: `{ success: true }`
   - Errors:
     - 400: Invalid or expired token.
     - 500: Database update error.

4. **GET /api/auth/me** (protected)
   - Actions:
     - Extract user ID from auth token (via auth middleware).
     - Retrieve user and profile from DB.
   - Response: `{ user: { id, email, emailVerified, createdAt }, profile: { certificationAgency, certificationLevel, loggedDives, comfortLevel, preferences } }`
   - Errors:
     - 401: Missing or invalid auth token.
     - 404: User not found (rare, indicates DB inconsistency).

5. **POST /api/auth/signout** (handled by NextAuth.js)
   - Actions:
     - Clear session cookie (handled by NextAuth.js `/api/auth/signout`).
   - Response: Redirect to landing page or `{ success: true }`.
   - Note: NextAuth.js provides built-in signout endpoint.

6. **GET /api/profile** (protected)
   - Actions:
     - Extract user ID from auth token.
     - Retrieve diver profile from DB.
   - Response: `{ profile: { id, userId, certificationAgency, certificationLevel, loggedDives, comfortLevel, preferences, createdAt, updatedAt } }`
   - Errors:
     - 401: Missing or invalid auth token.
     - 404: Profile not found (profile not yet created).

7. **PATCH /api/profile** (protected)
   - Accept: `{ certificationAgency?: string, certificationLevel?: string, loggedDives?: number, comfortLevel?: string, preferences?: object }`
   - Actions:
     - Extract user ID from auth token.
     - Update profile fields in DB (upsert: create if not exists).
   - Response: `{ success: true, profile: { ... } }`
   - Errors:
     - 401: Missing or invalid auth token.
     - 400: Invalid field values.
     - 500: Database error.

8. **DELETE /api/profile** (protected)
   - Actions:
     - Extract user ID from auth token.
     - Delete user account (cascade to profiles, sessions, conversations, leads).
     - Clear user session.
   - Response: `{ success: true, message: "Account deleted" }`
   - Errors:
     - 401: Missing or invalid auth token.
     - 500: Database delete error.

9. **GET /api/conversations** (protected)
   - Query: `?limit=20&offset=0&includeArchived=false`
   - Actions:
     - Extract user ID from auth token.
     - Retrieve user's conversations from DB (paginated).
   - Response: `{ conversations: [ { id, title, channelType, lastMessageAt, messageCount, isArchived } ], total: number, hasMore: boolean }`
   - Errors:
     - 401: Missing or invalid auth token.

10. **GET /api/conversations/:id** (protected)
    - Actions:
      - Extract user ID from auth token.
      - Retrieve conversation by ID (verify user owns conversation).
      - Return full message history from linked session.
    - Response: `{ conversation: { id, title, channelType, messages: [ { role, content, timestamp } ], createdAt, lastMessageAt } }`
    - Errors:
      - 401: Missing or invalid auth token.
      - 403: User does not own conversation.
      - 404: Conversation not found.

11. **POST /api/conversations/:id/resume** (protected)
    - Actions:
      - Extract user ID from auth token.
      - Retrieve conversation and linked session.
      - Create new session or update existing session with conversation history.
      - Return session ID for client to use.
    - Response: `{ success: true, sessionId: string }`
    - Errors:
      - 401: Missing or invalid auth token.
      - 403: User does not own conversation.
      - 404: Conversation not found.

12. **POST /api/conversations/:id/archive** (protected)
    - Actions:
      - Extract user ID from auth token.
      - Mark conversation as archived.
    - Response: `{ success: true }`
    - Errors:
      - 401: Missing or invalid auth token.
      - 403: User does not own conversation.
      - 404: Conversation not found.

13. **DELETE /api/conversations/:id** (protected)
    - Actions:
      - Extract user ID from auth token.
      - Hard delete conversation and linked session.
    - Response: `{ success: true }`
    - Errors:
      - 401: Missing or invalid auth token.
      - 403: User does not own conversation.
      - 404: Conversation not found.

**APIs to Modify:**

14. **POST /api/chat** (existing, add auth support)
    - Before: `{ sessionId?: string, message: string }`
    - After: Same payload, but extract user ID from auth token if present (via `optionalAuth` middleware).
    - Changes:
      - If `Authorization` header present, verify token and extract `userId`.
      - If `userId` present and session exists, update `sessions.user_id` (link session to user).
      - If `userId` present and new session, create session with `user_id` set and no `expires_at` (or 30-day expiry).
      - If no `userId`, behavior unchanged (guest session with 24h expiry).
      - On message save, if session linked to user, also update/create conversation record.
    - Response: `{ sessionId: string, response: string, metadata: object }`
    - Note: Backward compatible (guest flow unchanged).

15. **POST /api/session/new** (existing, add auth support)
    - Before: Creates guest session (24h expiry).
    - After: Accept optional user ID from auth token (via `optionalAuth` middleware).
    - Changes:
      - If `userId` present, create session with `user_id` set and 30-day expiry (or no expiry).
      - If no `userId`, create guest session with 24h expiry (existing behavior).
    - Response: `{ sessionId: string }`
    - Note: Backward compatible.

16. **POST /api/lead** (existing, add auth support)
    - Before: `{ type: "training" | "trip", data: object }`
    - After: Same payload, but extract user ID from auth token if present (via `optionalAuth` middleware).
    - Changes:
      - If `userId` present, include in lead record (`leads.user_id`).
      - If no `userId`, save with `user_id = NULL` (existing behavior).
    - Response: `{ success: true, leadId: string }`
    - Note: Backward compatible.

**Services/Modules to Add:**

17. **src/lib/auth/nextauth-config.ts**
    - Configure NextAuth.js with Credentials provider.
    - `authOptions` — NextAuth.js configuration object:
      - `providers`: Credentials provider with authorize callback.
      - `session`: JWT strategy with configurable maxAge.
      - `callbacks`: JWT and session callbacks to include user ID.
      - `pages`: Custom pages configuration (signin, signup, error).
    - `verifyPassword(password: string, hash: string): Promise<boolean>` — Verify password with bcrypt.
    - `hashPassword(password: string): Promise<string>` — Hash password with bcrypt.
    - `generateVerificationToken(userId: string, email: string): string` — Generate JWT for email verification.
    - `verifyVerificationToken(token: string): { userId: string, email: string }` — Verify email verification JWT.

18. **src/lib/auth/middleware.ts**
    - `requireAuth` — Middleware to protect routes:
      - Get session using `getServerSession(authOptions)`.
      - Extract `userId` from session.
      - Return 401 if no session.
    - `optionalAuth` — Middleware to optionally extract user ID:
      - Same as `requireAuth` but doesn't return 401 if no session.
      - Returns `userId = undefined` if no session.

19. **src/lib/auth/session-migration.ts**
    - `migrateGuestSessionToUser(sessionId: string, userId: string): Promise<void>` — Link guest session to user:
      - Update `sessions.user_id = userId`.
      - Remove or extend `expires_at`.
      - Create `conversations` record linked to session and user.

20. **src/lib/user/user-service.ts**
    - `createUser(data: { email: string, passwordHash: string, emailVerified: boolean }): Promise<User>` — Create user in DB.
    - `getUserById(userId: string): Promise<User | null>` — Retrieve user by ID.
    - `getUserByEmail(email: string): Promise<User | null>` — Retrieve user by email.
    - `updateEmailVerified(userId: string, verified: boolean): Promise<void>` — Update verification status.
    - `deleteUser(userId: string): Promise<void>` — Cascade delete user (profiles, sessions, conversations, leads anonymized/deleted).

21. **src/lib/user/profile-service.ts**
    - `createProfile(userId: string, data?: Partial<DiverProfileInput>): Promise<DiverProfile>` — Create profile (called on signup or first profile update).
    - `getProfile(userId: string): Promise<DiverProfile | null>` — Retrieve profile.
    - `updateProfile(userId: string, data: Partial<DiverProfileInput>): Promise<DiverProfile>` — Upsert profile (create if not exists).
    - `deleteProfile(userId: string): Promise<void>` — Delete profile (called during user deletion cascade).

22. **src/lib/conversation/conversation-service.ts**
    - `listConversations(userId: string, options: { limit: number, offset: number, includeArchived: boolean }): Promise<{ conversations: Conversation[], total: number }>` — Paginated list.
    - `getConversation(conversationId: string, userId: string): Promise<Conversation | null>` — Retrieve full conversation (verify ownership).
    - `createConversation(userId: string, sessionId: string, channelType: string): Promise<Conversation>` — Create conversation record.
    - `updateConversationTitle(conversationId: string, title: string): Promise<void>` — Update title (auto-generated or user-set).
    - `archiveConversation(conversationId: string, userId: string): Promise<void>` — Mark as archived (verify ownership).
    - `deleteConversation(conversationId: string, userId: string): Promise<void>` — Hard delete (verify ownership).
    - `getConversationBySessionId(sessionId: string): Promise<Conversation | null>` — Retrieve by linked session.

**Auth/Validation/Error Handling:**

- **Middleware:** All protected endpoints use `requireAuth` middleware; modified endpoints use `optionalAuth`.
- **Validation:**
  - Email: Valid format (regex), max 255 chars.
  - Password: Min 8 chars, at least one uppercase, one lowercase, one number (Clerk enforces).
  - Profile fields: Type validation (string, number, JSONB object).
- **Error Handling:**
  - 400: Bad request (validation errors).
  - 401: Unauthorized (missing/invalid token).
  - 403: Forbidden (accessing other user's data).
  - 404: Not found (user, profile, conversation).
  - 409: Conflict (email already registered).
  - 500: Server error (Clerk API error, database error).
- **Rate Limiting:** Add rate limiting to `/api/auth/signup` and `/api/auth/signin`:
  - 5 attempts per IP per 10 minutes.
  - Return 429 Too Many Requests if exceeded.

### Data

**Entities/Tables Involved:**

**New Tables:**

1. **users**
   ```sql
   CREATE TABLE users (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     email VARCHAR(255) UNIQUE NOT NULL,
     password_hash VARCHAR(255) NOT NULL,
     email_verified BOOLEAN DEFAULT FALSE,
     created_at TIMESTAMP DEFAULT NOW(),
     updated_at TIMESTAMP DEFAULT NOW()
   );
   
   CREATE INDEX idx_users_email ON users(email);
   ```

2. **diver_profiles**
   ```sql
   CREATE TABLE diver_profiles (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
     certification_agency VARCHAR(100),
     certification_level VARCHAR(100),
     logged_dives INTEGER,
     comfort_level VARCHAR(50),
     preferences JSONB,
     created_at TIMESTAMP DEFAULT NOW(),
     updated_at TIMESTAMP DEFAULT NOW()
   );
   
   CREATE INDEX idx_diver_profiles_user_id ON diver_profiles(user_id);
   ```

3. **conversations**
   ```sql
   CREATE TABLE conversations (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     user_id UUID REFERENCES users(id) ON DELETE CASCADE,
     session_id UUID UNIQUE NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
     title VARCHAR(255),
     channel_type VARCHAR(20) NOT NULL DEFAULT 'web',
     is_archived BOOLEAN DEFAULT FALSE,
     created_at TIMESTAMP DEFAULT NOW(),
     updated_at TIMESTAMP DEFAULT NOW(),
     last_message_at TIMESTAMP
   );
   
   CREATE INDEX idx_conversations_user_id ON conversations(user_id);
   CREATE INDEX idx_conversations_last_message_at ON conversations(last_message_at DESC);
   CREATE INDEX idx_conversations_user_id_last_message_at ON conversations(user_id, last_message_at DESC);
   ```

**Modified Tables:**

4. **sessions** (existing table, add column)
   ```sql
   ALTER TABLE sessions ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE SET NULL;
   CREATE INDEX idx_sessions_user_id ON sessions(user_id);
   ```
   - Existing columns: `id`, `diver_profile` (JSONB), `conversation_history` (JSONB), `created_at`, `expires_at`.

5. **leads** (existing table, add column)
   ```sql
   ALTER TABLE leads ADD COLUMN user_id UUID REFERENCES users(id) ON DELETE SET NULL;
   CREATE INDEX idx_leads_user_id ON leads(user_id);
   ```
   - Existing columns: `id`, `type`, `diver_profile` (JSONB), `request_details` (JSONB), `created_at`.

**Migrations:**

- **Migration 001:** `20250129_001_create_users_table.sql` — Create `users` table.
- **Migration 002:** `20250129_002_create_diver_profiles_table.sql` — Create `diver_profiles` table.
- **Migration 003:** `20250129_003_create_conversations_table.sql` — Create `conversations` table.
- **Migration 004:** `20250129_004_add_user_id_to_sessions.sql` — Add `user_id` to `sessions`.
- **Migration 005:** `20250129_005_add_user_id_to_leads.sql` — Add `user_id` to `leads`.

**Data Migration/Backfill:**

- **No backfill needed:** All new columns are nullable; existing rows remain unchanged.
- **Guest sessions:** Existing sessions have `user_id = NULL` (remain guest sessions).
- **Existing leads:** `user_id = NULL` (no retroactive linking).

**Backward Compatibility:**

- **100% backward compatible:** All changes are additive (new tables, nullable columns).
- **Guest sessions work identically:** No code changes affect guest flow when feature flag is off.
- **Database queries:** Existing queries work unchanged (new columns ignored if not selected).

### Infra / Config

**Environment Variables (add to .env.example):**

```bash
# NextAuth.js Authentication
NEXTAUTH_SECRET=<random-32-char-string>  # Required, generate with: openssl rand -base64 32
NEXTAUTH_URL=http://localhost:3000  # Required, full app URL

# Auth Provider (for future flexibility if migrating to Clerk)
AUTH_PROVIDER=nextauth  # Options: "nextauth" | "clerk"

# Session Configuration
SESSION_MAX_AGE_GUEST=86400  # 24 hours in seconds
SESSION_MAX_AGE_AUTHENTICATED=2592000  # 30 days in seconds

# Email Verification
REQUIRE_EMAIL_VERIFICATION=true

# Feature Flags
FEATURE_USER_AUTH_ENABLED=false  # MUST be false until PR9b is ready
```

**CI/CD Configuration:**

- **GitHub Actions:** Add NEXTAUTH_SECRET to CI secrets for integration tests.
- **Deployment:** Ensure migrations run before deploying new code (existing pipeline from PR1).

**Feature Flags:**

- `FEATURE_USER_AUTH_ENABLED` — Master toggle for all auth features (default: `false`).
  - When `false`: All new endpoints return 404 or 501 Not Implemented.
  - When `true`: Auth endpoints and modified endpoints use new logic.

---

## 4. PR Roadmap (Single-PR Plan)

### Phase 1: Setup & Dependencies

**Goal:** Install NextAuth.js and configure authentication infrastructure.

**Tasks:**
1. Install dependencies:
   ```bash
   pnpm add next-auth bcryptjs
   pnpm add -D @types/bcryptjs
   ```
2. Add environment variables to `.env.example` and `.env.local`:
   - `NEXTAUTH_SECRET` (generate with `openssl rand -base64 32`)
   - `NEXTAUTH_URL` (e.g., `http://localhost:3000`)
3. Create `src/lib/auth/nextauth-config.ts` with Credentials provider configuration.
4. Create NextAuth.js API route: `src/app/api/auth/[...nextauth]/route.ts`.
5. Test that NextAuth.js signin page loads at `/api/auth/signin`.

**Acceptance Criteria:**
- NextAuth.js installed and configured.
- Environment variables documented in `.env.example`.
- NextAuth.js API route responds at `/api/auth/signin`.

---

### Phase 2: Database Schema & Migrations

**Goal:** Create database tables and migrations for users, profiles, and conversations.

**Tasks:**
1. Create Drizzle schema definitions:
   - `src/db/schema/users.ts` — Users table schema.
   - `src/db/schema/diver-profiles.ts` — Diver profiles table schema.
   - `src/db/schema/conversations.ts` — Conversations table schema.
2. Update existing schema files:
   - `src/db/schema/sessions.ts` — Add `user_id` column.
   - `src/db/schema/leads.ts` — Add `user_id` column.
3. Generate migrations with Drizzle Kit:
   ```bash
   pnpm db:generate
   ```
4. Review generated SQL migration files in `src/db/migrations/`.
5. Run migrations locally:
   ```bash
   pnpm db:migrate
   ```
6. Verify tables created in database:
   ```sql
   \dt  -- List tables
   \d users  -- Describe users table
   \d diver_profiles
   \d conversations
   \d sessions
   \d leads
   ```

**Acceptance Criteria:**
- 5 migration files created (3 new tables, 2 column additions).
- Migrations run successfully without errors.
- All tables exist with correct schema (columns, types, constraints, indexes).
- Foreign key constraints work (test cascade delete on test data).

---

### Phase 3: Auth Middleware & Services

**Goal:** Implement authentication middleware and user/profile CRUD services.

**Tasks:**
1. Create `src/lib/auth/middleware.ts`:
   - Implement `requireAuth` middleware.
   - Implement `optionalAuth` middleware.
   - Export middleware functions.
2. Create `src/lib/auth/clerk-client.ts`:
   - Implement `verifyToken(token: string)`.
   - Implement `createClerkUser(email, password)`.
   - Implement `deleteClerkUser(clerkUserId)`.
   - Implement `sendVerificationEmail(email)`.
3. Create `src/lib/user/user-service.ts`:
   - Implement `createUser(data)`.
   - Implement `getUserById(userId)`.
   - Implement `getUserByEmail(email)`.
   - Implement `getUserByClerkId(clerkUserId)`.
   - Implement `updateEmailVerified(userId, verified)`.
   - Implement `deleteUser(userId)` with cascade delete.
4. Create `src/lib/user/profile-service.ts`:
   - Implement `createProfile(userId, data)`.
   - Implement `getProfile(userId)`.
   - Implement `updateProfile(userId, data)` with upsert logic.
   - Implement `deleteProfile(userId)`.
5. Create `src/lib/conversation/conversation-service.ts`:
   - Implement `listConversations(userId, options)`.
   - Implement `getConversation(conversationId, userId)`.
   - Implement `createConversation(userId, sessionId, channelType)`.
   - Implement `updateConversationTitle(conversationId, title)`.
   - Implement `archiveConversation(conversationId, userId)`.
   - Implement `deleteConversation(conversationId, userId)`.
   - Implement `getConversationBySessionId(sessionId)`.
6. Create `src/lib/auth/session-migration.ts`:
   - Implement `migrateGuestSessionToUser(sessionId, userId)`.

**Acceptance Criteria:**
- All services compile without TypeScript errors.
- Unit tests written for each service function (see Phase 5).
- Middleware functions correctly extract and verify tokens.
- Cascade delete works (deleteUser removes profiles, sessions, conversations).

---

### Phase 4: API Endpoints

**Goal:** Implement all authentication and profile management API endpoints.

**Tasks:**
1. Create new API routes in `src/app/api/auth/`:
   - `signup/route.ts` — POST /api/auth/signup
   - `signin/route.ts` — POST /api/auth/signin
   - `verify-email/route.ts` — POST /api/auth/verify-email
   - `me/route.ts` — GET /api/auth/me (protected)
   - `signout/route.ts` — POST /api/auth/signout
2. Create profile API routes in `src/app/api/profile/`:
   - `route.ts` — GET /api/profile (protected), PATCH /api/profile (protected), DELETE /api/profile (protected)
3. Create conversation API routes in `src/app/api/conversations/`:
   - `route.ts` — GET /api/conversations (protected)
   - `[id]/route.ts` — GET /api/conversations/:id (protected), DELETE /api/conversations/:id (protected)
   - `[id]/resume/route.ts` — POST /api/conversations/:id/resume (protected)
   - `[id]/archive/route.ts` — POST /api/conversations/:id/archive (protected)
4. Modify existing API routes:
   - `src/app/api/chat/route.ts` — Add `optionalAuth` middleware, handle user_id.
   - `src/app/api/session/new/route.ts` — Add `optionalAuth` middleware, handle user_id.
   - `src/app/api/lead/route.ts` — Add `optionalAuth` middleware, handle user_id.
5. Add feature flag checks to all new endpoints:
   ```typescript
   if (process.env.FEATURE_USER_AUTH_ENABLED !== 'true') {
     return NextResponse.json({ error: 'Not implemented' }, { status: 501 });
   }
   ```
6. Add rate limiting to signup and signin endpoints (using `express-rate-limit` or similar).

**Acceptance Criteria:**
- All endpoints return correct responses and status codes.
- Protected endpoints return 401 if no auth token provided.
- Feature flag blocks access when disabled.
- Integration tests pass (see Phase 5).

---

### Phase 5: Testing

**Goal:** Write comprehensive unit and integration tests for all auth logic.

**Tasks:**

**Unit Tests:**
1. `src/lib/auth/nextauth-config.test.ts`:
   - Test `hashPassword()` produces valid bcrypt hash.
   - Test `verifyPassword()` with valid and invalid passwords.
   - Test `generateVerificationToken()` produces valid JWT.
   - Test `verifyVerificationToken()` with valid and expired tokens.
2. `src/lib/auth/middleware.test.ts`:
   - Test `requireAuth` returns 401 if no session.
   - Test `requireAuth` attaches userId if valid session.
   - Test `optionalAuth` allows request without session.
3. `src/lib/user/user-service.test.ts`:
   - Test `createUser()` creates record in DB.
   - Test `getUserById()` retrieves user.
   - Test `deleteUser()` cascades to profiles, sessions, conversations.
4. `src/lib/user/profile-service.test.ts`:
   - Test `createProfile()`.
   - Test `updateProfile()` upserts (creates if not exists).
   - Test `getProfile()` returns null if not exists.
5. `src/lib/conversation/conversation-service.test.ts`:
   - Test `listConversations()` pagination.
   - Test `getConversation()` verifies ownership (403 if wrong user).
   - Test `archiveConversation()` and `deleteConversation()`.

**Integration Tests:**
1. **POST /api/auth/signup:**
   - Valid email/password → 200, user created in DB with hashed password, verification email sent (mock Resend).
   - Invalid email → 400.
   - Duplicate email → 409.
   - Email delivery error → 500 (user still created, can resend).
2. **NextAuth.js Signin:**
   - Valid credentials → 200, JWT session cookie set.
   - Invalid credentials → 401.
   - Unverified email → error message in callback.
3. **GET /api/auth/me:**
   - Valid session → 200, user and profile returned.
   - No session → 401.
4. **GET /api/profile:**
   - Valid session → 200, profile returned (or 404 if not created).
   - No session → 401.
5. **PATCH /api/profile:**
   - Valid token + data → 200, profile updated/created.
   - Invalid data → 400.
6. **DELETE /api/profile:**
   - Valid token → 200, user deleted from DB and Clerk, cascade verified.
7. **GET /api/conversations:**
   - Valid token → 200, list returned (empty if no conversations).
   - Pagination works (limit, offset).
8. **POST /api/chat (authenticated):**
   - Valid token + message → session linked to user, conversation created.
9. **POST /api/chat (guest):**
   - No token + message → guest session works (no regression).

**Test Environment Setup:**
- Use test database (separate from dev/prod).
- Mock Clerk API calls (use `nock` or `msw`).
- Mock Resend email API.
- Reset database between tests (`beforeEach` hook).

**Acceptance Criteria:**
- All unit tests pass: `pnpm test src/lib/`
- All integration tests pass: `pnpm test src/app/api/`
- Test coverage >80% for new code.
- No regressions in existing guest session tests.

---

### Phase 6: Documentation & Verification

**Goal:** Document setup, verify all endpoints work, prepare for PR9b.

**Tasks:**
1. Update `.env.example` with all new environment variables.
2. Create `docs/AUTH_SETUP.md` with:
   - Clerk account setup instructions.
   - How to obtain API keys.
   - Environment variable configuration.
   - Testing with Curl examples.
3. Update main `README.md`:
   - Add "User Authentication (V2)" section.
   - Link to AUTH_SETUP.md.
   - Note feature flag requirement.
4. Manual verification with Curl commands (see Verification section below).
5. Smoke test on staging environment:
   - Deploy with `FEATURE_USER_AUTH_ENABLED=false` → verify guest sessions work.
   - Enable feature flag → verify auth endpoints work.

**Acceptance Criteria:**
- All documentation complete and accurate.
- Manual Curl verification passes for all endpoints.
- Staging deployment successful.
- Feature flag toggle tested (on/off behavior verified).

---

## 5. Testing

### Unit Tests

**Test Files to Create:**

1. **src/lib/auth/clerk-client.test.ts**
   ```typescript
   describe('Clerk Client', () => {
     test('verifyToken returns userId for valid token', async () => {
       // Mock Clerk API response
       // Call verifyToken
       // Assert userId returned
     });
     
     test('verifyToken throws error for invalid token', async () => {
       // Mock Clerk API error
       // Call verifyToken
       // Assert error thrown
     });
     
     test('createClerkUser creates user in Clerk', async () => {
       // Mock Clerk API response
       // Call createClerkUser
       // Assert clerkUserId returned
     });
   });
   ```

2. **src/lib/auth/middleware.test.ts**
   ```typescript
   describe('Auth Middleware', () => {
     test('requireAuth returns 401 if no token', async () => {
       // Mock request without Authorization header
       // Call requireAuth
       // Assert 401 response
     });
     
     test('requireAuth attaches userId for valid token', async () => {
       // Mock request with valid token
       // Mock verifyToken success
       // Call requireAuth
       // Assert userId attached to request
     });
     
     test('optionalAuth allows request without token', async () => {
       // Mock request without token
       // Call optionalAuth
       // Assert request proceeds, userId undefined
     });
   });
   ```

3. **src/lib/user/user-service.test.ts**
   ```typescript
   describe('User Service', () => {
     test('createUser inserts user into database', async () => {
       // Call createUser
       // Query DB
       // Assert user exists
     });
     
     test('deleteUser cascades to profiles and sessions', async () => {
       // Create user, profile, session
       // Call deleteUser
       // Query DB
       // Assert profile and session deleted
     });
   });
   ```

4. **src/lib/user/profile-service.test.ts**
   ```typescript
   describe('Profile Service', () => {
     test('updateProfile creates profile if not exists', async () => {
       // Create user (no profile)
       // Call updateProfile
       // Query DB
       // Assert profile created
     });
     
     test('updateProfile updates existing profile', async () => {
       // Create user and profile
       // Call updateProfile with new data
       // Query DB
       // Assert profile updated
     });
   });
   ```

5. **src/lib/conversation/conversation-service.test.ts**
   ```typescript
   describe('Conversation Service', () => {
     test('listConversations returns user conversations only', async () => {
       // Create 2 users, each with 1 conversation
       // Call listConversations for user1
       // Assert only user1's conversation returned
     });
     
     test('getConversation returns 403 if wrong user', async () => {
       // Create conversation for user1
       // Call getConversation with user2's ID
       // Assert null or error
     });
   });
   ```

### Integration Tests

**Test Files to Create:**

1. **src/app/api/auth/signup/route.test.ts**
   ```typescript
   describe('POST /api/auth/signup', () => {
     test('creates user with valid data', async () => {
       const res = await fetch('/api/auth/signup', {
         method: 'POST',
         body: JSON.stringify({ email: 'test@example.com', password: 'Test1234' })
       });
       expect(res.status).toBe(200);
       const data = await res.json();
       expect(data.success).toBe(true);
       expect(data.userId).toBeDefined();
     });
     
     test('returns 409 for duplicate email', async () => {
       // Create user first
       // Try to create again
       // Assert 409
     });
   });
   ```

2. **src/app/api/auth/signin/route.test.ts**
   ```typescript
   describe('POST /api/auth/signin', () => {
     test('returns token for valid credentials', async () => {
       // Create user first
       // Sign in
       // Assert token returned
     });
     
     test('returns 401 for invalid credentials', async () => {
       // Sign in with wrong password
       // Assert 401
     });
   });
   ```

3. **src/app/api/profile/route.test.ts**
   ```typescript
   describe('Profile API', () => {
     test('GET /api/profile returns profile for authenticated user', async () => {
       // Create user and profile
       // GET /api/profile with token
       // Assert profile returned
     });
     
     test('PATCH /api/profile updates profile', async () => {
       // Create user
       // PATCH /api/profile with token and data
       // Query DB
       // Assert profile updated
     });
   });
   ```

4. **src/app/api/chat/route.test.ts**
   ```typescript
   describe('POST /api/chat (modified)', () => {
     test('links session to user if authenticated', async () => {
       // Create user
       // POST /api/chat with token
       // Query sessions table
       // Assert session.user_id = user.id
     });
     
     test('creates guest session if no token (regression)', async () => {
       // POST /api/chat without token
       // Query sessions table
       // Assert session.user_id IS NULL
       // Assert session.expires_at set to 24h
     });
   });
   ```

### Manual Testing (Curl Commands)

**1. Signup:**
```bash
curl -X POST http://localhost:3000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}'

# Expected: { "success": true, "userId": "...", "message": "Verification email sent" }
```

**2. Verify Email (simulate):**
```bash
# Get verification token from Clerk dashboard or test email
curl -X POST http://localhost:3000/api/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{"token":"..."}'

# Expected: { "success": true }
```

**3. Signin:**
```bash
curl -X POST http://localhost:3000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}'

# Expected: { "success": true, "token": "...", "user": { "id": "...", "email": "..." } }
# Save token for subsequent requests
export TOKEN="<token_from_response>"
```

**4. Get Current User:**
```bash
curl -X GET http://localhost:3000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Expected: { "user": { "id": "...", "email": "...", "emailVerified": true }, "profile": null }
```

**5. Update Profile:**
```bash
curl -X PATCH http://localhost:3000/api/profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"certificationAgency":"PADI","certificationLevel":"Open Water","loggedDives":25}'

# Expected: { "success": true, "profile": { "id": "...", "certificationAgency": "PADI", ... } }
```

**6. Get Profile:**
```bash
curl -X GET http://localhost:3000/api/profile \
  -H "Authorization: Bearer $TOKEN"

# Expected: { "profile": { "certificationAgency": "PADI", "certificationLevel": "Open Water", ... } }
```

**7. Send Chat Message (Authenticated):**
```bash
curl -X POST http://localhost:3000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"What is Open Water certification?"}'

# Expected: { "sessionId": "...", "response": "...", "metadata": {} }
# Verify in DB: SELECT user_id FROM sessions WHERE id='<sessionId>'; → should return user ID
```

**8. Send Chat Message (Guest, regression test):**
```bash
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is Open Water certification?"}'

# Expected: { "sessionId": "...", "response": "...", "metadata": {} }
# Verify in DB: SELECT user_id, expires_at FROM sessions WHERE id='<sessionId>'; → user_id NULL, expires_at ~24h from now
```

**9. List Conversations:**
```bash
curl -X GET "http://localhost:3000/api/conversations?limit=20&offset=0" \
  -H "Authorization: Bearer $TOKEN"

# Expected: { "conversations": [ ... ], "total": 1, "hasMore": false }
```

**10. Delete Account:**
```bash
curl -X DELETE http://localhost:3000/api/profile \
  -H "Authorization: Bearer $TOKEN"

# Expected: { "success": true, "message": "Account deleted" }
# Verify in DB: SELECT * FROM users WHERE id='<userId>'; → no rows
# Verify cascade: SELECT * FROM diver_profiles WHERE user_id='<userId>'; → no rows
```

---

## 6. Verification

### Commands to Run

**Install Dependencies:**
```bash
pnpm install
```

**Run Database Migrations:**
```bash
pnpm db:migrate
```

**Start Dev Server:**
```bash
pnpm dev
```

**Run Unit Tests:**
```bash
pnpm test src/lib/
```

**Run Integration Tests:**
```bash
pnpm test src/app/api/
```

**Run All Tests:**
```bash
pnpm test
```

**Typecheck:**
```bash
pnpm typecheck
```

**Lint:**
```bash
pnpm lint
```

**Build:**
```bash
pnpm build
```

### Manual Verification Checklist

**Setup:**
- [ ] Clerk account created and application configured.
- [ ] API keys added to `.env.local`.
- [ ] `FEATURE_USER_AUTH_ENABLED=false` in `.env.local` (initial state).
- [ ] Dependencies installed: `pnpm install`.
- [ ] Migrations run: `pnpm db:migrate`.

**Database Verification:**
- [ ] All tables created: `users`, `diver_profiles`, `conversations`.
- [ ] Columns added to existing tables: `sessions.user_id`, `leads.user_id`.
- [ ] Indexes created on foreign key columns.
- [ ] Cascade delete works (test with sample data).

**Feature Flag Off (Regression Test):**
- [ ] Set `FEATURE_USER_AUTH_ENABLED=false`.
- [ ] Start dev server: `pnpm dev`.
- [ ] Send guest chat message: Works unchanged.
- [ ] Submit lead: Works unchanged.
- [ ] Auth endpoints return 501: `curl http://localhost:3000/api/auth/signup` → 501.

**Feature Flag On (Auth Functionality):**
- [ ] Set `FEATURE_USER_AUTH_ENABLED=true`.
- [ ] Restart dev server.
- [ ] Signup: Curl command → 200, user created in DB.
- [ ] Verify DB: `SELECT * FROM users;` → user exists with `email_verified=false`.
- [ ] Signin (unverified): Curl command → 403 (email not verified).
- [ ] Manually verify email in Clerk dashboard or DB: `UPDATE users SET email_verified=true WHERE email='test@example.com';`.
- [ ] Signin (verified): Curl command → 200, token returned.
- [ ] Get current user: Curl with token → 200, user and profile returned (profile null if not created).
- [ ] Update profile: Curl with token → 200, profile created/updated.
- [ ] Get profile: Curl with token → 200, profile returned.
- [ ] Send authenticated chat message: Curl with token → session linked to user.
- [ ] Verify DB: `SELECT user_id FROM sessions WHERE id='<sessionId>';` → matches user ID.
- [ ] List conversations: Curl with token → conversation listed.
- [ ] Delete account: Curl with token → 200, user and cascade deleted.
- [ ] Verify cascade: `SELECT * FROM diver_profiles WHERE user_id='<userId>';` → no rows.

**Guest Flow Regression (Feature Flag On):**
- [ ] Send guest chat message (no token): Works unchanged.
- [ ] Verify DB: `SELECT user_id FROM sessions WHERE id='<sessionId>';` → NULL.
- [ ] Submit lead (no token): Works unchanged, `leads.user_id` is NULL.

**Error Handling:**
- [ ] Signup with invalid email → 400.
- [ ] Signup with duplicate email → 409.
- [ ] Signin with wrong password → 401.
- [ ] Protected endpoint without token → 401.
- [ ] Protected endpoint with invalid token → 401.
- [ ] Access other user's conversation → 403 or null.

**Performance/Load:**
- [ ] Signup → Signin → Update Profile → Chat: All complete <1s (local).
- [ ] List 100 conversations: <500ms (pagination works).

---

## 7. Rollback Plan

### Feature Flag Strategy

**Disable Auth Features:**
- Set `FEATURE_USER_AUTH_ENABLED=false` in production environment variables.
- All new auth endpoints return 501 Not Implemented.
- Modified endpoints (`/api/chat`, `/api/session/new`, `/api/lead`) revert to guest-only behavior.
- No user-facing impact (guest sessions work unchanged).

**Rollback Steps:**
1. Identify issue (auth endpoints failing, performance degradation, security concern).
2. Set `FEATURE_USER_AUTH_ENABLED=false` in Vercel/deployment platform.
3. Redeploy (or environment variable change takes effect immediately).
4. Verify guest sessions work.
5. Investigate issue offline, fix in new PR.

### Revert Strategy (Full Rollback)

**If feature flag is insufficient:**
1. Revert PR: `git revert <commit_hash>`.
2. Push revert commit: `git push origin main`.
3. CI/CD deploys reverted code.
4. Database migrations remain (no rollback needed; new tables/columns unused if code reverted).
5. Optional: Drop new tables and columns if not planning to re-implement:
   ```sql
   ALTER TABLE sessions DROP COLUMN user_id;
   ALTER TABLE leads DROP COLUMN user_id;
   DROP TABLE conversations;
   DROP TABLE diver_profiles;
   DROP TABLE users;
   ```

**Data Safety:**
- Guest sessions: No data loss (continue to work).
- Authenticated users: No users exist yet (PR9a is backend-only, no UI to create accounts).
- Existing leads: No changes (new column added but not used).

### Migration Rollback Scripts

Create rollback script for each migration (optional, for safety):

**Rollback 005 (add user_id to leads):**
```sql
ALTER TABLE leads DROP COLUMN IF EXISTS user_id;
```

**Rollback 004 (add user_id to sessions):**
```sql
ALTER TABLE sessions DROP COLUMN IF EXISTS user_id;
```

**Rollback 003 (create conversations):**
```sql
DROP TABLE IF EXISTS conversations;
```

**Rollback 002 (create diver_profiles):**
```sql
DROP TABLE IF EXISTS diver_profiles;
```

**Rollback 001 (create users):**
```sql
DROP TABLE IF EXISTS users;
```

---

## 8. Dependencies

### Upstream Dependencies (Must be complete before starting PR9a)

- **PR1:** Database Schema & Migrations — Required for Drizzle ORM and migration tooling.
- **PR3:** Model Provider & Session Logic — Required for existing session management code.
- **PR4:** Lead Capture & Delivery — Required to modify lead capture logic.

### External Dependencies

- **Clerk Account:** Free tier sufficient for dev/staging; paid tier for production (if >5k users).
- **Postgres Database:** Existing Neon or Supabase instance from PR1.
- **Resend API:** Already integrated in PR4; used for email verification (same API key).

### Optional Dependencies

- **PR7a-7c (Telegram):** Not required for PR9a; if complete, PR9c can link Telegram accounts; if not, PR9c can be deferred or implemented independently.

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Clerk API outage during development** | Cannot test signup/signin | 1. Use Clerk's test mode with mock data<br>2. Implement retry logic with exponential backoff<br>3. Monitor Clerk status page |
| **Database migration fails in production** | Deployment blocked | 1. Test migrations in staging environment first<br>2. Create rollback scripts for each migration<br>3. Use feature flag to disable features if migration incomplete |
| **Guest session regression** | Existing users lose functionality | 1. Comprehensive regression tests<br>2. Feature flag allows instant disable<br>3. Maintain parallel code paths (guest vs authenticated) |
| **Auth middleware performance overhead** | Increased API latency | 1. Cache Clerk token verification (in-memory or Redis)<br>2. Monitor P95 latency before/after<br>3. Use connection pooling for DB queries |
| **Clerk pricing becomes prohibitive** | Cost issue as users scale | 1. Abstract auth logic behind interface (easy to swap providers)<br>2. Keep user data in own DB (not Clerk)<br>3. Evaluate NextAuth.js as fallback |
| **Email verification not received** | Users cannot complete signup | 1. Use Resend with domain authentication (SPF, DKIM)<br>2. Add "Resend Email" button in PR9b<br>3. Provide support email for manual verification |
| **Foreign key cascade delete too aggressive** | Accidental data loss | 1. Test cascade delete thoroughly with sample data<br>2. Add confirmation step in PR9b (delete account UI)<br>3. Consider soft delete as alternative (future) |
| **Rate limiting blocks legitimate users** | Poor UX during high traffic | 1. Set generous limits (5 attempts per 10 min)<br>2. Allow bypass for verified users<br>3. Monitor rate limit hits, adjust if needed |
| **Token expiry during active session** | User kicked out unexpectedly | 1. Use long-lived tokens (30 days for authenticated)<br>2. Implement token refresh (Clerk handles automatically)<br>3. Graceful error handling in PR9b |

---

## 10. Trade-offs

| Decision | Alternative | Rationale |
|----------|-------------|-----------|
| **Use Clerk for auth** | NextAuth.js (self-hosted) | Clerk reduces infrastructure work for solo founder; NextAuth.js is more flexible but requires more setup and maintenance. Can swap later if needed. |
| **Email verification required** | Optional verification | Prevents spam accounts, ensures lead emails are deliverable. Adds friction but improves data quality. |
| **Feature flag defaults to OFF** | Enabled immediately | Safer deployment; allows backend testing in production without exposing features to users. |
| **Backend-only PR (no UI)** | Include signup UI in PR9a | Reduces risk; backend can be tested independently via Curl before exposing to users. PR9b adds UI. |
| **Store user data in app DB, not Clerk** | Use Clerk's user metadata | Improves data portability (easy to migrate to another auth provider); avoids vendor lock-in. |
| **30-day session expiry for authenticated users** | No expiry (manual signout only) | Balances convenience with security; inactive users eventually signed out to protect shared devices. |
| **Nullable user_id columns** | Require user_id (breaking change) | 100% backward compatible; guest sessions continue to work; no data migration needed. |
| **Hard delete on account deletion** | Soft delete (mark inactive) | GDPR compliance requires hard delete; soft delete can be added later if rollback needed. |
| **Single PR for all backend work** | Split into smaller PRs | Backend scope is well-defined and testable; splitting would add coordination overhead without reducing risk. |

---

## 11. Open Questions

**Q1: Should we implement password reset in PR9a, or rely on Clerk's built-in flow?**
- **Context:** Clerk provides password reset automatically via email.
- **Recommendation:** Use Clerk's built-in flow for PR9a; can add custom UI in PR9b if branding consistency is critical.
- **Decision:** Defer custom password reset UI to PR9b or V2.1.

**Q2: Should authenticated sessions have a maximum absolute lifetime (e.g., 90 days), or only inactivity-based expiry?**
- **Context:** Inactivity-based expiry means active users stay logged in indefinitely.
- **Recommendation:** Start with inactivity-based only (30 days); add absolute expiry in V2.1 if security review recommends it.
- **Decision:** Inactivity-based expiry for V2.0 (30 days).

**Q3: Should we use Clerk's webhook to sync user data, or poll on signin?**
- **Context:** Webhooks provide real-time sync but add complexity; polling on signin is simpler.
- **Recommendation:** Poll on signin for V2.0 (simpler); add webhook in V2.1 if sync issues occur.
- **Decision:** No webhook in PR9a; add in V2.1 if needed.

**Q4: Should rate limiting apply to authenticated users, or only guests?**
- **Context:** Authenticated users are less likely to abuse, but can still spam.
- **Recommendation:** Apply to both, but with higher limits for authenticated users (10 vs 5 attempts).
- **Decision:** Apply to both; monitor and adjust.

**Q5: Should account deletion be hard delete (remove from DB) or soft delete (mark inactive)?**
- **Context:** GDPR requires data deletion on request; soft delete allows rollback but complicates queries.
- **Recommendation:** Hard delete for GDPR compliance; document in privacy policy.
- **Decision:** Hard delete with cascade (profiles, sessions, conversations deleted; leads anonymized).

---

## 12. Summary

PR9a establishes the complete backend infrastructure for user authentication and profiles. This includes:

**Key Deliverables:**
- ✅ Clerk SDK integrated for authentication
- ✅ Database schema for users, profiles, and conversations (3 new tables)
- ✅ Auth middleware for protecting API routes
- ✅ User and profile CRUD services
- ✅ 13 new API endpoints + 3 modified endpoints
- ✅ Feature flag for safe deployment
- ✅ Comprehensive unit and integration tests
- ✅ 100% backward compatible (guest sessions unchanged)

**Success Criteria:**
- All tests pass (unit + integration)
- Migrations run successfully
- Feature flag toggle works (on/off behavior verified)
- Manual Curl verification passes for all endpoints
- Guest session regression tests pass (no breakage)
- Ready for PR9b (UI integration)

**Next Steps:**
- **PR9b:** Web UI integration (signup, signin, profile pages, session migration)
- **PR9c:** Telegram account linking (after PR9b + PR7b complete)

This PR can be safely deployed to production with `FEATURE_USER_AUTH_ENABLED=false`, allowing incremental testing and rollout without affecting existing users.
