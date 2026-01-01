"""
Unit tests for RAG pipeline.

Tests pipeline orchestration with mocked components.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.rag.pipeline import RAGPipeline
from app.services.rag.types import RAGContext, RetrievalResult


@pytest.fixture
def mock_retriever():
    """Mock retriever."""
    retriever = MagicMock()
    retriever.retrieve = AsyncMock(
        return_value=[
            RetrievalResult(
                chunk_id="1",
                text="Test chunk 1",
                similarity=0.95,
                metadata={"doc_type": "faq", "section_header": "## FAQ"},
            ),
            RetrievalResult(
                chunk_id="2",
                text="Test chunk 2",
                similarity=0.85,
                metadata={"doc_type": "guide", "destination": "Tioman"},
            ),
        ]
    )
    return retriever


@pytest.fixture
def pipeline(mock_retriever):
    """Create RAG pipeline with mocked retriever."""
    return RAGPipeline(retriever=mock_retriever)


class TestRAGPipeline:
    """Test RAG pipeline."""

    @pytest.mark.asyncio
    async def test_retrieve_context_success(self, pipeline, mock_retriever):
        """Test successful context retrieval."""
        context = await pipeline.retrieve_context("test query")

        assert isinstance(context, RAGContext)
        assert context.query == "test query"
        assert len(context.results) == 2
        assert context.formatted_context != ""
        mock_retriever.retrieve.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_context_empty_query_raises(self, pipeline):
        """Test that empty query raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await pipeline.retrieve_context("")

    @pytest.mark.asyncio
    async def test_retrieve_context_with_options(self, pipeline, mock_retriever):
        """Test context retrieval with custom options."""
        await pipeline.retrieve_context(
            "test query", top_k=3, min_similarity=0.8, filters={"doc_type": "faq"}
        )

        # Verify options were passed to retriever
        call_args = mock_retriever.retrieve.call_args
        options = call_args[0][1]
        assert options.top_k == 3
        assert options.min_similarity == 0.8
        assert options.filters == {"doc_type": "faq"}

    @pytest.mark.asyncio
    @patch("app.core.config.settings")
    async def test_retrieve_context_rag_disabled(self, mock_settings, mock_retriever):
        """Test that disabled RAG returns empty context."""
        mock_settings.enable_rag = False
        pipeline = RAGPipeline(retriever=mock_retriever)

        context = await pipeline.retrieve_context("test query")

        assert context.results == []
        assert context.formatted_context == ""
        mock_retriever.retrieve.assert_not_called()

    def test_format_context_empty(self, pipeline):
        """Test formatting empty results."""
        formatted = pipeline._format_context([])
        assert formatted == ""

    def test_format_context_with_results(self, pipeline):
        """Test formatting results with metadata."""
        results = [
            RetrievalResult(
                chunk_id="1",
                text="Test chunk 1",
                similarity=0.95,
                metadata={
                    "doc_type": "faq",
                    "section_header": "## FAQ",
                    "destination": "Tioman",
                },
            ),
            RetrievalResult(
                chunk_id="2",
                text="Test chunk 2",
                similarity=0.85,
                metadata={"doc_type": "guide"},
            ),
        ]

        formatted = pipeline._format_context(results)

        assert "[Context 1" in formatted
        assert "[Context 2" in formatted
        assert "Test chunk 1" in formatted
        assert "Test chunk 2" in formatted
        assert "Type: faq" in formatted
        assert "Destination: Tioman" in formatted
        assert "---" in formatted  # Separator

    @pytest.mark.asyncio
    async def test_retrieve_context_raw(self, pipeline, mock_retriever):
        """Test raw context retrieval (no formatting)."""
        results = await pipeline.retrieve_context_raw("test query")

        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(r, RetrievalResult) for r in results)
