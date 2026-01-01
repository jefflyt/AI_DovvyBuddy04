"""
Vector retrieval service for RAG.

Performs vector similarity search using pgvector.
"""

import logging
from typing import List, Optional

from sqlalchemy import func, select, text, literal_column

from app.db.models.content_embedding import ContentEmbedding
from app.db.session import get_session
from app.services.embeddings import create_embedding_provider_from_env

from .types import RetrievalOptions, RetrievalResult

logger = logging.getLogger(__name__)


class VectorRetriever:
    """Retrieves relevant content chunks using vector similarity search."""

    def __init__(self, embedding_provider=None):
        """
        Initialize vector retriever.

        Args:
            embedding_provider: Embedding provider instance (if None, creates from env)
        """
        self.embedding_provider = (
            embedding_provider or create_embedding_provider_from_env()
        )

    async def retrieve(
        self,
        query: str,
        options: Optional[RetrievalOptions] = None,
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant content chunks based on query.

        Args:
            query: Search query
            options: Retrieval options (default: RetrievalOptions())

        Returns:
            List of RetrievalResult objects, sorted by similarity (descending)

        Raises:
            ValueError: If query is empty
            Exception: If database or API error occurs
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if options is None:
            options = RetrievalOptions()

        # Generate embedding for query
        logger.info(f"Generating embedding for query: {query[:100]}...")
        query_embedding = await self.embedding_provider.embed_text(query)

        # Convert to pgvector format (string)
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

        # Build query
        session_maker = get_session()
        async with session_maker() as session:
            # Base query with cosine similarity
            # Using pgvector <=> operator: cosine distance = 1 - cosine similarity
            similarity_expr = literal_column(f"1 - (embedding <=> '{embedding_str}'::vector)")
            
            stmt = select(
                ContentEmbedding.id,
                ContentEmbedding.content_path,
                ContentEmbedding.chunk_text,
                ContentEmbedding.metadata_,
                similarity_expr.label("similarity"),
            )

            # Apply filters
            if options.filters:
                if "doc_type" in options.filters:
                    doc_type = options.filters["doc_type"]
                    if isinstance(doc_type, list):
                        stmt = stmt.where(
                            ContentEmbedding.metadata_["doc_type"].astext.in_(doc_type)
                        )
                    else:
                        stmt = stmt.where(
                            ContentEmbedding.metadata_["doc_type"].astext == doc_type
                        )

                if "destination" in options.filters:
                    stmt = stmt.where(
                        ContentEmbedding.metadata_["destination"].astext
                        == options.filters["destination"]
                    )

                if "tags" in options.filters and options.filters["tags"]:
                    # Check if any of the specified tags exist in metadata->tags array
                    for tag in options.filters["tags"]:
                        stmt = stmt.where(
                            ContentEmbedding.metadata_["tags"]
                            .astext.contains(f'"{tag}"')
                        )

            # Order by similarity and limit
            stmt = stmt.order_by(text("similarity DESC")).limit(options.top_k)

            # Execute query
            result = await session.execute(stmt)
            rows = result.all()

            # Convert to RetrievalResult
            results = []
            for row in rows:
                similarity = float(row.similarity)

                # Filter by minimum similarity
                if similarity < options.min_similarity:
                    continue

                results.append(
                    RetrievalResult(
                        chunk_id=str(row.id),
                        text=row.chunk_text,
                        similarity=similarity,
                        metadata=row.metadata_ or {},
                    )
                )

            logger.info(
                f"Retrieved {len(results)} chunks (filtered from {len(rows)} by min_similarity={options.min_similarity})"
            )

            return results
