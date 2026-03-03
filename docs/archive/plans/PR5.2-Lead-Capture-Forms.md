# PR5.2: Implement Lead Capture Forms

**Created:** January 28, 2026  
**Completed:** January 29, 2026  
**Status:** ✅ COMPLETED & VERIFIED  
**Parent:** PR5 (Chat Interface & Integration)  
**Actual Effort:** 4-6 hours

---

## 0) Assumptions

1. **Assumption:** Lead forms will be triggered manually (user clicks CTA) rather than auto-detected from conversation intent (NLP intent detection deferred to V2).
2. **Assumption:** Forms will be inline overlays within chat page rather than separate routes (keeps user in conversation context).
3. **Assumption:** Backend /api/leads endpoint from PR4 is fully functional and matches LeadRequest/LeadResponse types from API client.

---

## 1) Clarifying questions

None - requirements are clear from PR5 plan and PR4 implementation.

---

## 2) Feature summary

### Goal

Enable users to submit training or trip lead requests directly from the chat interface, converting conversations into business opportunities for partner dive shops.

### User story

As a user chatting with DovvyBuddy about certifications or destinations,  
When I'm ready to take action (get certified or book a trip),  
Then I should be able to submit my contact information and preferences through an inline form,  
So that a dive shop can follow up with me via email/phone.

### Acceptance criteria

1. Chat page displays "Request Training" and "Plan a Trip" buttons in UI (visible at all times or contextually)
2. Clicking either button opens an inline modal/overlay form without leaving the chat
3. Training form includes fields: name (required), email (required), phone (optional), agency preference (PADI/SSI/No Preference), certification level (dropdown), location preference (optional), additional message (optional)
4. Trip form includes fields: name (required), email (required), phone (optional), destination (text or dropdown), travel dates (text or date picker), certification level (dropdown), dive count (number), interests (checkboxes: wrecks, reefs, marine life, etc.), additional message (optional)
5. Form validates required fields client-side before submission (name, email)
6. Form validates email format (regex or validation library)
7. Submitting form calls apiClient.createLead() with correct payload
8. On successful submission, form closes and chat displays inline confirmation message: "Thanks! We'll be in touch soon. Feel free to keep asking questions."
9. On error, form displays error message without closing (user can retry)
10. User can cancel/close form without submitting (X button or Cancel button)
11. Form is mobile-responsive (renders as full-screen overlay on small screens, centered modal on desktop)
12. Session ID is included in lead payload (links lead to conversation history)
13. After submission, user can continue chatting in same session
14. Form resets when reopened (doesn't retain previous submission data)
15. Success confirmation includes leadId in console (for debugging/tracking)

### Non-goals (explicit)

- Auto-triggering form based on conversation intent (requires NLP, deferred to V2)
- Bot metadata hint for when to show form (backend doesn't return suggestLeadCapture yet)
- Pre-filling form fields from conversation context (requires backend extraction logic, deferred to V2)
- Multiple lead submissions per session tracking
- Lead submission history/list UI
- Real-time lead status updates (email delivery confirmation)
- CAPTCHA or bot protection (deferred to PR6)
- Advanced date picker component (use simple text input for "flexible" or "June 2026")
- Multi-step wizard form (all fields on one screen)

---

## 3) Approach overview

### Proposed UX (high-level)

Desktop (>768px):

1. Chat interface shows two buttons in header or below input: "Get Certified" | "Plan a Trip"
2. User clicks "Get Certified" → semi-transparent overlay appears with centered modal (max-width 600px)
3. Modal contains training form with 6-7 fields
4. User fills form, clicks "Submit" → loading spinner on button
5. On success → modal closes, chat displays: "✅ Thanks, [Name]! We'll contact you at [email] soon."
6. User continues chatting

Mobile (<768px):

1. Same buttons, smaller size or icon-only
2. Modal expands to full-screen (100vw x 100vh, with scroll if needed)
3. Close button (X) in top-right corner
4. Submit button fixed at bottom (always visible)

### Proposed API (high-level)

Endpoint: POST /api/leads (already implemented in PR4)

Training lead payload:
{
sessionId: "uuid",
email: "user@example.com",
name: "John Doe",
phone: "+1234567890", // optional
preferredContact: "email", // or "phone" or "whatsapp"
message: "Agency: PADI, Level: Open Water, Location: Singapore, Notes: ..."
}

Trip lead payload:
{
sessionId: "uuid",
email: "user@example.com",
name: "Jane Smith",
phone: "+1234567890",
preferredContact: "email",
message: "Destination: Tioman, Dates: June 2026, Certification: AOW, Dive Count: 25, Interests: Wrecks, Reefs, Notes: ..."
}

Backend response:
{
success: true,
leadId: "uuid",
message: "Thank you! We'll be in touch soon."
}

### Proposed data changes (high-level)

No database changes - leads table exists from PR1, /api/leads endpoint exists from PR4.

Component state additions (src/app/chat/page.tsx):

- showLeadForm: boolean (controls modal visibility)
- leadType: 'training' | 'trip' | null (which form to show)
- leadSubmitting: boolean (submission loading state)
- leadError: string | null (submission error message)

### AuthZ/authN rules (if any)

None - V1 is guest-only, no authentication required to submit leads.

Backend validation (from PR4):

- Email format validation
- Required field validation (email)
- Rate limiting (10 submissions per session ID)

---

## 4) PR plan

### PR Title

feat: Add lead capture forms for training and trip requests

### Branch name

feature/pr5.2-lead-capture-forms

### Scope (in)

- Add state variables for form management (showLeadForm, leadType, etc.) to chat page
- Add "Get Certified" and "Plan a Trip" buttons to chat UI
- Create LeadCaptureModal component (handles overlay and form rendering)
- Create TrainingLeadForm component (training-specific fields)
- Create TripLeadForm component (trip-specific fields)
- Add form validation (client-side, required fields + email format)
- Integrate with apiClient.createLead() method
- Add success confirmation message in chat (inline message bubble)
- Add error handling for submission failures
- Mobile-responsive modal layout (full-screen on <768px)
- Add cancel/close functionality
- Add form reset on open

### Out of scope (explicit)

- Auto-trigger based on conversation intent (NLP)
- Bot suggestion metadata (suggestLeadCapture)
- Pre-filling form from conversation context
- CAPTCHA / reCAPTCHA integration
- Advanced date picker component (use text input)
- Multi-step form wizard
- Lead submission history UI
- Real-time email delivery status
- Lead analytics/tracking dashboard

### Key changes by layer

#### Frontend

New files:

1. src/components/chat/LeadCaptureModal.tsx
   - Props: isOpen, onClose, leadType, onSubmit
   - Renders overlay (semi-transparent backdrop)
   - Renders modal container (centered or full-screen)
   - Conditionally renders TrainingLeadForm or TripLeadForm based on leadType
   - Handles ESC key to close
   - Handles backdrop click to close
   - Mobile-responsive styles

2. src/components/chat/TrainingLeadForm.tsx
   - Props: onSubmit, onCancel, isSubmitting, error
   - Fields: name (text, required), email (email, required), phone (tel, optional), agency (select: PADI/SSI/No Preference), certification level (select: None/OW/AOW/Rescue/Divemaster), location (text, optional), message (textarea, optional)
   - Client-side validation (required fields, email format)
   - Submit button with loading state
   - Cancel button
   - Error message display

3. src/components/chat/TripLeadForm.tsx
   - Props: same as TrainingLeadForm
   - Fields: name (text, required), email (email, required), phone (tel, optional), destination (text, required), dates (text, e.g., "June 2026" or "Flexible"), certification level (select), dive count (number), interests (checkboxes: Wrecks, Reefs, Marine Life, Macro, Drift, Night Dives), message (textarea, optional)
   - Same validation, submit, cancel patterns

Updated files:

1. src/app/chat/page.tsx
   - Add state: showLeadForm, leadType, leadSubmitting, leadError
   - Add handler: handleOpenLeadForm(type: 'training' | 'trip')
   - Add handler: handleCloseLeadForm()
   - Add handler: handleLeadSubmit(data: LeadFormData)
   - Add "Get Certified" button (header or fixed position)
   - Add "Plan a Trip" button (header or fixed position)
   - Add LeadCaptureModal component to render tree
   - Add inline success message to messages array after successful lead submission
   - Add error handling for ApiClientError in handleLeadSubmit

Button placement options (choose one):

- Option A: Fixed buttons below chat input (always visible)
- Option B: Floating action buttons (bottom-right corner, stacked)
- Option C: Header buttons (next to "DovvyBuddy Chat" title)
- Recommendation: Option C (header buttons) for desktop, Option B (floating) for mobile

#### Backend

No changes - /api/leads endpoint already implemented in PR4.

#### Data

No schema changes - leads table exists.

Expected DB writes:

- INSERT INTO leads (session_id, type, diver_profile, created_at)
- Type is inferred from lead content (training vs trip) or added as explicit column (PR4 implementation detail)

#### Infra/config

No environment variables needed (RESEND_API_KEY, LEAD_EMAIL_TO already configured in PR4).

#### Observability

Console logging (dev mode):

- "Opening lead form: {type}"
- "Lead submitted successfully: {leadId}"
- "Lead submission error: {error.message}"

Future (PR6):

- Track lead form open rate (analytics event)
- Track lead submission success/failure rate (analytics event)

---

### Edge cases to handle

1. **Form opened, user clicks backdrop:**
   - Close modal (same as Cancel button)
   - No data loss (form was not submitted)
   - User can reopen and fill again

2. **Form submission fails (network error):**
   - Keep modal open
   - Display error message: "Failed to submit. Please try again."
   - Keep form data intact (user doesn't have to re-type)
   - Retry button or user can click Submit again

3. **Form submission fails (validation error from backend):**
   - Display specific error: "Invalid email address" or "Email is required"
   - Highlight invalid field (if possible)
   - Keep form open for correction

4. **User submits multiple leads in same session:**
   - Allow (no restriction in V1)
   - Each submission creates new lead in DB
   - Backend rate limiting prevents spam (10 per session from PR4)

5. **Session expired while form is open:**
   - Form submission may fail (session no longer valid)
   - Error handler detects SESSION_EXPIRED
   - Close form, clear session (same as PR5.1 behavior)
   - User must start new chat before submitting lead

6. **User closes form, reopens with different type:**
   - Form resets (no data retention across opens)
   - Shows correct form based on new leadType

7. **Email field contains invalid format:**
   - Client-side validation catches on submit
   - Show error: "Please enter a valid email address"
   - Don't call API until valid

8. **Required field left empty:**
   - Client-side validation catches on submit
   - Show error: "Name and email are required"
   - Highlight empty fields (red border or inline error)

9. **User presses ESC key while form is open:**
   - Close modal (same as Cancel button)

10. **Form opened on mobile with keyboard:**
    - Ensure form is scrollable
    - Ensure submit button remains accessible (not hidden by keyboard)
    - Use position: sticky for submit button on mobile

---

### Migration/compatibility notes (if applicable)

No migration needed - new feature, no existing data.

Backwards compatibility:

- Users who already chatted (before this PR) can now submit leads
- No breaking changes to chat functionality

---

## 5) Testing & verification

### Automated tests to add/update

#### Unit

Files to create:

1. src/components/chat/**tests**/LeadCaptureModal.test.tsx
   - Test modal renders when isOpen=true
   - Test modal hidden when isOpen=false
   - Test onClose called when backdrop clicked
   - Test onClose called when ESC pressed
   - Test renders TrainingLeadForm when leadType='training'
   - Test renders TripLeadForm when leadType='trip'

2. src/components/chat/**tests**/TrainingLeadForm.test.tsx
   - Test all fields render correctly
   - Test required field validation (empty name, email)
   - Test email format validation (invalid email)
   - Test onSubmit called with correct data when valid
   - Test onCancel called when Cancel clicked
   - Test submit button disabled during isSubmitting
   - Test error message displayed when error prop provided

3. src/components/chat/**tests**/TripLeadForm.test.tsx
   - Same tests as TrainingLeadForm
   - Additional: Test checkboxes for interests
   - Additional: Test dive count number input

4. src/app/chat/**tests**/page.test.tsx (update existing or create)
   - Test "Get Certified" button opens training form
   - Test "Plan a Trip" button opens trip form
   - Test form closes on cancel
   - Test successful lead submission adds confirmation message to chat
   - Test failed lead submission displays error in form
   - Test form resets when reopened

#### Integration

File: tests/integration/lead-capture.test.ts (new)

Tests:

1. Test training lead submission end-to-end
   - Open training form
   - Fill all fields
   - Submit
   - Verify API called with correct payload
   - Verify success confirmation in chat
   - Verify lead in database (SELECT FROM leads WHERE email='test@example.com')

2. Test trip lead submission end-to-end
   - Same flow as training test
   - Verify interests array correctly formatted

3. Test validation error handling
   - Submit form with invalid email
   - Verify API returns 400 VALIDATION_ERROR
   - Verify error message displayed in form

4. Test rate limiting
   - Submit 11 leads in rapid succession
   - Verify 11th submission returns 429 RATE_LIMIT_EXCEEDED
   - Verify error message displayed

#### E2E (only if needed)

Deferred to PR6 (Playwright).

Manual testing covers E2E scenarios for now.

---

### Manual verification checklist

Pre-requisites:

- Backend running: cd src/backend && uvicorn app.main:app --reload
- Frontend running: pnpm dev
- Open http://localhost:3000/chat

Test cases:

1. **Training lead - happy path:**
   - [ ] Navigate to /chat
   - [ ] Send test message to create session
   - [ ] Click "Get Certified" button
   - [ ] Verify training form modal appears
   - [ ] Fill fields: Name="John Doe", Email="john@example.com", Agency="PADI", Level="Open Water"
   - [ ] Click Submit
   - [ ] Verify loading spinner on button
   - [ ] Verify modal closes on success
   - [ ] Verify chat displays: "✅ Thanks, John Doe! We'll contact you at john@example.com soon."
   - [ ] Check DB: SELECT \* FROM leads WHERE email='john@example.com';
   - [ ] Verify lead record exists with correct data
   - [ ] Check email inbox (LEAD_EMAIL_TO) for notification email

2. **Trip lead - happy path:**
   - [ ] Click "Plan a Trip" button
   - [ ] Verify trip form modal appears
   - [ ] Fill fields: Name="Jane Smith", Email="jane@example.com", Destination="Tioman", Dates="June 2026", Certification="AOW", Dive Count=25, Interests=[Wrecks, Reefs]
   - [ ] Click Submit
   - [ ] Verify success confirmation in chat
   - [ ] Verify lead in DB

3. **Validation - empty required fields:**
   - [ ] Open training form
   - [ ] Leave Name and Email empty
   - [ ] Click Submit
   - [ ] Verify error message: "Name and email are required"
   - [ ] Verify form stays open
   - [ ] Verify API not called (check network tab)

4. **Validation - invalid email:**
   - [ ] Open training form
   - [ ] Fill Name="Test", Email="not-an-email"
   - [ ] Click Submit
   - [ ] Verify error message: "Please enter a valid email address"
   - [ ] Verify form stays open
   - [ ] Fix email to "test@example.com", submit
   - [ ] Verify success

5. **Cancel form:**
   - [ ] Open training form
   - [ ] Fill some fields
   - [ ] Click Cancel button
   - [ ] Verify modal closes
   - [ ] Verify no lead created in DB
   - [ ] Reopen form
   - [ ] Verify form is reset (previous data cleared)

6. **Close via backdrop click:**
   - [ ] Open form
   - [ ] Click outside modal (on dark overlay)
   - [ ] Verify modal closes

7. **Close via ESC key:**
   - [ ] Open form
   - [ ] Press ESC key
   - [ ] Verify modal closes

8. **Submission error handling:**
   - [ ] Stop backend (Ctrl+C in backend terminal)
   - [ ] Open form, fill fields, submit
   - [ ] Verify error message: "Failed to submit. Please try again."
   - [ ] Verify form stays open with data intact
   - [ ] Restart backend
   - [ ] Click Submit again (don't re-fill)
   - [ ] Verify success

9. **Multiple submissions:**
   - [ ] Submit training lead
   - [ ] Verify success
   - [ ] Immediately submit trip lead (same session)
   - [ ] Verify success
   - [ ] Check DB: SELECT \* FROM leads WHERE session_id='your-session-id';
   - [ ] Verify 2 lead records exist

10. **Rate limiting (if backend implements it):**
    - [ ] Submit 11 leads rapidly (can automate with script)
    - [ ] Verify 11th submission fails with rate limit error
    - [ ] Verify error message displayed

11. **Mobile responsive - training form:**
    - [ ] Open Chrome DevTools, switch to iPhone 12 (390x844)
    - [ ] Open training form
    - [ ] Verify modal is full-screen (not centered)
    - [ ] Verify all fields are visible and tappable
    - [ ] Verify submit button is accessible (not hidden by virtual keyboard)
    - [ ] Fill and submit form
    - [ ] Verify success

12. **Mobile responsive - trip form:**
    - [ ] Same as test 11, but with trip form
    - [ ] Verify checkboxes are tappable (not too small)
    - [ ] Verify form is scrollable if content exceeds viewport

13. **Continue chatting after lead submission:**
    - [ ] Submit lead successfully
    - [ ] Verify confirmation message appears in chat
    - [ ] Send new chat message: "Tell me more about Tioman"
    - [ ] Verify bot responds normally
    - [ ] Verify session continues (same sessionId)

14. **Form reset on reopen:**
    - [ ] Open training form
    - [ ] Fill all fields but don't submit
    - [ ] Close form (Cancel)
    - [ ] Reopen training form
    - [ ] Verify all fields are empty (not pre-filled)

15. **Console logging:**
    - [ ] Open console
    - [ ] Click "Get Certified"
    - [ ] Verify log: "Opening lead form: training"
    - [ ] Submit form
    - [ ] Verify log: "Lead submitted successfully: {leadId}"

---

### Commands to run

Install (if new dependencies added):
pnpm install

Note: May add email validation library (e.g., validator or zod) - update package.json if needed.

Dev:
Terminal 1: cd src/backend && uvicorn app.main:app --reload
Terminal 2: pnpm dev

Test:
pnpm test

Test integration:
pnpm test:integration

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

- "Get Certified" and "Plan a Trip" buttons removed
- Users cannot submit leads from chat (back to PR5 behavior)
- Existing leads in DB are preserved
- Backend /api/leads endpoint still works (can be called directly if needed)

### Feature flag (optional)

Could add feature flag if cautious:

- Environment variable: NEXT_PUBLIC_FEATURE_LEAD_CAPTURE_ENABLED=true
- Hide buttons if false
- Allows gradual rollout or quick disable without code change

### Data considerations

No database migration needed - rollback only affects frontend.

Leads submitted during this PR:

- Remain in DB (no cleanup needed)
- Can still be processed by partner shops (email notifications already sent)

---

## 7) Follow-ups (optional)

1. **Auto-trigger based on conversation intent (V2):**
   - Add NLP intent detection (e.g., "I want to get certified" → suggest training form)
   - Backend returns metadata: { suggestLeadCapture: true, type: 'training' }
   - Frontend shows inline CTA: "Ready to get started? [Get Certified]"

2. **Pre-fill form from conversation (V2):**
   - Backend extracts name, location, preferences from conversation history
   - Returns pre-fill data in metadata
   - Frontend populates form fields (user can edit before submitting)

3. **CAPTCHA integration (PR6 or V1.1):**
   - Add Google reCAPTCHA v3 to forms
   - Prevents spam/bot submissions
   - Required for public launch

4. **Advanced date picker (V2):**
   - Replace text input with calendar component (e.g., react-datepicker)
   - Allow date range selection for trip dates
   - Improves UX for trip planning

5. **Lead submission analytics (PR6):**
   - Track form open rate (impressions)
   - Track completion rate (submissions / opens)
   - Track field-level drop-off (which fields cause abandonment)
   - Use Vercel Analytics or PostHog

6. **Email confirmation to user (V1.1):**
   - Send confirmation email to user after lead submission
   - "We received your request. A dive shop will contact you within 24 hours."
   - Requires Resend template setup

7. **Multi-step form wizard (V2):**
   - Break trip form into 3 steps: Contact Info → Trip Details → Preferences
   - Reduces cognitive load, improves completion rate
   - Adds complexity (state management, progress indicator)

8. **Lead status tracking (V2):**
   - Allow user to check lead status (Pending, Contacted, Booked)
   - Requires auth + user profiles (PR8)
   - Backend API: GET /api/leads/:id/status

---

**End of PR5.2 Plan**

---

## Implementation Verification (Completed January 29, 2026)

### ✅ Implemented Features

1. **Lead Capture Modal (src/components/chat/LeadCaptureModal.tsx)**
   - ✅ Overlay with backdrop (semi-transparent)
   - ✅ ESC key to close
   - ✅ Backdrop click to close
   - ✅ Conditionally renders TrainingLeadForm or TripLeadForm
   - ✅ Mobile-responsive (full-screen on <768px)

2. **Training Lead Form (src/components/chat/TrainingLeadForm.tsx)**
   - ✅ All required fields (name, email)
   - ✅ Optional fields (phone, agency, certification level, location, message)
   - ✅ Client-side validation
   - ✅ Email format validation
   - ✅ Submit with loading state
   - ✅ Cancel button
   - ✅ Error message display

3. **Trip Lead Form (src/components/chat/TripLeadForm.tsx)**
   - ✅ All required fields (name, email, destination)
   - ✅ Optional fields (phone, dates, certification, dive count, message)
   - ✅ Interests checkboxes (wrecks, reefs, marine life, etc.)
   - ✅ Client-side validation
   - ✅ Same patterns as TrainingLeadForm

4. **Chat Page Integration (src/app/chat/page.tsx)**
   - ✅ State management (showLeadForm, leadType, leadSubmitting, leadError)
   - ✅ "Get Certified" button (line 416)
   - ✅ "Plan a Trip" button (line 434)
   - ✅ handleOpenLeadForm function (lines 194-201)
   - ✅ handleCloseLeadForm function (lines 203-208)
   - ✅ handleLeadSubmit function (lines 221-292)
   - ✅ Success confirmation message in chat (lines 282-288)
   - ✅ Error handling with ApiClientError

5. **Backend Integration**
   - ✅ POST /api/leads endpoint exists (src/backend/app/api/routes/lead.py)
   - ✅ Lead capture and email delivery working
   - ✅ Payload format matches (training/trip types)
   - ✅ Session ID included in lead payload

6. **Test Coverage**
   - ✅ LeadCaptureModal tests (src/components/chat/**tests**/LeadCaptureModal.test.tsx)
   - ✅ TrainingLeadForm tests (src/components/chat/**tests**/TrainingLeadForm.test.tsx)
   - ✅ TripLeadForm tests (src/components/chat/**tests**/TripLeadForm.test.tsx)
   - ✅ Component unit tests passing

### 🎯 Acceptance Criteria Status

| #   | Criteria                                             | Status      |
| --- | ---------------------------------------------------- | ----------- |
| 1   | "Request Training" and "Plan a Trip" buttons visible | ✅ Verified |
| 2   | Clicking button opens inline modal                   | ✅ Verified |
| 3   | Training form has all required fields                | ✅ Verified |
| 4   | Trip form has all required fields                    | ✅ Verified |
| 5   | Client-side validation before submission             | ✅ Verified |
| 6   | Email format validation                              | ✅ Verified |
| 7   | Form calls apiClient.createLead()                    | ✅ Verified |
| 8   | Success shows confirmation in chat                   | ✅ Verified |
| 9   | Error displays in form without closing               | ✅ Verified |
| 10  | User can cancel/close form                           | ✅ Verified |
| 11  | Mobile-responsive modal                              | ✅ Verified |
| 12  | Session ID included in payload                       | ✅ Verified |
| 13  | User can continue chatting after submission          | ✅ Verified |
| 14  | Form resets when reopened                            | ✅ Verified |
| 15  | Success confirmation includes leadId                 | ✅ Verified |

### 📝 Manual Testing Results

**Tested by user on January 29, 2026:**

- Training lead submission verified
- Trip lead submission verified
- Form validation tested (empty fields, invalid email)
- Cancel/close functionality verified
- Mobile responsive design confirmed
- Error handling tested
- Multiple submissions in same session verified

### 🔧 Technical Implementation Notes

**Key Files Created:**

- `src/components/chat/LeadCaptureModal.tsx` (155 lines)
- `src/components/chat/TrainingLeadForm.tsx`
- `src/components/chat/TripLeadForm.tsx`
- `src/components/chat/__tests__/LeadCaptureModal.test.tsx`
- `src/components/chat/__tests__/TrainingLeadForm.test.tsx`
- `src/components/chat/__tests__/TripLeadForm.test.tsx`

**Key Files Modified:**

- `src/app/chat/page.tsx` - Lead form state and handlers

**API Integration:**

- Training leads: POST /api/leads with type='training'
- Trip leads: POST /api/leads with type='trip'
- Response includes leadId for tracking
- Email notifications sent via Resend

**Edge Cases Handled:**

- ✅ Form opened, user clicks backdrop
- ✅ Network error during submission
- ✅ Backend validation error
- ✅ Multiple submissions in same session
- ✅ Session expired while form open
- ✅ Form type switching
- ✅ ESC key to close
- ✅ Mobile keyboard handling

---
