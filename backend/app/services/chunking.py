"""Service wrappers for content processing scripts."""

from typing import Any, Dict, List

from app.services.embeddings import create_embedding_provider_from_env
from app.services.rag import chunk_text


class ChunkingService:
    """Wrapper service for text chunking."""
    
    def chunk_text(
        self,
        text: str,
        metadata: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Chunk text into smaller segments.
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Use the RAG chunker
        chunks = chunk_text(text)
        
        # Add metadata to each chunk
        return [
            {
                "text": chunk,
                "metadata": {**metadata},
            }
            for chunk in chunks
        ]


class EmbeddingService:
    """Wrapper service for embedding generation."""
    
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
