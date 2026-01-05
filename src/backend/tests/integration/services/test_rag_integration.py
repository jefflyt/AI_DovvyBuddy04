"""
Integration tests for RAG pipeline.

Tests end-to-end RAG with real database and APIs (marked as slow for CI).
"""

import pytest
import os

from app.services.rag import RAGPipeline
from app.db.session import init_db


pytestmark = pytest.mark.slow


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

    context = await pipeline.retrieve_context(query, top_k=3)

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

    context = await pipeline.retrieve_context(
        query, top_k=5, filters={"doc_type": "certification"}
    )

    assert isinstance(context.results, list)
    # Verify results match filter (if any results)
    for result in context.results:
        if result.metadata.get("doc_type"):
            assert result.metadata["doc_type"] == "certification"


@pytest.mark.asyncio
async def test_rag_similarity_threshold(pipeline, db):
    """Test RAG with similarity threshold."""
    query = "What is decompression sickness?"

    context = await pipeline.retrieve_context(query, min_similarity=0.7)

    # All results should meet threshold
    for result in context.results:
        assert result.similarity >= 0.7


@pytest.mark.asyncio
async def test_rag_raw_results(pipeline, db):
    """Test raw results without formatting."""
    query = "How deep can I dive?"

    results = await pipeline.retrieve_context_raw(query, top_k=2)

    assert isinstance(results, list)
    if results:
        assert all(hasattr(r, "text") for r in results)
        assert all(hasattr(r, "similarity") for r in results)
        assert all(hasattr(r, "metadata") for r in results)
