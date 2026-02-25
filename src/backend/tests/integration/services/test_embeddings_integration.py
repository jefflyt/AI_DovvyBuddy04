"""
Integration tests for embedding provider.

Tests real API calls (marked as slow for CI).
"""

import pytest
import os

from app.services.embeddings import GeminiEmbeddingProvider
from app.core.config import settings


pytestmark = pytest.mark.slow


@pytest.fixture
def gemini_api_key():
    """Get Gemini API key from environment."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        pytest.skip("GEMINI_API_KEY not set")
    return key


@pytest.fixture
def provider(gemini_api_key):
    """Create real Gemini embedding provider."""
    return GeminiEmbeddingProvider(
        api_key=gemini_api_key,
        model=settings.embedding_model,
        use_cache=False
    )


@pytest.mark.asyncio
async def test_real_embed_text(provider):
    """Test real embedding generation."""
    text = "What is PADI Open Water certification?"

    embedding = await provider.embed_text(text)

    assert isinstance(embedding, list)
    assert len(embedding) == provider.dimension
    assert all(isinstance(x, float) for x in embedding)
    assert any(x != 0.0 for x in embedding)  # Not all zeros


@pytest.mark.asyncio
async def test_real_embed_batch(provider):
    """Test real batch embedding generation."""
    texts = [
        "What is PADI Open Water certification?",
        "How deep can I dive with Open Water?",
        "What equipment do I need for diving?",
    ]

    embeddings = await provider.embed_batch(texts)

    assert len(embeddings) == 3
    assert all(len(emb) == provider.dimension for emb in embeddings)
    # Verify embeddings are different
    assert embeddings[0] != embeddings[1]
    assert embeddings[1] != embeddings[2]


@pytest.mark.asyncio
async def test_cache_behavior(gemini_api_key):
    """Test that cache reduces API calls."""
    provider = GeminiEmbeddingProvider(
        api_key=gemini_api_key,
        model=settings.embedding_model,
        use_cache=True
    )
    text = "Test caching behavior"

    # First call - cache miss
    embedding1 = await provider.embed_text(text)
    stats1 = provider.cache.get_stats()
    assert stats1["misses"] == 1
    assert stats1["hits"] == 0

    # Second call - cache hit
    embedding2 = await provider.embed_text(text)
    stats2 = provider.cache.get_stats()
    assert stats2["hits"] == 1
    assert embedding1 == embedding2
