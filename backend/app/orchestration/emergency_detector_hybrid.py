"""
Hybrid emergency detector with keyword + LLM validation.

Fast keyword-based detection for clear emergencies, with LLM fallback for ambiguous cases.
"""

import json
import logging
from typing import List, Optional

from app.core.config import settings
from app.services.llm.factory import create_llm_provider
from app.services.llm.types import LLMMessage

logger = logging.getLogger(__name__)


class EmergencyDetector:
    """
    Hybrid emergency detector for safety-critical messages.
    
    Uses two-tier approach:
    1. Keyword detection for fast, deterministic emergency detection
    2. LLM validation for ambiguous cases (e.g., "What is DCS?" vs "I have DCS")
    """

    # Symptom keywords indicating potential medical emergency
    SYMPTOM_KEYWORDS: List[str] = [
        "chest pain",
        "can't breathe",
        "cannot breathe",
        "difficulty breathing",
        "hard to breathe",
        "dizzy",
        "dizziness",
        "numb",
        "numbness",
        "paralyzed",
        "paralysis",
        "bleeding",
        "unconscious",
        "confused",
        "confusion",
        "tingling",
        "weak",
        "weakness",
        "can't feel",
        "cannot feel",
        "vision problems",
        "blurred vision",
        "hearing loss",
        "ringing ears",
        "nausea",
        "vomiting",
        "severe headache",
        "seizure",
        "convulsions",
    ]

    # First-person context indicators (must be present with symptom)
    FIRST_PERSON_KEYWORDS: List[str] = [
        "i",
        "i'm",
        "i am",
        "my",
        "me",
        "i've",
        "i have",
    ]

    # Dive-related context indicators
    DIVE_CONTEXT_KEYWORDS: List[str] = [
        "after dive",
        "after diving",
        "during dive",
        "during diving",
        "while diving",
        "post dive",
        "post-dive",
    ]

    LLM_VALIDATION_PROMPT = """You are an emergency classifier for a diving safety chatbot.

Your task: Determine if this message represents an ACTIVE MEDICAL EMERGENCY.

**EMERGENCY (return true):**
- Person is experiencing symptoms NOW: "I have chest pain", "I feel dizzy"
- Symptoms after/during diving: "I felt numb after diving"
- Immediate help needed: "My buddy is unconscious"

**NOT EMERGENCY (return false):**
- Educational questions: "What is DCS?", "What causes ear pain?"
- Hypothetical: "Can asthma cause problems?"
- General information: "Tell me about decompression sickness"
- Past tense without urgency: "I had a cold last week"

Respond with ONLY a JSON object:
{"is_emergency": true} or {"is_emergency": false}"""

    def __init__(self):
        """Initialize with optional LLM for ambiguous cases."""
        # Lazy init LLM only when needed
        self._llm = None
        logger.info("EmergencyDetector initialized (hybrid keyword + LLM)")

    async def detect_emergency(
        self, 
        message: str, 
        conversation_history: Optional[List[dict]] = None
    ) -> tuple[bool, str]:
        """
        Detect if message indicates active medical emergency.
        
        Uses fast keyword check first, LLM validation for ambiguous cases.

        Args:
            message: User message to analyze
            conversation_history: Optional conversation context (for future enhancement)

        Returns:
            Tuple of (is_emergency: bool, emergency_response: str)
        """
        if not message or len(message.strip()) == 0:
            return False, ""

        message_lower = message.lower()

        # Fast path: Check for symptom keywords
        has_symptom = any(keyword in message_lower for keyword in self.SYMPTOM_KEYWORDS)
        
        if not has_symptom:
            return False, ""  # No symptom keywords = not emergency

        # Check for first-person context
        has_first_person = any(keyword in message_lower for keyword in self.FIRST_PERSON_KEYWORDS)
        has_dive_context = any(keyword in message_lower for keyword in self.DIVE_CONTEXT_KEYWORDS)

        # Clear emergency: symptom + first person + dive context
        if has_symptom and has_first_person and has_dive_context:
            logger.warning(f"🚨 EMERGENCY DETECTED (keywords): {message[:50]}...")
            return True, self.get_emergency_response()

        # Ambiguous case: symptom present but unclear context
        # Use LLM to distinguish "I have chest pain" (emergency) from "What causes chest pain?" (educational)
        if has_symptom:
            is_emergency = await self._validate_with_llm(message)
            if is_emergency:
                logger.warning(f"🚨 EMERGENCY DETECTED (LLM validated): {message[:50]}...")
                return True, self.get_emergency_response()
            else:
                logger.info(f"✅ Educational query (not emergency): {message[:50]}...")
                return False, ""

        return False, ""

    async def _validate_with_llm(self, message: str) -> bool:
        """
        Use LLM to validate ambiguous emergency cases.

        Args:
            message: User message to validate

        Returns:
            True if LLM confirms emergency
        """
        try:
            # Lazy initialization of LLM
            if self._llm is None:
                self._llm = create_llm_provider(
                    provider_name="gemini",
                    model="gemini-2.0-flash-exp",
                    temperature=0.0,  # Deterministic
                    max_tokens=10,  # Just need {"is_emergency": true/false}
                )

            messages = [
                LLMMessage(role="system", content=self.LLM_VALIDATION_PROMPT),
                LLMMessage(role="user", content=f"Classify this message:\n\n{message}")
            ]

            response = await self._llm.generate(messages)
            response_text = response.content.strip()

            # Parse JSON response
            try:
                result = json.loads(response_text)
                return result.get("is_emergency", False)
            except json.JSONDecodeError:
                # Fallback: check if response contains "true"
                return "true" in response_text.lower()

        except Exception as e:
            logger.error(f"LLM emergency validation failed: {e}", exc_info=True)
            # Safe fallback: assume emergency (better false positive than missing real emergency)
            logger.warning("LLM validation failed, defaulting to EMERGENCY for safety")
            return True

    def get_emergency_response(self) -> str:
        """Get standard emergency response with immediate action guidance."""
        return """⚠️ **EMERGENCY: Seek Immediate Medical Attention**

If you are experiencing symptoms after diving, this may be serious. **Do not delay seeking medical help.**

**Immediate Actions:**
1. Call emergency services: 999 (Malaysia MERS) or 112 (mobile)
2. Contact DAN (Divers Alert Network):
   - Malaysia: +60-15-4600-0109
   - International: +61-8-8212-9242 (DAN Asia-Pacific)
   - Global: +1-919-684-9111 (24/7, accepts collect calls)
3. Breathe 100% oxygen if available and trained
4. Lie flat and stay calm
5. Do NOT attempt to dive again

**Malaysia Hyperbaric Chambers:**
- Peninsular: IUHM Lumut +60-5-681-9485 (24/7)
- Sabah (Sipadan area): Semporna Navy +60-89-785-101
- Labuan: +60-12-401-0598
- Kota Kinabalu: +60-88-251-326

**Maritime Emergency (Missing Diver):**
- MRCC Port Klang: +60-3-3167-0530 (24/7)
- Malaysian Maritime Enforcement: +60-3-8943-4001

I'm an AI assistant and cannot provide emergency medical care. The RAG system contains comprehensive Malaysia diving emergency contacts - ask about specific regions for detailed information."""
