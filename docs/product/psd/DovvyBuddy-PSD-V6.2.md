# DovvyBuddy (AI Diving Bot) — Product Specification Document (PSD) — V6.2

**Document Version:** V6.2  
**Last Updated:** December 21, 2025  
**Status:** Ready for Implementation (Option A: Web V1 + Telegram V1.1)

---

## 1. Overview

### 1.1 Product Summary

DovvyBuddy is a **diver-first** AI assistant that helps **prospective and recreational divers** (new students, OW→AOW divers, and travel divers) make decisions with less confusion and more confidence — **without pretending to be an instructor**.

It is intentionally **not a dive shop directory**. Dive shops/schools appear only when a diver asks to **connect with a professional** (training or guided dives).

Core capabilities:

- **Certification Navigator (agency-aware, V1):**
  - Explains what each step means (Open Water / advanced-level / specialties) in plain language.
  - Compares common pathways across **PADI and SSI** (initial focus), and handles other agencies with a “best-effort equivalency + verify” pattern.
  - Clarifies common confusions (e.g., PADI AOW is typically structured around “Adventure Dives,” not five full specialty courses; verification required with the instructor/operator).
- **Confidence + uncertainty handling for new students (V1):**
  - Normalizes common fears (mask, breathing, equalization, buoyancy, depth anxiety) and explains course structure and expectations.
  - Shares **prerequisite information** (age bands, swim/comfort checks, required paperwork/medical questionnaires) as **information only**, with clear “confirm with your instructor/agency” prompts.
- **Trip research for OW/AOW travel divers (V1):**
  - Destination + site guidance limited to the **covered set**, with certification-level suitability noted.
  - Logistics and seasonal notes grounded in curated content.
- **Lead capture and warm handoff (V1):**
  - When a diver is ready, collect context and send a qualified inquiry to a partner shop/school.
  - **No booking flow**.

The initial public version is a **web chatbot only**, with intentionally small, high-quality coverage.

### 1.2 Goals

**Diver outcomes (primary):**

- G-01: Reduce confusion for prospective divers by explaining Open Water pathways, prerequisites, and what to expect (agency-aware, non-advisory).
- G-02: Help OW divers understand advanced-level options and choose next steps with clearer tradeoffs.
- G-03: Help travel divers (OW/AOW) shortlist **covered** destinations/sites that fit constraints (time, season, interests, comfort level) with high signal and clear limits.
- G-04: Build trust via grounded answers, explicit uncertainty, and consistent safety disclaimers.

**Business outcomes (secondary, enabled by diver focus):**

- G-05: Convert high-intent diver conversations into **qualified, context-rich leads** for partner shops/schools.
- G-06: Prove a diver-first wedge (repeat usage + lead conversion) in a limited set of destinations before scaling.

### 1.3 Non-Goals

- NG-01: No direct booking of flights, accommodation, or dives in V1.
- NG-02: No dive log storage for users in V1.
- NG-03: No photo-based marine life recognition in V1.
- NG-04: No decompression calculations, medical advice, or technical dive planning beyond generic, non-personalized information and links to authoritative sources.
- NG-05: No multi-language support in V1 (English only).
- NG-06: No B2B dashboards for dive shops in V1.
- NG-07: No “global” answers presented as authoritative (if a destination/site is not covered, the bot must say so).

### 1.4 Scope — Public V1 (Lean)

**In Scope (V1):**

- Web-based chatbot UI (desktop + mobile web).
- RAG over curated content for:
  - Open Water certification guide (PADI + SSI focus): structure, FAQs, common fears/uncertainties, prerequisites (information-only).
  - Advanced-level guide (PADI + SSI focus): benefits, structure, prerequisites (information-only), and “what’s next” options.
  - Certification comparison & equivalency notes (PADI↔SSI; other agencies handled with verify-first equivalency guidance).
  - **1 destination initially** (add 2nd only after first destination meets stability criteria: ≥5 leads/week, 0 critical bugs, partners satisfied with lead quality).
  - **5–10 dive sites per destination** (with certification-level suitability noted).
  - **2–3 partner shops/schools per destination**.
  - 1–2 safety reference docs (general + destination-specific if available).
  - 1 logistics/getting-there guide per destination.
- Guest-only, session-based memory (no user accounts).
- Inline lead capture (minimal fields) for training and trip inquiries, with automated delivery to partner(s).
- Basic analytics (sessions, key funnels, leads by type: training vs trip).
- Out-of-scope handling (covered vs not covered; no booking; no medical advice).
- Basic error handling + operational visibility.

**Explicitly Out of Scope (V1):**

- Flight schedule API integration (defer).
- ML-based recommendation ranking.
- Telegram or other messaging integrations.
- User authentication and profiles.
- Payments/subscriptions.
- Dive logs and media storage.
- B2B dashboards.
- Any personalized decompression/safety computations.
- Trip outline generation.

### 1.5 Certification System Support (Diver-First)

**V1 explicit support (compare + explain):**

- **PADI:** OW, AOW, Rescue, Divemaster; core specialties (high-level).
- **SSI:** Open Water Diver, Advanced Adventurer (and common equivalents), Stress & Rescue, Divemaster; key specialties (high-level).

**Other systems (handled safely):**

- CMAS, NAUI, SDI/TDI, RAID, etc. are supported via a **self-declared mapping flow**:
  - Ask: agency + level + logged dives.
  - Provide a best-effort equivalency suggestion **with “verify with instructor/agency” disclaimer**.
  - If user can’t map, switch to concept-level explanations instead of agency-specific promises.

**Certification Navigator rules (must-have):**

- Separate **facts** vs **judgment**.
- For “what should I take next?”, give options + questions to ask a real instructor (no directives).
- If sources conflict or are unclear, say so and suggest verification.

### 1.6 Product Positioning: Diver-First, Not Shop-First

- Primary database is diver intent + context (session-level in V1; persistable later), not a shop directory.
- Shops appear at the last step: “Connect me with a professional for training/trips.”
- Monetization flywheel: diver demand → easier shop onboarding.

---

## 2. Personas (Priority Order)

### P-01 – Prospective New Diver (Primary)

- Profile: Non-certified; curious; may have snorkeled or done a Discover Scuba.
- Goals: Understand OW; reduce fear; compare PADI/SSI at high level; find a reputable school.
- Success: Clarity + training lead submitted.

### P-02 – OW Diver Seeking Advanced Certification (Primary)

- Profile: OW certified; ~4–20 dives.
- Goals: Understand advanced-level options; choose next step; find reputable training.
- Success: Confident plan + training lead submitted.

### P-03 – Certified Diver Planning a Dive Trip (Secondary)

- Profile: OW/AOW; ~10–100+ dives.
- Goals: Research covered destinations/sites; connect with reputable operators.
- Success: Shortlist + warm handoff.

### P-04 – Dive Shop Owner / Manager (Indirect)

- Goal: Receive fewer, better-qualified leads.
- Success: Lead context reduces back-and-forth.

---

## 3. Key Use Cases (Priority Order)

### UC-00 — Compare Certification Pathways (PADI vs SSI) and Plan Next Steps

- Concept-first explanation → agency-specific orientation where covered.
- Provide decision checklist + optional handoff to partner.

### UC-01 — Learn to Dive: Open Water Certification

- Grounded answers, confidence-building, prerequisites as info-only.
- Optional training lead capture.

### UC-02 — Advance Certification: OW → Advanced Level

- Explain structure and typical options; no directives.
- Optional training lead capture.

### UC-03 — Research a Covered Destination / Dive Sites

- RAG-grounded overview; suggest 2–5 sites from covered set.

### UC-04 — Discover Suitable Destination (Covered Set Only)

- Ask a few follow-ups, return 1–3 covered suggestions; refuse uncovered.

### UC-05 — Capture and Send a Qualified Lead

- Capture minimal fields; deliver to partner via email (webhook optional).

### UC-06 — Safety / No-Fly / Medical Queries

- General info only; disclaimers; redirect to professionals.

---

## 4. Functional Requirements (FRs)

### 4.1 Conversation & Session Management

**FR-01 — Web Chat Interface (V1 / Must Have)**  
Provide a web-based chat interface.

**FR-02 — Session-Based Memory for Guests (V1 / Must Have)**

- Session lifetime: 24 hours of inactivity OR explicit reset.
- No cross-session memory.

**FR-02A — Diver Profile Capture (Session-Level) (V1 / Must Have)**  
Maintain a lightweight `diver_profile` inside the session:

- certification_agency (optional)
- certification_level (optional)
- approximate_dive_count (optional)
- comfort_level / concerns (optional)
- travel intent (optional)

**FR-03 — User-Controlled Reset (V1 / Must Have)**  
Visible “New chat” clears session context.

### 4.2 Destination Discovery & Recommendations

**FR-04 — Covered-Set Recommendations (V1 / Must Have)**  
Recommend only from configured set.

**FR-05 — Out-of-Scope Handling (V1 / Must Have)**  
Refuse unsupported destinations/sites, booking requests, and medical advice; redirect without inventing facts.

**FR-06 — Dive Site Details (V1 / Must Have)**  
Concise site descriptions grounded in curated content.

**FR-06A — Certification Navigator: Agency Comparison (V1 / Must Have)**

- Concept-first → agency-specific where covered.
- Comparisons, not recommendations.
- Always prompt verification for prerequisites/costs/standards.

**FR-06B — Prerequisite Information Mode (V1 / Must Have)**  
Prerequisites are information-only. No medical clearance judgments.

**FR-06C — Uncertainty/Fear Support Flow (V1 / Must Have)**  
Ask 1–3 clarifying questions; reassure based on training structure; offer professional handoff.

### 4.3 Knowledge Retrieval (RAG) & Content

**FR-07 — RAG over Curated Content (V1 / Must Have)**  
Retrieve/ground responses on curated docs.

**FR-08 — Hallucination Guardrails (V1 / Must Have)**

- Say unknown when not in corpus.
- Provide ranges, not point estimates.
- Never invent specific facts.

### 4.4 Safety Guidance

**FR-09 — Safety Response Mode (V1 / Must Have)**  
General info only; disclaimers; direct urgent cases to local emergency services / qualified professionals. No decompression schedule calculations.

### 4.5 Lead Capture & Routing

(Keep as in V6.1: FR-10 through FR-15 unchanged.)

### 4.6 Analytics & Ops

(Keep as in V6.1: FR-16 through FR-18 unchanged.)

### 4.7 Integrations

**FR-19 — Flight Schedule API (Out of Scope V1)**  
Defer to later phase.

---

## 5. Non-Functional Requirements (NFRs)

(Keep as in V6.1: NFR-01 through NFR-06 unchanged.)

---

## 6. Architecture & Data Model (Confirmed)

### 6.1 Architecture (Confirmed: Option 1)

**Decision:** **Next.js (React) + Vercel + Postgres (Neon or Supabase)**

You want **Google ADK** for orchestration while keeping Next.js for the web experience. Use a small split:

- **Web app (Next.js on Vercel):**
  - Chat UI, landing pages, later auth.
  - Calls an agent endpoint (e.g., `/chat`) over HTTPS.
- **Agent service (ADK runtime):**
  - Orchestrates retrieval, safety policies, and model calls.
  - Serves both web (V1) and Telegram (V1.1).

Recommended deployment for the agent service:

- **Google Cloud Run** (containerized service).

### 6.1A Model Provider Plan (Confirmed)

- **Dev / early production:** Groq API for LLM inference.
- **Production target:** Google Gemini API.

Requirement:

- All model calls go through a `ModelProvider` interface with an environment switch (`LLM_PROVIDER=groq|gemini`).

### 6.2 Retrieval Method (Confirmed: Option A)

**Decision:** Retrieval Method Option A — **embedded vector search** (no dedicated managed vector DB service).

Implementation:

- Store curated markdown content in a repo folder (versioned in Git).
- Ingest → chunk → embed → build an index inside the agent service.
- Use **Gemini embeddings from day 1** so retrieval behavior matches production even if generation uses Groq in dev.

Index persistence (pick one):

- **A1: Object-storage-backed index**
  - Build an index artifact and store it in cloud object storage (e.g., GCS).
  - On startup, agent service downloads the index to local disk.
- **A2: Postgres + pgvector (still “embedded” in one DB)**
  - Store vectors in your existing Postgres database.

Recommendation:

- Prefer **A2 (Postgres + pgvector)** if you plan to scale Cloud Run instances or want simple persistence/backups.
- Use **A1** only if you are confident you’ll keep single-instance behavior and can tolerate index download on cold starts.

---

## 6.3 Data Model (Lean V1)

### Destination

```
id: UUID (primary key)
name: VARCHAR(255)
country: VARCHAR(100)
is_active: BOOLEAN (default true)
created_at: TIMESTAMP
```

### DiveSite (updated)

Yes — include **minimum certification**. It improves recommendation filtering and expectation-setting, and reduces “surprise” for new divers.

```
id: UUID (primary key)
destination_id: UUID (foreign key → destinations.id)
name: VARCHAR(255)

# Suitability (guidance, not a hard gate)
min_certification_level: VARCHAR(50)
  # examples: 'DSD/Non-certified', 'Open Water', 'Advanced Open Water', 'Rescue+', 'Tech-only', 'Unknown'
min_logged_dives: INTEGER (nullable)
  # optional; only when partners/public sources specify a minimum experience

# Basic descriptors
difficulty_band: VARCHAR(50)  # 'Beginner' | 'Intermediate' | 'Advanced'
access_type: VARCHAR(50)      # 'Shore' | 'Boat'

is_active: BOOLEAN (default true)
created_at: TIMESTAMP
```

**Safety framing requirement:** `min_certification_level` is a _typical suitability signal_, not an approval to dive. Operators and local conditions can change requirements; always say “confirm with the operator/instructor.”

---

## 12. Release Plan & Roadmap

(Keep as in V6.1: V1 web, V1.1 Telegram thin client + “Email me my plan,” V2 profiles + log, V2.1 species ID, V3 personalization/ML.)

---

## Document Changelog

**V6.2 (December 21, 2025):**

- Confirmed **Architecture Option 1**: Next.js + Vercel + Postgres.
- Confirmed **Retrieval Option A** with **Google ADK orchestration** and a **model-provider switch**: Groq (dev) → Gemini (prod).
- Added explicit retrieval persistence options (object-storage-backed index vs Postgres+pgvector).
- Confirmed `DiveSite.min_certification_level` (and optional `min_logged_dives`) for suitability filtering.
