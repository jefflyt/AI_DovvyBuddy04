"""
Context builder for orchestration.
"""

import logging
from typing import List, Optional

from app.agents.types import AgentContext
from app.services.rag.pipeline import RAGPipeline

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builds agent context from conversation and RAG results."""

    def __init__(self, rag_pipeline: Optional[RAGPipeline] = None):
        """
        Initialize context builder.

        Args:
            rag_pipeline: RAG pipeline for retrieval (if None, creates default)
        """
        self.rag_pipeline = rag_pipeline or RAGPipeline()

    async def build_context(
        self,
        query: str,
        conversation_history: List[dict],
        diver_profile: Optional[dict] = None,
        use_rag: bool = True,
    ) -> AgentContext:
        """
        Build agent context.

        Args:
            query: User query
            conversation_history: Previous conversation messages
            diver_profile: Optional diver profile data
            use_rag: Whether to use RAG retrieval

        Returns:
            AgentContext with query, history, and RAG results
        """
        # Retrieve RAG context if enabled
        rag_context = None
        rag_citations = []
        if use_rag and self.rag_pipeline.enabled:
            try:
                logger.info(f"🔍 RAG ENABLED - Retrieving context for: {query[:100]}")
                rag_result = await self.rag_pipeline.retrieve_context(query)
                rag_context = rag_result.formatted_context
                rag_citations = rag_result.citations  # PR6.2: Extract citations
                logger.info(f"✓ Retrieved {len(rag_result.results)} RAG chunks, context length: {len(rag_context) if rag_context else 0}")
                if rag_result.results:
                    logger.info(f"  First result: {rag_result.results[0].text[:100]}...")
                else:
                    logger.warning("⚠️ RAG returned NO results!")
            except Exception as e:
                logger.error(f"❌ RAG retrieval FAILED: {e}", exc_info=True)
                rag_context = None
                rag_citations = []
        else:
            logger.warning(f"⚠️ RAG NOT ENABLED: use_rag={use_rag}, pipeline.enabled={self.rag_pipeline.enabled}")

        # Build context
        context = AgentContext(
            query=query,
            conversation_history=conversation_history,
            diver_profile=diver_profile,
            rag_context=rag_context,
            metadata={
                "has_rag": bool(rag_context),
                "rag_citations": rag_citations,  # PR6.2: Pass citations through metadata
                "history_length": len(conversation_history),
            },
        )

        return context

    def trim_history(
        self,
        conversation_history: List[dict],
        max_messages: int = 20
    ) -> List[dict]:
        """
        Trim conversation history to last N messages.

        Args:
            conversation_history: Full conversation history
            max_messages: Maximum messages to keep

        Returns:
            Trimmed conversation history
        """
        if len(conversation_history) <= max_messages:
            return conversation_history

        trimmed = conversation_history[-max_messages:]
        logger.info(
            f"Trimmed conversation history: {len(conversation_history)} -> {len(trimmed)}"
        )
        return trimmed
