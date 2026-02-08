"""
RAG pipeline orchestration.

Coordinates query embedding, retrieval, and context formatting.
"""

import logging
from typing import List, Optional

from app.core.config import settings

from .retriever import VectorRetriever
from .types import RAGContext, RetrievalOptions, RetrievalResult

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Orchestrates the RAG pipeline: query → embed → retrieve → format."""

    def __init__(self, retriever: Optional[VectorRetriever] = None):
        """
        Initialize RAG pipeline.

        Args:
            retriever: Vector retriever instance (if None, creates default)
        """
        self.retriever = retriever or VectorRetriever()
        self.enabled = settings.enable_rag

    async def retrieve_context(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_similarity: Optional[float] = None,
        filters: Optional[dict] = None,
    ) -> RAGContext:
        """
        Retrieve relevant context for a query.

        Args:
            query: User query
            top_k: Number of chunks to retrieve (default: from settings)
            min_similarity: Minimum similarity threshold (default: from settings)
            filters: Optional filters (doc_type, destination, tags)

        Returns:
            RAGContext with results and formatted context

        Raises:
            ValueError: If RAG is disabled or query is invalid
        """
        if not self.enabled:
            logger.warning("RAG is disabled, returning empty context")
            return RAGContext(
                query=query,
                results=[],
                formatted_context="NO_DATA",
                citations=[],
                has_data=False,
            )

        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        complexity = None
        if top_k is None:
            complexity = self._assess_query_complexity(query)
            if complexity == "skip":
                logger.info("Query complexity: skip, skipping RAG")
                return RAGContext(
                    query=query,
                    results=[],
                    formatted_context="NO_DATA",
                    citations=[],
                    has_data=False,
                )

        selected_top_k = top_k
        if selected_top_k is None and complexity:
            selected_top_k = 3 if complexity == "medium" else 5

        # Build retrieval options
        options = RetrievalOptions(
            top_k=selected_top_k or settings.rag_top_k,
            min_similarity=min_similarity or settings.rag_min_similarity,
            filters=filters or {},
        )

        if complexity:
            logger.info(f"Query complexity: {complexity}, using top_k={options.top_k}")

        # Retrieve chunks using hybrid or semantic search
        if settings.rag_use_hybrid:
            logger.info(f"Using hybrid search (keyword_weight={settings.rag_keyword_weight})")
            results = await self.retriever.retrieve_hybrid(
                query, 
                options,
                keyword_weight=settings.rag_keyword_weight
            )
        else:
            logger.info("Using semantic-only search")
            results = await self.retriever.retrieve(query, options)

        # Format context
        formatted_context = self._format_context(results)
        
        # Extract citations for RAF enforcement
        citations = [r.source_citation for r in results if r.source_citation]
        has_data = len(results) > 0

        # Log retrieval details for debugging
        if results:
            avg_similarity = sum(r.similarity for r in results) / len(results)
            max_similarity = max(r.similarity for r in results)
            logger.info(
                f"RAG pipeline: retrieved {len(results)} chunks for query '{query[:80]}...'"
                f" | avg_similarity={avg_similarity:.3f}, max_similarity={max_similarity:.3f}"
                f" | citations={len(citations)}"
            )
            # Log top result for debugging context issues
            if results:
                top_result = results[0]
                logger.debug(
                    f"Top RAG result: similarity={top_result.similarity:.3f}, "
                    f"source={top_result.source_citation}, text_preview={top_result.text[:100]}..."
                )
        else:
            logger.warning(f"RAG pipeline: NO results found for query: {query[:100]}...")

        return RAGContext(
            query=query,
            results=results,
            formatted_context=formatted_context,
            citations=citations,
            has_data=has_data,
        )

    def _format_context(self, results: List[RetrievalResult]) -> str:
        """
        Format retrieval results into context string.
        Returns NO_DATA signal when no results (RAF requirement).

        Args:
            results: List of retrieval results

        Returns:
            Formatted context string or NO_DATA signal
        """
        if not results:
            return "NO_DATA"  # Explicit signal for RAF enforcement

        # Format each chunk naturally without confusing labels
        formatted_chunks = []
        for result in results:
            # Just use the text content directly
            formatted_chunks.append(result.text)

        return "\n\n".join(formatted_chunks)

    def _assess_query_complexity(self, query: str) -> str:
        """
        Assess query complexity for dynamic top_k selection.

        Returns:
            "skip" | "medium" | "complex"
        """
        normalized = query.strip().lower()

        if not normalized:
            return "medium"

        skip_phrases = {
            "hi",
            "hello",
            "hey",
            "thanks",
            "thank you",
            "ok",
            "okay",
            "yes",
            "no",
        }

        if normalized in skip_phrases:
            return "skip"

        if any(phrase in normalized for phrase in [
            "can you repeat",
            "what do you mean",
            "clarify",
            "more detail",
            "say that again",
        ]):
            return "skip"

        complex_indicators = [
            "where can i",
            "best sites",
            "dive sites",
            "destination",
            "plan a trip",
            "plan trip",
            "recommend",
            "itinerary",
        ]

        if len(normalized) > 100:
            return "complex"

        if any(indicator in normalized for indicator in complex_indicators):
            return "complex"

        return "medium"

    async def retrieve_context_raw(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_similarity: Optional[float] = None,
        filters: Optional[dict] = None,
    ) -> List[RetrievalResult]:
        """
        Retrieve raw results without formatting.

        Args:
            query: User query
            top_k: Number of chunks to retrieve (default: from settings)
            min_similarity: Minimum similarity threshold (default: from settings)
            filters: Optional filters (doc_type, destination, tags)

        Returns:
            List of RetrievalResult objects

        Raises:
            ValueError: If RAG is disabled or query is invalid
        """
        context = await self.retrieve_context(query, top_k, min_similarity, filters)
        return context.results
