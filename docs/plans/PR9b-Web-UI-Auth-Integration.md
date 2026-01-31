# PR8b: Web UI Auth Integration & Guest Session Migration

**Branch Name:** `feature/pr8b-web-ui-auth-integration`  
**Status:** Planned  
**Date:** December 29, 2025  
**Updated:** January 8, 2026 (Backend clarification)  
**Based on:** PR9-User-Auth-Profiles.md, PR9a-Auth-Infrastructure.md

> **✅ BACKEND NOTE:** Frontend will integrate with Python/FastAPI auth endpoints (from PR8a) using NextAuth.js for session management. API calls go to FastAPI backend. Original plan focuses on React/Next.js frontend components.

---

## 1. Feature/Epic Summary

### Objective

Integrate authentication UI into the web interface, enabling users to sign up, sign in, manage profiles, and access conversation history. This PR makes authentication visible and usable to end users while maintaining full backward compatibility with guest sessions. Users can optionally migrate their active guest session to a new account, preserving their current conversation.

### User Impact

**Primary Users (All Divers):**
- **New users** can create accounts to save conversation history and preferences across devices.
- **Returning users** can sign in and resume previous conversations from any device.
- **Guest users** continue to use the app without signup (no forced registration).
- **Active guest users** who decide to sign up can import their current conversation into their new account.

**User Flows Enabled:**
- Browse landing page → Click "Sign Up" → Create account → Verify email → Start chatting with persistent history.
- Start chatting as guest → Decide to save conversation → Sign up → Import guest session → Continue as authenticated user.
- Sign in from different device → View conversation history → Resume previous chat.
- Update diver profile (certification, dive count) → Get better-tailored recommendations.
- Delete account → All data removed (GDPR compliance).

### Dependencies

**Upstream (Must be complete):**
- **PR8a:** Auth Infrastructure & User/Profile Schema (REQUIRED) — Backend APIs, database tables, auth middleware.
- **PR1-6:** Full web V1 functionality (database, RAG, sessions, lead capture, landing page, chat interface, E2E testing).

**External Dependencies:**
- **NextAuth.js React Hooks:** `useSession()` hook from `next-auth/react` for client-side session access.
- **NextAuth.js:** Already configured in PR8a with Credentials provider.

**Optional:**
- **PR7a-7c (Telegram):** Not required for PR8b; Telegram account linking is in PR8c.

### Assumptions

- **Assumption:** Custom auth forms are used (NextAuth.js Credentials provider doesn't have prebuilt components like Clerk); styling with Tailwind CSS.
- **Assumption:** Email verification is required (enforced by Clerk); unverified users see banner prompting to check email.
- **Assumption:** Profile completion is optional after signup (dismissible banner); users can complete later.
- **Assumption:** Guest session migration is opt-in (user chooses to import or start fresh); failed migrations log error but don't block signup.
- **Assumption:** Conversation history page shows most recent conversations first (sorted by `last_message_at`).
- **Assumption:** Users can archive conversations (soft delete) but not permanently delete individual conversations (only full account deletion).
  - Rationale: Simplifies V2.0; add granular delete in V2.1 if users request.
- **Assumption:** Mobile-responsive UI is tested manually on common viewports (no automated visual regression testing in V2.0).
- **Assumption:** Auth state is managed by NextAuth.js React hooks (`useSession()`); no custom auth context needed.
- **Assumption:** Sign out clears all client-side state (localStorage session ID, etc.).

---

## 2. Complexity & Fit

### Classification

**Single-PR** (Frontend-focused with clear integration points)

### Rationale

**Why Single-PR:**
- **Focused on UI layer:** All backend endpoints ready from PR8a; this PR only adds frontend components and pages.
- **Well-defined integration points:** Auth state from Clerk hooks, API calls to existing endpoints.
- **Incremental testing:** Can test each page/flow independently before merging.
- **Feature-flagged:** Uses same `FEATURE_USER_AUTH_ENABLED` flag from PR8a; can be enabled gradually.
- **Clear acceptance criteria:** Signup → Signin → Profile → History → Delete account flows are straightforward to test.

**Estimated Effort:**
- **Frontend:** Medium-High (10+ new components, 6 new pages, auth state integration).
- **Backend:** None (all endpoints from PR8a).
- **Testing:** Medium (component tests, integration tests, E2E smoke test).
- **Design/UX:** Low-Medium (mobile-responsive styling with Tailwind).

**Estimated Time:** 3-5 days for solo founder (depends on Clerk UI customization needs).

---

## 3. Full-Stack Impact

### Frontend

**New Pages:**

1. **`/app/auth/signin/page.tsx`** — Sign-in page
   - Custom form with email and password fields.
   - Uses NextAuth.js `signIn('credentials', {...})` for authentication.
   - Redirects to `/chat` after successful signin.
   - Link to signup page ("Don't have an account? Sign up").
   - Link to password reset (custom implementation or deferred to V2.1).

2. **`/app/auth/signup/page.tsx`** — Sign-up page
   - Custom form with email, password, confirm password fields.
   - Calls `POST /api/auth/signup` to create user.
   - Includes email, password fields.
   - Optional: Name field (stored in user profile).
   - Redirects to email verification page after signup.
   - Link to signin page ("Already have an account? Sign in").

3. **`/app/auth/verify/page.tsx`** — Email verification confirmation
   - Shows "Check your email" message with instructions.
   - "Resend verification email" button (calls custom resend endpoint).
   - If `?token=...` in URL, auto-verifies by calling `POST /api/auth/verify-email`.
   - Redirects to chat page after verification confirmed.

4. **`/app/profile/page.tsx`** — User profile management (protected)
   - Displays current user info (email, joined date).
   - Editable diver profile form:
     - Certification agency (dropdown: PADI, SSI, CMAS, NAUI, Other).
     - Certification level (dropdown: Open Water, Advanced, Rescue, Divemaster, Instructor, Other).
     - Logged dives (number input).
     - Comfort level (dropdown: Beginner, Intermediate, Advanced).
     - Preferences (textarea or structured fields: preferred dive types, interests).
   - "Save Profile" button (calls `PATCH /api/profile`).
   - Success/error messages.
   - Link to settings page.

5. **`/app/settings/page.tsx`** — Account settings (protected)
   - Display current email (non-editable in V2.0; add change email in V2.1).
   - "Change Password" section (custom form, calls dedicated endpoint or deferred to V2.1).
   - "Delete Account" section:
     - Warning message ("This will permanently delete all your data").
     - "Delete My Account" button (requires confirmation).
     - Confirmation modal with re-enter email or checkbox.
     - Calls `DELETE /api/profile`.
     - Redirects to landing page after deletion.
   - Link to profile page.

6. **`/app/history/page.tsx`** — Conversation history (protected)
   - List of user's conversations (paginated, 20 per page).
   - Each conversation card shows:
     - Auto-generated title (first user message, truncated to 50 chars).
     - Channel type badge (Web or Telegram).
     - Last message timestamp (relative: "2 hours ago", "3 days ago").
     - Message count (optional).
   - Actions per conversation:
     - "Resume" button → Loads conversation into chat page.
     - "Archive" button → Marks as archived (hidden from default view).
   - Toggle "Show Archived" (includes archived conversations in list).
   - Empty state: "No conversations yet. Start chatting to see history here."
   - Pagination controls (Previous / Next).

**Modified Pages:**

7. **`/app/page.tsx`** (Landing page)
   - **Header changes:**
     - If guest (not signed in): Show "Sign In" and "Sign Up" buttons in header.
     - If authenticated: Show user avatar (or initials) with dropdown menu.
   - **User dropdown menu (authenticated):**
     - Profile
     - Conversation History
     - Settings
     - Sign Out
   - **CTA changes:**
     - Guest: "Start Chatting" (existing behavior, leads to chat as guest).
     - Authenticated: "Go to Chat" or "Continue Last Conversation" (if history exists).

8. **`/app/chat/page.tsx`** (Chat interface)
   - **Detect auth state:**
     - Use NextAuth.js `useSession()` hook to check if signed in.
   - **If authenticated:**
     - Show "View History" button in header/sidebar.
     - Session is automatically linked to user via NextAuth.js session cookie (backend handles in `/api/chat`).
     - On first message, session is automatically linked to user (handled by backend).
     - If resuming conversation from history, load `sessionId` from URL param or state.
   - **If guest:**
     - Existing behavior (no history button).
     - Optional: Show banner "Sign up to save your conversations" (dismissible).
   - **Sign out handling:**
     - Use NextAuth.js `signOut()` function.
     - Clear local `sessionId` from localStorage/cookies.
     - Clear chat message history from state.
     - Redirect to landing page.

9. **`/app/layout.tsx`** (Root layout)
   - **Wrap app in NextAuth.js SessionProvider:**
     - Add `<SessionProvider>` from `next-auth/react` at root.
   - **Navigation changes:**
     - Conditionally render header based on auth state using `useSession()`.
     - Protected routes: If user visits `/profile`, `/settings`, or `/history` without being signed in, redirect to `/auth/signin`.

**New Components:**

10. **`src/components/auth/SignInForm.tsx`**
    - Email and password inputs.
    - "Sign In" button.
    - Error message display.
    - "Forgot password?" link (deferred to V2.1).
    - "Don't have an account? Sign up" link.
    - Calls `signIn('credentials', { email, password, redirect: false })` from next-auth/react.
    - Handles success/error states.

11. **`src/components/auth/SignUpForm.tsx`**
    - Email, password, confirm password inputs.
    - Optional: Name, certification level (basic profile fields).
    - "Sign Up" button.
    - Error message display.
    - "Already have an account? Sign in" link.
    - Calls `POST /api/auth/signup` directly (custom signup endpoint).

12. **`src/components/auth/UserMenu.tsx`**
    - Dropdown menu triggered by user avatar.
    - Menu items:
      - Profile (link to `/profile`)
      - History (link to `/history`)
      - Settings (link to `/settings`)
      - Sign Out (triggers NextAuth.js `signOut()`, redirects to landing).
    - Shows user email and avatar/initials.
    - Styled with Tailwind (dropdown overlay, hover effects).

13. **`src/components/auth/EmailVerificationBanner.tsx`**
    - Banner shown at top of app if user signed in but email not verified.
    - Message: "Please verify your email. Check your inbox for a verification link."
    - "Resend Email" button.
    - Dismissible (but reappears on page reload if still unverified).

14. **`src/components/profile/DiverProfileForm.tsx`**
    - Form with fields:
      - Certification agency (select dropdown).
      - Certification level (select dropdown).
      - Logged dives (number input, min 0, max 9999).
      - Comfort level (radio buttons or select).
      - Preferences (textarea or structured inputs).
    - "Save" button (loading state during API call).
    - Success/error toast or inline message.
    - Form validation (required fields, number ranges).

15. **`src/components/profile/ProfileCompletionPrompt.tsx`**
    - Banner shown after signup (or on profile page if incomplete).
    - Message: "Complete your diver profile to get better recommendations."
    - "Complete Profile" button (expands form or links to profile page).
    - Dismissible (saves dismissal state to localStorage).

16. **`src/components/profile/ConversationHistoryList.tsx`**
    - Renders list of conversations from API response.
    - Maps over `conversations` array, renders `<ConversationCard />` for each.
    - Shows pagination controls if `hasMore = true`.
    - Shows empty state if no conversations.

17. **`src/components/profile/ConversationCard.tsx`**
    - Single conversation display:
      - Title (truncated, clickable to resume).
      - Channel badge (icon + "Web" or "Telegram").
      - Timestamp (formatted: "2 hours ago").
      - Actions: Resume button, Archive button (Archive → Archive icon, shows "Unarchive" if archived).
    - Hover effect, responsive layout.

18. **`src/components/chat/GuestSessionMigrationPrompt.tsx`**
    - Banner/modal shown after signup if guest session active.
    - Message: "You have an active conversation. Would you like to save it to your account?"
    - Buttons: "Save Conversation" (calls migration API), "Start Fresh" (creates new session).
    - Shows loading state during migration.
    - On success: Dismisses, shows success toast.
    - On error: Shows error message, offers retry or start fresh.

19. **`src/components/chat/GuestSignupPrompt.tsx`** (optional)
    - Dismissible banner in chat page for guest users.
    - Message: "Sign up to save your conversations and access them from any device."
    - "Sign Up" button (links to `/auth/signup`).
    - "Dismiss" button (saves dismissal to localStorage, doesn't show again for 7 days).

20. **`src/components/settings/DeleteAccountConfirmation.tsx`**
    - Modal triggered by "Delete Account" button.
    - Warning message with consequences listed:
      - All conversations deleted.
      - Profile data removed.
      - Cannot be undone.
    - Confirmation input: "Type DELETE to confirm" or checkbox "I understand this cannot be undone."
    - "Cancel" and "Delete My Account" buttons.
    - On confirm: Calls `DELETE /api/profile`, signs out, redirects to landing.

**UI States:**

- **Guest mode:** Header shows "Sign In" / "Sign Up"; no history button in chat; no protected pages accessible.
- **Authenticated mode:** Header shows user menu; chat shows history button; protected pages accessible.
- **Email unverified:** Banner at top prompts verification; some features may be limited (optional).
- **Profile incomplete:** Dismissible banner prompts profile completion (optional).
- **Session migration:** After signup, if guest session active, prompt to save conversation.
- **Loading states:** All forms and API calls show loading spinners/disabled buttons during requests.
- **Error states:** Form validation errors shown inline; API errors shown as toasts or inline messages.

**Navigation/Entry Points:**

- **Landing page header:** "Sign In" / "Sign Up" buttons (guest) → User avatar menu (authenticated).
- **Chat page:** "View History" button (authenticated only).
- **User menu:** Links to Profile, History, Settings, Sign Out.
- **Profile page:** Link to Settings.
- **Settings page:** Link to Profile.
- **History page:** Resume button loads conversation into chat.

### Backend

**No new backend changes** — All APIs implemented in PR8a.

**Frontend API Integration:**

- **Signup:** Calls `POST /api/auth/signup` with email/password.
- **Signin:** Calls NextAuth.js `signIn('credentials', {...})` function.
- **Email verification:** Custom flow; user clicks link in email with token, calls `POST /api/auth/verify-email`.
- **Get current user:** `GET /api/auth/me` (called on app load to hydrate user state, or use NextAuth.js session).
- **Get profile:** `GET /api/profile` (called on profile page load).
- **Update profile:** `PATCH /api/profile` (called on save button).
- **Delete account:** `DELETE /api/profile` (called on confirmation).
- **List conversations:** `GET /api/conversations?limit=20&offset=0` (called on history page load).
- **Resume conversation:** `POST /api/conversations/:id/resume` (returns `sessionId`, loads into chat).
- **Archive conversation:** `POST /api/conversations/:id/archive`.
- **Chat with auth:** `POST /api/chat` — NextAuth.js session cookie automatically sent (no manual Authorization header needed).
- **Migrate guest session:** Calls migration logic (part of signup flow or separate API call).

### Data

**No new data model changes** — All schema from PR8a.

**Frontend State Management:**

- **Auth state:** Managed by NextAuth.js React hooks (`useSession()`).
- **Profile state:** Fetched on page load, stored in React state, updated on save.
- **Conversation history state:** Fetched on history page load, paginated.
- **Chat session state:** Existing session management (sessionId in localStorage), now linked to user if authenticated.

### Infra / Config

**Environment Variables (no new vars, use from PR8a):**

```bash
# Already configured in PR8a
NEXTAUTH_SECRET=<random-32-char-string>
NEXTAUTH_URL=http://localhost:3000
FEATURE_USER_AUTH_ENABLED=true  # Enable for PR8b
```

**NextAuth.js Configuration:**

- **Custom Pages (in nextauth-config.ts):**
  - Sign-in page: `/auth/signin`
  - Sign-up page: `/auth/signup` (linked from signin page)
  - Error page: `/auth/error` (optional, can use default)
- **Callbacks (in nextauth-config.ts):**
  - After sign-in redirect: `/chat`
  - After sign-out redirect: `/`
- **Email templates:** Custom verification email sent via Resend API in signup endpoint.

---

## 4. PR Roadmap (Single-PR Plan)

### Phase 1: NextAuth.js SessionProvider & Protected Routes Setup

**Goal:** Set up NextAuth.js SessionProvider and route protection logic.

**Tasks:**
1. Wrap app in `<SessionProvider>` in `/app/layout.tsx`:
   ```typescript
   'use client';
   import { SessionProvider } from 'next-auth/react';
   
   export default function RootLayout({ children }) {
     return (
       <SessionProvider>
         <html>
           <body>{children}</body>
         </html>
       </SessionProvider>
     );
   }
   ```
2. Create `src/lib/auth/protected-route.tsx` middleware:
   - Higher-order component or hook to check auth state.
   - Uses `useSession()` from `next-auth/react`.
   - Redirects to `/auth/signin` if not authenticated.
3. Test auth state detection with `useSession()` hook in a test page.

**Acceptance Criteria:**
- SessionProvider initialized.
- `useSession()` hook returns session data when signed in, `null` when guest.
- Protected route HOC redirects to signin if not authenticated.

---

### Phase 2: Auth Pages (Signin, Signup, Verify)

**Goal:** Implement signup, signin, and email verification pages.

**Tasks:**
1. Create `/app/auth/signin/page.tsx`:
   - Custom form with email and password inputs.
   - Submit calls `signIn('credentials', { email, password, redirect: false })`.
   - Handle errors (invalid credentials, email not verified).
   - On success, redirect to `/chat`.
   - Style with Tailwind (centered card, responsive).
2. Create `/app/auth/signup/page.tsx`:
   - Custom form with email, password, confirm password.
   - Submit calls `POST /api/auth/signup`.
   - On success, redirect to `/auth/verify`.
   - Style consistently with signin.
3. Create `/app/auth/verify/page.tsx`:
   - Display "Check your email" message.
   - "Resend verification email" button (calls custom resend endpoint).
   - If `?token=...` in URL, auto-verify and redirect to signin.
   - Manual flow: user clicks link in email, opens verify page with token.
4. Create `src/components/auth/SignInForm.tsx` and `SignUpForm.tsx` components.
5. Test signup → verify → signin flow manually.

**Acceptance Criteria:**
- Signup page creates user in DB with hashed password.
- Verification email sent via Resend API.
- Signin page authenticates user via NextAuth.js Credentials provider.
- Verify page handles token verification.
- Email verification received (check test email inbox).

---

### Phase 3: User Menu & Header Integration

**Goal:** Add user menu to header, show auth state in UI.

**Tasks:**
1. Create `src/components/auth/UserMenu.tsx`:
   - Dropdown triggered by avatar/initials.
   - Menu items: Profile, History, Settings, Sign Out.
   - Sign Out button calls NextAuth.js `signOut()`, redirects to landing.
2. Modify `/app/page.tsx` (landing) header:
   - Check auth state with `useSession()`.
   - If guest: Show "Sign In" / "Sign Up" buttons.
   - If authenticated: Show `<UserMenu />`.
3. Modify `/app/chat/page.tsx` header:
   - Add "View History" button if authenticated.
4. Style user menu with Tailwind (dropdown, transitions).

**Acceptance Criteria:**
- Landing page header shows correct buttons based on auth state.
- User menu dropdown works, links navigate correctly.
- Sign Out clears session and redirects to landing.

---

### Phase 4: Profile Management Page

**Goal:** Build profile page with editable diver profile form.

**Tasks:**
1. Create `/app/profile/page.tsx` (protected):
   - Protect with auth redirect logic.
   - Fetch profile on load: `GET /api/profile`.
   - Display user email, join date (read-only).
2. Create `src/components/profile/DiverProfileForm.tsx`:
   - Fields: certification agency, level, logged dives, comfort level, preferences.
   - Dropdowns styled with Tailwind.
   - "Save" button calls `PATCH /api/profile`.
   - Show loading state during API call.
   - Show success toast on save.
3. Add form validation (required fields, number ranges).
4. Test profile update → verify DB updated.

**Acceptance Criteria:**
- Profile page loads user data.
- Form fields populate with existing data (if profile exists).
- Save button updates profile in DB.
- Error handling for API failures.

---

### Phase 5: Conversation History Page

**Goal:** Display user's conversation history with resume and archive actions.

**Tasks:**
1. Create `/app/history/page.tsx` (protected):
   - Fetch conversations: `GET /api/conversations?limit=20&offset=0`.
   - Display list with `<ConversationHistoryList />`.
2. Create `src/components/profile/ConversationHistoryList.tsx`:
   - Maps over conversations, renders `<ConversationCard />`.
   - Pagination controls (Previous / Next).
   - "Show Archived" toggle.
3. Create `src/components/profile/ConversationCard.tsx`:
   - Title, channel badge, timestamp.
   - "Resume" button → Calls `POST /api/conversations/:id/resume`, navigates to chat with `sessionId`.
   - "Archive" button → Calls `POST /api/conversations/:id/archive`, removes from list.
4. Handle empty state ("No conversations yet").
5. Test resume flow → verify chat loads conversation history.

**Acceptance Criteria:**
- History page lists conversations.
- Resume button loads conversation into chat.
- Archive button hides conversation from list.
- Pagination works for >20 conversations.

---

### Phase 6: Settings Page & Account Deletion

**Goal:** Build settings page with account deletion flow.

**Tasks:**
1. Create `/app/settings/page.tsx` (protected):
   - Display current email (read-only).
   - "Change Password" button → Redirects to Clerk's password change flow or shows Clerk component.
   - "Delete Account" section with warning.
2. Create `src/components/settings/DeleteAccountConfirmation.tsx`:
   - Modal with warning message.
   - Confirmation input ("Type DELETE" or checkbox).
   - "Cancel" and "Delete My Account" buttons.
   - On confirm: Call `DELETE /api/profile`.
   - Sign out and redirect to landing.
3. Test account deletion → verify user, profile, sessions, conversations deleted from DB.

**Acceptance Criteria:**
- Settings page shows email.
- Change password flow works (via Clerk).
- Delete account confirmation modal appears.
- Account deletion removes all user data.

---

### Phase 7: Guest Session Migration

**Goal:** Allow guest users to save their conversation when signing up.

**Tasks:**
1. Create `src/components/chat/GuestSessionMigrationPrompt.tsx`:
   - Banner/modal shown after signup if guest session exists.
   - "Save Conversation" button → Calls migration logic.
   - "Start Fresh" button → Creates new session, ignores guest session.
2. Implement migration logic in signup flow:
   - After Clerk signup completes, check if `sessionId` exists in localStorage.
   - If yes, call `POST /api/auth/migrate-session` (new endpoint to add or inline logic).
   - Backend (from PR8a): Update `sessions.user_id`, create conversation record.
3. Test flow: Start chat as guest → Sign up → See migration prompt → Save → Verify conversation in history.

**Acceptance Criteria:**
- Migration prompt appears after signup if guest session active.
- "Save Conversation" successfully links session to user.
- Conversation appears in user's history.
- "Start Fresh" creates new session, guest session expires.

---

### Phase 8: Chat Page Auth Integration

**Goal:** Update chat page to include auth token in API calls, show history button.

**Tasks:**
1. Modify `/app/chat/page.tsx`:
   - Check auth state with `useUser()`.
   - If authenticated:
     - Add "View History" button in UI.
     - Include `Authorization: Bearer <token>` in `/api/chat` requests (get token from Clerk's `getToken()`).
   - If guest:
     - Existing behavior (no token).
     - Optional: Show "Sign up to save" banner (dismissible).
2. Handle session resume:
   - If navigating to chat from history "Resume" button, load `sessionId` from URL param or passed state.
   - Fetch session messages from backend (or already included in conversation data).
3. Test authenticated chat → verify session linked to user in DB.

**Acceptance Criteria:**
- Authenticated users see "View History" button.
- Chat API calls include auth token.
- Sessions are automatically linked to user.
- Resume from history loads conversation correctly.

---

### Phase 9: Optional Features & Polish

**Goal:** Add nice-to-have features and polish UX.

**Tasks:**
1. Create `src/components/auth/EmailVerificationBanner.tsx`:
   - Show at top of app if email unverified.
   - "Resend Email" button.
2. Create `src/components/profile/ProfileCompletionPrompt.tsx`:
   - Show after signup or on profile page if incomplete.
   - Dismissible with localStorage persistence.
3. Create `src/components/chat/GuestSignupPrompt.tsx` (optional):
   - Banner in chat for guests.
   - "Sign up to save conversations."
4. Mobile responsiveness:
   - Test all pages on mobile viewport (375px, 768px).
   - Ensure dropdowns, forms, and history list work on small screens.
5. Loading states:
   - Add spinners to all API calls (profile save, conversation load, etc.).
6. Error handling:
   - Consistent error toast/banner for API failures.

**Acceptance Criteria:**
- Email verification banner shows when needed.
- Profile completion prompt dismissible.
- Mobile UI works on common viewports.
- All forms have loading states.

---

### Phase 10: Testing & Verification

**Goal:** Comprehensive testing of all auth flows.

**Tasks:**
1. **Unit tests:**
   - Component tests for forms, user menu, history list.
2. **Integration tests:**
   - Test auth state detection.
   - Test profile update flow.
   - Test conversation resume flow.
3. **E2E smoke test:**
   - Signup → Verify → Profile update → Chat → History → Delete account.
4. **Manual testing checklist:**
   - All flows in different browsers (Chrome, Safari, Firefox).
   - Mobile testing (iOS Safari, Android Chrome).
5. **Regression testing:**
   - Guest chat flow still works (no auth).
   - Lead capture works for both guest and authenticated.

**Acceptance Criteria:**
- All tests pass.
- E2E smoke test completes successfully.
- No regressions in guest flows.
- Manual checklist complete.

---

## 5. Testing

### Unit Tests

**Component Tests (Vitest + React Testing Library):**

1. **`src/components/auth/UserMenu.test.tsx`**
   ```typescript
   describe('UserMenu', () => {
     test('renders user email', () => {
       render(<UserMenu user={{ email: 'test@example.com' }} />);
       expect(screen.getByText('test@example.com')).toBeInTheDocument();
     });
     
     test('sign out button calls signOut', () => {
       const signOutMock = jest.fn();
       render(<UserMenu user={{...}} signOut={signOutMock} />);
       fireEvent.click(screen.getByText('Sign Out'));
       expect(signOutMock).toHaveBeenCalled();
     });
   });
   ```

2. **`src/components/profile/DiverProfileForm.test.tsx`**
   ```typescript
   describe('DiverProfileForm', () => {
     test('renders form fields', () => {
       render(<DiverProfileForm profile={{}} />);
       expect(screen.getByLabelText('Certification Agency')).toBeInTheDocument();
       expect(screen.getByLabelText('Logged Dives')).toBeInTheDocument();
     });
     
     test('validates logged dives (min 0)', () => {
       render(<DiverProfileForm />);
       const input = screen.getByLabelText('Logged Dives');
       fireEvent.change(input, { target: { value: '-5' } });
       fireEvent.submit(screen.getByRole('button', { name: 'Save' }));
       expect(screen.getByText('Must be 0 or greater')).toBeInTheDocument();
     });
     
     test('calls onSave with form data', async () => {
       const onSaveMock = jest.fn();
       render(<DiverProfileForm onSave={onSaveMock} />);
       fireEvent.change(screen.getByLabelText('Logged Dives'), { target: { value: '25' } });
       fireEvent.submit(screen.getByRole('button', { name: 'Save' }));
       await waitFor(() => expect(onSaveMock).toHaveBeenCalledWith({ loggedDives: 25, ... }));
     });
   });
   ```

3. **`src/components/profile/ConversationCard.test.tsx`**
   ```typescript
   describe('ConversationCard', () => {
     test('renders conversation title and timestamp', () => {
       const conversation = {
         id: '1',
         title: 'How do I get Open Water certified?',
         lastMessageAt: new Date('2025-12-28T10:00:00Z'),
         channelType: 'web'
       };
       render(<ConversationCard conversation={conversation} />);
       expect(screen.getByText('How do I get Open Water certified?')).toBeInTheDocument();
       expect(screen.getByText(/1 day ago/i)).toBeInTheDocument();
     });
     
     test('resume button calls onResume', () => {
       const onResumeMock = jest.fn();
       render(<ConversationCard conversation={{...}} onResume={onResumeMock} />);
       fireEvent.click(screen.getByText('Resume'));
       expect(onResumeMock).toHaveBeenCalled();
     });
   });
   ```

### Integration Tests

**API Integration Tests:**

1. **Profile update flow:**
   ```typescript
   test('profile page updates profile via API', async () => {
     // Mock Clerk auth
     mockClerkAuth({ userId: 'user-1', email: 'test@example.com' });
     
     // Mock API response
     fetchMock.patch('/api/profile', { success: true, profile: {...} });
     
     render(<ProfilePage />);
     await waitForElementToBeRemoved(() => screen.queryByText('Loading...'));
     
     fireEvent.change(screen.getByLabelText('Logged Dives'), { target: { value: '30' } });
     fireEvent.click(screen.getByText('Save'));
     
     await waitFor(() => expect(screen.getByText('Profile updated')).toBeInTheDocument());
     expect(fetchMock.calls('/api/profile')).toHaveLength(1);
   });
   ```

2. **Conversation history flow:**
   ```typescript
   test('history page lists and resumes conversations', async () => {
     mockClerkAuth({ userId: 'user-1' });
     
     // Mock conversations API
     fetchMock.get('/api/conversations?limit=20&offset=0', {
       conversations: [{ id: 'conv-1', title: 'Test conversation', ... }],
       total: 1,
       hasMore: false
     });
     
     // Mock resume API
     fetchMock.post('/api/conversations/conv-1/resume', { success: true, sessionId: 'sess-1' });
     
     render(<HistoryPage />);
     await waitForElementToBeRemoved(() => screen.queryByText('Loading...'));
     
     expect(screen.getByText('Test conversation')).toBeInTheDocument();
     
     fireEvent.click(screen.getByText('Resume'));
     
     await waitFor(() => expect(window.location.pathname).toBe('/chat'));
   });
   ```

### E2E Tests (Playwright)

**E2E Smoke Test:**

```typescript
// tests/e2e/auth-flow.spec.ts
import { test, expect } from '@playwright/test';

test('complete auth flow: signup → profile → chat → history → delete', async ({ page }) => {
  // 1. Navigate to landing page
  await page.goto('http://localhost:3000');
  
  // 2. Click Sign Up
  await page.click('text=Sign Up');
  await expect(page).toHaveURL(/\/auth\/signup/);
  
  // 3. Fill signup form
  const testEmail = `test-${Date.now()}@example.com`;
  await page.fill('input[name="email"]', testEmail);
  await page.fill('input[name="password"]', 'Test1234!');
  await page.click('button:has-text("Sign Up")');
  
  // 4. Verify email verification page
  await expect(page).toHaveURL(/\/auth\/verify/);
  await expect(page.locator('text=Check your email')).toBeVisible();
  
  // 5. Manually verify email (or mock verification for test)
  // In test: Use Clerk test mode or API to auto-verify
  await page.evaluate(() => {
    // Simulate verification (test helper)
    window.clerkTestHelpers?.verifyEmail();
  });
  
  // 6. Navigate to chat
  await page.goto('http://localhost:3000/chat');
  await expect(page.locator('text=View History')).toBeVisible(); // Authenticated
  
  // 7. Send message
  await page.fill('textarea[placeholder*="message"]', 'What is Open Water certification?');
  await page.click('button:has-text("Send")');
  await expect(page.locator('text=/Open Water/i')).toBeVisible({ timeout: 10000 });
  
  // 8. Navigate to profile
  await page.click('button[aria-label="User menu"]'); // Avatar/menu button
  await page.click('text=Profile');
  await expect(page).toHaveURL(/\/profile/);
  
  // 9. Update profile
  await page.selectOption('select[name="certificationLevel"]', 'Open Water');
  await page.fill('input[name="loggedDives"]', '25');
  await page.click('button:has-text("Save")');
  await expect(page.locator('text=Profile updated')).toBeVisible();
  
  // 10. Navigate to history
  await page.click('text=Conversation History'); // From nav or direct
  await expect(page).toHaveURL(/\/history/);
  await expect(page.locator('text=/What is Open Water/i')).toBeVisible();
  
  // 11. Resume conversation
  await page.click('button:has-text("Resume")');
  await expect(page).toHaveURL(/\/chat/);
  await expect(page.locator('text=/What is Open Water/i')).toBeVisible(); // Message history loaded
  
  // 12. Delete account
  await page.click('button[aria-label="User menu"]');
  await page.click('text=Settings');
  await expect(page).toHaveURL(/\/settings/);
  await page.click('button:has-text("Delete Account")');
  
  // Confirmation modal
  await expect(page.locator('text=/permanently delete/i')).toBeVisible();
  await page.fill('input[placeholder*="DELETE"]', 'DELETE');
  await page.click('button:has-text("Delete My Account")');
  
  // 13. Verify redirect to landing and signed out
  await expect(page).toHaveURL('http://localhost:3000');
  await expect(page.locator('text=Sign In')).toBeVisible(); // Guest state
});
```

### Manual Testing Checklist

**Signup Flow:**
- [ ] Navigate to landing page, click "Sign Up".
- [ ] Fill email and password, submit.
- [ ] Receive verification email (check inbox).
- [ ] Click verification link, redirected to chat.
- [ ] User is signed in (see user menu in header).

**Signin Flow:**
- [ ] Navigate to landing page, click "Sign In".
- [ ] Enter valid credentials, submit.
- [ ] Redirected to chat, signed in.
- [ ] Try invalid credentials → See error message.

**Profile Management:**
- [ ] Navigate to profile page via user menu.
- [ ] See current profile data (or empty if not set).
- [ ] Update certification level, logged dives, preferences.
- [ ] Click "Save" → See success message.
- [ ] Refresh page → Verify data persisted.

**Conversation History:**
- [ ] Start chat as authenticated user, send multiple messages.
- [ ] Navigate to history page.
- [ ] See conversation listed with title and timestamp.
- [ ] Click "Resume" → Chat loads conversation.
- [ ] Click "Archive" → Conversation hidden (unless "Show Archived" enabled).

**Guest Session Migration:**
- [ ] Open incognito window, start chat as guest.
- [ ] Send a message ("Test guest message").
- [ ] Click "Sign Up" (from banner or header).
- [ ] Complete signup flow.
- [ ] See migration prompt: "Save conversation?"
- [ ] Click "Save Conversation" → Verify conversation in history.
- [ ] Resume conversation → See guest message included.

**Settings & Account Deletion:**
- [ ] Navigate to settings page.
- [ ] See current email (read-only).
- [ ] Click "Change Password" → Redirected to Clerk password change.
- [ ] Click "Delete Account" → See confirmation modal.
- [ ] Enter "DELETE", click "Delete My Account".
- [ ] Redirected to landing, signed out.
- [ ] Verify user deleted from DB (manual query or API test).

**Mobile Responsiveness:**
- [ ] Test all pages on mobile viewport (375px width).
- [ ] User menu dropdown works on mobile.
- [ ] Profile form fields stack vertically, readable.
- [ ] Conversation history cards responsive.
- [ ] Chat interface usable on mobile (existing from PR5).

**Error Handling:**
- [ ] Submit profile form with invalid data → See error message.
- [ ] Simulate API failure (disconnect network) → See error toast.
- [ ] Try to access protected page as guest → Redirected to signin.
- [ ] Incorrect signin credentials → See error message.

**Regression Testing (Guest Flow):**
- [ ] Open incognito window.
- [ ] Navigate to landing, click "Start Chatting" (guest CTA).
- [ ] Send message → Verify response (no auth required).
- [ ] Submit lead as guest → Verify lead captured (no user_id).
- [ ] Refresh page → Session persists (localStorage).
- [ ] Wait 24h (or manually expire) → Session expires.

---

## 6. Verification

### Commands to Run

**Install Dependencies (if needed):**
```bash
pnpm install
```

**Start Dev Server:**
```bash
pnpm dev
```

**Run Unit Tests:**
```bash
pnpm test src/components/
```

**Run E2E Tests:**
```bash
pnpm test:e2e
```

**Typecheck:**
```bash
pnpm typecheck
```

**Lint:**
```bash
pnpm lint
```

**Build (production):**
```bash
pnpm build
```

### Environment Setup for Testing

**Local Development:**
1. Set `FEATURE_USER_AUTH_ENABLED=true` in `.env.local`.
2. Ensure `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` is set.
3. Ensure Clerk application has correct redirect URLs configured.
4. Run `pnpm dev`.

**Staging/Production:**
1. Set environment variables in Vercel dashboard.
2. Configure Clerk redirect URLs for production domain.
3. Deploy via CI/CD pipeline.

### Manual Verification Steps

**Step-by-Step Verification:**

1. **Feature Flag Check:**
   - [ ] Confirm `FEATURE_USER_AUTH_ENABLED=true` in environment.

2. **Landing Page:**
   - [ ] Visit `http://localhost:3000`.
   - [ ] Verify "Sign In" and "Sign Up" buttons visible (guest state).

3. **Signup:**
   - [ ] Click "Sign Up".
   - [ ] Fill form: `test-$(date +%s)@example.com`, password `Test1234!`.
   - [ ] Submit, verify redirected to `/auth/verify`.
   - [ ] Check test email inbox for verification link.
   - [ ] Click link, verify redirected to `/chat`.

4. **Post-Signup State:**
   - [ ] Verify user menu visible in header (avatar/initials).
   - [ ] Click user menu, see Profile, History, Settings, Sign Out.

5. **Profile Page:**
   - [ ] Click "Profile" from menu.
   - [ ] Verify email displayed correctly.
   - [ ] Fill certification agency: PADI, level: Open Water, dives: 25.
   - [ ] Click "Save", verify success message.
   - [ ] Refresh page, verify data persisted.

6. **Chat (Authenticated):**
   - [ ] Navigate to `/chat`.
   - [ ] Verify "View History" button visible.
   - [ ] Send message: "What is Advanced Open Water?"
   - [ ] Verify response received.
   - [ ] Check DB: `SELECT user_id FROM sessions WHERE id='<sessionId>';` → Verify user ID present.

7. **Conversation History:**
   - [ ] Click "View History" (or navigate to `/history`).
   - [ ] Verify conversation listed with title matching first message.
   - [ ] Click "Resume" → Verify redirected to chat with conversation loaded.

8. **Archive Conversation:**
   - [ ] In history page, click "Archive" on a conversation.
   - [ ] Verify conversation hidden from default view.
   - [ ] Toggle "Show Archived" → Verify conversation reappears.

9. **Guest Session Migration:**
   - [ ] Open incognito window.
   - [ ] Navigate to `/chat` (guest).
   - [ ] Send message: "I am a guest user."
   - [ ] Click "Sign Up" (from banner or header).
   - [ ] Complete signup flow.
   - [ ] Verify migration prompt appears.
   - [ ] Click "Save Conversation".
   - [ ] Navigate to history → Verify guest message included in conversation.

10. **Settings & Delete Account:**
    - [ ] Navigate to `/settings`.
    - [ ] Verify email displayed.
    - [ ] Click "Delete Account".
    - [ ] In modal, type "DELETE" or check confirmation box.
    - [ ] Click "Delete My Account".
    - [ ] Verify redirected to landing, signed out.
    - [ ] Check DB: `SELECT * FROM users WHERE email='<test_email>';` → No rows.

11. **Mobile Testing:**
    - [ ] Resize browser to 375px width (iPhone SE).
    - [ ] Verify all pages render correctly (no horizontal scroll).
    - [ ] Test user menu dropdown (tap outside to close).
    - [ ] Test profile form (fields stack vertically).
    - [ ] Test conversation history (cards responsive).

12. **Regression: Guest Flow:**
    - [ ] Open new incognito window.
    - [ ] Navigate to landing, verify "Sign In"/"Sign Up" visible.
    - [ ] Click "Start Chatting" (or navigate to `/chat`).
    - [ ] Send message as guest → Verify response.
    - [ ] Submit lead → Verify lead captured (no user_id).
    - [ ] Refresh page → Session persists.

---

## 7. Rollback Plan

### Feature Flag Strategy

**Disable Auth UI:**
- Set `FEATURE_USER_AUTH_ENABLED=false` in production environment.
- Auth pages return 404 or redirect to landing.
- Chat page reverts to guest-only behavior (no "View History" button).
- Landing page shows guest CTAs only (no user menu).

**Rollback Steps:**
1. Identify issue (auth flow broken, UX problem, performance issue).
2. Set `FEATURE_USER_AUTH_ENABLED=false` in Vercel.
3. Redeploy or wait for environment variable to propagate.
4. Verify guest flows work.
5. Fix issue offline, redeploy with fix.

### Revert Strategy (Full Rollback)

**If feature flag is insufficient:**
1. Revert PR: `git revert <commit_hash>`.
2. Push revert commit: `git push origin main`.
3. CI/CD deploys reverted code.
4. Auth UI removed, app reverts to guest-only (PR6 state).
5. Existing user data in DB remains (no data loss, but inaccessible until feature re-enabled).

**Data Safety:**
- **Guest users:** No impact, continue using guest sessions.
- **Authenticated users:** Cannot sign in (UI hidden), but data safe in DB. Can re-access when feature re-enabled.
- **Backend APIs:** Still functional (from PR8a), just no UI to call them.

---

## 8. Dependencies

### Upstream Dependencies (Must be complete)

- **PR8a:** Auth Infrastructure & User/Profile Schema (REQUIRED) — All backend APIs and database tables.
- **PR1-6:** Web V1 functionality (database, chat, lead capture, landing page).

### External Dependencies

- **Clerk Account:** Application configured with redirect URLs.
- **Test Email Service:** For receiving verification emails during testing (use temp email service or personal inbox).

### Optional Dependencies

- **PR7a-7c (Telegram):** Not required; Telegram account linking is PR8c (separate from web UI).

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Email verification not received** | Users cannot complete signup | 1. Use Resend with domain authentication (SPF, DKIM)<br>2. Add "Resend Email" button<br>3. Check spam folder prompt<br>4. Support email for manual verification |
| **Guest session migration fails** | User loses active conversation | 1. Make migration optional ("Skip" button)<br>2. Test migration logic thoroughly<br>3. Log failures for debugging<br>4. Fail gracefully (allow user to continue as authenticated without migration) |
| **Profile form UX confusing** | Users abandon profile completion | 1. Make profile optional (dismissible prompt)<br>2. Clear help text and examples<br>3. Progress indicator if multi-step<br>4. Default values for dropdowns |
| **History page performance (many conversations)** | Slow load, poor UX | 1. Paginate list (20 per page)<br>2. Add loading skeleton<br>3. Optimize DB query (indexed on user_id, last_message_at)<br>4. Consider virtual scrolling in V2.1 |
| **Auth token expiry mid-conversation** | User kicked out unexpectedly | 1. Clerk handles token refresh automatically<br>2. Graceful error handling (prompt re-login)<br>3. Save draft message to localStorage<br>4. Long-lived tokens (30 days) |
| **Mobile UI issues** | Poor UX on small screens | 1. Test on real devices (iOS, Android)<br>2. Use responsive Tailwind classes<br>3. Test touch interactions (dropdown, forms)<br>4. Avoid fixed-width elements |
| **Clerk component styling conflicts** | Clerk UI doesn't match app branding | 1. Use Clerk's appearance customization API<br>2. Override CSS with Tailwind<br>3. Consider custom forms in V2.1 if branding critical |
| **Signup abandonment due to friction** | Low signup rate | 1. Make profile completion optional<br>2. Allow guest usage without signup<br>3. Clear value proposition ("Save your conversations")<br>4. A/B test signup flow in V2.1 |
| **Delete account regret** | Users accidentally delete data | 1. Strong confirmation modal<br>2. Type "DELETE" to confirm<br>3. Warning message with consequences<br>4. Consider "cooling off" period in V2.1 (mark for deletion, delete after 7 days) |

---

## 10. Trade-offs

| Decision | Alternative | Rationale |
|----------|-------------|-----------|
| **Use Clerk's prebuilt UI components** | Custom auth forms | Faster development for solo founder; Clerk components are accessible and secure out-of-box. Custom forms can be added in V2.1 if branding requires. |
| **Profile completion is optional** | Required before using chat | Reduces signup friction; users can complete profile when needed (e.g., before submitting lead). Optional banner prompts completion. |
| **Guest session migration is opt-in** | Automatic migration | Gives user control; avoids confusion if migration fails. Explicit choice ("Save" or "Start Fresh") is clearer UX. |
| **Conversation archive (soft delete) only** | Allow hard delete of individual conversations | Simpler V2.0; users can delete entire account if needed. Granular conversation deletion can be added in V2.1 if requested. |
| **Auto-generated conversation titles** | User-editable titles | Simpler UX; titles from first message are usually descriptive. Editable titles can be added in V2.1 if users request. |
| **Email verification required** | Optional verification | Prevents spam, ensures lead emails are deliverable. Adds friction but improves data quality. Can revisit in V2.1 if signup rate is too low. |
| **Pagination over infinite scroll** | Infinite scroll for history | Pagination is simpler to implement and test; works well for small conversation counts (<100). Infinite scroll can be added in V2.1 if needed. |
| **Single PR for all UI work** | Split into smaller PRs (signin, profile, history) | UI changes are cohesive and interdependent (user menu, auth state, etc.); splitting would add coordination overhead. Single PR is testable incrementally. |

---

## 11. Open Questions

**Q1: Should we auto-trigger profile completion prompt after signup, or only show on profile page?**
- **Context:** Profile is optional; prompt could be intrusive vs helpful.
- **Recommendation:** Show dismissible banner after signup and in chat (if profile incomplete). Don't block user.
- **Decision:** Dismissible banner after signup; can revisit in V2.1 if completion rate is low.

**Q2: Should conversation titles be auto-generated or user-editable?**
- **Context:** Auto-generation (first user message, truncated) is simple; editing adds feature.
- **Recommendation:** Auto-generate for V2.0; add editing in V2.1 if users request.
- **Decision:** Auto-generated titles for V2.0.

**Q3: Should we allow users to delete individual conversations, or only archive?**
- **Context:** Archive (soft delete) is simpler; hard delete is permanent.
- **Recommendation:** Archive only for V2.0; add hard delete in V2.1 if users need it (e.g., delete sensitive conversations).
- **Decision:** Archive only; hard delete in V2.1.

**Q4: Should "View History" button be in chat header, sidebar, or user menu?**
- **Context:** Chat header is most visible; user menu is consistent with other profile actions.
- **Recommendation:** Add to chat header (persistent button) for easy access.
- **Decision:** Chat header (next to "New Chat" button).

**Q5: Should we implement password reset UI in PR8b, or rely on Clerk's flow?**
- **Context:** Clerk provides password reset automatically via email; custom UI is branding consistency.
- **Recommendation:** Use Clerk's built-in flow for V2.0 (settings page links to Clerk); custom UI in V2.1 if branding critical.
- **Decision:** Clerk's built-in flow for V2.0.

**Q6: Should guest session migration prompt be a modal (blocking) or banner (non-blocking)?**
- **Context:** Modal forces decision; banner is less intrusive but may be missed.
- **Recommendation:** Modal after signup (one-time, dismissible); clearer UX.
- **Decision:** Modal prompt after signup.

---

## 12. Summary

PR8b completes the user-facing authentication experience for DovvyBuddy V2. This PR adds all UI components needed for users to create accounts, manage profiles, access conversation history, and control their data.

**Key Deliverables:**
- ✅ 6 new pages: Signin, Signup, Verify, Profile, Settings, History
- ✅ 10+ new components: User menu, profile form, conversation cards, session migration prompt, etc.
- ✅ Auth state integration with Clerk hooks
- ✅ Guest session migration flow
- ✅ Mobile-responsive UI (Tailwind)
- ✅ Comprehensive testing (unit, integration, E2E)
- ✅ 100% backward compatible (guest flow unchanged)

**Success Criteria:**
- Users can sign up, verify email, and sign in.
- Profile page allows editing certification and dive history.
- Conversation history lists past chats with resume/archive actions.
- Guest users can migrate active session on signup.
- Account deletion removes all user data (GDPR-compliant).
- All tests pass (unit + integration + E2E).
- Mobile UI works on common viewports.
- No regressions in guest flows.

**Next Steps:**
- **PR8c:** Telegram account linking (after PR8b + PR7b complete).
- **V2.1:** Dive log storage, trip planning history, personalized recommendations.

This PR is ready for implementation and will provide a complete authenticated web experience for DovvyBuddy users.
