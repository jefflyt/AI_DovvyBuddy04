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

        # Simple, helpful prompt
        system_prompt = """You are DovvyBuddy, a friendly and knowledgeable scuba diving trip planner.

YOUR TASK:
Answer the user's question about diving destinations using the information provided below.

FORMATTING:
- Use bullet points (•) when listing dive sites
- Include any details mentioned: site names, depths, difficulty levels, marine life
- Be enthusiastic and helpful!

IMPORTANT:
- If you find specific dive site names in the information below, LIST THEM by name
- If you only find general descriptions, share what you know and offer to help plan their trip
- Always end with a helpful follow-up question like "When are you thinking of going?" or "What's your certification level?"
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
            logger.error(f"❌ TripAgent: NO RAG context provided! This will cause hallucination.")
            # Force NO_DATA response if no context
            query_text = f"NO_DATA\n\nQuestion: {context.query}"

        messages.append(LLMMessage(role="user", content=query_text))

        return messages
