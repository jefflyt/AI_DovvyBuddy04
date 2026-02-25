"""
Embedding services for generating and caching vector embeddings.
"""

from .base import EmbeddingProvider
from .factory import create_embedding_provider, create_embedding_provider_from_env
from .gemini import GeminiEmbeddingProvider

__all__ = [
    "EmbeddingProvider",
    "GeminiEmbeddingProvider",
    "create_embedding_provider",
    "create_embedding_provider_from_env",
]
