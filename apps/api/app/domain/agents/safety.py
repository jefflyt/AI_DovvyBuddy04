"""
Safety agent for medical queries and safety disclaimers.
"""

import logging
from typing import Optional

from app.domain.orchestration.emergency_detector_hybrid import EmergencyDetector
from app.domain.orchestration.medical_detector import MedicalQueryDetector
from app.infrastructure.services.llm.base import LLMProvider
from app.infrastructure.services.llm.factory import create_llm_provider
from app.infrastructure.services.llm.types import LLMMessage
from app.prompts.specialists_v1 import LEGACY_SAFETY_SYSTEM_PROMPT

from .base import Agent, AgentResult
from .types import AgentCapability, AgentContext, AgentType

logger = logging.getLogger(__name__)


class SafetyAgent(Agent):
    """Agent for handling safety-related and medical queries."""
    
    # Shared LLM-based detectors (replaces keyword matching)
    _medical_detector: Optional[MedicalQueryDetector] = None
    _emergency_detector: Optional[EmergencyDetector] = None

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
        Check if query is likely medical/health-related.

        This method is synchronous by contract, so we use a lightweight
        keyword gate. Definitive classification still happens in execute().

        Args:
            context: Agent context to evaluate

        Returns:
            True if query is genuinely medical/health-related
        """
        query = (context.query or "").lower()
        medical_terms = (
            "pain",
            "injury",
            "bleeding",
            "dcs",
            "decompression",
            "medical",
            "asthma",
            "chest",
            "ear",
            "sinus",
            "emergency",
        )
        return any(term in query for term in medical_terms)

    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute safety agent.

        Args:
            context: Agent context with query

        Returns:
            AgentResult with safety disclaimer and guidance
        """
        try:
            # Lazy initialization of emergency detector
            if SafetyAgent._emergency_detector is None:
                SafetyAgent._emergency_detector = EmergencyDetector()
            
            # Check if this is an emergency using shared hybrid detector
            is_emergency, emergency_response = await SafetyAgent._emergency_detector.detect_emergency(
                context.query,
                conversation_history=context.conversation_history
            )

            if is_emergency:
                result = AgentResult(
                    response=emergency_response,
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

    def _build_messages(self, context: AgentContext) -> list:
        """Build message list for LLM."""
        messages = []

        system_prompt = LEGACY_SAFETY_SYSTEM_PROMPT
        messages.append(LLMMessage(role="system", content=system_prompt))

        # Conversation history
        for msg in context.conversation_history[-5:]:  # Fewer messages for safety queries
            messages.append(LLMMessage(role=msg["role"], content=msg["content"]))

        # Current query
        messages.append(LLMMessage(role="user", content=context.query))

        return messages
