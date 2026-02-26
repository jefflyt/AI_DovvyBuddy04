"""
Unit tests for embedding provider.

Tests embedding generation with mocked API calls.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.embeddings import GeminiEmbeddingProvider
from app.services.embeddings.cache import EmbeddingCache
from app.services.embeddings.gemini import RateLimitError


@pytest.fixture
def mock_embedding():
    """Mock embedding vector (768 dimensions)."""
    return [0.1] * 768


@pytest.fixture
def gemini_provider():
    """Create a Gemini embedding provider with mocked API."""
    with patch("google.genai.Client"):
        provider = GeminiEmbeddingProvider(api_key="test-key", use_cache=False)
        return provider


class TestGeminiEmbeddingProvider:
    """Test Gemini embedding provider."""

    def test_initialization(self):
        """Test provider initialization."""
        with patch("google.genai.Client"):
            provider = GeminiEmbeddingProvider(api_key="test-key")
            assert provider.model == "text-embedding-004"
            assert provider.dimension == 768
            assert provider.cache is not None

    def test_initialization_with_matryoshka_dimension(self):
        """Test provider initialization with Matryoshka truncation."""
        with patch("google.genai.Client"):
            # Valid truncation dimension
            provider = GeminiEmbeddingProvider(api_key="test-key", dimension=512)
            assert provider.dimension == 512
            
            # Invalid dimension should fall back to native
            provider = GeminiEmbeddingProvider(api_key="test-key", dimension=999)
            assert provider.dimension == 768
            
            # Explicit None should use native
            provider = GeminiEmbeddingProvider(api_key="test-key", dimension=None)
            assert provider.dimension == 768

    def test_initialization_without_api_key(self):
        """Test that initialization fails without API key."""
        with pytest.raises(ValueError, match="API key is required"):
            GeminiEmbeddingProvider(api_key="")

    @pytest.mark.asyncio
    async def test_embed_text_success(self, gemini_provider, mock_embedding):
        """Test successful single text embedding."""
        # Mock the embed_content method
        mock_response = MagicMock()
        mock_response.embeddings = [MagicMock(values=mock_embedding)]
        gemini_provider.client.models.embed_content = MagicMock(return_value=mock_response)

        result = await gemini_provider.embed_text("test text")

        assert result == mock_embedding
        assert len(result) == 768
        gemini_provider.client.models.embed_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_embed_text_empty_raises(self, gemini_provider):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await gemini_provider.embed_text("")

    @pytest.mark.asyncio
    async def test_embed_text_invalid_dimension_raises(self, gemini_provider):
        """Test that wrong dimension raises ValueError."""
        # Mock the embed_content method with wrong dimension
        mock_response = MagicMock()
        mock_response.embeddings = [MagicMock(values=[0.1] * 100)]
        gemini_provider.client.models.embed_content = MagicMock(return_value=mock_response)

        with pytest.raises(ValueError, match="Expected embedding dimension"):
            await gemini_provider.embed_text("test")

    @pytest.mark.asyncio
    async def test_embed_batch_success(self, gemini_provider, mock_embedding):
        """Test successful batch embedding."""
        texts = ["text1", "text2", "text3"]

        # Mock the embed_content method
        mock_response = MagicMock()
        mock_response.embeddings = [MagicMock(values=mock_embedding)]
        gemini_provider.client.models.embed_content = MagicMock(return_value=mock_response)

        results = await gemini_provider.embed_batch(texts)

        assert len(results) == 3
        assert all(len(emb) == 768 for emb in results)
        assert gemini_provider.client.models.embed_content.call_count == 3

    @pytest.mark.asyncio
    async def test_embed_batch_empty_raises(self, gemini_provider):
        """Test that empty batch raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await gemini_provider.embed_batch([])

    def test_get_dimension(self, gemini_provider):
        """Test get_dimension method."""
        assert gemini_provider.get_dimension() == 768

    def test_get_model_name(self, gemini_provider):
        """Test get_model_name method."""
        assert gemini_provider.get_model_name() == "text-embedding-004"


class TestEmbeddingCache:
    """Test embedding cache."""

    def test_cache_initialization(self):
        """Test cache initialization."""
        cache = EmbeddingCache(max_size=100, ttl_seconds=3600)
        assert cache.max_size == 100
        assert cache.ttl_seconds == 3600
        assert len(cache.cache) == 0

    def test_cache_set_and_get(self):
        """Test setting and getting from cache."""
        cache = EmbeddingCache(max_size=100, ttl_seconds=3600)
        embedding = [0.1, 0.2, 0.3]

        cache.set("test", embedding)
        result = cache.get("test")

        assert result == embedding
        assert cache.hits == 1
        assert cache.misses == 0

    def test_cache_miss(self):
        """Test cache miss."""
        cache = EmbeddingCache(max_size=100, ttl_seconds=3600)

        result = cache.get("nonexistent")

        assert result is None
        assert cache.misses == 1

    def test_cache_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = EmbeddingCache(max_size=2, ttl_seconds=3600)

        cache.set("key1", [0.1])
        cache.set("key2", [0.2])
        cache.set("key3", [0.3])  # Should evict key1

        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == [0.2]
        assert cache.get("key3") == [0.3]

    def test_cache_stats(self):
        """Test cache statistics."""
        cache = EmbeddingCache(max_size=100, ttl_seconds=3600)

        cache.set("key1", [0.1])
        cache.get("key1")  # Hit
        cache.get("key2")  # Miss

        stats = cache.get_stats()
        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    def test_cache_clear(self):
        """Test cache clearing."""
        cache = EmbeddingCache(max_size=100, ttl_seconds=3600)

        cache.set("key1", [0.1])
        cache.clear()

        assert len(cache.cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0
