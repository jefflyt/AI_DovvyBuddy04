---

# Make DovvyBuddy conversations less “static”

## Title

Make DovvyBuddy conversations less “static” via Intent + State + Mandatory Follow-up

## Problem / Why

Current chat behavior often feels like a one-shot Q&A: it answers, then stops. This reduces engagement and makes the assistant feel less like a dive buddy/instructor and more like a search box. We need a deterministic mechanism that sustains dialogue without adding fluff or increasing unsafe “advice” behavior.

## Goal

Increase conversational continuity while preserving dive safety, accuracy, and MVP simplicity.

## Non-goals

- No “personality agent” that invents banter or adds ungrounded facts
- No multi-agent orchestration in V1
- No additional UI complexity beyond minimal changes needed

## Proposed approach

Implement a “Next-Turn Obligation” system:

1. Classify each user message into a small intent set (5–8 intents).
2. Track minimal session state (4–5 fields).
3. For all non-emergency intents, end every assistant response with exactly one continuation prompt that either:
   - resolves the highest-impact missing state, or
   - advances the user’s task via a relevant next step.
4. For emergency/medical intents, disable expansion and use strict safe handling.

## Intent set (V1)

- `INFO_LOOKUP`
- `DIVE_PLANNING`
- `CONDITIONS`
- `SKILL_EXPLANATION`
- `MARINE_LIFE`
- `GEAR`
- `AGENCY_CERT`
- `EMERGENCY_MEDICAL` (special-case: no follow-up expansion)

## Minimal session state

- `cert_level`: `unknown` | `OW` | `AOW` | `DM` | `Instructor`
- `context_mode`: `learning` | `planning` | `briefing` | `curiosity`
- `location_known`: boolean
- `conditions_known`: boolean
- (optional) `last_intent`: string

## Acceptance criteria

- For any non-emergency user message: assistant response ends with one and only one continuation question/prompt.
- Continuation question must be specific (no “Anything else?”).
- Continuation question must not introduce new factual claims.
- `EMERGENCY_MEDICAL` path never asks exploratory follow-ups; uses safety-first guidance + referral language.
- Add unit tests for:
  - intent classification routing
  - “exactly one follow-up” enforcement
  - emergency bypass
- Add basic telemetry counters (optional): % turns with follow-up, average turns/session, drop-off after 1st answer.

## Examples

**User:** “Is this dive site good?”

**Assistant:** “It can knowably fit certain experience levels and conditions. What certification level are you diving at?”

**User:** “What is a DSMB?”

**Assistant:** “A DSMB is a surface marker buoy used to signal your position. Is this for learning, planning, or a pre-dive briefing?”

## Risks & mitigations

- **Risk:** Feels interrogative — **Mitigation:** One follow-up only; prioritize highest-impact unknown.
- **Risk:** Safety dilution — **Mitigation:** Emergency/medical intent disables expansion; add guardrails.

## Implementation notes

- Keep logic deterministic: follow-up selection based on missing-state priority.
- Use template-based follow-up strings per intent.
- Store state in session memory/local storage as appropriate.

## Definition of done

- Conversation feels continuous (≥3 turns average in internal test scripts) without added verbosity.
- No regression in safety refusal behavior.

## Owner / Priority

- **Priority:** High (improves engagement/retention with low engineering risk)
- **Target:** Next sprint / next PR
