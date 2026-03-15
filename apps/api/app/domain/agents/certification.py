"""
Certification agent for PADI/SSI certification guidance.
"""

import logging
from typing import Optional

from app.infrastructure.services.llm.base import LLMProvider
from app.infrastructure.services.llm.factory import create_llm_provider
from app.infrastructure.services.llm.types import LLMMessage
from app.prompts.specialists_v1 import (
    LEGACY_CERTIFICATION_SYSTEM_PROMPT,
    NO_VERIFIED_DATA_RESPONSE,
)

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
            if not context.rag_context or context.rag_context == "NO_DATA":
                return AgentResult(
                    response=NO_VERIFIED_DATA_RESPONSE,
                    agent_type=self.agent_type,
                    confidence=0.0,
                    metadata={
                        "no_data": True,
                        "raf_enforced": True,
                        "citations": [],
                    },
                )

            messages = self._build_messages(context)
            response = await self.llm_provider.generate(messages)
            citations = context.metadata.get("rag_citations", [])

            result = AgentResult(
                response=response.content,
                agent_type=self.agent_type,
                confidence=0.9 if citations else 0.6,
                metadata={
                    "model": response.model,
                    "tokens_used": response.tokens_used,
                    "citations": citations,
                },
            )

            self._log_execution(context, result)
            return result

        except Exception as e:
            return await self._handle_error(context, e)

    def _build_messages(self, context: AgentContext) -> list:
        """Build message list for LLM."""
        messages = []

        system_prompt = LEGACY_CERTIFICATION_SYSTEM_PROMPT
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
