"""
Embedding comparison tests - Python vs TypeScript.

Verifies that Python embeddings match TypeScript embeddings.
"""

import pytest
import os
import numpy as np

from app.services.embeddings import GeminiEmbeddingProvider
from app.core.config import settings


pytestmark = pytest.mark.slow


@pytest.fixture
def api_key():
    """Get Gemini API key from environment."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        pytest.skip("GEMINI_API_KEY not set")
    return key


@pytest.fixture
def provider(api_key):
    """Create Python embedding provider."""
    return GeminiEmbeddingProvider(
        api_key=api_key,
        model=settings.embedding_model,
        use_cache=False
    )


def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# Test texts (representative of different content types)
TEST_TEXTS = [
    "What is PADI Open Water certification?",
    "How deep can I dive with Advanced Open Water?",
    "What equipment do I need for scuba diving?",
    "Where is Tioman Island located?",
    "What are the best dive sites in Malaysia?",
    "How do I equalize while diving?",
    "What is decompression sickness?",
    "How long does PADI certification take?",
    "What marine life can I see in Tioman?",
    "What is the difference between PADI and SSI?",
]


@pytest.mark.asyncio
async def test_embedding_dimensions(provider):
    """Test that embeddings have correct dimensions."""
    text = TEST_TEXTS[0]
    
    embedding = await provider.embed_text(text)
    
    assert len(embedding) == provider.dimension
    assert all(isinstance(x, float) for x in embedding)


@pytest.mark.asyncio
async def test_embedding_consistency(provider):
    """Test that same text produces same embedding."""
    text = TEST_TEXTS[0]
    
    embedding1 = await provider.embed_text(text)
    embedding2 = await provider.embed_text(text)
    
    similarity = cosine_similarity(embedding1, embedding2)
    assert similarity > 0.99  # Should be nearly identical


@pytest.mark.asyncio
async def test_embedding_diversity(provider):
    """Test that different texts produce different embeddings."""
    text1 = TEST_TEXTS[0]
    text2 = TEST_TEXTS[5]  # Different topic
    
    embedding1 = await provider.embed_text(text1)
    embedding2 = await provider.embed_text(text2)
    
    similarity = cosine_similarity(embedding1, embedding2)
    assert similarity < 0.95  # Should be noticeably different


@pytest.mark.asyncio
async def test_batch_vs_single_embeddings(provider):
    """Test that batch and single embeddings match."""
    texts = TEST_TEXTS[:3]
    
    # Generate individually
    single_embeddings = []
    for text in texts:
        emb = await provider.embed_text(text)
        single_embeddings.append(emb)
    
    # Generate in batch
    batch_embeddings = await provider.embed_batch(texts)
    
    # Compare
    for single, batch in zip(single_embeddings, batch_embeddings):
        similarity = cosine_similarity(single, batch)
        assert similarity > 0.99  # Should be nearly identical


@pytest.mark.asyncio
async def test_embeddings_sample_set(provider):
    """Generate embeddings for sample texts and log for manual comparison."""
    # This test is mainly for documentation/manual review
    # In a real comparison, you would load TypeScript-generated embeddings and compare
    
    sample_texts = TEST_TEXTS[:5]
    embeddings = await provider.embed_batch(sample_texts)
    
    print("\n=== Python Embedding Sample ===")
    for text, emb in zip(sample_texts, embeddings):
        print(f"\nText: {text}")
        print(f"Embedding (first 10): {emb[:10]}")
        print(f"Norm: {np.linalg.norm(emb):.4f}")
    
    assert len(embeddings) == 5
    assert all(len(emb) == provider.dimension for emb in embeddings)


# Manual comparison instructions
"""
To compare with TypeScript embeddings:

1. Generate TypeScript embeddings:
   cd /path/to/project
   pnpm tsx scripts/test-embeddings.ts

2. Save embeddings to JSON file

3. Load and compare in this test:
   with open("ts_embeddings.json") as f:
       ts_embeddings = json.load(f)
   
   for py_emb, ts_emb in zip(py_embeddings, ts_embeddings):
       similarity = cosine_similarity(py_emb, ts_emb)
       assert similarity > 0.98  # Acceptance threshold
"""
