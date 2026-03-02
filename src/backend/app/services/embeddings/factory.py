"""
Factory for creating embedding provider instances.

Provides convenient methods to create providers from configuration.
"""

import logging
from typing import Optional

from app.core.config import settings

from .base import EmbeddingProvider
from .gemini import GeminiEmbeddingProvider

logger = logging.getLogger(__name__)


def create_embedding_provider(
    provider_name: str = "gemini",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    dimension: Optional[int] = None,
    use_cache: bool = True,
) -> EmbeddingProvider:
    """
    Create an embedding provider instance.

    Args:
        provider_name: Name of the provider ("gemini")
        api_key: API key (if None, uses from settings)
        model: Model name (if None, uses from settings)
        dimension: Target output dimension for Matryoshka truncation (if None, uses from settings)
        use_cache: Whether to enable caching

    Returns:
        EmbeddingProvider instance

    Raises:
        ValueError: If provider is unknown or API key is missing
    """
    provider_name = provider_name.lower()

    if provider_name == "gemini":
        key = api_key or settings.gemini_api_key
        if not key:
            raise ValueError("Gemini API key is required (GEMINI_API_KEY env var)")

        model_name = model or settings.embedding_model
        target_dimension = dimension if dimension is not None else settings.embedding_dimension

        logger.info(f"Creating Gemini embedding provider with model={model_name}, dimension={target_dimension}")
        return GeminiEmbeddingProvider(
            api_key=key,
            model=model_name,
            dimension=target_dimension,
            use_cache=use_cache
        )

    else:
        raise ValueError(f"Unknown embedding provider: {provider_name}")


def create_embedding_provider_from_env() -> EmbeddingProvider:
    """
    Create an embedding provider from environment configuration.

    Returns:
        EmbeddingProvider instance configured from settings

    Raises:
        ValueError: If configuration is invalid
    """
    # Currently only Gemini is supported
    return create_embedding_provider(
        provider_name=settings.default_embedding_provider,
        api_key=settings.gemini_api_key,
        model=settings.embedding_model,
        dimension=settings.embedding_dimension,
        use_cache=True,
    )
