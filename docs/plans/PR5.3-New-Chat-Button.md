# PR5.3: Add "New Chat" Button

**Created:** January 28, 2026  
**Completed:** January 29, 2026  
**Status:** ✅ COMPLETED & VERIFIED  
**Parent:** PR5 (Chat Interface & Integration)  
**Actual Effort:** 1 hour

---

## 0) Assumptions

1. **Assumption:** "New Chat" button will be in the chat page header (next to title or in top-right corner).
2. **Assumption:** Confirmation dialog is needed only if conversation has 2+ messages (prevents accidental resets).
3. **Assumption:** Starting new chat clears both component state AND localStorage (from PR5.1).

---

## 1) Clarifying questions

None - requirements are straightforward.

---

## 2) Feature summary

### Goal

Allow users to manually reset their chat session and start a fresh conversation without refreshing the page.

### User story

As a user chatting with DovvyBuddy,  
When I want to start a new conversation on a different topic,  
Then I should be able to click "New Chat" button to reset my session,  
So that I can begin fresh without my previous conversation context affecting new responses.

### Acceptance criteria

1. "New Chat" button is visible in chat page header (desktop and mobile)
2. Button is always enabled (no disabled state)
3. Clicking button shows confirmation dialog if conversation has 2+ messages: "Start a new chat? Your current conversation will be cleared."
4. Clicking button immediately resets session if conversation has 0-1 messages (no confirmation needed)
5. Confirming "New Chat" clears messages array in component state
6. Confirming "New Chat" sets sessionId to null in component state
7. Confirming "New Chat" removes sessionId from localStorage (calls localStorage.removeItem)
8. After reset, chat shows empty state message: "Ask me anything about diving..."
9. Next message user sends creates a new session (backend generates new sessionId)
10. Canceling confirmation dialog does nothing (conversation remains intact)
11. Button has clear visual design (icon + text or icon-only on mobile)
12. Button is keyboard accessible (tab navigation, Enter to activate)

### Non-goals (explicit)

- Saving previous conversation before clearing (requires session history feature, V2)
- Undo "New Chat" action (no session recovery)
- Archiving old conversation (requires auth + storage, V2)
- Confirmation checkbox "Don't show this again" (over-engineering for V1)
- Keyboard shortcut (e.g., Cmd+N) for new chat (nice-to-have, defer to V2)

---

## 3) Approach overview

### Proposed UX (high-level)

Desktop (>768px):
1. "New Chat" button in top-right corner of header (or next to title)
2. Button shows icon (➕ or 🔄) + text "New Chat"
3. User clicks → confirmation dialog appears (if 2+ messages)
4. Dialog: "Start a new chat? Your current conversation will be cleared." [Cancel] [New Chat]
5. User clicks "New Chat" → dialog closes, messages cleared, input focused

Mobile (<768px):
1. "New Chat" button in header (icon-only to save space, or hamburger menu)
2. Same confirmation dialog (modal overlay)
3. Dialog buttons stacked vertically for easier tapping

Confirmation dialog implementation options:
- Option A: Browser native confirm() - simplest, no custom UI
- Option B: Custom modal component - better UX, matches app design
- Recommendation: Option A for V1 (fast), Option B for V2 (polish)

### Proposed API (high-level)

No API changes needed.

Current behavior:
- POST /api/chat without sessionId → backend creates new session
- This already happens automatically when sessionId is null

### Proposed data changes (high-level)

No database changes.

State changes (src/app/chat/page.tsx):
- messages: [] (reset to empty array)
- sessionId: null (reset to null)
- localStorage: remove 'dovvybuddy-session-id' key

### AuthZ/authN rules (if any)

None - feature is available to all users (guest mode).

---

## 4) PR plan

### PR Title

feat: Add "New Chat" button to reset chat session

### Branch name

feature/pr5.3-new-chat-button

### Scope (in)

- Add "New Chat" button to chat page header
- Add handleNewChat function to reset state and localStorage
- Add confirmation dialog (if conversation has 2+ messages)
- Add button styling (desktop and mobile)
- Add keyboard accessibility (tab focus, Enter activation)
- Update empty state message (ensure it displays after reset)

### Out of scope (explicit)

- Session history/list (multiple saved conversations)
- Undo new chat action
- Saving conversation before clearing
- Keyboard shortcut (Cmd+N / Ctrl+N)
- Custom modal component for confirmation (use native confirm() in V1)
- Analytics tracking (defer to PR6)

### Key changes by layer

#### Frontend

File: src/app/chat/page.tsx

Changes:

1. Add handleNewChat function:
   - Check if messages.length >= 2
   - If yes, show confirmation: window.confirm("Start a new chat? Your current conversation will be cleared.")
   - If user cancels, return early (do nothing)
   - If confirmed or no confirmation needed:
     - Clear messages: setMessages([])
     - Clear sessionId: setSessionId(null)
     - Clear localStorage: localStorage.removeItem('dovvybuddy-session-id')
     - Optional: focus input field for immediate typing

2. Add "New Chat" button to header:
   - Position: top-right corner (or next to title)
   - Text: "New Chat" (desktop) or icon-only (mobile)
   - Icon: ➕ or 🔄 (use emoji or SVG icon)
   - onClick: handleNewChat
   - Styling: secondary button style (not primary like "Send")
   - Accessible label: aria-label="Start a new chat"

3. Ensure empty state message displays after reset:
   - Current implementation already handles messages.length === 0
   - No changes needed (verify in testing)

File structure (no new files needed):
- All changes in src/app/chat/page.tsx

#### Backend

No changes.

#### Data

No schema changes.

#### Infra/config

No environment variables needed.

#### Observability

Console logging (dev mode):
- "New chat started, session cleared"

---

### Edge cases to handle

1. **User clicks "New Chat" with no messages:**
   - No confirmation dialog (nothing to clear)
   - Clear state anyway (idempotent operation)
   - Show empty state message

2. **User clicks "New Chat" with 1 message (user only, no assistant reply yet):**
   - No confirmation dialog (conversation hasn't started)
   - Clear message and sessionId

3. **User clicks "New Chat" and cancels confirmation:**
   - Do nothing (conversation remains intact)
   - Focus returns to chat (user can continue chatting)

4. **User clicks "New Chat" while message is sending (isLoading=true):**
   - Allow (don't disable button during loading)
   - Confirmation dialog still shows
   - If user confirms, ongoing request completes but response is ignored (component state cleared)
   - Acceptable behavior for V1

5. **User clicks "New Chat", confirms, then immediately sends message:**
   - New message creates new session (sessionId=null triggers backend to create session)
   - Expected behavior

6. **localStorage unavailable (private browsing):**
   - localStorage.removeItem() throws error (SecurityError)
   - Wrap in try-catch (same pattern as PR5.1)
   - Session still clears in-memory state

7. **User has submitted lead, then clicks "New Chat":**
   - Conversation cleared (including lead confirmation message)
   - Lead still saved in DB (not affected by frontend state reset)
   - Expected behavior

8. **Multiple tabs open, user clicks "New Chat" in one tab:**
   - Tab 1: Session cleared, localStorage removed
   - Tab 2: Still has old sessionId (from localStorage, now stale)
   - Tab 2 next message: Backend may return SESSION_NOT_FOUND (sessionId cleared)
   - Tab 2 error handler clears localStorage, starts new session
   - Acceptable behavior for V1 (no cross-tab sync)

---

### Migration/compatibility notes (if applicable)

No migration needed - new feature, no existing data.

Backwards compatibility:
- Users currently using chat (before this PR) will see new "New Chat" button
- No breaking changes to existing functionality

---

## 5) Testing & verification

### Automated tests to add/update

#### Unit

File: src/app/chat/__tests__/page.test.tsx (update existing or create)

Tests to add:

1. Test "New Chat" button renders
   - Render component
   - Verify button exists with text "New Chat"
   - Verify button is enabled

2. Test handleNewChat with no messages (no confirmation)
   - Render component with messages=[]
   - Click "New Chat" button
   - Verify no confirmation dialog (mock window.confirm, expect not called)
   - Verify messages array cleared
   - Verify sessionId set to null
   - Verify localStorage.removeItem called

3. Test handleNewChat with 1 message (no confirmation)
   - Render component with messages=[{user message}]
   - Click "New Chat"
   - Verify no confirmation dialog
   - Verify state cleared

4. Test handleNewChat with 2+ messages (confirmation shown, user confirms)
   - Render component with messages=[{user}, {assistant}]
   - Mock window.confirm to return true
   - Click "New Chat"
   - Verify window.confirm called with correct message
   - Verify messages cleared
   - Verify sessionId cleared
   - Verify localStorage.removeItem called

5. Test handleNewChat with 2+ messages (confirmation shown, user cancels)
   - Render component with messages=[{user}, {assistant}]
   - Mock window.confirm to return false
   - Click "New Chat"
   - Verify window.confirm called
   - Verify messages NOT cleared (state unchanged)
   - Verify localStorage.removeItem NOT called

6. Test localStorage error handling
   - Mock localStorage.removeItem to throw SecurityError
   - Click "New Chat"
   - Verify app doesn't crash
   - Verify state still cleared (even if localStorage fails)

#### Integration

No integration tests needed - unit tests cover functionality.

Manual testing covers end-to-end behavior.

#### E2E (only if needed)

Deferred to PR6 (Playwright).

---

### Manual verification checklist

Pre-requisites:
- Backend running: cd src/backend && uvicorn app.main:app --reload
- Frontend running: pnpm dev
- Open http://localhost:3000/chat

Test cases:

1. **New Chat with no messages:**
   - [ ] Navigate to /chat
   - [ ] Verify empty state message displayed
   - [ ] Click "New Chat" button
   - [ ] Verify no confirmation dialog
   - [ ] Verify empty state still displayed
   - [ ] Verify no errors in console

2. **New Chat with 1 message (user only):**
   - [ ] Send message: "What is Open Water certification?"
   - [ ] Wait for response (don't send another message)
   - [ ] Click "New Chat" button
   - [ ] Verify no confirmation dialog
   - [ ] Verify messages cleared
   - [ ] Verify empty state displayed
   - [ ] Verify localStorage 'dovvybuddy-session-id' removed (check Application tab)

3. **New Chat with conversation (confirm):**
   - [ ] Send 2-3 messages, wait for responses
   - [ ] Click "New Chat" button
   - [ ] Verify confirmation dialog appears: "Start a new chat? Your current conversation will be cleared."
   - [ ] Click "OK" / "New Chat" (confirm)
   - [ ] Verify messages cleared
   - [ ] Verify empty state displayed
   - [ ] Verify sessionId removed from localStorage
   - [ ] Send new message: "Tell me about SSI"
   - [ ] Verify response received
   - [ ] Verify new sessionId created in localStorage (different from before)

4. **New Chat with conversation (cancel):**
   - [ ] Send 2-3 messages
   - [ ] Click "New Chat" button
   - [ ] Verify confirmation dialog
   - [ ] Click "Cancel" (reject)
   - [ ] Verify dialog closes
   - [ ] Verify messages still displayed (not cleared)
   - [ ] Verify sessionId still in localStorage
   - [ ] Send another message
   - [ ] Verify conversation continues (same sessionId)

5. **New Chat during message loading:**
   - [ ] Send message
   - [ ] Immediately click "New Chat" before response arrives
   - [ ] Confirm dialog
   - [ ] Verify messages cleared
   - [ ] Note: Response may still arrive but won't be displayed (state cleared)
   - [ ] Send new message
   - [ ] Verify new session starts

6. **New Chat after lead submission:**
   - [ ] Send message to create session
   - [ ] Submit lead (use PR5.2 form if available, or skip if not merged yet)
   - [ ] Verify lead confirmation message in chat
   - [ ] Click "New Chat", confirm
   - [ ] Verify messages cleared (including lead confirmation)
   - [ ] Verify lead still in DB: SELECT * FROM leads ORDER BY created_at DESC LIMIT 1;

7. **Mobile responsive:**
   - [ ] Open Chrome DevTools, switch to iPhone 12 (390x844)
   - [ ] Send 2 messages
   - [ ] Locate "New Chat" button (should be visible, not hidden)
   - [ ] Click button (verify tap target is large enough, 44x44px minimum)
   - [ ] Verify confirmation dialog is readable on small screen
   - [ ] Confirm, verify reset works

8. **Keyboard accessibility:**
   - [ ] Navigate to /chat
   - [ ] Press Tab repeatedly until "New Chat" button is focused
   - [ ] Verify focus visible (outline or highlight)
   - [ ] Press Enter key
   - [ ] Verify confirmation dialog appears (or action triggers if no messages)

9. **Private browsing (localStorage unavailable):**
   - [ ] Open chat in private/incognito window
   - [ ] Send 2 messages
   - [ ] Click "New Chat", confirm
   - [ ] Verify messages cleared
   - [ ] Verify no errors in console (localStorage.removeItem error caught)
   - [ ] Send new message
   - [ ] Verify new session works

10. **Multiple tabs:**
    - [ ] Open /chat in Tab 1, send 2 messages
    - [ ] Note sessionId in localStorage
    - [ ] Open /chat in Tab 2 (same browser)
    - [ ] Verify Tab 2 has same sessionId (from localStorage)
    - [ ] In Tab 1, click "New Chat", confirm
    - [ ] Verify Tab 1 messages cleared, localStorage cleared
    - [ ] Switch to Tab 2
    - [ ] Verify Tab 2 still shows old messages (hasn't refreshed)
    - [ ] In Tab 2, send message
    - [ ] Verify error (sessionId no longer valid) or new session created
    - [ ] Acceptable behavior for V1

11. **Console logging:**
    - [ ] Open console
    - [ ] Send 2 messages
    - [ ] Click "New Chat", confirm
    - [ ] Verify log: "New chat started, session cleared"

12. **Button visual design:**
    - [ ] Verify button has clear label/icon
    - [ ] Verify button doesn't clash with "Send" button (different color/style)
    - [ ] Verify button is visible against header background

---

### Commands to run

Install:
pnpm install

Dev:
Terminal 1: cd src/backend && uvicorn app.main:app --reload
Terminal 2: pnpm dev

Test:
pnpm test

Lint:
pnpm lint

Typecheck:
pnpm typecheck

Build:
pnpm build

---

## 6) Rollback plan

### If critical bugs found post-merge

Rollback strategy:
1. Revert commit: git revert <commit-sha>
2. Redeploy to Vercel

Impact of rollback:
- "New Chat" button removed
- Users can still start new chat by refreshing page
- No data loss (sessions in DB unaffected)
- No breaking changes to existing functionality

### Feature flag (not needed)

No feature flag needed - simple, low-risk UI change.

### Data considerations

No database changes - rollback only affects frontend.

No user data affected (sessions are server-side, localStorage is per-browser).

---

## 7) Follow-ups (optional)

1. **Custom confirmation modal (V2):**
   - Replace window.confirm() with custom Modal component
   - Better UX (matches app design, animated transitions)
   - Can add "Don't ask again" checkbox if users find confirmation annoying

2. **Keyboard shortcut (V2):**
   - Add Cmd+N / Ctrl+N to trigger "New Chat"
   - Register global keyboard listener
   - Show tooltip: "Press Cmd+N for new chat"

3. **Undo "New Chat" (V2):**
   - Save last conversation in temporary storage before clearing
   - Show toast: "Chat cleared. [Undo]"
   - Restore messages if user clicks "Undo" within 5 seconds
   - Requires careful state management

4. **Session history list (V2):**
   - Save multiple sessions in localStorage (or DB with auth)
   - Add "Recent Chats" sidebar
   - Allow user to switch between sessions
   - "New Chat" becomes "+" button to create additional session

5. **Conversation export before clearing (V2):**
   - Add option: "Export conversation before starting new chat?"
   - Download as TXT or PDF
   - Useful for users who want to save advice/recommendations

6. **Analytics tracking (PR6):**
   - Track "New Chat" button clicks (event)
   - Measure conversation length before reset (metric)
   - Understand user behavior (are they starting over due to poor responses?)

7. **Auto-suggest "New Chat" (V2):**
   - After X messages or Y minutes, show prompt: "Want to start a fresh conversation?"
   - Useful if conversation context becomes too long/confused

---

**End of PR5.3 Plan**

---

## Implementation Verification (Completed January 29, 2026)

### ✅ Implemented Features

1. **handleNewChat Function (src/app/chat/page.tsx)**
   - ✅ Confirmation logic for 2+ messages (lines 99-106)
   - ✅ Native window.confirm() dialog
   - ✅ Clears messages, sessionId, localStorage (calls clearSession)
   - ✅ Development logging (line 114)
   - ✅ No confirmation for 0-1 messages

2. **New Chat Button UI (src/app/chat/page.tsx)**
   - ✅ Button in header (lines 375-397)
   - ✅ Gray background (#6b7280) - distinct from primary buttons
   - ✅ Icon (➕) + text "New Chat"
   - ✅ onClick handler: handleNewChat
   - ✅ aria-label for accessibility (line 378)
   - ✅ title attribute for tooltip (line 393)
   - ✅ Always enabled (no disabled state)

3. **Responsive Design (src/app/chat/page.tsx)**
   - ✅ Inline CSS-in-JS with <style jsx> (lines 298-304)
   - ✅ Text hidden on mobile (<768px)
   - ✅ Icon-only display on small screens
   - ✅ Button part of flexbox layout with other action buttons

4. **clearSession Integration**
   - ✅ Uses existing clearSession helper (lines 77-90)
   - ✅ Clears localStorage with error handling
   - ✅ Resets sessionId to null
   - ✅ Clears messages array
   - ✅ Clears error state

5. **Test Coverage (src/app/chat/__tests__/page.test.tsx)**
   - ✅ New Chat functionality test suite (lines 202+)
   - ✅ Confirmation logic tests (4 tests)
   - ✅ clearSession state cleanup tests (3 tests)
   - ✅ Edge case tests (6 tests)
   - ✅ Confirmation dialog text test (1 test)
   - ✅ All 14 new tests passing (30 total tests passing)

### 🎯 Acceptance Criteria Status

| # | Criteria | Status |
|---|----------|--------|
| 1 | "New Chat" button visible in header | ✅ Verified |
| 2 | Button always enabled | ✅ Verified |
| 3 | Confirmation dialog if 2+ messages | ✅ Verified |
| 4 | No confirmation if 0-1 messages | ✅ Verified |
| 5 | Clears messages array on confirm | ✅ Verified |
| 6 | Sets sessionId to null on confirm | ✅ Verified |
| 7 | Removes sessionId from localStorage | ✅ Verified |
| 8 | Shows empty state message after reset | ✅ Verified |
| 9 | Next message creates new session | ✅ Verified |
| 10 | Canceling dialog does nothing | ✅ Verified |
| 11 | Button has clear visual design | ✅ Verified |
| 12 | Keyboard accessible (tab + Enter) | ✅ Verified |

### 📝 Manual Testing Results

**Tested by user on January 29, 2026:**
- ✅ New Chat with no messages (no confirmation)
- ✅ New Chat with 1 message (no confirmation)
- ✅ New Chat with 2+ messages (confirmation shown)
- ✅ User confirms → messages cleared, sessionId removed
- ✅ User cancels → conversation intact
- ✅ New Chat during message loading
- ✅ New Chat after lead submission (lead preserved in DB)
- ✅ Mobile responsive (icon-only on <768px)
- ✅ Keyboard accessibility (Tab + Enter)
- ✅ Private browsing mode (localStorage error handled)
- ✅ Multiple tabs behavior
- ✅ Console logging in dev mode
- ✅ Button visual design (gray, distinct from other buttons)

### 🔧 Technical Implementation Notes

**Key Files Modified:**
- `src/app/chat/page.tsx` - handleNewChat function, button UI, responsive CSS
- `src/app/chat/__tests__/page.test.tsx` - 14 new unit tests

**Implementation Details:**
- Uses native window.confirm() for V1 (custom modal deferred to V2)
- Confirmation message: "Start a new chat? Your current conversation will be cleared."
- Button positioned with lead capture buttons in header
- Flex layout with gap ensures proper spacing
- Mobile CSS hides `.new-chat-text` class below 768px

**Edge Cases Handled:**
- ✅ No messages (idempotent operation)
- ✅ 1 message (user only, no conversation yet)
- ✅ User cancels confirmation
- ✅ New Chat during loading (allowed)
- ✅ Immediate message after New Chat
- ✅ localStorage unavailable (try-catch wrapper)
- ✅ Lead submitted then New Chat (DB unaffected)
- ✅ Multiple tabs (each tab independent)

**Performance:**
- No API calls needed for New Chat
- Instant state reset (synchronous)
- localStorage.removeItem wrapped in try-catch (no crashes)

### 🚀 Next Steps (Deferred to V2)

- Custom confirmation modal (better UX)
- Keyboard shortcut (Cmd+N / Ctrl+N)
- Undo New Chat action
- Session history list
- Conversation export before clearing
- Analytics tracking

---
