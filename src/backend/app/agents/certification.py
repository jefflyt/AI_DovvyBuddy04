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
        system_prompt = """You are DovvyBuddy's Certification Expert. Provide SHORT, conversational answers (2-4 paragraphs max).

Your expertise: PADI/SSI certifications, prerequisites, training pathways.

IMPORTANT FORMATTING:
- Write in plain text, NO markdown, NO bullet points, NO asterisks
- Use natural paragraphs with proper spacing
- Keep responses concise and conversational
- Emphasize key certification names naturally in the text

Guidelines:
- Give clear, practical certification guidance
- Compare PADI/SSI when relevant
- Mention prerequisites briefly
- Always note: verify details with certified instructors
- For medical questions: consult diving medical professional

RESPONSE DISCIPLINE (CRITICAL):
- Default length: 3-5 sentences OR ≤120 tokens (whichever comes first)
- Address ONE primary idea per response
- NEVER mention: "provided context", "source", "filename", "document", "retrieval", "according to the context", bracketed references [Source: ...]
- If information is insufficient, ask a clarifying question instead
- Style: Professional, direct, calm. No fluff, no cheerleading, no repetition
- Avoid generic closers like "Let me know if you need anything else"
- Safety notes: ONE sentence max (unless emergency override)

Tone: Friendly, encouraging, concise.
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
