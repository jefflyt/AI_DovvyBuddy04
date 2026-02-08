"""
Retrieval agent for RAG-based information retrieval.
"""

import logging
from typing import Optional

from app.services.llm.base import LLMProvider
from app.services.llm.factory import create_llm_provider
from app.services.llm.types import LLMMessage
from app.services.rag.pipeline import RAGPipeline
from app.core.config import settings
from app.prompts.rag import RAG_SYSTEM_PROMPT, NO_RAG_PROMPT

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
        # Use default model from settings (single source of truth)
        self.llm_provider = llm_provider or create_llm_provider(
            provider_name=settings.default_llm_provider,
            temperature=0.7
        )
        self.rag_pipeline = rag_pipeline or RAGPipeline()

    def get_tool_definition(self) -> dict:
        """Define knowledge base tool for Gemini."""
        return {
            "name": "knowledge_base",
            "description": "Retrieve information about diving certifications, safety, equipment, marine life, or general FAQs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's question"
                    },
                    "topic": {
                        "type": "string",
                        "description": "The general topic (e.g., 'safety', 'equipment', 'certification')"
                    }
                },
                "required": ["query"]
            }
        }

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
            rag_context = None
            has_citations = False
            
            if context.rag_context:
                rag_context_str = context.rag_context
                # Check if NO_DATA signal present (RAF requirement)
                if rag_context_str == "NO_DATA":
                    return self._handle_no_data(context)
                has_citations = True
            else:
                rag_result = await self.rag_pipeline.retrieve_context(context.query)
                rag_context_str = rag_result.formatted_context
                
                # Check NO_DATA signal (RAF requirement)
                if rag_context_str == "NO_DATA" or not rag_result.has_data:
                    return self._handle_no_data(context)
                    
                has_citations = len(rag_result.citations) > 0
                rag_context = rag_result

            # Build messages with context
            messages = self._build_messages(context, rag_context_str)

            # Generate response
            response = await self.llm_provider.generate(messages)

            result = AgentResult(
                response=response.content,
                agent_type=self.agent_type,
                confidence=0.8 if has_citations else 0.5,
                metadata={
                    "model": response.model,
                    "tokens_used": response.tokens_used,
                    "prompt_tokens": response.prompt_tokens,
                    "completion_tokens": response.completion_tokens,
                    "cost_usd": response.cost_usd,
                    "has_rag_context": bool(rag_context_str),
                    "has_citations": has_citations,
                    "citations": rag_context.citations if rag_context else [],
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

        # Conversation history (recent context for continuity)
        for msg in context.conversation_history[-6:]:  # Last 3 turns (6 messages)
            messages.append(
                LLMMessage(
                    role=msg["role"],
                    content=msg["content"]
                )
            )

        # Current query (last message gets priority)
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
        if rag_context and rag_context != "NO_DATA":
            return RAG_SYSTEM_PROMPT.format(context=rag_context)
        else:
            return NO_RAG_PROMPT

    def _handle_no_data(self, context: AgentContext) -> AgentResult:
        """
        Handle NO_DATA signal from RAG (RAF requirement).
        
        When no relevant grounding data is found, refuse to answer factual
        questions rather than hallucinating.

        Args:
            context: Agent context

        Returns:
            AgentResult with appropriate no-data response
        """
        response = """I don't have specific information about that in my knowledge base. 

To ensure I provide you with accurate information, I can only answer based on verified content. 

Could you try:
- Rephrasing your question
- Asking about a different topic
- Or let me know if you'd like general guidance instead of specific facts

What would be most helpful for you?"""
        
        return AgentResult(
            response=response,
            agent_type=self.agent_type,
            confidence=0.0,
            metadata={
                "no_data": True,
                "raf_enforced": True,
            },
        )
