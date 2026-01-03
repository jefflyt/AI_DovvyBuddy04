"""
Safety agent for medical queries and safety disclaimers.
"""

import logging
import re
from typing import Optional

from app.services.llm.base import LLMProvider
from app.services.llm.factory import create_llm_provider
from app.services.llm.types import LLMMessage

from .base import Agent, AgentResult
from .types import AgentCapability, AgentContext, AgentType

logger = logging.getLogger(__name__)


class SafetyAgent(Agent):
    """Agent for handling safety-related and medical queries."""

    # Keywords that indicate medical/safety concerns
    MEDICAL_KEYWORDS = [
        "medical", "health", "condition", "disease", "illness", "medication",
        "surgery", "doctor", "physician", "cold", "flu", "asthma", "diabetes",
        "heart", "lung", "ear", "sinus", "pregnant", "pregnancy", "injury",
        "emergency", "accident", "dcs", "decompression", "barotrauma"
    ]

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """
        Initialize safety agent.

        Args:
            llm_provider: LLM provider (if None, creates default)
        """
        super().__init__(
            agent_type=AgentType.SAFETY,
            name="Safety Agent",
            description="Provides safety disclaimers and redirects medical queries",
            capabilities=[AgentCapability.SAFETY_DISCLAIMER],
        )
        self.llm_provider = llm_provider or create_llm_provider()

    def can_handle(self, context: AgentContext) -> bool:
        """
        Check if query contains medical/safety keywords.

        Args:
            context: Agent context to evaluate

        Returns:
            True if query contains medical/safety keywords
        """
        query_lower = context.query.lower()
        return any(keyword in query_lower for keyword in self.MEDICAL_KEYWORDS)

    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute safety agent.

        Args:
            context: Agent context with query

        Returns:
            AgentResult with safety disclaimer and guidance
        """
        try:
            # Detect if this is an emergency
            is_emergency = self._is_emergency(context.query)

            if is_emergency:
                result = AgentResult(
                    response=self._get_emergency_response(),
                    agent_type=self.agent_type,
                    confidence=1.0,
                    metadata={"is_emergency": True},
                )
            else:
                # Generate contextual safety response
                messages = self._build_messages(context)
                response = await self.llm_provider.generate(messages)

                result = AgentResult(
                    response=response.content,
                    agent_type=self.agent_type,
                    confidence=1.0,
                    metadata={
                        "model": response.model,
                        "tokens_used": response.tokens_used,
                        "is_emergency": False,
                    },
                )

            self._log_execution(context, result)
            return result

        except Exception as e:
            return await self._handle_error(context, e)

    def _is_emergency(self, query: str) -> bool:
        """Check if query indicates an emergency situation."""
        emergency_keywords = [
            "emergency", "urgent", "accident", "injured", "pain", "bleeding",
            "unconscious", "drowning", "can't breathe", "chest pain", "dcs symptoms"
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in emergency_keywords)

    def _get_emergency_response(self) -> str:
        """Get emergency response with immediate action guidance."""
        return """⚠️ **EMERGENCY SITUATION DETECTED**

If you or someone else is experiencing a diving-related emergency:

1. **CALL EMERGENCY SERVICES IMMEDIATELY** (911 or local emergency number)
2. For diving emergencies, contact DAN (Divers Alert Network):
   - USA/Canada: +1-919-684-9111 (24/7)
   - International: Contact your local DAN chapter
3. Do NOT attempt self-treatment
4. Provide 100% oxygen if available and trained to do so
5. Keep the person lying flat and monitor vital signs

**Common diving emergencies:**
- Decompression Sickness (DCS)
- Arterial Gas Embolism (AGE)
- Lung overexpansion injuries
- Near-drowning

I am an AI assistant and cannot provide emergency medical care. Please seek professional help immediately.
"""

    def _build_messages(self, context: AgentContext) -> list:
        """Build message list for LLM."""
        messages = []

        # System prompt with safety guidelines
        system_prompt = """You are DovvyBuddy's Safety Advisor, specializing in diving safety and medical considerations.

YOUR ROLE:
- Provide general safety information and guidelines
- Redirect medical questions to qualified professionals
- Offer safety disclaimers for medical conditions
- Explain when to consult dive medicine specialists
- Provide general safety best practices

CRITICAL GUIDELINES:
⚠️ NEVER provide specific medical advice or diagnoses
⚠️ ALWAYS recommend consulting qualified medical professionals
⚠️ For any medical condition, advise seeing a dive medicine physician
⚠️ Emphasize the importance of proper training and certification
⚠️ Highlight that diving with certain conditions requires medical clearance

RESPONSE STRUCTURE:
1. Acknowledge the safety/medical concern
2. Provide general safety information (if appropriate)
3. **ALWAYS include a clear disclaimer to consult medical professionals**
4. Recommend specific resources (DAN, dive medicine physicians)
5. Emphasize safety-first approach

TONE: Serious, professional, and protective. Prioritize safety above all else.
"""
        messages.append(LLMMessage(role="system", content=system_prompt))

        # Conversation history
        for msg in context.conversation_history[-5:]:  # Fewer messages for safety queries
            messages.append(LLMMessage(role=msg["role"], content=msg["content"]))

        # Current query
        messages.append(LLMMessage(role="user", content=context.query))

        return messages
