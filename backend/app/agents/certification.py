"""
Certification agent for PADI/SSI certification guidance.
"""

import logging
from typing import Optional

from app.services.llm.base import LLMProvider
from app.services.llm.factory import create_llm_provider
from app.services.llm.types import LLMMessage

from .base import Agent, AgentResult
from .types import AgentCapability, AgentContext, AgentType

logger = logging.getLogger(__name__)


class CertificationAgent(Agent):
    """Agent for handling certification-related queries (PADI, SSI, etc.)."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """
        Initialize certification agent.

        Args:
            llm_provider: LLM provider (if None, creates default)
        """
        super().__init__(
            agent_type=AgentType.CERTIFICATION,
            name="Certification Agent",
            description="Provides guidance on diving certifications and training pathways",
            capabilities=[AgentCapability.CERTIFICATION_GUIDANCE],
        )
        self.llm_provider = llm_provider or create_llm_provider()

    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute certification agent.

        Args:
            context: Agent context with query

        Returns:
            AgentResult with certification guidance
        """
        try:
            messages = self._build_messages(context)
            response = await self.llm_provider.generate(messages)

            result = AgentResult(
                response=response.content,
                agent_type=self.agent_type,
                confidence=0.9,
                metadata={
                    "model": response.model,
                    "tokens_used": response.tokens_used,
                },
            )

            self._log_execution(context, result)
            return result

        except Exception as e:
            return await self._handle_error(context, e)

    def _build_messages(self, context: AgentContext) -> list:
        """Build message list for LLM."""
        messages = []

        # System prompt
        system_prompt = """You are DovvyBuddy's Certification Expert, specializing in diving certification guidance.

YOUR EXPERTISE:
- PADI certification pathways (Open Water, Advanced, Rescue, Divemaster, etc.)
- SSI certification system and equivalencies
- Prerequisites and requirements for each level
- Course structure, duration, and typical costs
- Age requirements and medical considerations

GUIDELINES:
- Provide clear, accurate information about certification pathways
- Explain prerequisites and what each certification enables
- Compare PADI and SSI when relevant
- Recommend appropriate certifications based on diver goals
- Always mention that students should verify details with certified instructors
- For medical questions, advise consulting a diving medical professional
- For specific pricing or availability, recommend contacting local dive centers

TONE: Knowledgeable, encouraging, and safety-focused. Help divers understand their certification options and make informed decisions about their diving education.
"""
        messages.append(LLMMessage(role="system", content=system_prompt))

        # Conversation history
        for msg in context.conversation_history[-10:]:
            messages.append(LLMMessage(role=msg["role"], content=msg["content"]))

        # Current query (add context if available)
        query_text = context.query
        if context.rag_context:
            query_text = f"Context:\n{context.rag_context}\n\nQuestion: {context.query}"

        messages.append(LLMMessage(role="user", content=query_text))

        return messages
