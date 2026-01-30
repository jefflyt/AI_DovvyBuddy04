"""
Unit tests for context builder.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.orchestration.context_builder import ContextBuilder
from app.services.rag.types import RAGContext, RetrievalResult


@pytest.mark.asyncio
async def test_build_context_basic():
    """Test basic context building without RAG."""
    builder = ContextBuilder()

    # Mock RAG pipeline to be disabled
    builder.rag_pipeline.enabled = False

    context = await builder.build_context(
        query="test query",
        conversation_history=[],
        use_rag=False,
    )

    assert context.query == "test query"
    assert context.conversation_history == []
    assert context.rag_context is None
    assert context.metadata["has_rag"] is False


@pytest.mark.asyncio
async def test_build_context_with_history():
    """Test context building with conversation history."""
    builder = ContextBuilder()
    builder.rag_pipeline.enabled = False

    history = [
        {"role": "user", "content": "First message"},
        {"role": "assistant", "content": "First response"},
    ]

    context = await builder.build_context(
        query="test query",
        conversation_history=history,
        use_rag=False,
    )

    assert len(context.conversation_history) == 2
    assert context.metadata["history_length"] == 2


@pytest.mark.asyncio
async def test_build_context_with_rag():
    """Test context building with RAG retrieval."""
    builder = ContextBuilder()

    # Mock RAG pipeline
    mock_rag_result = RAGContext(
        query="test query",
        results=[
            RetrievalResult(
                chunk_text="Retrieved chunk",
                similarity=0.9,
                metadata={},
            )
        ],
        formatted_context="Retrieved chunk",
    )

    builder.rag_pipeline.retrieve_context = AsyncMock(return_value=mock_rag_result)
    builder.rag_pipeline.enabled = True

    context = await builder.build_context(
        query="test query",
        conversation_history=[],
        use_rag=True,
    )

    assert context.rag_context == "Retrieved chunk"
    assert context.metadata["has_rag"] is True
    builder.rag_pipeline.retrieve_context.assert_called_once_with("test query")


@pytest.mark.asyncio
async def test_build_context_rag_failure():
    """Test context building when RAG fails."""
    builder = ContextBuilder()

    # Mock RAG to raise exception
    builder.rag_pipeline.retrieve_context = AsyncMock(side_effect=Exception("RAG error"))
    builder.rag_pipeline.enabled = True

    # Should not raise, should handle gracefully
    context = await builder.build_context(
        query="test query",
        conversation_history=[],
        use_rag=True,
    )

    assert context.rag_context is None
    assert context.metadata["has_rag"] is False


def test_trim_history():
    """Test conversation history trimming."""
    builder = ContextBuilder()

    # Create history with 30 messages
    history = [{"role": "user", "content": f"Message {i}"} for i in range(30)]

    # Trim to last 20
    trimmed = builder.trim_history(history, max_messages=20)

    assert len(trimmed) == 20
    assert trimmed[0]["content"] == "Message 10"  # First of last 20
    assert trimmed[-1]["content"] == "Message 29"  # Last message


def test_trim_history_no_trim_needed():
    """Test trimming when history is already short enough."""
    builder = ContextBuilder()

    history = [{"role": "user", "content": f"Message {i}"} for i in range(10)]
    trimmed = builder.trim_history(history, max_messages=20)

    assert len(trimmed) == 10
    assert trimmed == history


@pytest.mark.asyncio
async def test_build_context_with_diver_profile():
    """Test context building with diver profile."""
    builder = ContextBuilder()
    builder.rag_pipeline.enabled = False

    diver_profile = {
        "certification_level": "Advanced Open Water",
        "dive_count": 50,
    }

    context = await builder.build_context(
        query="test query",
        conversation_history=[],
        diver_profile=diver_profile,
        use_rag=False,
    )

    assert context.diver_profile == diver_profile
