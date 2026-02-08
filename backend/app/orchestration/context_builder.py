"""
Context builder for orchestration.
"""

import logging
from typing import List, Optional

from app.agents.types import AgentContext
from app.core.config import settings
from app.services.rag.pipeline import RAGPipeline
from app.services.rag.token_utils import count_tokens

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
        rag_tokens = None
        if use_rag and self.rag_pipeline.enabled:
            try:
                logger.info(f"🔍 RAG ENABLED - Retrieving context for: {query[:100]}")
                rag_result = await self.rag_pipeline.retrieve_context(query)
                rag_context = rag_result.formatted_context
                rag_citations = rag_result.citations  # PR6.2: Extract citations
                logger.info(f"✓ Retrieved {len(rag_result.results)} RAG chunks, context length: {len(rag_context) if rag_context else 0}")
                if rag_context and rag_context != "NO_DATA":
                    rag_tokens = count_tokens(rag_context)
                    logger.info(
                        "RAG context prepared: chunks=%s, rag_tokens=%s",
                        len(rag_result.results),
                        rag_tokens,
                    )
                if rag_result.results:
                    logger.info(f"  First result: {rag_result.results[0].text[:100]}...")
                else:
                    logger.warning("⚠️ RAG returned NO results!")
            except Exception as e:
                logger.error(f"❌ RAG retrieval FAILED: {e}", exc_info=True)
                rag_context = None
                rag_citations = []
                rag_tokens = None
        else:
            logger.warning(f"⚠️ RAG NOT ENABLED: use_rag={use_rag}, pipeline.enabled={self.rag_pipeline.enabled}")

        recent_history = conversation_history[-6:]
        trimmed_history, history_tokens = self._truncate_history_by_tokens(
            recent_history,
            settings.max_history_tokens,
        )

        # Build context
        context = AgentContext(
            query=query,
            conversation_history=trimmed_history,
            diver_profile=diver_profile,
            rag_context=rag_context,
            metadata={
                "has_rag": bool(rag_context),
                "rag_citations": rag_citations,  # PR6.2: Pass citations through metadata
                "rag_tokens": rag_tokens,
                "history_length": len(trimmed_history),
                "history_tokens": history_tokens,
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

    def _truncate_history_by_tokens(
        self,
        history: List[dict],
        max_tokens: int,
    ) -> tuple[List[dict], int]:
        """
        Truncate conversation history by token budget.

        Args:
            history: List of messages
            max_tokens: Token budget

        Returns:
            Tuple of (trimmed history, token count)
        """
        if not history:
            return [], 0

        kept: List[dict] = []
        total_tokens = 0

        for msg in reversed(history):
            role = msg.get("role", "")
            content = msg.get("content", "")
            message_tokens = count_tokens(f"{role}: {content}")

            if total_tokens + message_tokens > max_tokens:
                break

            kept.append(msg)
            total_tokens += message_tokens

        trimmed = list(reversed(kept))
        logger.info(
            "History truncated: %s/%s messages, %s tokens",
            len(trimmed),
            len(history),
            total_tokens,
        )
        return trimmed, total_tokens
