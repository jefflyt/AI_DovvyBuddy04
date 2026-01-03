"""RAG repository for database operations on embeddings."""

from typing import Any, Dict, List, Optional

from sqlalchemy import delete, func, select, text
from sqlalchemy.orm import Session

from app.db.models import ContentEmbedding


class RAGRepository:
    """Repository for RAG-related database operations."""
    
    def __init__(self, db: Session):
        """Initialize repository with database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def insert_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """Insert embedding chunks into database.
        
        Args:
            chunks: List of chunk dictionaries with text, embedding, and metadata
        """
        for chunk in chunks:
            embedding_obj = ContentEmbedding(
                content=chunk["text"],
                embedding=chunk["embedding"],
                metadata_=chunk.get("metadata", {}),
            )
            self.db.add(embedding_obj)
        
        self.db.commit()
    
    def delete_by_content_path(self, content_path: str) -> int:
        """Delete all embeddings for a given content path.
        
        Args:
            content_path: Content path to delete embeddings for
            
        Returns:
            Number of embeddings deleted
        """
        stmt = delete(ContentEmbedding).where(
            ContentEmbedding.metadata_["content_path"].astext == content_path
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount
    
    def delete_by_pattern(self, pattern: str) -> int:
        """Delete embeddings matching a content path pattern.
        
        Args:
            pattern: SQL LIKE pattern (e.g., 'certifications/%')
            
        Returns:
            Number of embeddings deleted
        """
        stmt = delete(ContentEmbedding).where(
            ContentEmbedding.metadata_["content_path"].astext.like(pattern)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount
    
    def delete_all(self) -> int:
        """Delete all embeddings from database.
        
        Returns:
            Number of embeddings deleted
        """
        stmt = delete(ContentEmbedding)
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount
    
    def count_all(self) -> int:
        """Count total number of embeddings.
        
        Returns:
            Total embedding count
        """
        stmt = select(func.count()).select_from(ContentEmbedding)
        result = self.db.execute(stmt)
        return result.scalar() or 0
    
    def count_by_pattern(self, pattern: str) -> int:
        """Count embeddings matching a content path pattern.
        
        Args:
            pattern: SQL LIKE pattern (e.g., 'certifications/%')
            
        Returns:
            Number of matching embeddings
        """
        stmt = select(func.count()).select_from(ContentEmbedding).where(
            ContentEmbedding.metadata_["content_path"].astext.like(pattern)
        )
        result = self.db.execute(stmt)
        return result.scalar() or 0
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all embeddings from database.
        
        Returns:
            List of embedding dictionaries
        """
        stmt = select(ContentEmbedding)
        result = self.db.execute(stmt)
        embeddings = result.scalars().all()
        
        return [
            {
                "id": emb.id,
                "text": emb.content,
                "embedding": emb.embedding,
                "metadata": emb.metadata_,
            }
            for emb in embeddings
        ]
    
    def search_by_metadata(
        self,
        metadata_filter: Dict[str, Any],
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search embeddings by metadata filter.
        
        Args:
            metadata_filter: Dictionary of metadata key-value pairs to match
            limit: Maximum number of results
            
        Returns:
            List of matching embedding dictionaries
        """
        stmt = select(ContentEmbedding)
        
        # Apply metadata filters
        for key, value in metadata_filter.items():
            stmt = stmt.where(ContentEmbedding.metadata_[key].astext == str(value))
        
        stmt = stmt.limit(limit)
        
        result = self.db.execute(stmt)
        embeddings = result.scalars().all()
        
        return [
            {
                "id": emb.id,
                "text": emb.content,
                "embedding": emb.embedding,
                "metadata": emb.metadata_,
            }
            for emb in embeddings
        ]
    
    def search_by_similarity(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        similarity_threshold: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Search embeddings by vector similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of results with text, metadata, and similarity score
        """
        # Use pgvector's cosine similarity operator
        stmt = text("""
            SELECT 
                id,
                content,
                metadata_,
                1 - (embedding <=> :query_embedding::vector) as similarity
            FROM content_embeddings
            WHERE 1 - (embedding <=> :query_embedding::vector) >= :threshold
            ORDER BY embedding <=> :query_embedding::vector
            LIMIT :top_k
        """)
        
        result = self.db.execute(
            stmt,
            {
                "query_embedding": query_embedding,
                "threshold": similarity_threshold,
                "top_k": top_k,
            }
        )
        
        return [
            {
                "id": row.id,
                "text": row.content,
                "metadata": row.metadata_,
                "similarity": float(row.similarity),
            }
            for row in result
        ]
