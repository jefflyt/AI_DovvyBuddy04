"""
Unit tests for RAG pipeline.

Tests pipeline orchestration with mocked components.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.config import settings
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
                source_citation="content/faq/test.md",
            ),
            RetrievalResult(
                chunk_id="2",
                text="Test chunk 2",
                similarity=0.85,
                metadata={"doc_type": "guide", "destination": "Tioman"},
                source_citation="content/destinations/tioman.md",
            ),
        ]
    )
    retriever.retrieve_hybrid = AsyncMock(
        return_value=retriever.retrieve.return_value
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
        if settings.rag_use_hybrid:
            mock_retriever.retrieve_hybrid.assert_called_once()
        else:
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
        call_args = (
            mock_retriever.retrieve_hybrid.call_args
            if settings.rag_use_hybrid
            else mock_retriever.retrieve.call_args
        )
        options = call_args[0][1]
        assert options.top_k == 3
        assert options.min_similarity == 0.8
        assert options.filters == {"doc_type": "faq"}

    @pytest.mark.asyncio
    @patch("app.services.rag.pipeline.settings")
    async def test_retrieve_context_rag_disabled(self, mock_settings, mock_retriever):
        """Test that disabled RAG returns empty context."""
        mock_settings.enable_rag = False
        pipeline = RAGPipeline(retriever=mock_retriever)

        context = await pipeline.retrieve_context("test query")

        assert context.results == []
        assert context.formatted_context == "NO_DATA"
        mock_retriever.retrieve.assert_not_called()
        mock_retriever.retrieve_hybrid.assert_not_called()

    def test_format_context_empty(self, pipeline):
        """Test formatting empty results returns NO_DATA."""
        formatted = pipeline._format_context([])
        assert formatted == "NO_DATA"

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
                source_citation="content/faq/test.md",
            ),
            RetrievalResult(
                chunk_id="2",
                text="Test chunk 2",
                similarity=0.85,
                metadata={"doc_type": "guide"},
                source_citation="content/guide/test.md",
            ),
        ]

        formatted = pipeline._format_context(results)

        assert "Test chunk 1" in formatted
        assert "Test chunk 2" in formatted
        assert "\n\n" in formatted

    def test_assess_query_complexity_skip(self, pipeline):
        assert pipeline._assess_query_complexity("Hi") == "skip"

    def test_assess_query_complexity_medium(self, pipeline):
        assert pipeline._assess_query_complexity("What is buoyancy?") == "medium"

    def test_assess_query_complexity_complex(self, pipeline):
        assert (
            pipeline._assess_query_complexity("Where can I dive in Tioman?")
            == "complex"
        )

    @pytest.mark.asyncio
    async def test_dynamic_top_k_medium(self, pipeline, mock_retriever):
        await pipeline.retrieve_context("What is nitrox?")
        call_args = (
            mock_retriever.retrieve_hybrid.call_args
            if settings.rag_use_hybrid
            else mock_retriever.retrieve.call_args
        )
        options = call_args[0][1]
        assert options.top_k == 3

    @pytest.mark.asyncio
    async def test_dynamic_top_k_complex(self, pipeline, mock_retriever):
        await pipeline.retrieve_context("Where can I dive in Tioman?")
        call_args = (
            mock_retriever.retrieve_hybrid.call_args
            if settings.rag_use_hybrid
            else mock_retriever.retrieve.call_args
        )
        options = call_args[0][1]
        assert options.top_k == 5

    @pytest.mark.asyncio
    async def test_dynamic_top_k_skip(self, pipeline, mock_retriever):
        context = await pipeline.retrieve_context("Hello")
        assert context.formatted_context == "NO_DATA"
        assert context.results == []
        mock_retriever.retrieve.assert_not_called()
        mock_retriever.retrieve_hybrid.assert_not_called()

    @pytest.mark.asyncio
    async def test_retrieve_context_raw(self, pipeline, mock_retriever):
        """Test raw context retrieval (no formatting)."""
        results = await pipeline.retrieve_context_raw("test query")

        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(r, RetrievalResult) for r in results)
