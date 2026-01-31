# PR9c: Telegram Account Linking & Cross-Channel Session Sync

**Branch Name:** `feature/pr9c-telegram-account-linking`  
**Status:** Planned  
**Date:** December 29, 2025  
**Updated:** January 8, 2026 (Backend clarification)  
**Based on:** PR9-User-Auth-Profiles.md, PR9a-Auth-Infrastructure.md, PR9b-Web-UI-Auth-Integration.md

> **✅ BACKEND NOTE:** Account linking will be implemented in Python/FastAPI backend with Python Telegram bot integration. Original plan paths reference TypeScript but implementation will be Python-based.

---

## 1. Feature/Epic Summary

### Objective

Enable Telegram users to link their Telegram account to a DovvyBuddy web account, allowing conversation history and profile data to sync seamlessly across channels (web and Telegram). This completes the multi-channel authenticated experience, ensuring users have a consistent profile and conversation history whether they interact via web browser or Telegram bot.

### User Impact

**Primary Users (Divers):**
- **Telegram users** can link their Telegram account to their web account and access the same conversation history and profile across both channels.
- **Web users** who also use Telegram can continue conversations seamlessly between devices/channels.
- **Mobile-first users** get unified experience across their preferred communication channels.
- **Cross-device users** can start a conversation on web and continue on Telegram (or vice versa).

**User Flows Enabled:**
- Telegram user → Types `/link` in bot → Receives magic link → Opens in browser → Signs in/signs up → Confirms linking → Telegram account linked.
- Telegram user (linked) → Sends message → Bot uses user's profile for personalized responses → Conversation saved to history.
- Web user → Links Telegram in settings → Types `/link` in Telegram → Confirms → Both accounts linked.
- Telegram user → Types `/unlink` → Confirms → Telegram account unlinked (can re-link anytime).
- Cross-channel: Start conversation on web → Send message on Telegram → Messages appear in same conversation thread.

### Dependencies

**Upstream (Must be complete):**
- **PR9a:** Auth Infrastructure & User/Profile Schema (REQUIRED) — Backend user tables, auth middleware.
- **PR9b:** Web UI Auth Integration (REQUIRED) — Web signup/signin flow, settings page.
- **PR9a:** Agent Service Extraction (REQUIRED if agent logic is standalone).
- **PR7b:** Telegram Bot Adapter (REQUIRED) — Basic Telegram bot with guest sessions.

**External Dependencies:**
- **Telegram Bot:** Deployed and running from PR7b.
- **NextAuth.js:** Already integrated for web auth in PR9a/PR9b.
- **Database:** Postgres instance with user/profile tables from PR9a.

**Optional:**
- **PR9c (Telegram Lead Capture):** Not required for PR9c; lead capture can work with or without account linking.

### Assumptions

- **Assumption:** Telegram bot from PR7b is deployed and accessible (webhook mode recommended for production).
- **Assumption:** Agent service from PR9a is deployed and shared by both web and Telegram channels.
- **Assumption:** Session management reuses existing `sessions` table with `channel_type` field ("web" or "telegram").
- **Assumption:** One Telegram account can link to one web account (1:1 relationship enforced by unique constraint).
- **Assumption:** Magic link tokens expire after 10 minutes (short-lived for security).
- **Assumption:** Linking flow requires user to authenticate on web (cannot link without signing in or signing up).
- **Assumption:** Unlinked Telegram users continue to use guest sessions (PR7b behavior, 24h expiry).
- **Assumption:** Linked Telegram users have persistent sessions (same as authenticated web users, 30-day inactivity expiry).
- **Assumption:** Conversation history syncs automatically (messages sent on Telegram appear in web history, and vice versa).
- **Assumption:** Profile updates on web reflect in Telegram responses (bot uses latest profile data).
- **Assumption:** Telegram bot commands are text-only (no voice, photos, location in V2.0 linking flow).

---

## 2. Complexity & Fit

### Classification

**Single-PR** (Cross-channel integration with clear scope)

### Rationale

**Why Single-PR:**
- **Well-defined scope:** Telegram linking logic, magic link flow, database column addition, bot command handlers.
- **Clear integration points:** Web settings page + Telegram bot commands + backend API endpoints.
- **Testable independently:** Can test linking flow end-to-end with deployed Telegram bot.
- **Low risk:** Additive feature (doesn't change existing web or Telegram guest flows).
- **Backend mostly ready:** User tables exist (PR9a), only need `telegram_user_id` column and linking endpoints.

**Estimated Effort:**
- **Backend:** Low-Medium (linking API endpoints, token generation/verification, lookup by Telegram ID).
- **Frontend (Web):** Low (settings page additions: show linked status, unlink button).
- **Telegram Bot:** Low-Medium (new commands: `/link`, `/unlink`, `/profile`; webhook handler updates).
- **Testing:** Medium (test linking flow, cross-channel sync, unlink, error cases).

**Estimated Time:** 2-3 days for solo founder (depends on Telegram bot deployment complexity).

---

## 3. Full-Stack Impact

### Frontend (Web)

**Modified Pages:**

1. **`/app/settings/page.tsx`** (existing from PR9b)
   - Add "Linked Accounts" section below account settings.
   - **If Telegram linked:**
     - Display: "Telegram: @username" (or Telegram user ID if username not available).
     - "Unlink Telegram" button → Calls `POST /api/auth/unlink-telegram`.
     - Confirmation: "Are you sure? You'll need to re-link to sync conversations."
   - **If Telegram not linked:**
     - Display: "No Telegram account linked."
     - Instructions: "Open Telegram and send `/link` to @DovvyBuddyBot to get a linking code."
     - Note: "You'll be asked to sign in on the web to complete linking."

2. **`/app/auth/link-telegram/page.tsx`** (new page)
   - Handles magic link callback from Telegram linking flow.
   - URL format: `/auth/link-telegram?token=<magic_link_token>`
   - **Flow:**
     - Extract token from URL query params.
     - Check if user is signed in (NextAuth.js `useSession()` hook).
     - If not signed in: Redirect to `/auth/signin` with return URL (`/auth/link-telegram?token=...`).
     - If signed in: Show confirmation UI.
       - Display: "Link your Telegram account (@username or Telegram ID) to your DovvyBuddy account?"
       - Buttons: "Confirm" (calls linking API), "Cancel" (returns to settings).
     - On confirm:
       - Call `POST /api/auth/link-telegram` with token.
       - Show success message: "Telegram account linked! You can now use the bot with your DovvyBuddy account."
       - Link to return to settings or chat.
     - On error:
       - Show error message (expired token, already linked, etc.).
       - Offer retry or return to settings.

**New Components:**

3. **`src/components/settings/TelegramLinkingSection.tsx`**
   - Displays linked Telegram status.
   - Handles unlink confirmation modal.
   - Shows linking instructions if not linked.

4. **`src/components/settings/TelegramUnlinkConfirmation.tsx`**
   - Modal with warning: "Unlinking will disconnect your Telegram bot from this account. Conversations will no longer sync."
   - Buttons: "Cancel", "Unlink Telegram".

### Backend

**APIs to Add:**

1. **POST /api/auth/link-telegram** (protected)
   - Accept: `{ token: string }` (magic link token from Telegram bot).
   - Actions:
     - Verify token (check expiry, validity).
     - Extract `telegramUserId` and `telegramUsername` from token payload.
     - Check if Telegram ID already linked to another user (enforce uniqueness).
     - Update `users.telegram_user_id` and `users.telegram_username`.
     - Return success.
   - Response: `{ success: true, telegramUsername: string }`
   - Errors:
     - 400: Invalid or expired token.
     - 409: Telegram account already linked to another user.
     - 500: Database error.

2. **POST /api/auth/unlink-telegram** (protected)
   - Actions:
     - Extract user ID from auth token.
     - Set `users.telegram_user_id = NULL` and `users.telegram_username = NULL`.
     - Return success.
   - Response: `{ success: true }`
   - Errors:
     - 401: Not authenticated.
     - 404: No Telegram account linked.
     - 500: Database error.

3. **GET /api/auth/telegram-link-status** (protected)
   - Actions:
     - Extract user ID from auth token.
     - Query `users` table for `telegram_user_id` and `telegram_username`.
   - Response: `{ isLinked: boolean, telegramUsername: string | null, telegramUserId: string | null }`
   - Errors:
     - 401: Not authenticated.

**APIs to Modify:**

4. **POST /api/telegram/webhook** (existing from PR7b)
   - Before: Always creates guest session for each Telegram user ID.
   - After: Check if `telegram_user_id` is linked to a user account:
     - Query: `SELECT id FROM users WHERE telegram_user_id = <telegram_user_id>`.
     - If linked: Use user's authenticated session (fetch or create with `user_id`).
     - If not linked: Use guest session (existing PR7b behavior).
   - Update session lookup logic to check `user_id` and `channel_type = 'telegram'`.

**Services/Modules to Add:**

5. **src/lib/auth/telegram-link-service.ts**
   - `generateTelegramLinkToken(telegramUserId: string, telegramUsername: string | null): Promise<string>`
     - Generates one-time JWT token with payload: `{ telegramUserId, telegramUsername, expiresAt }`.
     - Token expiry: 10 minutes.
     - Returns signed JWT.
   - `verifyTelegramLinkToken(token: string): Promise<{ telegramUserId: string, telegramUsername: string | null }>`
     - Verifies JWT signature and expiry.
     - Returns payload if valid.
     - Throws error if expired or invalid.
   - `linkTelegramAccount(userId: string, telegramUserId: string, telegramUsername: string | null): Promise<void>`
     - Check if `telegramUserId` already linked to another user (throw error if yes).
     - Update `users` table: `UPDATE users SET telegram_user_id = ?, telegram_username = ? WHERE id = ?`.
   - `unlinkTelegramAccount(userId: string): Promise<void>`
     - Update `users` table: `UPDATE users SET telegram_user_id = NULL, telegram_username = NULL WHERE id = ?`.
   - `getUserByTelegramId(telegramUserId: string): Promise<User | null>`
     - Query: `SELECT * FROM users WHERE telegram_user_id = ?`.
     - Returns user if found, null otherwise.

**Telegram Bot Changes:**

6. **New Commands (add to Telegram bot from PR7b):**
   - **`/link`** — Initiates account linking flow.
     - Bot response:
       ```
       To link your Telegram account to DovvyBuddy:
       
       1. Click the link below to sign in or sign up on the web:
       https://dovvybuddy.com/auth/link-telegram?token=<magic_link_token>
       
       2. Confirm linking on the web page.
       
       3. Return here and type /profile to verify your account is linked.
       
       Note: This link expires in 10 minutes.
       ```
     - Bot action:
       - Generate magic link token: `generateTelegramLinkToken(telegramUserId, telegramUsername)`.
       - Store token temporarily (in-memory or Redis, key: `telegram_link:<token>`, value: `{ telegramUserId, telegramUsername }`, TTL: 10 min).
       - Send message with link.
   
   - **`/unlink`** — Unlinks Telegram account.
     - Bot response:
       ```
       Are you sure you want to unlink your Telegram account?
       
       You'll lose access to your conversation history and saved profile. You can re-link anytime by typing /link.
       
       To confirm, type: /unlink confirm
       ```
     - On `/unlink confirm`:
       - Query user by Telegram ID: `getUserByTelegramId(telegramUserId)`.
       - If linked: Call `unlinkTelegramAccount(userId)`.
       - Send confirmation: "Your Telegram account has been unlinked."
       - If not linked: "No linked account found."
   
   - **`/profile`** — Shows current diver profile (if linked).
     - Bot response (if linked):
       ```
       Your DovvyBuddy Profile:
       
       Email: user@example.com
       Certification: PADI Open Water
       Logged Dives: 25
       Comfort Level: Intermediate
       
       To update your profile, visit: https://dovvybuddy.com/profile
       ```
     - Bot response (if not linked):
       ```
       You don't have a linked account yet.
       
       Type /link to connect your Telegram to your DovvyBuddy account.
       ```

7. **Modified Commands (update from PR7b):**
   - **`/start`** — Welcome message with linking prompt.
     - If not linked: Include "Type /link to save your conversations and access your profile."
     - If linked: "Welcome back! Your conversations are saved to your DovvyBuddy account."

**Webhook Handler Updates:**

8. **Handle incoming messages from Telegram:**
   - On message received:
     - Extract `telegramUserId` from update.
     - Check if linked: `getUserByTelegramId(telegramUserId)`.
     - If linked:
       - Fetch or create session with `user_id` and `channel_type = 'telegram'`.
       - Use user's diver profile for context.
       - Save messages to conversation linked to user.
     - If not linked:
       - Use guest session (existing PR7b behavior).
       - Session expires after 24h.
   - Forward message to agent service (same as PR7b).

### Data

**Modified Tables:**

1. **users** (add columns)
   ```sql
   ALTER TABLE users ADD COLUMN telegram_user_id VARCHAR(255) UNIQUE;
   ALTER TABLE users ADD COLUMN telegram_username VARCHAR(255);
   
   CREATE INDEX idx_users_telegram_user_id ON users(telegram_user_id);
   ```
   - `telegram_user_id`: Telegram's unique user ID (numeric string, e.g., "123456789").
   - `telegram_username`: Telegram username (without "@", e.g., "johndoe"). Nullable (not all users have usernames).

**Migrations:**

- **Migration 006:** `20250129_006_add_telegram_to_users.sql`
  - Add `telegram_user_id` and `telegram_username` columns to `users` table.
  - Add unique constraint on `telegram_user_id`.

**Data Integrity:**

- **Uniqueness:** One Telegram account can only link to one web account (enforced by unique constraint).
- **Nullable:** Both columns are nullable (existing users and unlinked users have NULL values).
- **Cleanup on unlink:** Columns set to NULL when user unlinks (no cascade needed).

**Backward Compatibility:**

- **100% backward compatible:** New columns are nullable; existing users unaffected.
- **Unlinked Telegram users:** Continue to work as guest sessions (PR7b behavior).
- **Web-only users:** No changes (Telegram columns remain NULL).

### Infra / Config

**Environment Variables (no new vars, use existing):**

```bash
# Already configured in PR7b
TELEGRAM_BOT_TOKEN=<bot_token_from_BotFather>
TELEGRAM_WEBHOOK_URL=https://your-telegram-bot.run.app/webhook

# Already configured in PR9a
CLERK_SECRET_KEY=sk_test_...
DATABASE_URL=postgresql://...

# Feature flag (optional, for gradual rollout)
FEATURE_TELEGRAM_LINKING_ENABLED=true
```

**Telegram Bot Configuration:**

- **Bot commands:** Update command list in BotFather to include `/link`, `/unlink`, `/profile`.
- **Webhook URL:** Should already be configured from PR7b.

---

## 4. PR Roadmap (Single-PR Plan)

### Phase 1: Database Schema Update

**Goal:** Add Telegram user ID columns to users table.

**Tasks:**
1. Create migration: `20250129_006_add_telegram_to_users.sql`.
2. Add `telegram_user_id VARCHAR(255) UNIQUE` and `telegram_username VARCHAR(255)` to `users` table.
3. Run migration locally: `pnpm db:migrate`.
4. Verify columns added: `\d users` in psql.

**Acceptance Criteria:**
- Migration runs successfully.
- Columns added with correct types and constraints.
- Unique index created on `telegram_user_id`.

---

### Phase 2: Backend Linking Services & APIs

**Goal:** Implement token generation, verification, and linking logic.

**Tasks:**
1. Create `src/lib/auth/telegram-link-service.ts`:
   - Implement `generateTelegramLinkToken()` (JWT with 10 min expiry).
   - Implement `verifyTelegramLinkToken()` (verify JWT).
   - Implement `linkTelegramAccount()` (update users table, check uniqueness).
   - Implement `unlinkTelegramAccount()` (set columns to NULL).
   - Implement `getUserByTelegramId()` (query users by Telegram ID).
2. Create API routes:
   - `src/app/api/auth/link-telegram/route.ts` (POST, protected).
   - `src/app/api/auth/unlink-telegram/route.ts` (POST, protected).
   - `src/app/api/auth/telegram-link-status/route.ts` (GET, protected).
3. Add error handling for duplicate Telegram ID (409 Conflict).
4. Write unit tests for telegram-link-service.

**Acceptance Criteria:**
- Token generation produces valid JWT.
- Token verification succeeds for valid tokens, fails for expired/invalid.
- Linking updates database correctly.
- Unlinking sets columns to NULL.
- Duplicate linking returns 409 error.

---

### Phase 3: Telegram Bot Commands

**Goal:** Add `/link`, `/unlink`, `/profile` commands to Telegram bot.

**Tasks:**
1. Update Telegram bot command handler (from PR7b):
   - Add `/link` command handler:
     - Generate token: `generateTelegramLinkToken(telegramUserId, telegramUsername)`.
     - Construct magic link URL.
     - Send message with link and instructions.
   - Add `/unlink` command handler:
     - First call: Send confirmation prompt.
     - `/unlink confirm`: Look up user, call unlinking service, send confirmation.
   - Add `/profile` command handler:
     - Check if linked: `getUserByTelegramId(telegramUserId)`.
     - If linked: Fetch profile, format and send.
     - If not linked: Prompt to link.
2. Update `/start` command to mention linking feature.
3. Update BotFather command list:
   ```
   link - Link your Telegram to your DovvyBuddy account
   unlink - Unlink your Telegram account
   profile - View your diver profile
   ```

**Acceptance Criteria:**
- `/link` command sends magic link.
- `/unlink` command requires confirmation, successfully unlinks.
- `/profile` shows profile for linked users, prompts to link for unlinked.
- `/start` mentions linking feature.

---

### Phase 4: Telegram Webhook Session Logic

**Goal:** Update webhook handler to detect linked users and use authenticated sessions.

**Tasks:**
1. Modify Telegram webhook handler (from PR7b):
   - On message received, extract `telegramUserId`.
   - Query: `getUserByTelegramId(telegramUserId)`.
   - If user found (linked):
     - Fetch or create session with `user_id` and `channel_type = 'telegram'`.
     - Load user's diver profile for context.
     - Session has 30-day inactivity expiry (same as web authenticated users).
   - If user not found (unlinked):
     - Use guest session (existing PR7b logic, 24h expiry).
   - Forward message to agent service (same as PR7b).
2. Ensure conversation messages are saved to `conversations` table for linked users.

**Acceptance Criteria:**
- Linked Telegram users use authenticated sessions.
- Unlinked users continue to use guest sessions (no regression).
- Messages from linked users appear in web conversation history.

---

### Phase 5: Web UI Integration (Settings Page)

**Goal:** Add Telegram linking section to settings page.

**Tasks:**
1. Create `src/components/settings/TelegramLinkingSection.tsx`:
   - Fetch link status: `GET /api/auth/telegram-link-status`.
   - Display linked status (username/ID) or instructions to link.
   - "Unlink Telegram" button (if linked).
2. Create `src/components/settings/TelegramUnlinkConfirmation.tsx`:
   - Confirmation modal with warning.
   - On confirm: Call `POST /api/auth/unlink-telegram`.
3. Update `/app/settings/page.tsx`:
   - Add `<TelegramLinkingSection />` component.
4. Create `/app/auth/link-telegram/page.tsx`:
   - Handle magic link callback.
   - Check auth state (redirect to signin if needed).
   - Show confirmation UI.
   - Call `POST /api/auth/link-telegram` on confirm.
   - Show success/error messages.

**Acceptance Criteria:**
- Settings page shows Telegram linking section.
- Link status displays correctly (linked vs. unlinked).
- Unlink button works, requires confirmation.
- Magic link page handles authentication and linking.

---

### Phase 6: Cross-Channel Session Sync Testing

**Goal:** Verify messages sync between web and Telegram.

**Tasks:**
1. Test cross-channel sync:
   - User signs in on web, sends message.
   - User opens Telegram bot (linked account), sends message.
   - Verify both messages appear in web conversation history.
   - Verify conversation has single `conversations` record with messages from both channels.
2. Test profile consistency:
   - User updates profile on web (certification level).
   - User sends message on Telegram.
   - Verify bot response uses updated profile context.
3. Test session isolation:
   - User A (linked) and User B (unlinked) both send messages on Telegram.
   - Verify User A's messages saved to authenticated session.
   - Verify User B's messages use guest session (expire after 24h).

**Acceptance Criteria:**
- Messages from web and Telegram appear in same conversation.
- Profile updates on web reflect in Telegram bot responses.
- Linked and unlinked users have correct session behavior.

---

### Phase 7: Testing & Verification

**Goal:** Comprehensive testing of linking flow and edge cases.

**Tasks:**

**Unit Tests:**
1. `src/lib/auth/telegram-link-service.test.ts`:
   - Test token generation and verification.
   - Test linking with valid/duplicate Telegram IDs.
   - Test unlinking.

**Integration Tests:**
2. Test `/link` command in Telegram:
   - Send `/link`, receive magic link.
   - Click link (or simulate), complete linking on web.
   - Verify `users.telegram_user_id` updated.
3. Test `/unlink` command:
   - Send `/unlink confirm`, verify account unlinked.
   - Verify columns set to NULL.
4. Test cross-channel sync:
   - Send message on web → Verify appears in Telegram session context.
   - Send message on Telegram → Verify appears in web history.

**E2E Tests:**
5. Full linking flow:
   - User signs up on web.
   - User opens Telegram, types `/link`.
   - User clicks magic link, confirms linking.
   - User types `/profile`, sees linked profile.
   - User sends message on Telegram, checks web history.
6. Unlink and re-link:
   - User unlinks Telegram.
   - User types `/link` again, completes linking.
   - Verify re-linking works.

**Acceptance Criteria:**
- All unit tests pass.
- Integration tests verify linking/unlinking.
- E2E test completes full flow.
- Cross-channel sync verified.

---

## 5. Testing

### Unit Tests

**Test Files to Create:**

1. **src/lib/auth/telegram-link-service.test.ts**
   ```typescript
   describe('Telegram Link Service', () => {
     test('generateTelegramLinkToken creates valid JWT', async () => {
       const token = await generateTelegramLinkToken('123456789', 'johndoe');
       expect(token).toBeDefined();
       expect(typeof token).toBe('string');
     });
     
     test('verifyTelegramLinkToken returns payload for valid token', async () => {
       const token = await generateTelegramLinkToken('123456789', 'johndoe');
       const payload = await verifyTelegramLinkToken(token);
       expect(payload.telegramUserId).toBe('123456789');
       expect(payload.telegramUsername).toBe('johndoe');
     });
     
     test('verifyTelegramLinkToken throws error for expired token', async () => {
       const expiredToken = '<expired_jwt>';
       await expect(verifyTelegramLinkToken(expiredToken)).rejects.toThrow();
     });
     
     test('linkTelegramAccount updates users table', async () => {
       const userId = 'user-1';
       await linkTelegramAccount(userId, '123456789', 'johndoe');
       const user = await getUserById(userId);
       expect(user.telegram_user_id).toBe('123456789');
       expect(user.telegram_username).toBe('johndoe');
     });
     
     test('linkTelegramAccount throws error for duplicate Telegram ID', async () => {
       await linkTelegramAccount('user-1', '123456789', 'johndoe');
       await expect(linkTelegramAccount('user-2', '123456789', 'janedoe')).rejects.toThrow();
     });
     
     test('unlinkTelegramAccount sets columns to NULL', async () => {
       await linkTelegramAccount('user-1', '123456789', 'johndoe');
       await unlinkTelegramAccount('user-1');
       const user = await getUserById('user-1');
       expect(user.telegram_user_id).toBeNull();
       expect(user.telegram_username).toBeNull();
     });
   });
   ```

### Integration Tests

**Telegram Bot Command Tests (mock Telegram API):**

1. **Test `/link` command:**
   ```typescript
   test('Telegram /link command sends magic link', async () => {
     const telegramUpdate = {
       message: {
         from: { id: 123456789, username: 'johndoe' },
         text: '/link'
       }
     };
     
     const response = await handleTelegramUpdate(telegramUpdate);
     
     expect(response.text).toContain('https://dovvybuddy.com/auth/link-telegram?token=');
     expect(response.text).toContain('10 minutes');
   });
   ```

2. **Test `/unlink` command:**
   ```typescript
   test('Telegram /unlink command unlinks account', async () => {
     // First, link account
     await linkTelegramAccount('user-1', '123456789', 'johndoe');
     
     const telegramUpdate = {
       message: {
         from: { id: 123456789, username: 'johndoe' },
         text: '/unlink confirm'
       }
     };
     
     const response = await handleTelegramUpdate(telegramUpdate);
     
     expect(response.text).toContain('unlinked');
     
     const user = await getUserByTelegramId('123456789');
     expect(user).toBeNull();
   });
   ```

3. **Test `/profile` command (linked):**
   ```typescript
   test('Telegram /profile command shows profile for linked user', async () => {
     await linkTelegramAccount('user-1', '123456789', 'johndoe');
     await updateProfile('user-1', { certificationLevel: 'Open Water', loggedDives: 25 });
     
     const telegramUpdate = {
       message: {
         from: { id: 123456789, username: 'johndoe' },
         text: '/profile'
       }
     };
     
     const response = await handleTelegramUpdate(telegramUpdate);
     
     expect(response.text).toContain('Open Water');
     expect(response.text).toContain('25');
   });
   ```

**API Endpoint Tests:**

4. **Test `POST /api/auth/link-telegram`:**
   ```typescript
   test('POST /api/auth/link-telegram links account', async () => {
     const token = await generateTelegramLinkToken('123456789', 'johndoe');
     
     const response = await fetch('/api/auth/link-telegram', {
       method: 'POST',
       headers: {
         'Authorization': `Bearer ${validUserToken}`,
         'Content-Type': 'application/json'
       },
       body: JSON.stringify({ token })
     });
     
     expect(response.status).toBe(200);
     const data = await response.json();
     expect(data.success).toBe(true);
     expect(data.telegramUsername).toBe('johndoe');
     
     // Verify in DB
     const user = await getUserById('user-1');
     expect(user.telegram_user_id).toBe('123456789');
   });
   ```

5. **Test duplicate linking (409 error):**
   ```typescript
   test('POST /api/auth/link-telegram returns 409 for duplicate Telegram ID', async () => {
     const token = await generateTelegramLinkToken('123456789', 'johndoe');
     
     // Link to user-1
     await fetch('/api/auth/link-telegram', {
       method: 'POST',
       headers: { 'Authorization': `Bearer ${user1Token}` },
       body: JSON.stringify({ token })
     });
     
     // Try to link to user-2 (should fail)
     const response = await fetch('/api/auth/link-telegram', {
       method: 'POST',
       headers: { 'Authorization': `Bearer ${user2Token}` },
       body: JSON.stringify({ token })
     });
     
     expect(response.status).toBe(409);
   });
   ```

### E2E Tests (Manual)

**Full Linking Flow:**

1. **Setup:**
   - Deploy Telegram bot from PR7b.
   - Deploy web app with PR9a + PR9b.
   - Create test user on web (sign up).

2. **Test Linking:**
   - [ ] Open Telegram, start chat with bot.
   - [ ] Send `/start`, verify welcome message.
   - [ ] Send `/link`, verify magic link received.
   - [ ] Click magic link (opens browser).
   - [ ] Verify redirected to `/auth/link-telegram?token=...`.
   - [ ] If not signed in: Redirected to sign in, then back to link page.
   - [ ] See confirmation: "Link Telegram account @johndoe?"
   - [ ] Click "Confirm".
   - [ ] See success message: "Telegram account linked!"
   - [ ] Return to Telegram, send `/profile`.
   - [ ] Verify profile shown (email, certification, etc.).

3. **Test Cross-Channel Sync:**
   - [ ] On web: Navigate to `/chat`, send message "Test from web".
   - [ ] On Telegram: Send message "Test from Telegram".
   - [ ] On web: Navigate to `/history`, verify both messages in same conversation.
   - [ ] Click "Resume" in web history, verify both messages visible in chat.

4. **Test Profile Sync:**
   - [ ] On web: Navigate to `/profile`, update logged dives to 50.
   - [ ] On Telegram: Send message "Where can I dive with 50 dives?"
   - [ ] Verify bot response considers 50 dives (e.g., suggests intermediate sites).

5. **Test Unlinking:**
   - [ ] On web: Navigate to `/settings`, see "Telegram: @johndoe".
   - [ ] Click "Unlink Telegram", confirm.
   - [ ] See success message: "Telegram account unlinked."
   - [ ] On Telegram: Send `/profile`.
   - [ ] Verify message: "You don't have a linked account yet."

6. **Test Re-Linking:**
   - [ ] On Telegram: Send `/link` again.
   - [ ] Complete linking flow (click link, confirm).
   - [ ] Verify successfully re-linked.

### Manual Testing Checklist

**Linking Flow:**
- [ ] `/link` command sends magic link with valid token.
- [ ] Magic link expires after 10 minutes (test with old token).
- [ ] Linking requires web authentication (redirects to signin if not logged in).
- [ ] Confirmation page shows correct Telegram username/ID.
- [ ] Linking updates database (`users.telegram_user_id`).
- [ ] Duplicate linking returns error (409).

**Unlinking Flow:**
- [ ] `/unlink` requires confirmation (`/unlink confirm`).
- [ ] Unlinking sets `telegram_user_id` to NULL in database.
- [ ] After unlinking, Telegram bot uses guest sessions.

**Cross-Channel Sync:**
- [ ] Message sent on web appears in Telegram conversation context (next message considers history).
- [ ] Message sent on Telegram appears in web conversation history.
- [ ] Conversation has single record in `conversations` table.
- [ ] Timestamps correct for both channels.

**Profile Sync:**
- [ ] Profile updated on web reflects in Telegram bot responses.
- [ ] Profile shown in `/profile` command matches web profile.

**Error Handling:**
- [ ] Expired token shows error message (not crash).
- [ ] Invalid token returns 400 error.
- [ ] Unlinking when not linked returns appropriate message.
- [ ] `/profile` for unlinked user prompts to link.

**Regression Testing:**
- [ ] Unlinked Telegram users continue to use guest sessions (PR7b behavior).
- [ ] Web-only users (no Telegram) unaffected (columns remain NULL).
- [ ] Guest session expiry works (24h for unlinked Telegram users).

---

## 6. Verification

### Commands to Run

**Install Dependencies:**
```bash
pnpm install
```

**Run Database Migration:**
```bash
pnpm db:migrate
```

**Start Dev Server (Web):**
```bash
pnpm dev
```

**Deploy Telegram Bot (if not already running):**
```bash
# Assuming bot deployed on Cloud Run or similar from PR7b
gcloud run deploy telegram-bot --source . --region us-central1
```

**Run Unit Tests:**
```bash
pnpm test src/lib/auth/telegram-link-service.test.ts
```

**Run Integration Tests:**
```bash
pnpm test src/app/api/auth/link-telegram/
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

### Manual Verification Steps

**1. Database Verification:**
```sql
-- Verify columns added
\d users

-- Should show:
-- telegram_user_id | character varying(255) | | | 
-- telegram_username | character varying(255) | | | 

-- Verify unique constraint
\d+ users
-- Should show unique index on telegram_user_id
```

**2. Backend API Verification (Curl):**

```bash
# Sign in first to get token
export TOKEN="<auth_token_from_signin>"

# Generate test token (mock)
export TELEGRAM_TOKEN="<generated_token_from_telegram_link_service>"

# Link Telegram account
curl -X POST http://localhost:3000/api/auth/link-telegram \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"token":"'$TELEGRAM_TOKEN'"}'

# Expected: { "success": true, "telegramUsername": "johndoe" }

# Check link status
curl -X GET http://localhost:3000/api/auth/telegram-link-status \
  -H "Authorization: Bearer $TOKEN"

# Expected: { "isLinked": true, "telegramUsername": "johndoe", "telegramUserId": "123456789" }

# Verify in DB
psql $DATABASE_URL -c "SELECT email, telegram_user_id, telegram_username FROM users WHERE telegram_user_id IS NOT NULL;"

# Unlink Telegram account
curl -X POST http://localhost:3000/api/auth/unlink-telegram \
  -H "Authorization: Bearer $TOKEN"

# Expected: { "success": true }

# Verify in DB
psql $DATABASE_URL -c "SELECT email, telegram_user_id, telegram_username FROM users WHERE email='test@example.com';"
# telegram_user_id should be NULL
```

**3. Telegram Bot Verification:**

```
# In Telegram app:
1. Open bot (@DovvyBuddyBot or your bot username)
2. Send: /start
   Expected: Welcome message with mention of /link

3. Send: /link
   Expected: Magic link with instructions

4. Click link (opens browser)
   Expected: Redirected to /auth/link-telegram?token=...

5. Sign in if needed
   Expected: Confirmation page

6. Click "Confirm"
   Expected: "Telegram account linked!" message

7. Return to Telegram
8. Send: /profile
   Expected: Profile displayed (email, certification, etc.)

9. Send: /unlink confirm
   Expected: "Telegram account has been unlinked."

10. Send: /profile
    Expected: "You don't have a linked account yet."
```

**4. Cross-Channel Sync Verification:**

```
# On web:
1. Sign in at http://localhost:3000/auth/signin
2. Navigate to /chat
3. Send message: "Test from web"

# On Telegram:
4. Send message: "Test from Telegram"

# On web:
5. Navigate to /history
6. Verify single conversation with both messages
7. Click "Resume"
8. Verify both messages visible in chat

# Verify in DB:
psql $DATABASE_URL -c "SELECT id, user_id, channel_type, last_message_at FROM conversations WHERE user_id='<user_id>';"
# Should show single conversation with channel_type 'web' or 'telegram' (whichever was first)
# Note: Channel type may reflect first creation, but conversation includes messages from both channels
```

---

## 7. Rollback Plan

### Feature Flag Strategy

**Disable Telegram Linking:**
- Set `FEATURE_TELEGRAM_LINKING_ENABLED=false` in environment variables.
- Linking endpoints return 501 Not Implemented.
- Telegram bot commands `/link`, `/unlink`, `/profile` return "Feature temporarily unavailable."
- Existing linked accounts continue to work (no unlinking forced).

**Rollback Steps:**
1. Identify issue (linking broken, sync issues, security concern).
2. Set `FEATURE_TELEGRAM_LINKING_ENABLED=false`.
3. Redeploy or wait for env var to propagate.
4. Verify unlinked Telegram users work (guest sessions).
5. Fix issue offline, re-enable feature.

### Revert Strategy (Full Rollback)

**If feature flag is insufficient:**
1. Revert PR: `git revert <commit_hash>`.
2. Push revert commit: `git push origin main`.
3. CI/CD deploys reverted code.
4. Linking UI removed from settings page.
5. Telegram bot commands removed (or return "Not available").
6. Database migration can remain (columns unused if code reverted).
7. Optional: Drop columns if not planning to re-implement:
   ```sql
   ALTER TABLE users DROP COLUMN IF EXISTS telegram_user_id;
   ALTER TABLE users DROP COLUMN IF EXISTS telegram_username;
   ```

**Data Safety:**
- **Linked users:** Cannot access linked features (bot uses guest sessions), but data safe in DB.
- **Unlinked users:** No impact (continue using guest sessions).
- **Web-only users:** No impact (columns remain NULL).

---

## 8. Dependencies

### Upstream Dependencies (Must be complete)

- **PR9a:** Auth Infrastructure & User/Profile Schema (REQUIRED) — User tables, auth middleware.
- **PR9b:** Web UI Auth Integration (REQUIRED) — Signup/signin flow, settings page.
- **PR9a:** Agent Service Extraction (REQUIRED if agent is standalone).
- **PR7b:** Telegram Bot Adapter (REQUIRED) — Basic bot with guest sessions.

### External Dependencies

- **Telegram Bot:** Deployed and accessible (webhook mode recommended).
- **BotFather:** Command list updated with `/link`, `/unlink`, `/profile`.
- **Database:** Postgres instance with migrations from PR9a.

### Optional Dependencies

- **PR9c (Telegram Lead Capture):** Not required; lead capture can work with or without linking.

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Magic link token intercepted** | Attacker could link victim's Telegram to their account | 1. Short-lived tokens (10 min expiry)<br>2. One-time use (invalidate after linking)<br>3. Require web authentication (cannot link without signing in)<br>4. Show clear confirmation UI ("Link @username to your account?") |
| **User links multiple Telegram accounts** | Data integrity issues | 1. Enforce unique constraint on `telegram_user_id`<br>2. Allow only one Telegram account per user<br>3. Show error if trying to link already-linked Telegram account |
| **User forgets they linked** | Confusion when bot uses profile data | 1. Show linking status in `/profile` command<br>2. Clear unlink instructions in bot<br>3. Show linked status in web settings |
| **Cross-channel sync race condition** | Message order inconsistency | 1. Use timestamps to order messages<br>2. Accept eventual consistency (rare edge case)<br>3. Add optimistic locking if issue occurs frequently |
| **Telegram bot downtime** | Users cannot link or use bot | 1. Graceful error handling in web UI ("Bot temporarily unavailable")<br>2. Monitor bot uptime (Cloud Run logs)<br>3. Allow retry |
| **Token generation/verification failure** | Linking flow broken | 1. Comprehensive error logging<br>2. Test token expiry thoroughly<br>3. Use well-tested JWT library (jsonwebtoken or jose) |
| **Database unique constraint violation** | Linking fails with unclear error | 1. Check uniqueness before INSERT/UPDATE<br>2. Return clear 409 error message<br>3. Handle constraint violation gracefully |
| **User unlinks then re-links multiple times** | Session confusion | 1. Clear old Telegram sessions on unlink<br>2. Create fresh session on re-link<br>3. Test re-linking flow thoroughly |

---

## 10. Trade-offs

| Decision | Alternative | Rationale |
|----------|-------------|-----------|
| **Magic link flow** | Telegram Web App (inline OAuth) | Magic link is simpler to implement and works on all Telegram clients (mobile, desktop, web). Telegram Web App requires more complex setup and may not work on all clients. |
| **One Telegram account per user** | Allow multiple Telegram accounts | Simplifies data model and UX; most users only have one Telegram account. Multi-account support can be added in V2.2+ if demand exists. |
| **10-minute token expiry** | Longer expiry (30 min, 1 hour) | Short expiry reduces security risk (token interception); 10 minutes is enough time to complete flow. Can increase if users report issues. |
| **Require confirmation on web** | Auto-link on token click | Explicit confirmation is clearer UX and safer (user sees what they're linking). Auto-link could be confusing if user clicks wrong link. |
| **Store Telegram username in DB** | Fetch from Telegram API on demand | Storing username avoids API calls for display; usernames rarely change. Can sync username on next bot interaction if needed. |
| **Single PR for linking + sync** | Split into linking (PR9c) and sync (PR8d) | Linking and sync are tightly coupled; splitting would add complexity. Single PR is testable end-to-end. |
| **JWT for magic link tokens** | Database-backed tokens | JWT is stateless (no DB storage needed); simpler for short-lived tokens. DB-backed tokens are overkill for 10-minute expiry. |
| **Unlink requires confirmation** | Instant unlink | Confirmation prevents accidental unlink (no undo). User has time to reconsider. |

---

## 11. Open Questions

**Q1: Should we allow users to link multiple web accounts to one Telegram account?**
- **Context:** Current design is 1 Telegram : 1 Web account.
- **Recommendation:** No, enforce 1:1 for V2.0 simplicity. Multi-account support adds complexity (user must choose which account to use).
- **Decision:** 1:1 relationship enforced by unique constraint.

**Q2: Should Telegram username be synced periodically, or only on linking?**
- **Context:** Users can change Telegram username; stored username may become stale.
- **Recommendation:** Store on linking, update on next bot interaction (check if username changed). Don't poll Telegram API.
- **Decision:** Store on linking, update opportunistically (next message or command).

**Q3: Should we track which channel (web or Telegram) a conversation was started on?**
- **Context:** Conversations can span both channels; `conversations.channel_type` currently stores origin channel.
- **Recommendation:** Keep `channel_type` as origin channel for analytics; actual messages can come from both.
- **Decision:** `channel_type` is origin channel (where conversation started); messages from both channels are included.

**Q4: Should unlinking delete Telegram-originated conversations, or keep them?**
- **Context:** After unlinking, user loses access to Telegram bot with profile data.
- **Recommendation:** Keep conversations (they're part of user's history). User can delete account if they want to remove all data.
- **Decision:** Keep conversations; unlinking only disconnects Telegram account, doesn't delete data.

**Q5: Should we support Telegram group chats (multiple users) in V2.0?**
- **Context:** Current design is 1-on-1 chats only (as per PR7b assumptions).
- **Recommendation:** No, defer to V2.2+. Group chats have complex use cases (multiple users, permissions, etc.).
- **Decision:** 1-on-1 chats only for V2.0.

**Q6: Should `/profile` command be paginated if user has long preference text?**
- **Context:** Telegram messages have 4096 character limit.
- **Recommendation:** Truncate preferences in `/profile` output; show full preferences on web.
- **Decision:** Show summary in Telegram, link to web for full details.

---

## 12. Summary

PR9c completes the multi-channel authentication experience by enabling Telegram users to link their accounts to DovvyBuddy. This ensures a seamless, unified experience across web and Telegram with synchronized conversation history and consistent diver profiles.

**Key Deliverables:**
- ✅ Telegram account linking via magic link flow
- ✅ Database schema update (2 columns: `telegram_user_id`, `telegram_username`)
- ✅ Backend APIs for linking, unlinking, and status check
- ✅ Telegram bot commands: `/link`, `/unlink`, `/profile`
- ✅ Cross-channel session sync (messages from both channels in same conversation)
- ✅ Profile sync (updates on web reflect in Telegram bot)
- ✅ Web UI integration (settings page shows linked status, unlink button)
- ✅ Comprehensive testing (unit, integration, E2E manual tests)

**Success Criteria:**
- Users can link Telegram to web account via magic link.
- Linked users access same profile and conversation history on both channels.
- Messages sent on web appear in Telegram conversation context, and vice versa.
- Unlinking disconnects Telegram account, reverts to guest sessions.
- All tests pass (unit + integration + E2E manual).
- No regressions (unlinked users continue to use guest sessions).

**User Value:**
- **Unified experience:** Start conversation on web, continue on mobile Telegram.
- **Persistent history:** Conversations saved regardless of channel.
- **Consistent profile:** Bot uses latest profile data from web.
- **Flexibility:** Link/unlink anytime, no lock-in.

**Next Steps After PR9c:**
- **PR9:** Dive log storage and management (V2 core feature).
- **PR10:** Trip planning history and itinerary generation.
- **PR11:** Personalized recommendations based on dive history.

This PR completes the V2.0 authentication and multi-channel foundation, enabling DovvyBuddy to provide a cohesive experience across all user touchpoints.
