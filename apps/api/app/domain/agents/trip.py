"""
Trip agent for destination and dive site recommendations.
"""

import logging
from typing import Optional

from app.infrastructure.services.llm.base import LLMProvider
from app.infrastructure.services.llm.factory import create_llm_provider
from app.infrastructure.services.llm.types import LLMMessage
from app.prompts.specialists_v1 import (
    LEGACY_TRIP_SYSTEM_PROMPT,
    NO_VERIFIED_DATA_RESPONSE,
)

from .base import Agent, AgentResult
from .types import AgentCapability, AgentContext, AgentType

logger = logging.getLogger(__name__)


class TripAgent(Agent):
    """Agent for handling trip planning and destination queries."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """
        Initialize trip agent.

        Args:
            llm_provider: LLM provider (if None, creates default)
        """
        super().__init__(
            agent_type=AgentType.TRIP,
            name="Trip Agent",
            description="Provides destination recommendations and dive site information",
            capabilities=[AgentCapability.DESTINATION_RECOMMENDATION],
        )
        self.llm_provider = llm_provider or create_llm_provider()

    def get_tool_definition(self) -> dict:
        """Define trip planning tool for Gemini."""
        return {
            "name": "trip_planner",
            "description": "Plan a diving trip, recommend destinations, or find dive sites.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string", 
                        "description": "The user's trip-related request"
                    },
                    "location": {
                        "type": "string",
                        "description": "Specific location mentioned, or null"
                    }
                },
                "required": ["query"]
            }
        }

    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute trip agent.

        Args:
            context: Agent context with query

        Returns:
            AgentResult with destination recommendations
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

        system_prompt = LEGACY_TRIP_SYSTEM_PROMPT

        # Add diver profile context if available
        if context.diver_profile:
            cert_level = context.diver_profile.get("certification_level", "unknown")
            experience = context.diver_profile.get("dive_count", "unknown")
            system_prompt += f"\n\nDIVER PROFILE: Certification: {cert_level}, Experience: {experience} dives"

        messages.append(LLMMessage(role="system", content=system_prompt))

        # Conversation history
        for msg in context.conversation_history[-10:]:
            messages.append(LLMMessage(role=msg["role"], content=msg["content"]))

        # Current query with RAG context
        query_text = context.query
        
        # CRITICAL: Log whether RAG context exists
        if context.rag_context:
            logger.info(f"✅ TripAgent: RAG context EXISTS (length: {len(context.rag_context)} chars)")
            logger.debug(f"RAG context preview: {context.rag_context[:200]}...")
            query_text = f"""Destination Information:
{context.rag_context}

Question: {context.query}"""
        else:
            logger.error("TripAgent received no RAG context")
            query_text = f"NO_DATA\n\nQuestion: {context.query}"

        messages.append(LLMMessage(role="user", content=query_text))

        return messages
