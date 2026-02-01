"""
Lightweight medical query detector using LLM.

Uses fast LLM to classify if a user query is about medical/health concerns
vs general diving questions (dive sites, destinations, certifications).
"""

import json
import logging
from typing import Optional

from app.core.config import settings
from app.services.llm.factory import create_llm_provider
from app.services.llm.types import LLMMessage

logger = logging.getLogger(__name__)


class MedicalQueryDetector:
    """Detect if user query is medical/health-related using LLM."""

    SYSTEM_PROMPT = """You are a medical query classifier for a diving chatbot.

Your task: Determine if the user's question is about MEDICAL/HEALTH concerns.

**MEDICAL queries** (return true):
- Medical conditions: asthma, heart disease, diabetes, ear infections
- Symptoms: dizziness, pain, nausea, breathing problems
- Medications and diving compatibility
- Health clearance questions
- Physical fitness for diving

**NOT MEDICAL** (return false):
- Dive sites and destinations ("What dive sites are near X?")
- Certifications and training ("What is Open Water certification?")
- Equipment and gear ("What regulator should I buy?")
- Marine life ("What fish can I see?")
- Dive conditions ("What's the visibility like?")
- Trip planning ("When should I visit X?")

Respond with ONLY a JSON object:
{"is_medical": true} or {"is_medical": false}

No explanations, no extra text."""

    def __init__(self):
        """Initialize with fast, lightweight LLM."""
        # Use fastest model for quick classification (from settings)
        self.llm = create_llm_provider(
            provider_name=settings.default_llm_provider,
            temperature=0.0,  # Deterministic
            max_tokens=10,  # Just need {"is_medical": true/false}
        )
        logger.info("MedicalQueryDetector initialized")

    async def is_medical_query(self, user_message: str) -> bool:
        """
        Classify if user query is medical/health-related.

        Args:
            user_message: User's original question

        Returns:
            True if medical query, False otherwise
        """
        if not user_message or len(user_message.strip()) == 0:
            return False

        try:
            messages = [
                LLMMessage(role="system", content=self.SYSTEM_PROMPT),
                LLMMessage(role="user", content=f"Classify this query:\n\n{user_message}")
            ]

            response = await self.llm.generate(messages)
            response_text = response.content.strip()

            # Parse JSON response
            try:
                result = json.loads(response_text)
                is_medical = result.get("is_medical", False)
                logger.info(f"Medical query classification: {is_medical} for: {user_message[:50]}...")
                return is_medical
            except json.JSONDecodeError:
                # Fallback: check if response contains "true"
                is_medical = "true" in response_text.lower()
                logger.warning(f"Failed to parse JSON, fallback result: {is_medical}")
                return is_medical

        except Exception as e:
            logger.error(f"Medical query detection failed: {e}", exc_info=True)
            # Safe fallback: assume not medical (won't wrongly show disclaimer)
            return False
