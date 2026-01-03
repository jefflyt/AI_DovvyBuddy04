"""
Trip agent for destination and dive site recommendations.
"""

import logging
from typing import Optional

from app.services.llm.base import LLMProvider
from app.services.llm.factory import create_llm_provider
from app.services.llm.types import LLMMessage

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

    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute trip agent.

        Args:
            context: Agent context with query

        Returns:
            AgentResult with destination recommendations
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
        system_prompt = """You are DovvyBuddy's Trip Planning Expert, specializing in diving destinations and dive sites.

YOUR EXPERTISE:
- Diving destinations worldwide (Southeast Asia, Caribbean, Red Sea, Pacific, etc.)
- Specific dive sites and their characteristics
- Seasonal considerations and best times to visit
- Marine life and unique features of each location
- Certification requirements for different dive sites
- Budget considerations and travel logistics

GUIDELINES:
- Recommend destinations based on diver's certification level, experience, and preferences
- Consider seasonal factors (weather, marine life, visibility)
- Provide information about dive site difficulty and conditions
- Mention unique marine life and underwater features
- Include practical information (accessibility, typical costs)
- For specific booking or availability, recommend contacting dive operators
- Always consider safety and appropriate certification levels

TONE: Enthusiastic, helpful, and detail-oriented. Help divers discover amazing dive destinations that match their skill level and interests.
"""
        # Add diver profile context if available
        if context.diver_profile:
            cert_level = context.diver_profile.get("certification_level", "unknown")
            experience = context.diver_profile.get("dive_count", "unknown")
            system_prompt += f"\n\nDIVER PROFILE: Certification: {cert_level}, Experience: {experience} dives"

        messages.append(LLMMessage(role="system", content=system_prompt))

        # Conversation history
        for msg in context.conversation_history[-10:]:
            messages.append(LLMMessage(role=msg["role"], content=msg["content"]))

        # Current query (add context if available)
        query_text = context.query
        if context.rag_context:
            query_text = f"Destination Information:\n{context.rag_context}\n\nQuestion: {context.query}"

        messages.append(LLMMessage(role="user", content=query_text))

        return messages
