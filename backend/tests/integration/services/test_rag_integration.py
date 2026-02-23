"""
Integration tests for RAG pipeline.

Tests end-to-end RAG with real database and APIs (marked as slow for CI).
"""

import os
import pytest

from google.genai import errors as genai_errors

from app.services.rag import RAGPipeline
from app.db.session import init_db


pytestmark = pytest.mark.slow


def _is_network_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return any(
        token in message
        for token in [
            "nodename nor servname",
            "name or service not known",
            "failed to resolve",
            "connection error",
            "connecterror",
            "temporarily unavailable",
        ]
    )


def _skip_if_unavailable(exc: Exception) -> None:
    if isinstance(exc, genai_errors.ClientError) and "text-embedding-004" in str(exc):
        pytest.skip("Embedding model not available for integration test")
    if _is_network_error(exc):
        pytest.skip("Network unavailable for integration test")


@pytest.fixture(scope="module")
async def db():
    """Initialize database."""
    await init_db()


@pytest.fixture
def api_key():
    """Get Gemini API key from environment."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        pytest.skip("GEMINI_API_KEY not set")
    return key


@pytest.fixture
def pipeline(api_key):
    """Create real RAG pipeline."""
    return RAGPipeline()


@pytest.mark.asyncio
async def test_rag_end_to_end(pipeline, db):
    """Test end-to-end RAG pipeline with real database."""
    query = "What is PADI Open Water certification?"
    try:
        context = await pipeline.retrieve_context(query, top_k=3)
    except Exception as exc:
        _skip_if_unavailable(exc)
        raise

    assert context.query == query
    assert isinstance(context.results, list)
    # Results may be empty if database has no embeddings yet
    if context.results:
        assert all(result.similarity > 0 for result in context.results)
        assert context.formatted_context


@pytest.mark.asyncio
async def test_rag_with_filters(pipeline, db):
    """Test RAG with metadata filters."""
    query = "What certifications do I need?"
    try:
        context = await pipeline.retrieve_context(
            query, top_k=5, filters={"doc_type": "certification"}
        )
    except Exception as exc:
        _skip_if_unavailable(exc)
        raise

    assert isinstance(context.results, list)
    # Verify results match filter (if any results)
    for result in context.results:
        if result.metadata.get("doc_type"):
            assert result.metadata["doc_type"] == "certification"


@pytest.mark.asyncio
async def test_rag_similarity_threshold(pipeline, db):
    """Test RAG with similarity threshold."""
    query = "What is decompression sickness?"
    try:
        context = await pipeline.retrieve_context(query, min_similarity=0.7)
    except Exception as exc:
        _skip_if_unavailable(exc)
        raise

    # All results should meet threshold
    for result in context.results:
        assert result.similarity >= 0.7


@pytest.mark.asyncio
async def test_rag_raw_results(pipeline, db):
    """Test raw results without formatting."""
    query = "How deep can I dive?"
    try:
        results = await pipeline.retrieve_context_raw(query, top_k=2)
    except Exception as exc:
        _skip_if_unavailable(exc)
        raise

    assert isinstance(results, list)
    if results:
        assert all(hasattr(r, "text") for r in results)
        assert all(hasattr(r, "similarity") for r in results)
        assert all(hasattr(r, "metadata") for r in results)


@pytest.mark.asyncio
async def test_rag_skip_greeting(pipeline, db):
    """Skip RAG for greetings."""
    context = await pipeline.retrieve_context("Hello")

    assert context.results == []
    assert context.formatted_context == "NO_DATA"
    assert context.has_data is False
