"""
Unit tests for vector retriever.

Tests retrieval with mocked database.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.rag.retriever import VectorRetriever
from app.services.rag.types import RetrievalOptions, RetrievalResult


@pytest.fixture
def mock_embedding_provider():
    """Mock embedding provider."""
    provider = MagicMock()
    provider.embed_text = AsyncMock(return_value=[0.1] * 768)
    return provider


@pytest.fixture
def retriever(mock_embedding_provider):
    """Create retriever with mocked embedding provider."""
    return VectorRetriever(embedding_provider=mock_embedding_provider)


class TestVectorRetriever:
    """Test vector retriever."""

    @pytest.mark.asyncio
    async def test_retrieve_empty_query_raises(self, retriever):
        """Test that empty query raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await retriever.retrieve("")

    @pytest.mark.asyncio
    async def test_retrieve_success(self, retriever, mock_embedding_provider):
        """Test successful retrieval."""
        # Mock database results
        mock_rows = [
            MagicMock(
                id=uuid4(),
                content_path="test.md",
                chunk_text="Test chunk 1",
                metadata_={"doc_type": "faq"},
                similarity=0.95,
            ),
            MagicMock(
                id=uuid4(),
                content_path="test2.md",
                chunk_text="Test chunk 2",
                metadata_={"doc_type": "guide"},
                similarity=0.85,
            ),
        ]

        with patch("app.services.rag.retriever.get_session") as mock_get_session:
            mock_session = MagicMock()
            mock_result = MagicMock()
            mock_result.all.return_value = mock_rows
            mock_session.execute = AsyncMock(return_value=mock_result)
            mock_session.__aenter__.return_value = mock_session
            mock_session.__aexit__.return_value = None
            mock_session_maker = MagicMock(return_value=mock_session)
            mock_get_session.return_value = mock_session_maker

            results = await retriever.retrieve("test query")

            assert len(results) == 2
            assert all(isinstance(r, RetrievalResult) for r in results)
            assert results[0].text == "Test chunk 1"
            assert results[0].similarity == 0.95
            assert results[1].text == "Test chunk 2"
            assert results[1].similarity == 0.85

    @pytest.mark.asyncio
    async def test_retrieve_with_filters(self, retriever):
        """Test retrieval with filters."""
        options = RetrievalOptions(
            top_k=3,
            min_similarity=0.7,
            filters={"doc_type": "faq", "destination": "Tioman"},
        )

        with patch("app.services.rag.retriever.get_session") as mock_get_session:
            mock_session = MagicMock()
            mock_result = MagicMock()
            mock_result.all.return_value = []
            mock_session.execute = AsyncMock(return_value=mock_result)
            mock_session.__aenter__.return_value = mock_session
            mock_session.__aexit__.return_value = None
            mock_session_maker = MagicMock(return_value=mock_session)
            mock_get_session.return_value = mock_session_maker

            results = await retriever.retrieve("test query", options)

            assert isinstance(results, list)
            # Verify that execute was called (filters applied)
            mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_filters_by_min_similarity(self, retriever):
        """Test that results below min_similarity are filtered out."""
        mock_rows = [
            MagicMock(
                id=uuid4(),
                content_path="test.md",
                chunk_text="High similarity",
                metadata_={},
                similarity=0.9,
            ),
            MagicMock(
                id=uuid4(),
                content_path="test2.md",
                chunk_text="Low similarity",
                metadata_={},
                similarity=0.4,
            ),
        ]

        options = RetrievalOptions(min_similarity=0.5)

        with patch("app.services.rag.retriever.get_session") as mock_get_session:
            mock_session = MagicMock()
            mock_result = MagicMock()
            mock_result.all.return_value = mock_rows
            mock_session.execute = AsyncMock(return_value=mock_result)
            mock_session.__aenter__.return_value = mock_session
            mock_session.__aexit__.return_value = None
            mock_session_maker = MagicMock(return_value=mock_session)
            mock_get_session.return_value = mock_session_maker

            results = await retriever.retrieve("test query", options)

            # Only high similarity result should be returned
            assert len(results) == 1
            assert results[0].similarity == 0.9
