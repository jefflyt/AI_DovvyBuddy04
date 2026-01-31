# Malaysia Emergency Contacts Content Ingestion

**Date:** 2026-01-31  
**Owner:** jefflyt  
**Status:** ⏳ Pending API Key Configuration

## Overview

Added comprehensive Malaysia diving emergency contacts document to the content directory. The document needs to be ingested into the RAG system once API credentials are configured.

## Content Added

**File:** [content/safety/diving-emergency-contacts-malaysia.md](../../content/safety/diving-emergency-contacts-malaysia.md)

**Size:** 28KB, comprehensive emergency reference document

**Content Sections:**
1. Quick reference table for critical contacts
2. National emergency services (MERS 999, SaveME app)
3. Divers Alert Network (DAN) Asia-Pacific contacts
4. Hyperbaric chambers (7 facilities across Malaysia)
5. Maritime rescue coordination (MRCC, MMEA)
6. Marine envenomation/poison control
7. Ambulance services (government and 30+ private providers)
8. Major hospital A&E departments
9. Regional considerations (Peninsular, Sabah, Sarawak)
10. Emergency preparedness for dive instructors
11. Essential Malay phrases
12. Cost considerations and insurance

## Code Updates Completed ✅

Updated emergency response text in multiple locations to reference Malaysia-specific contacts:

### 1. Hybrid EmergencyDetector

**File:** [backend/app/orchestration/emergency_detector_hybrid.py](../../backend/app/orchestration/emergency_detector_hybrid.py)

**Changes:**
- Updated `get_emergency_response()` to include Malaysia contacts
- Added DAN Malaysia: +60-15-4600-0109
- Added MERS 999 and mobile 112
- Listed all Malaysia hyperbaric chambers with phone numbers
- Added MRCC and maritime emergency contacts
- Added note about RAG system containing comprehensive details

### 2. Safety Prompts

**File:** [backend/app/prompts/safety.py](../../backend/app/prompts/safety.py)

**Changes:**
- Updated `SAFETY_DISCLAIMER` to include DAN Malaysia hotline
- Added note directing users to ask about "Malaysia diving emergency contacts"
- Updated `EMERGENCY_RESPONSE` with Malaysia-specific:
  - Emergency numbers (999, 112)
  - DAN Malaysia hotline
  - All 4 main hyperbaric chambers
  - Maritime rescue contacts
  - Note about comprehensive info in knowledge base

## Pending: RAG Ingestion ⏳

### Current Blocker

API key not configured in `.env.local`:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### Ingestion Command

Once API key is configured, run:
```bash
cd backend
python scripts/ingest_content.py
```

**Expected Result:**
- 16 markdown files processed
- New Malaysia emergency contacts document chunked and embedded
- Approximately 50-100 chunks created (document is detailed)
- RAG system can retrieve emergency contacts by region/facility type

### Alternative: Manual Ingestion

If API key remains unavailable, content can be ingested when production credentials are available or during deployment setup.

## Impact on User Experience

### Immediate Benefits (Code Updates)

✅ **Emergency responses now Malaysia-specific:**
- Users get relevant local emergency numbers (999 vs 911)
- Correct DAN hotline for Malaysia (+60 vs +1)
- Actual hyperbaric chamber locations with direct contacts
- Maritime rescue coordination centers

✅ **Prompts reference knowledge base:**
- Users informed comprehensive info available
- Can ask: "What are Malaysia diving emergency contacts?"
- Can ask: "Where is nearest hyperbaric chamber to Sipadan?"

### After RAG Ingestion

🔮 **Enhanced retrieval:**
- RAG can fetch specific regional contacts (Sabah vs Peninsular)
- Can retrieve ambulance services by location (Kuala Lumpur vs Semporna)
- Can provide hospital A&E contacts by region
- Can retrieve poison control for marine envenomation

## Testing Checklist

### Manual Testing (After Ingestion)

- [ ] Query: "What's the emergency number in Malaysia?"
  - Should return: 999 (MERS) or 112 (mobile)
  
- [ ] Query: "Where is the nearest hyperbaric chamber to Sipadan?"
  - Should return: Semporna Navy Base +60-89-785-101
  
- [ ] Query: "I need DAN Malaysia contact"
  - Should return: +60-15-4600-0109
  
- [ ] Query: "What if a diver goes missing near Tioman?"
  - Should return: MRCC Port Klang +60-3-3167-0530
  
- [ ] Query: "Private ambulance in Kuala Lumpur?"
  - Should return: St. John +60-3-9285-5294 or other providers

### Emergency Detection Testing

- [ ] "I have chest pain after diving" → Should trigger emergency response with Malaysia numbers
- [ ] "What is DCS?" → Should NOT trigger emergency (educational query)
- [ ] Response should include DAN Malaysia +60-15-4600-0109

## Related Documents

- [Content file](../../content/safety/diving-emergency-contacts-malaysia.md) - Source document
- [Keyword Elimination Summary](./keyword-elimination-summary.md) - Related emergency detection work
- [PR6.2 Manual Testing](../plans/PR0-VERIFICATION-RESULTS.md) - Testing context

## Future Enhancements

1. **Regional Auto-Detection:** Detect user's diving location from conversation context and provide region-specific contacts
2. **Multi-Language Support:** Malay translations for emergency phrases (already in content)
3. **Cost Estimates:** Surface ambulance/chamber cost info when users ask about expenses
4. **Insurance Integration:** Link DAN coverage info with emergency responses

## Notes for Production

- **Verify contacts before production launch:** Emergency numbers change, verify currency
- **Update schedule:** Quarterly review of emergency contacts (hospitals, chambers)
- **Regional expansion:** Consider adding Thailand, Philippines, Indonesia emergency contacts
- **API rate limits:** Embeddings for large documents consume tokens, monitor costs

---

**Action Required:** Configure `GEMINI_API_KEY` in `.env.local` and run ingestion script to complete RAG integration.
