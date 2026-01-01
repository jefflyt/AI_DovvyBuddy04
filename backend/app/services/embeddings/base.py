"""
Base interface for embedding providers.

Defines the contract that all embedding providers must implement.
"""

from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    """Abstract base class for embedding generation providers."""

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """
        Generate an embedding vector for a single text.

        Args:
            text: The text to embed

        Returns:
            List of floats representing the embedding vector

        Raises:
            ValueError: If text is empty or invalid
            Exception: If API call fails after retries
        """
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts in a batch.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors, one per input text

        Raises:
            ValueError: If texts list is empty or contains invalid texts
            Exception: If API call fails after retries
        """
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get the dimension of embeddings produced by this provider.

        Returns:
            Integer dimension (e.g., 768 for text-embedding-004)
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name of the embedding model.

        Returns:
            String model name (e.g., "text-embedding-004")
        """
        pass
