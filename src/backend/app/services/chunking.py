"""Service wrappers for content processing scripts."""

import asyncio
from typing import Any, Dict, List

from app.services.embeddings import create_embedding_provider_from_env
from app.services.rag import chunk_text


class ChunkingService:
    """Wrapper service for text chunking."""
    
    def chunk_text(
        self,
        text: str,
        metadata: Dict[str, Any],
        content_path: str = "",
    ) -> List[Dict[str, Any]]:
        """Chunk text into smaller segments.
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            content_path: Path to content file for metadata
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Use the RAG chunker - it returns ContentChunk objects
        chunks = chunk_text(text, content_path, frontmatter=metadata)
        
        # Convert ContentChunk objects to dictionaries
        return [
            {
                "text": chunk.text,
                "metadata": chunk.metadata,
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
        # Run async method in sync context using asyncio.run()
        try:
            return asyncio.run(self.provider.embed_batch(texts))
        except RuntimeError:
            # If there's already an event loop running, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.provider.embed_batch(texts))
            finally:
                loop.close()
                asyncio.set_event_loop(None)
