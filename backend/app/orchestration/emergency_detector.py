"""
Emergency detector for safety-critical message classification.

Uses keyword-based detection (NOT LLM) for deterministic, fast, safety-first behavior.
Detects symptom keywords + first-person context to identify medical emergencies.
"""

import logging
import re
from typing import List

logger = logging.getLogger(__name__)


class EmergencyDetector:
    """
    Keyword-based emergency detector for safety-critical messages.
    
    Detects medical emergencies by looking for:
    1. Symptom keywords (chest pain, difficulty breathing, etc.)
    2. First-person context (I, my, me, after dive, during dive)
    
    Educational queries like "What is DCS?" are NOT treated as emergencies.
    """

    # Symptom keywords indicating potential medical emergency
    SYMPTOM_KEYWORDS: List[str] = [
        "chest pain",
        "chest hurts",
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
        "after the dive",
        "after diving",
        "during dive",
        "during diving",
        "while diving",
        "post dive",
        "post-dive",
    ]

    def is_emergency(self, message: str) -> bool:
        """
        Check if message indicates a medical emergency.
        
        Returns True only if:
        1. Message contains at least one symptom keyword, AND
        2. Message contains first-person context OR dive context
        
        This prevents educational queries like "What is DCS?" from being
        classified as emergencies while catching actual medical situations
        like "I have chest pain after diving".
        
        Args:
            message: User's message to check
            
        Returns:
            True if emergency detected, False otherwise
        """
        normalized = message.lower().strip()

        # Check for symptom keyword
        has_symptom = any(
            symptom in normalized for symptom in self.SYMPTOM_KEYWORDS
        )

        if not has_symptom:
            return False

        educational_patterns = [
            r"^what\s+is\b",
            r"^tell\s+me\s+about\b",
            r"^explain\b",
            r"^can\s+you\s+explain\b",
        ]
        if any(re.search(pattern, normalized) for pattern in educational_patterns):
            return False

        # Check for first-person context
        has_first_person = any(
            re.search(rf"\b{re.escape(keyword)}\b", normalized)
            for keyword in self.FIRST_PERSON_KEYWORDS
        )

        # Exclude third-person framing even when first-person tokens appear.
        third_person_patterns = [
            r"\bmy\s+(friend|buddy|partner|wife|husband|son|daughter|mom|dad)\b",
            r"\bhe|she|they\b",
        ]
        has_third_person_context = any(
            re.search(pattern, normalized) for pattern in third_person_patterns
        )

        # Check for dive context
        has_dive_context = any(
            keyword in normalized for keyword in self.DIVE_CONTEXT_KEYWORDS
        )

        # Emergency requires personal or dive context, but not third-person framing.
        is_emergency = has_symptom and (has_first_person or has_dive_context) and not has_third_person_context

        if is_emergency:
            logger.warning(
                f"Emergency detected: symptom={has_symptom}, "
                f"first_person={has_first_person}, "
                f"dive_context={has_dive_context}, "
                f"message_preview='{normalized[:100]}...'"
            )
        else:
            logger.debug(
                f"No emergency: symptom={has_symptom}, "
                f"first_person={has_first_person}, "
                f"dive_context={has_dive_context}"
            )

        return is_emergency

    def get_emergency_response(self) -> str:
        """
        Get standard emergency response message.
        
        Returns:
            Emergency response with safety guidance
        """
        return (
            "⚠️ **EMERGENCY: Seek Immediate Medical Attention**\n\n"
            "If you are experiencing symptoms after diving, this may be serious. "
            "**Do not delay seeking medical help.**\n\n"
            "**Immediate Actions:**\n"
            "1. Call emergency services (911/112) or local dive emergency number\n"
            "2. Contact DAN (Divers Alert Network): +1-919-684-9111 (24/7)\n"
            "3. Breathe 100% oxygen if available\n"
            "4. Lie flat and stay calm\n"
            "5. Do NOT attempt to dive again\n\n"
            "**DAN Emergency Hotline:** +1-919-684-9111 (accepts collect calls)\n\n"
            "I'm an AI assistant and cannot provide emergency medical care. "
            "Please contact a medical professional immediately."
        )
