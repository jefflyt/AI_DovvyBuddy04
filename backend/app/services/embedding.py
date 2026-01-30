"""Embedding service for content processing scripts."""

from typing import List

from app.services.embeddings import create_embedding_provider_from_env


class EmbeddingService:
    """Service for generating embeddings."""
    
    def __init__(self):
        """Initialize embedding service."""
        self.provider = create_embedding_provider_from_env()
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        return self.provider.embed_batch(texts)
