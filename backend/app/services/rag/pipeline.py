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

        # Build retrieval options
        options = RetrievalOptions(
            top_k=top_k or settings.rag_top_k,
            min_similarity=min_similarity or settings.rag_min_similarity,
            filters=filters or {},
        )

        # Retrieve chunks
        results = await self.retriever.retrieve(query, options)

        # Format context
        formatted_context = self._format_context(results)
        
        # Extract citations for RAF enforcement
        citations = [r.source_citation for r in results if r.source_citation]
        has_data = len(results) > 0

        logger.info(
            f"RAG pipeline: retrieved {len(results)} chunks, {len(citations)} citations for query: {query[:100]}..."
        )

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

        # Format each chunk with citation metadata for RAF
        formatted_chunks = []
        for i, result in enumerate(results, 1):
            # Extract useful metadata
            metadata = result.metadata
            doc_type = metadata.get("doc_type", "")
            section = metadata.get("section_header", "")
            citation = result.source_citation or "unknown"
            destination = metadata.get("destination", "")

            # Build context header
            header_parts = []
            if doc_type:
                header_parts.append(f"Type: {doc_type}")
            if destination:
                header_parts.append(f"Destination: {destination}")
            if section:
                header_parts.append(f"Section: {section}")

            header = f"[Context {i}" + (f" - {', '.join(header_parts)}" if header_parts else "") + "]"

            # Format chunk
            formatted_chunks.append(f"{header}\n{result.text}")

        return "\n\n---\n\n".join(formatted_chunks)

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
