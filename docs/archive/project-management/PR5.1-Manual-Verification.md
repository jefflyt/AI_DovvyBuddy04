# PR5.1 Manual Verification Checklist

**Created:** January 29, 2026  
**Status:** Ready for Testing  
**Related Plan:** [PR5.1-localStorage-Persistence.md](../plans/PR5.1-localStorage-Persistence.md)

---

## Pre-requisites

Before starting manual verification:

1. **Backend running:**

   ```bash
   cd src/backend
   uvicorn app.main:app --reload
   ```

2. **Frontend running:**

   ```bash
   pnpm dev
   ```

3. **Browser DevTools open:**
   - Chrome/Edge: F12 → Application tab → Local Storage → http://localhost:3000
   - Firefox: F12 → Storage tab → Local Storage → http://localhost:3000
   - Safari: Develop menu → Show Web Inspector → Storage tab

---

## Test Cases

### 1. First-time user (no localStorage)

**Steps:**

- [ ] Clear localStorage (Application tab → Local Storage → delete all)
- [ ] Navigate to http://localhost:3000/chat
- [ ] Verify no sessionId in localStorage
- [ ] Send first message: "What is Open Water certification?"
- [ ] Verify sessionId appears in localStorage with key `dovvybuddy-session-id`
- [ ] Verify value is valid UUID format (e.g., `123e4567-e89b-12d3-a456-426614174000`)

**Expected Result:**

- ✅ SessionId stored in localStorage after first message
- ✅ UUID format validated
- ✅ Session indicator appears in UI (Session: 123e4567...)

---

### 2. Page refresh (session restore)

**Steps:**

- [ ] Continue from test 1 (sessionId in localStorage)
- [ ] Send 2-3 more messages
- [ ] Note the sessionId value in localStorage
- [ ] Refresh page (Cmd+R / Ctrl+R)
- [ ] Verify sessionId in localStorage is unchanged
- [ ] Verify conversation history is NOT displayed (current limitation)
- [ ] Send new message: "Tell me more"
- [ ] Verify response continues from previous context

**Expected Result:**

- ✅ SessionId persists across refresh
- ✅ Backend retrieves conversation history
- ✅ New message uses restored sessionId
- ⚠️ UI doesn't pre-load history (acceptable for V1)

---

### 3. Browser close and reopen

**Steps:**

- [ ] Close browser tab completely
- [ ] Reopen http://localhost:3000/chat in new tab
- [ ] Verify sessionId restored from localStorage
- [ ] Send message, verify session continues

**Expected Result:**

- ✅ SessionId persists after browser close
- ✅ Session works after reopening

---

### 4. Session expired

**Steps:**

- [ ] Create a session by sending a message
- [ ] Note the sessionId from localStorage
- [ ] Manually expire session in DB:
  ```sql
  UPDATE sessions
  SET expires_at = NOW() - INTERVAL '1 hour'
  WHERE id = 'your-session-id';
  ```
- [ ] Send another message
- [ ] Verify error message: "Your session has expired. Starting a new chat..."
- [ ] Verify old sessionId cleared from localStorage
- [ ] Send another message
- [ ] Verify new sessionId created and saved to localStorage

**Expected Result:**

- ✅ Error message displayed
- ✅ Old sessionId cleared
- ✅ New session created automatically
- ✅ No crash or data loss

---

### 5. Private browsing (localStorage unavailable)

**Steps:**

- [ ] Open chat in private/incognito window
- [ ] Send message
- [ ] Verify session works (sessionId in memory)
- [ ] Open browser console, verify warning: "localStorage unavailable, session will not persist"
- [ ] Refresh page
- [ ] Verify new session created (old sessionId lost)

**Expected Result:**

- ✅ App works without localStorage
- ✅ Warning logged in console (dev mode)
- ⚠️ Session lost on refresh (expected behavior)

---

### 6. Multiple tabs (same session)

**Steps:**

- [ ] Open http://localhost:3000/chat in Tab 1
- [ ] Send message, note sessionId in localStorage
- [ ] Open http://localhost:3000/chat in Tab 2 (same browser)
- [ ] Verify both tabs have same sessionId (from localStorage)
- [ ] Send message in Tab 1
- [ ] Switch to Tab 2, send message
- [ ] Verify both messages go to same session (check backend logs or DB)
- [ ] Refresh Tab 2
- [ ] Verify Tab 2 still has correct sessionId

**Expected Result:**

- ✅ Both tabs share same sessionId
- ✅ Both tabs can send messages
- ⚠️ Tabs don't see each other's messages without refresh (expected for V1)

---

### 7. Invalid sessionId in localStorage

**Steps:**

- [ ] Open dev tools → Application → Local Storage
- [ ] Manually edit `dovvybuddy-session-id` to invalid value: "not-a-uuid"
- [ ] Refresh page
- [ ] Send message
- [ ] Verify backend returns SESSION_NOT_FOUND error
- [ ] Verify localStorage cleared
- [ ] Verify new session created

**Expected Result:**

- ✅ Invalid sessionId detected
- ✅ localStorage cleared automatically
- ✅ New session created without crash

---

### 8. Console logging (dev mode)

**Steps:**

- [ ] Open dev tools → Console
- [ ] Clear localStorage, refresh page
- [ ] Send first message
- [ ] Verify log: "Session saved to localStorage: {uuid}"
- [ ] Refresh page
- [ ] Verify log: "Session restored from localStorage: {uuid}"

**Expected Result:**

- ✅ Restoration logged
- ✅ Save logged
- ✅ Session expiry logged (if triggered)

---

## Browser Compatibility

Test on the following browsers:

- [ ] **Chrome** (latest)
- [ ] **Firefox** (latest)
- [ ] **Safari** (latest)
- [ ] **Edge** (latest)

**Expected:** Feature works identically on all browsers.

---

## Edge Cases

### localStorage Quota Exceeded

**Note:** Difficult to test manually. Covered by unit tests.

**Steps (if testing):**

- [ ] Fill localStorage with large data until quota exceeded
- [ ] Verify app continues to work (session in memory)
- [ ] Verify warning logged in console

---

### Multiple Sessions (Different Devices)

**Note:** Out of scope for V1 (requires auth for cross-device sync).

**Current Behavior:**

- Each device has independent sessionId in localStorage
- No session sharing across devices

---

## Verification Results

**Tester:** \***\*\*\*\*\***\_\***\*\*\*\*\***  
**Date:** \***\*\*\*\*\***\_\***\*\*\*\*\***  
**Browser:** \***\*\*\*\*\***\_\***\*\*\*\*\***  
**Result:** ☐ Pass ☐ Fail

**Issues Found:**

1. ***
2. ***
3. ***

**Notes:**

---

---

---

---

## Automated Tests

Before marking PR complete, run:

```bash
# Unit tests
pnpm test

# Integration tests (requires backend running)
pnpm test:integration

# Typecheck
pnpm typecheck

# Lint
pnpm lint
```

**All tests must pass.**

---

## Definition of Done

- [x] Code changes implemented in `src/app/chat/page.tsx`
- [x] Unit tests added in `src/app/chat/__tests__/page.test.tsx`
- [x] Integration tests added in `tests/integration/session-persistence.test.ts`
- [ ] All automated tests pass
- [ ] Manual verification completed for all 8 test cases
- [ ] Tested on Chrome, Firefox, Safari, Edge
- [ ] Console logs verified (dev mode only)
- [ ] localStorage persistence confirmed
- [ ] Session expiry handling verified
- [ ] Code review completed
- [ ] PR merged to main
- [ ] Deployed to Vercel preview
- [ ] Smoke test on production (if deployed)

---

**End of Manual Verification Checklist**
