# PR4: Lead Capture & Delivery - Feature Plan

**Branch Name:** `feature/pr4-lead-capture`  
**Status:** Planned  
**Date:** December 28, 2025

---

## 1. Feature/Epic Summary

### Objective

Implement the lead capture and delivery system that converts qualified user inquiries into actionable business leads. This is the core monetization touchpoint—enabling the bot to collect structured lead data (for training or trip requests) and deliver it to partner dive shops via email, creating the business value conversion point for DovvyBuddy.

### User Impact

- Users can submit structured inquiries for dive training or trip planning directly through conversations
- Partner shops receive context-rich leads with complete diver profile information
- System captures and persists all leads for tracking, follow-up, and analytics
- Seamless conversion flow maintains user experience while generating business value

### Dependencies

**Requires:**

- PR1 (Database Schema) — `leads` table must be defined and migrated

**Soft dependencies:**

- PR3 (Model Provider & Session) — Session context provides diver profile data to enrich leads (optional enrichment)

**Enables:**

- PR5 (Chat Interface) — Frontend lead capture form will call these APIs

**External:**

- Resend API account and credentials for email delivery

### Assumptions

- **Assumption:** Email delivery is the primary channel for V1; webhook is optional/secondary
- **Assumption:** Lead validation is server-side only; no complex frontend validation in this PR
- **Assumption:** Lead delivery is synchronous (fire-and-forget acceptable for V1); async queue deferred to V2
- **Assumption:** No partner shop management UI; leads go to a single configured email address
- **Assumption:** Lead persistence takes priority over delivery—leads must be saved even if email fails
- **Assumption:** Session context (diver profile) is optional enrichment, not required for lead capture

---

## 2. Complexity & Fit

### Classification: `Single-PR`

### Rationale

- **Single user flow:** Capture lead → validate → persist → deliver
- **Limited layers affected:** Backend API + data layer only (no frontend in this PR per MASTER_PLAN scope)
- **No schema changes needed:** `leads` table already defined in PR1
- **One external integration:** Resend API (well-documented, straightforward)
- **Low risk to existing functionality:** Additive feature, no changes to existing endpoints
- **Can be tested end-to-end:** Testable with curl/Postman before frontend integration in PR5
- **Self-contained business logic:** Lead validation, persistence, and delivery are cohesive and should be deployed together

---

## 3. Full-Stack Impact

### Frontend

**No changes planned.**  
Frontend integration happens in PR5 (LeadCaptureForm component will call `/api/lead`). This PR is API-only.

### Backend

**Significant changes:**

**New modules to create:**

- `src/lib/lead/types.ts` — TypeScript interfaces for lead payloads
- `src/lib/lead/validation.ts` — Zod schemas for lead validation
- `src/lib/lead/service.ts` — Business logic: `captureLead()`, `deliverLead()`, `captureAndDeliverLead()`
- `src/lib/lead/email-template.ts` — HTML/text email builders
- `src/lib/lead/index.ts` — Barrel export

**New API endpoint:**

- `POST /api/lead` — Accept lead payload, validate, persist, deliver
  - Request: `{ type: "training" | "trip", data: TrainingLeadData | TripLeadData, sessionId?: string }`
  - Response: `{ success: true, leadId: string }` (201) or `{ error: string, details?: array }` (400/500)

**Validation concerns:**

- Required fields by lead type (training vs trip)
- Email format validation (RFC 5322 compliant)
- Phone format validation (optional field, flexible format for international numbers)
- Message field max length (2000 chars to prevent abuse)
- Sanitization of user-provided text fields (XSS prevention)

**Error Handling:**

- 400 for validation errors with field-level details
- 500 for database failures (log full error, return user-friendly message)
- 500 for delivery failures BUT lead still persisted (log error, don't fail request)
- Structured JSON error responses: `{ error: string, code: string, details?: array }`

**Authentication/Authorization:**

- None (guest sessions only per MASTER_PLAN)
- Rate limiting deferred to future PR (note as risk mitigation)

### Data

**Tables used:**

- `leads` — INSERT operations only (schema defined in PR1)
  - `id` (UUID, primary key)
  - `type` (training | trip)
  - `diver_profile` (JSONB, from session context if available)
  - `request_details` (JSONB, validated lead data)
  - `created_at` (timestamp)

**No migrations needed** — Schema already exists from PR1

**Data operations (via Drizzle ORM):**

- `db.insert(leads).values({ ... }).returning()` — Create lead record

**Data structure (JSONB fields):**

request_details for training lead:

```
{
  name: string,
  email: string,
  phone?: string,
  agency?: "PADI" | "SSI" | "Other",
  level?: string (e.g., "Open Water", "Advanced"),
  location?: string (preferred training location),
  message?: string
}
```

request_details for trip lead:

```
{
  name: string,
  email: string,
  phone?: string,
  destination?: string,
  dates?: string (free text for flexibility),
  certification_level?: string,
  dive_count?: number,
  interests?: string (e.g., "wrecks, night diving"),
  message?: string
}
```

diver_profile (from session, optional):

```
{
  certification_level?: string,
  dive_count?: number,
  interests?: string[],
  fears?: string[]
}
```

### Infra / Config

**Environment variables to add:**

- `RESEND_API_KEY` — Required, API key from Resend dashboard
- `LEAD_EMAIL_TO` — Required, destination email for lead notifications
- `LEAD_WEBHOOK_URL` — Optional, for future webhook integration
- `LEAD_EMAIL_FROM` — Optional, defaults to "leads@dovvybuddy.com" (requires Resend domain verification)

**Update `.env.example`** with new variables and usage notes

**Dependencies to install:**

- `resend` — Resend SDK for email delivery
- `zod` — Schema validation (may already be installed in PR3)

**CI/CD:**

- No changes; existing pipeline covers new code

---

## 4. PR Roadmap (Single-PR Plan)

### PR4: Lead Capture & Delivery

**Goal**  
Enable the system to capture qualified user leads (training or trip inquiries) and deliver them to partner dive shops via email, creating the core business value conversion point that transforms user inquiries into actionable revenue opportunities.

---

#### Scope

**In scope:**

- Lead type definitions (Training Lead, Trip Lead) with TypeScript interfaces
- Zod validation schemas for both lead types with field-level error messages
- Lead service functions: `captureLead()`, `deliverLead()`, `captureAndDeliverLead()`
- Email template builder (HTML + plain text) with professional formatting
- `POST /api/lead` endpoint with validation and error handling
- Resend API integration for email delivery
- Unit tests for validation schemas and service functions
- Integration tests for `/api/lead` endpoint
- Environment variable configuration and documentation
- Error logging for delivery failures

**Out of scope:**

- Frontend lead capture form (deferred to PR5)
- Webhook delivery (optional enhancement for later)
- Partner shop management/routing (single destination for V1)
- Lead status tracking/updates (no status field in V1)
- Admin dashboard for lead viewing (future feature)
- Rate limiting on lead submissions (security enhancement for later)
- CAPTCHA or bot protection (future security enhancement)
- Lead deduplication logic (future optimization)
- SMS/WhatsApp delivery channels (future expansion)

---

#### Backend Changes

**Module: `src/lib/lead/types.ts`**

Define TypeScript interfaces and types:

- `LeadType` — Union type: `"training" | "trip"`
- `TrainingLeadData` — Interface for training inquiries
  - `name: string` (required)
  - `email: string` (required)
  - `phone?: string` (optional)
  - `agency?: "PADI" | "SSI" | "Other"` (optional)
  - `level?: string` (optional, e.g., "Open Water", "Advanced")
  - `location?: string` (optional, preferred training location)
  - `message?: string` (optional, additional notes)
- `TripLeadData` — Interface for trip inquiries
  - `name: string` (required)
  - `email: string` (required)
  - `phone?: string` (optional)
  - `destination?: string` (optional)
  - `dates?: string` (optional, free text for flexibility)
  - `certification_level?: string` (optional)
  - `dive_count?: number` (optional)
  - `interests?: string` (optional, comma-separated or free text)
  - `message?: string` (optional)
- `LeadPayload` — Combined request type
  - `type: LeadType`
  - `data: TrainingLeadData | TripLeadData`
  - `sessionId?: string` (optional, for session context enrichment)
- `LeadRecord` — Database record type
  - `id: string` (UUID)
  - `type: LeadType`
  - `diver_profile: DiverProfile | null` (JSONB)
  - `request_details: TrainingLeadData | TripLeadData` (JSONB)
  - `created_at: Date`
- `DiverProfile` — Session context type (from PR3)
  - `certification_level?: string`
  - `dive_count?: number`
  - `interests?: string[]`
  - `fears?: string[]`

**Module: `src/lib/lead/validation.ts`**

Zod schemas for request validation:

- `trainingLeadSchema` — Zod schema for training leads
  - `name: z.string().min(1, "Name is required").max(100, "Name too long")`
  - `email: z.string().email("Invalid email format")`
  - `phone: z.string().optional()`
  - `agency: z.enum(["PADI", "SSI", "Other"]).optional()`
  - `level: z.string().max(50).optional()`
  - `location: z.string().max(200).optional()`
  - `message: z.string().max(2000, "Message too long").optional()`

- `tripLeadSchema` — Zod schema for trip leads
  - `name: z.string().min(1, "Name is required").max(100, "Name too long")`
  - `email: z.string().email("Invalid email format")`
  - `phone: z.string().optional()`
  - `destination: z.string().max(100).optional()`
  - `dates: z.string().max(100).optional()`
  - `certification_level: z.string().max(50).optional()`
  - `dive_count: z.number().int().min(0, "Dive count must be non-negative").optional()`
  - `interests: z.string().max(500).optional()`
  - `message: z.string().max(2000, "Message too long").optional()`

- `leadPayloadSchema` — Discriminated union based on `type` field
  - Validates `type` field first
  - Routes to appropriate schema based on type
  - Returns field-level error messages for validation failures

- Helper function: `validateLeadPayload(payload: unknown): LeadPayload`
  - Parses and validates using `leadPayloadSchema`
  - Throws validation error with structured field details
  - Sanitizes string fields (trim whitespace, prevent XSS)

**Module: `src/lib/lead/service.ts`**

Business logic functions:

- `captureLead(payload: LeadPayload, diverProfile?: DiverProfile): Promise<LeadRecord>`
  - Generate UUID for lead ID
  - Extract diver profile from session context (if sessionId provided)
  - Validate payload using `validateLeadPayload()`
  - Insert into `leads` table via Drizzle ORM
  - Return created lead record
  - Error handling: Database errors throw with context

- `deliverLead(lead: LeadRecord): Promise<void>`
  - Build email content using template functions
  - Send via Resend API
  - Log success with lead ID and timestamp
  - Log failure but DON'T throw (lead already persisted)
  - Include lead ID in email subject for tracking
  - Set reply-to as lead's email for easy response

- `captureAndDeliverLead(payload: LeadPayload, sessionId?: string): Promise<LeadRecord>`
  - Orchestration function that coordinates capture + delivery
  - Retrieve session context if sessionId provided (optional)
  - Call `captureLead()` first (ensures persistence)
  - Call `deliverLead()` second (fire-and-forget)
  - Return lead record even if delivery fails
  - Log full flow with lead ID

**Module: `src/lib/lead/email-template.ts`**

Email formatting functions:

- `buildLeadEmailHtml(lead: LeadRecord): string`
  - Returns formatted HTML email with:
    - Lead type badge (Training / Trip) with color coding
    - Contact information section (name, email, phone)
    - Request details section (formatted key-value pairs)
    - Diver profile summary (if available from session)
    - Timestamp (formatted for readability)
    - Footer with DovvyBuddy branding and disclaimer
  - Escape HTML in user input to prevent XSS
  - Responsive design (mobile-friendly)

- `buildLeadEmailText(lead: LeadRecord): string`
  - Plain text version for email clients without HTML
  - Same structure as HTML but text-formatted
  - Fallback for accessibility

- `buildLeadEmailSubject(lead: LeadRecord): string`
  - Format: `[DovvyBuddy] New ${lead.type} Lead: ${lead.request_details.name} [${lead.id.slice(0, 8)}]`
  - Includes lead ID prefix for tracking

**Module: `src/lib/lead/index.ts`**

Barrel export for clean imports:

- Export all types, validation functions, service functions
- Default export: `captureAndDeliverLead` (main entry point)

**API Endpoint: `src/app/api/lead/route.ts`**

POST handler:

- Parse JSON body
- Validate Content-Type header (must be application/json)
- Extract sessionId from request (cookie or body)
- Validate payload using Zod schema
- If validation fails: return 400 with `{ error: "Validation failed", details: [...] }`
- Call `captureAndDeliverLead(payload, sessionId)`
- On success: return 201 with `{ success: true, leadId: string }`
- On database error: return 500 with `{ error: "Failed to capture lead", code: "DB_ERROR" }`
- On unexpected error: return 500 with `{ error: "Internal server error", code: "UNKNOWN" }`
- Log all requests with outcome (success/failure) and lead ID

Error response format:

```
{
  error: string (user-friendly message),
  code: string (error code for debugging),
  details?: Array<{ field: string, message: string }> (for validation errors)
}
```

---

#### Frontend Changes

**No frontend changes in this PR.**  
All work is backend API. UI integration (LeadCaptureForm component) happens in PR5.

---

#### Data Changes

**No migrations needed.**  
Assumes PR1 has already created `leads` table with required schema:

- `id` (UUID, primary key)
- `type` (text, enum constraint or check)
- `diver_profile` (JSONB, nullable)
- `request_details` (JSONB, not null)
- `created_at` (timestamp with timezone, default NOW())

**ORM:** Drizzle ORM (per MASTER_PLAN and copilot-project.md)

**Data operations:**

- INSERT only (no UPDATE or DELETE in V1)
- Use Drizzle's typed schema from `src/db/schema/leads.ts` (defined in PR1)
- Example: `db.insert(leads).values({ ... }).returning()`

**Indexes (verify in PR1):**

- Primary key on `id`
- Index on `created_at` for chronological queries (optional but recommended)
- Index on `type` for filtering by lead type (optional)

**Backward compatibility:**

- All changes are additive (new API endpoint, no schema changes)
- Existing database state unaffected
- Can be deployed without coordinating with frontend (API-first)

---

#### Infra / Config

**Environment variables to add to `.env.example`:**

```
# Lead Capture & Delivery Configuration
RESEND_API_KEY=re_xxxxxxxxxxxx          # Required: API key from Resend dashboard
LEAD_EMAIL_TO=leads@diveshop.com        # Required: Destination email for lead notifications
LEAD_EMAIL_FROM=leads@dovvybuddy.com    # Optional: Sender email (requires domain verification)
LEAD_WEBHOOK_URL=                       # Optional: Webhook endpoint for CRM integration (future)
```

**Update `.env.example` with:**

- Comments explaining each variable
- Example values (sanitized)
- Links to Resend documentation
- Note about domain verification for custom FROM address

**Dependencies to add (package.json):**

- `resend` — Resend SDK for email delivery (latest stable)
- `zod` — Schema validation (if not already installed in PR3)
- `uuid` — UUID generation (if not already installed in PR3)

**Resend setup requirements:**

- Account created at resend.com
- API key generated
- (Optional but recommended) Domain verified for custom FROM address
- Test email sent to verify setup

**CI/CD:**

- No changes; existing `pnpm typecheck && pnpm lint && pnpm test && pnpm build` covers new code
- Ensure RESEND_API_KEY is NOT in environment (tests should mock)

---

#### Testing

**Unit Tests:**

1. **Validation tests** (`src/lib/lead/__tests__/validation.test.ts`)
   - Valid training lead passes validation
   - Valid trip lead passes validation
   - Missing required `name` fails with correct error message
   - Missing required `email` fails with correct error message
   - Invalid email format fails (test: "notanemail", "test@", "@example.com")
   - `message` over 2000 chars fails
   - Unknown lead type fails
   - Extra fields are stripped (security)
   - Phone field accepts various formats (optional field flexibility)
   - `dive_count` must be non-negative integer
   - Whitespace trimming works correctly

2. **Service tests** (`src/lib/lead/__tests__/service.test.ts`)
   - Mock Drizzle ORM database operations
   - `captureLead()` generates valid UUID
   - `captureLead()` persists to database correctly
   - `captureLead()` includes diver profile when provided
   - `captureLead()` works without diver profile (optional)
   - `captureLead()` throws on database error
   - `deliverLead()` calls Resend API with correct payload
   - `deliverLead()` logs error but doesn't throw on email failure
   - `captureAndDeliverLead()` returns lead even if delivery fails
   - `captureAndDeliverLead()` enriches lead with session context

3. **Email template tests** (`src/lib/lead/__tests__/email-template.test.ts`)
   - `buildLeadEmailHtml()` includes all required sections
   - `buildLeadEmailHtml()` escapes HTML in user input (XSS prevention)
   - `buildLeadEmailHtml()` handles missing optional fields gracefully
   - `buildLeadEmailText()` formats correctly as plain text
   - `buildLeadEmailSubject()` includes lead type and ID
   - Templates render correctly for training leads
   - Templates render correctly for trip leads
   - Templates include diver profile when available

**Integration Tests:**

1. **API endpoint tests** (`src/app/api/lead/__tests__/route.test.ts`)
   - Mock database and Resend API
   - POST `/api/lead` with valid training lead returns 201
   - POST `/api/lead` with valid trip lead returns 201
   - Response includes valid UUID `leadId`
   - POST `/api/lead` with missing `name` returns 400 with field error
   - POST `/api/lead` with missing `email` returns 400 with field error
   - POST `/api/lead` with invalid email format returns 400
   - POST `/api/lead` with unknown type returns 400
   - POST `/api/lead` with message over 2000 chars returns 400
   - POST `/api/lead` with database failure returns 500
   - POST `/api/lead` persists lead even if email delivery fails
   - POST `/api/lead` with sessionId enriches lead with diver profile
   - POST `/api/lead` without sessionId works (optional enrichment)
   - Malformed JSON returns 400

**Manual Testing:**

1. **Curl tests for training lead:**
   - Start dev server: `pnpm dev`
   - Test minimal training lead:
     ```
     curl -X POST http://localhost:3000/api/lead \
       -H "Content-Type: application/json" \
       -d '{"type":"training","data":{"name":"John Doe","email":"john@example.com"}}'
     ```
   - Expected: 201 response with `{ success: true, leadId: "..." }`
   - Test full training lead:
     ```
     curl -X POST http://localhost:3000/api/lead \
       -H "Content-Type: application/json" \
       -d '{"type":"training","data":{"name":"John Doe","email":"john@example.com","phone":"+1-555-0100","agency":"PADI","level":"Open Water","location":"San Diego","message":"Looking to get certified in March"}}'
     ```

2. **Curl tests for trip lead:**
   - Test full trip lead:
     ```
     curl -X POST http://localhost:3000/api/lead \
       -H "Content-Type: application/json" \
       -d '{"type":"trip","data":{"name":"Jane Doe","email":"jane@example.com","destination":"Bali","dates":"March 2026","certification_level":"Advanced Open Water","dive_count":50,"interests":"wrecks, manta rays","message":"Interested in USAT Liberty wreck"}}'
     ```

3. **Database verification:**
   - Connect to database
   - Query: `SELECT * FROM leads ORDER BY created_at DESC LIMIT 5;`
   - Verify lead record created with correct structure
   - Verify `request_details` JSONB contains all submitted fields
   - Verify `created_at` timestamp is recent

4. **Email verification:**
   - Check email inbox at `LEAD_EMAIL_TO` address
   - Verify email received with correct subject line
   - Verify HTML formatting displays correctly
   - Verify all lead details included
   - Test reply-to address (should be lead's email)
   - Check Resend dashboard for delivery logs

5. **Error handling tests:**
   - Test validation error:
     ```
     curl -X POST http://localhost:3000/api/lead \
       -H "Content-Type: application/json" \
       -d '{"type":"training","data":{"name":"No Email"}}'
     ```
   - Expected: 400 with `{ error: "Validation failed", details: [...] }`
   - Test invalid email:
     ```
     curl -X POST http://localhost:3000/api/lead \
       -H "Content-Type: application/json" \
       -d '{"type":"training","data":{"name":"John","email":"notanemail"}}'
     ```
   - Expected: 400 with email validation error

---

#### Verification

**Commands to run:**

Based on `.github/copilot-project.md`:

- Install dependencies: `pnpm install`
- Run dev server: `pnpm dev`
- Run all tests: `pnpm test`
- Run specific test file: `pnpm test src/lib/lead/__tests__/validation.test.ts`
- Lint code: `pnpm lint`
- Type check: `pnpm typecheck`
- Build project: `pnpm build`

**Manual verification checklist:**

1. **Environment setup:**
   - [ ] Create Resend account at resend.com
   - [ ] Generate API key in Resend dashboard
   - [ ] Copy `.env.example` to `.env.local`
   - [ ] Set `RESEND_API_KEY` in `.env.local`
   - [ ] Set `LEAD_EMAIL_TO` to your test email
   - [ ] Verify database connection (from PR1 setup)

2. **Dependencies:**
   - [ ] Run `pnpm install`
   - [ ] Verify `resend` package installed
   - [ ] Verify `zod` package installed

3. **Unit tests:**
   - [ ] Run `pnpm test src/lib/lead/__tests__/validation.test.ts`
   - [ ] All validation tests pass
   - [ ] Run `pnpm test src/lib/lead/__tests__/service.test.ts`
   - [ ] All service tests pass
   - [ ] Run `pnpm test src/lib/lead/__tests__/email-template.test.ts`
   - [ ] All template tests pass

4. **Integration tests:**
   - [ ] Run `pnpm test src/app/api/lead/__tests__/route.test.ts`
   - [ ] All API endpoint tests pass

5. **Type checking:**
   - [ ] Run `pnpm typecheck`
   - [ ] No TypeScript errors in lead modules

6. **Linting:**
   - [ ] Run `pnpm lint`
   - [ ] No linting errors in lead modules

7. **Build:**
   - [ ] Run `pnpm build`
   - [ ] Build succeeds without errors
   - [ ] No tree-shaking warnings for lead modules

8. **Manual API testing (Training Lead):**
   - [ ] Start dev server: `pnpm dev`
   - [ ] Send minimal training lead via curl (see manual testing section)
   - [ ] Verify 201 response with valid UUID
   - [ ] Check database: lead record exists
   - [ ] Check email: notification received with correct details
   - [ ] Send full training lead via curl
   - [ ] Verify all optional fields included in email

9. **Manual API testing (Trip Lead):**
   - [ ] Send full trip lead via curl
   - [ ] Verify 201 response
   - [ ] Check database: lead record exists with trip type
   - [ ] Check email: trip-specific fields displayed correctly

10. **Error handling:**
    - [ ] Send lead with missing name (400 error)
    - [ ] Send lead with invalid email (400 error with field details)
    - [ ] Send lead with unknown type (400 error)
    - [ ] Send lead with message > 2000 chars (400 error)
    - [ ] Verify error responses have structured format

11. **Session enrichment (if PR3 complete):**
    - [ ] Create session via `/api/chat` (from PR3)
    - [ ] Send lead with sessionId in request
    - [ ] Verify `diver_profile` populated in database record
    - [ ] Verify diver profile section included in email

12. **CI verification:**
    - [ ] Push branch to GitHub
    - [ ] Verify CI pipeline passes (lint, typecheck, test, build)
    - [ ] No warnings or errors in CI logs

---

#### Rollback Plan

**Feature flag:** Not required

- This is an additive endpoint with no impact on existing functionality
- No changes to existing API routes or database schema
- Can be safely deployed and rolled back independently

**Revert strategy:**

- Simple git revert of the PR commit
- No data migration to undo (leads table structure unchanged)
- Leads already captured remain in database (no harm, can be manually reviewed)
- No frontend changes to coordinate (frontend integration in PR5)

**Quick disable (if needed):**
If email delivery becomes problematic:

1. Remove or unset `RESEND_API_KEY` environment variable
2. Leads will still persist to database
3. Email delivery will fail gracefully (logged but not thrown)
4. Manual export/delivery can be done as fallback using database query
5. Add webhook delivery in follow-up PR if email unreliable

**Monitoring:**

- Check application logs for delivery failures
- Monitor Resend dashboard for bounce/spam reports
- Query database for lead capture rate

---

#### Dependencies

**PR Dependencies:**

| PR                            | Status   | Requirement                    | Notes                                 |
| ----------------------------- | -------- | ------------------------------ | ------------------------------------- |
| PR1: Database Schema          | Required | `leads` table must exist       | Run migrations before testing         |
| PR3: Model Provider & Session | Soft     | Session context enriches leads | Can work without; enrichment optional |

**External Dependencies:**

| Service    | Requirement         | Setup Steps                                                                                                                             |
| ---------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Resend     | API key             | 1. Create account at resend.com<br>2. Generate API key<br>3. (Optional) Verify domain for custom FROM address<br>4. Test email delivery |
| PostgreSQL | Database connection | From PR1 setup; verify connection string in .env                                                                                        |

**NPM Dependencies:**

| Package  | Version | Purpose                              |
| -------- | ------- | ------------------------------------ |
| `resend` | Latest  | Email delivery API client            |
| `zod`    | Latest  | Schema validation (may be from PR3)  |
| `uuid`   | Latest  | Lead ID generation (may be from PR3) |

---

#### Risks & Mitigations

| Risk                                                                 | Likelihood | Impact | Mitigation                                                                                                                                                                                                                                                           |
| -------------------------------------------------------------------- | ---------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Email delivery failures** (rate limits, invalid key, API downtime) | Medium     | Medium | 1. Persist lead to DB first (success independent of delivery)<br>2. Log delivery errors with full context<br>3. Don't fail API response if delivery fails<br>4. Monitor Resend dashboard for delivery metrics<br>5. Add webhook fallback in future PR                |
| **Spam filtering** of lead emails                                    | Medium     | High   | 1. Use Resend with proper domain authentication (SPF/DKIM)<br>2. Test delivery to multiple email providers (Gmail, Outlook, etc.)<br>3. Avoid spam trigger words in templates<br>4. Use professional sender address<br>5. Include unsubscribe footer (best practice) |
| **Invalid/spam lead submissions**                                    | Medium     | Low    | 1. Basic validation (email format, length limits)<br>2. Rate limiting in follow-up PR<br>3. CAPTCHA in PR5 (frontend integration)<br>4. Monitor lead quality metrics<br>5. Add honeypot field in future                                                              |
| **Large message field** causing database/email issues                | Low        | Low    | 1. Cap message field at 2000 characters<br>2. Validate in Zod schema<br>3. Test with max-length messages                                                                                                                                                             |
| **Resend API outage**                                                | Low        | Medium | 1. Leads persisted to DB regardless<br>2. Can manually export and deliver<br>3. Add webhook delivery channel as backup<br>4. Monitor Resend status page                                                                                                              |
| **Email reply-to not working**                                       | Low        | Low    | 1. Test reply-to functionality manually<br>2. Include lead email in email body as fallback<br>3. Document for partner shops                                                                                                                                          |
| **XSS in email templates**                                           | Low        | High   | 1. Escape all user input in HTML email builder<br>2. Test with malicious input (script tags, etc.)<br>3. Use text-only email as fallback                                                                                                                             |

---

## 5. Milestones & Sequence

### Milestone: Lead Capture MVP

**User value unlocked:**  
The system can convert chat conversations into actionable business leads that partners receive via email. This completes the core business model loop: user inquiry → bot guidance → qualified lead → partner follow-up.

**PRs included:**

- PR4: Lead Capture & Delivery (this PR)

**What "done" means:**

- POST `/api/lead` endpoint accepts and validates training and trip lead payloads
- Valid leads are persisted to the database with all required data
- Lead notification emails are delivered to configured recipient address
- Email includes all lead details, contact info, and optional diver profile
- Validation errors return structured, user-friendly error messages
- All unit and integration tests pass
- Manual verification confirms end-to-end flow works (curl → DB → email)
- CI pipeline passes (lint, typecheck, test, build)
- Documentation updated (API docs, environment variables)

---

## 6. Risks, Trade-offs, and Open Questions

### Major Risks

**Technical Risks:**

| Risk                                                | Impact                                                  | Mitigation                                                                                                                                                      |
| --------------------------------------------------- | ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Email deliverability issues (bounces, spam filters) | Leads lost or delayed; partners don't receive inquiries | 1. Use reputable service (Resend) with auth<br>2. Test with multiple providers<br>3. Persist to DB first (can retry/export)<br>4. Add webhook as backup channel |
| Resend API rate limiting                            | Lead delivery fails during traffic spikes               | 1. Monitor usage vs limits<br>2. Add queue-based async delivery in V2<br>3. Implement exponential backoff retry                                                 |
| Database write failures                             | Lead capture fails; user data lost                      | 1. Proper error handling and logging<br>2. Return 500 with retry guidance<br>3. Monitor DB performance and connection pool                                      |

**Product Risks:**

| Risk                           | Impact                                    | Mitigation                                                                                                                                                |
| ------------------------------ | ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spam/bot submissions           | Partner receives junk leads; trust eroded | 1. Basic validation now<br>2. Rate limiting in follow-up PR<br>3. CAPTCHA in PR5<br>4. Monitor lead quality metrics                                       |
| Incomplete lead data           | Partner can't follow up effectively       | 1. Capture as much context as possible from session<br>2. Make email/name required<br>3. Encourage message field usage in UI (PR5)                        |
| Privacy concerns (storing PII) | User trust issues; compliance risks       | 1. Minimal data collection (no passwords, SSN, etc.)<br>2. Add privacy policy (future)<br>3. Consider GDPR compliance for V2<br>4. Secure database access |

### Trade-offs

| Decision                        | Trade-off                                                        | Rationale                                                                            |
| ------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **Email-first delivery**        | Simpler than webhook, but requires partner to monitor email      | Email is universally understood; webhook can be added later without breaking changes |
| **Synchronous delivery**        | Simpler than queue-based async, but adds latency to API response | V1 traffic is low; async complexity not justified yet; can add queue in V2 if needed |
| **Single recipient email**      | Simpler than partner routing, but limits multi-partner scenarios | V1 is single destination; routing logic can be added when expanding destinations     |
| **No lead status tracking**     | Simpler schema, but no visibility into lead lifecycle            | V1 focuses on capture; status tracking (contacted, converted) is V2 admin feature    |
| **Fire-and-forget email**       | No retry logic, but simpler implementation                       | Lead persisted to DB; manual retry possible; async retry can be added in V2          |
| **Optional session enrichment** | Lead works without session, but less context                     | Allows lead capture from external sources (future); session enrichment is bonus      |
| **2000 char message limit**     | May truncate long messages, but prevents abuse                   | Sufficient for V1 use cases; higher limit can be added if needed                     |

### Design Decisions

| Topic | Decision | Rationale |
|-------|----------|-----------|
| **Email delivery failure** | Silent fail with logging | Lead persistence > delivery confirmation; user sees success regardless; avoids duplicate submissions from retries |
| **Session context** | Optional enrichment | Reduces coupling with PR3; allows external lead sources (future); diver profile is bonus context |
| **LEAD_EMAIL_TO format** | Single email address | Sufficient for V1 single destination; partner routing deferred to multi-destination expansion |
| **Delivery status tracking** | No DB tracking; use Resend logs | Adds schema/webhook complexity; dashboard visibility sufficient for V1 |
| **Lead deduplication** | Same email + type within 5 minutes | Prevents accidental double-clicks and simple bot spam; return existing lead ID (200 OK) |
| **Timestamp timezone** | UTC in DB; display with "UTC" label in email | Clear and unambiguous; localization deferred |
| **Phone validation** | Flexible; max 20 chars | International formats vary wildly; strict validation creates friction |
| **Email branding** | Text only; no images | Simpler, smaller, avoids spam filters; logo adds hosting complexity |

### Future Enhancements

- **Honeypot field** for simple bot protection (hidden form field)
- **Rate limiting** per IP address (Cloudflare or in-app)
- **CAPTCHA** integration in PR5 frontend
- **Webhook delivery** as backup channel for email
- **`source` field** for lead attribution (`web_chat`, `telegram`, `landing_page`)
- **Queue-based async delivery** for high traffic scenarios
- **Partner routing** when expanding to multiple destinations

---

## Definition of Done

**Code Complete:**

- [ ] All source files created per file structure
- [ ] TypeScript interfaces defined with proper types (no `any`)
- [ ] Zod validation schemas complete with field-level error messages
- [ ] Lead service functions implemented (captureLead, deliverLead, captureAndDeliverLead)
- [ ] Email templates render correctly (HTML + plain text)
- [ ] POST `/api/lead` endpoint working with all error cases handled
- [ ] Barrel exports in index.ts for clean imports

**Testing Complete:**

- [ ] Unit tests written for validation schemas
- [ ] Unit tests written for service functions
- [ ] Unit tests written for email templates
- [ ] Integration tests written for API endpoint
- [ ] All tests passing locally
- [ ] Test coverage >80% for lead modules (optional but recommended)
- [ ] Manual testing checklist completed (curl tests, database verification, email verification)

**Documentation Complete:**

- [ ] `.env.example` updated with new variables and comments
- [ ] Inline code comments for complex logic
- [ ] JSDoc comments for public functions
- [ ] README updated if necessary (API endpoint documentation)
- [ ] This PR plan document reflects actual implementation

**Quality Checks:**

- [ ] `pnpm lint` passes with no errors
- [ ] `pnpm typecheck` passes with no errors
- [ ] `pnpm test` passes all tests
- [ ] `pnpm build` succeeds without warnings
- [ ] No console.log statements (use proper logging)
- [ ] Error messages are user-friendly (no stack traces in responses)

**Integration Ready:**

- [ ] API endpoint testable via curl/Postman
- [ ] Database schema compatible (PR1 migrations run)
- [ ] Environment variables documented
- [ ] Resend account setup and verified
- [ ] Email delivery tested to multiple providers

**Git & CI:**

- [ ] Branch created: `feature/pr4-lead-capture`
- [ ] Commits are atomic and well-described
- [ ] No merge conflicts with main
- [ ] CI pipeline passes (GitHub Actions)
- [ ] No failing checks in PR

**Review Ready:**

- [ ] Code follows project coding guidelines
- [ ] No obvious security issues (XSS, SQL injection via ORM)
- [ ] Performance considerations addressed (N+1 queries, etc.)
- [ ] Edge cases handled (null values, empty strings, etc.)
- [ ] Ready for PR review and approval

---

**End of PR4 Plan**
