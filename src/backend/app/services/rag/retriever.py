"""
Vector retrieval service for RAG.

Performs vector similarity search using pgvector.
"""

import logging
from typing import List, Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import bindparam, func, select, text

from app.core.config import settings
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
        self._result_cache = {}  # Cache for RRF merging

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

        expected_dimension = settings.embedding_dimension
        if len(query_embedding) != expected_dimension:
            raise ValueError(
                f"Expected embedding dimension {expected_dimension}, got {len(query_embedding)}"
            )

        # Build query
        session_maker = get_session()
        async with session_maker() as session:
            # Base query with cosine similarity
            # Using pgvector <=> operator: cosine distance = 1 - cosine similarity
            query_vector = bindparam(
                "query_embedding",
                value=query_embedding,
                type_=Vector(expected_dimension),
            )
            similarity_expr = (
                1 - ContentEmbedding.embedding.cosine_distance(query_vector)
            )

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

                # Extract metadata and citation
                metadata = row.metadata_ or {}
                source_citation = metadata.get("content_path")

                results.append(
                    RetrievalResult(
                        chunk_id=str(row.id),
                        text=row.chunk_text,
                        similarity=similarity,
                        metadata=metadata,
                        source_citation=source_citation,
                    )
                )

            logger.info(
                f"Retrieved {len(results)} chunks (filtered from {len(rows)} by min_similarity={options.min_similarity})"
            )

            return results

    async def retrieve_hybrid(
        self,
        query: str,
        options: Optional[RetrievalOptions] = None,
        keyword_weight: float = 0.3,
    ) -> List[RetrievalResult]:
        """
        Hybrid search combining keyword + semantic search.
        
        Args:
            query: Search query
            options: Retrieval options (default: RetrievalOptions())
            keyword_weight: Weight for keyword results (0-1, default: 0.3)
        
        Returns:
            Merged and re-ranked results using Reciprocal Rank Fusion
        """
        if options is None:
            options = RetrievalOptions()
        
        # Clear cache for new query
        self._result_cache = {}
        
        # 1. Semantic search (existing method)
        logger.info(f"Hybrid search: Running semantic search for '{query[:50]}...'")
        semantic_results = await self.retrieve(query, options)
        
        # 2. Keyword search (new)
        logger.info(f"Hybrid search: Running keyword search for '{query[:50]}...'")
        keyword_results = await self._keyword_search(query, options)
        
        # 3. Merge using Reciprocal Rank Fusion
        logger.info(f"Hybrid search: Merging {len(semantic_results)} semantic + {len(keyword_results)} keyword results")
        merged_results = self._merge_rrf(
            semantic_results, 
            keyword_results,
            keyword_weight
        )
        
        # Return top-k results
        final_results = merged_results[:options.top_k]
        logger.info(f"Hybrid search: Returning {len(final_results)} merged results")
        
        return final_results

    async def _keyword_search(
        self,
        query: str,
        options: RetrievalOptions,
    ) -> List[RetrievalResult]:
        """
        Full-text search using PostgreSQL tsvector.
        
        Args:
            query: Search query
            options: Retrieval options
        
        Returns:
            List of results ranked by FTS relevance
        """
        if not query or not query.strip():
            return []
        
        session_maker = get_session()
        async with session_maker() as session:
            # Use ts_rank for relevance scoring
            stmt = select(
                ContentEmbedding.id,
                ContentEmbedding.content_path,
                ContentEmbedding.chunk_text,
                ContentEmbedding.metadata_,
                func.ts_rank(
                    ContentEmbedding.chunk_text_tsv,
                    func.plainto_tsquery('english', query)
                ).label("rank")
            ).where(
                ContentEmbedding.chunk_text_tsv.op('@@')(
                    func.plainto_tsquery('english', query)
                )
            )
            
            # Apply metadata filters if present
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
            
            stmt = stmt.order_by(text("rank DESC")).limit(options.top_k * 2)
            
            result = await session.execute(stmt)
            rows = result.all()
            
            results = [
                RetrievalResult(
                    chunk_id=str(row.id),
                    text=row.chunk_text,
                    similarity=float(row.rank),  # Use FTS rank as similarity
                    metadata=row.metadata_ or {},
                    source_citation=(row.metadata_ or {}).get("content_path")
                )
                for row in rows
            ]
            
            logger.info(f"Keyword search found {len(results)} results")
            return results

    def _merge_rrf(
        self,
        semantic_results: List[RetrievalResult],
        keyword_results: List[RetrievalResult],
        keyword_weight: float = 0.3,
        k: int = 60,
    ) -> List[RetrievalResult]:
        """
        Merge results using Reciprocal Rank Fusion.
        
        RRF formula: score = Σ(weight / (k + rank))
        
        Args:
            semantic_results: Results from semantic search
            keyword_results: Results from keyword search
            keyword_weight: Weight for keyword results (0-1)
            k: RRF constant (default: 60)
        
        Returns:
            Merged and re-ranked results
        """
        scores = {}
        semantic_weight = 1 - keyword_weight
        
        # Score semantic results
        for rank, result in enumerate(semantic_results, 1):
            chunk_id = result.chunk_id
            scores[chunk_id] = scores.get(chunk_id, 0) + semantic_weight / (k + rank)
            if chunk_id not in self._result_cache:
                self._result_cache[chunk_id] = result
        
        # Score keyword results
        for rank, result in enumerate(keyword_results, 1):
            chunk_id = result.chunk_id
            scores[chunk_id] = scores.get(chunk_id, 0) + keyword_weight / (k + rank)
            if chunk_id not in self._result_cache:
                self._result_cache[chunk_id] = result
        
        # Sort by combined score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        # Return merged results with updated similarity scores
        merged = []
        for chunk_id in sorted_ids:
            result = self._result_cache[chunk_id]
            # Create new result with RRF score
            merged_result = RetrievalResult(
                chunk_id=result.chunk_id,
                text=result.text,
                similarity=scores[chunk_id],  # Use RRF score
                metadata=result.metadata,
                source_citation=result.source_citation
            )
            merged.append(merged_result)
        
        return merged
