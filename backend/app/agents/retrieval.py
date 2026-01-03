"""
Retrieval agent for RAG-based information retrieval.
"""

import logging
from typing import Optional

from app.services.llm.base import LLMProvider
from app.services.llm.factory import create_llm_provider
from app.services.llm.types import LLMMessage
from app.services.rag.pipeline import RAGPipeline

from .base import Agent, AgentResult
from .types import AgentCapability, AgentContext, AgentType

logger = logging.getLogger(__name__)


class RetrievalAgent(Agent):
    """Agent for RAG-based information retrieval and general queries."""

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        rag_pipeline: Optional[RAGPipeline] = None,
    ):
        """
        Initialize retrieval agent.

        Args:
            llm_provider: LLM provider (if None, creates default)
            rag_pipeline: RAG pipeline (if None, creates default)
        """
        super().__init__(
            agent_type=AgentType.RETRIEVAL,
            name="Retrieval Agent",
            description="Retrieves relevant information using RAG and generates responses",
            capabilities=[AgentCapability.RAG_RETRIEVAL, AgentCapability.GENERAL_CONVERSATION],
        )
        self.llm_provider = llm_provider or create_llm_provider()
        self.rag_pipeline = rag_pipeline or RAGPipeline()

    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute retrieval agent.

        Args:
            context: Agent context with query

        Returns:
            AgentResult with RAG-enhanced response
        """
        try:
            # Use RAG context if provided, otherwise retrieve
            if context.rag_context:
                rag_context_str = context.rag_context
            else:
                rag_result = await self.rag_pipeline.retrieve_context(context.query)
                rag_context_str = rag_result.formatted_context

            # Build messages with context
            messages = self._build_messages(context, rag_context_str)

            # Generate response
            response = await self.llm_provider.generate(messages)

            result = AgentResult(
                response=response.content,
                agent_type=self.agent_type,
                confidence=0.8,
                metadata={
                    "model": response.model,
                    "tokens_used": response.tokens_used,
                    "has_rag_context": bool(rag_context_str),
                },
            )

            self._log_execution(context, result)
            return result

        except Exception as e:
            return await self._handle_error(context, e)

    def _build_messages(self, context: AgentContext, rag_context: str) -> list:
        """
        Build message list for LLM.

        Args:
            context: Agent context
            rag_context: RAG retrieval context

        Returns:
            List of LLMMessage objects
        """
        messages = []

        # System prompt
        system_prompt = self._build_system_prompt(rag_context)
        messages.append(LLMMessage(role="system", content=system_prompt))

        # Conversation history
        for msg in context.conversation_history[-10:]:  # Last 10 messages
            messages.append(
                LLMMessage(
                    role=msg["role"],
                    content=msg["content"]
                )
            )

        # Current query
        messages.append(LLMMessage(role="user", content=context.query))

        return messages

    def _build_system_prompt(self, rag_context: str) -> str:
        """
        Build system prompt with RAG context.

        Args:
            rag_context: Retrieved context from RAG

        Returns:
            System prompt string
        """
        base_prompt = """You are DovvyBuddy, an expert AI assistant for scuba diving enthusiasts.
Your role is to provide accurate, helpful information about diving destinations, certifications, safety, and equipment.

IMPORTANT GUIDELINES:
- Be friendly, knowledgeable, and safety-conscious
- Always prioritize diver safety in your responses
- For medical questions, advise consulting medical professionals
- For certification questions, recommend contacting official agencies (PADI, SSI, etc.)
- Use the provided context to give accurate, specific information
- If you don't know something, say so honestly

"""
        if rag_context:
            base_prompt += f"""
RELEVANT INFORMATION:
{rag_context}

Use the above information to answer the user's question accurately. If the information doesn't cover the question, provide general guidance based on your diving knowledge.
"""

        return base_prompt
