"""Test RAG retrieval to ensure database access works correctly."""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.rag.retriever import VectorRetriever
from app.services.rag.types import RetrievalOptions
from app.db.session import init_db


async def test_rag():
    """Test RAG retrieval with Malaysia emergency query."""
    print("Testing RAG retrieval...\n")
    
    # Initialize database
    await init_db()
    
    retriever = VectorRetriever()
    
    # Test query for Malaysia emergency contacts
    query = "What is the emergency number in Malaysia for diving accidents?"
    print(f"Query: {query}\n")
    
    options = RetrievalOptions(
        top_k=3,
        min_similarity=0.5
    )
    
    results = await retriever.retrieve(query, options)
    
    print(f"Found {len(results)} results:\n")
    
    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"  Similarity: {result.similarity:.4f}")
        print(f"  Content Path: {result.metadata.get('content_path', 'N/A')}")
        print(f"  Text Preview: {result.text[:200]}...")
        print()
    
    if results:
        print("✅ RAG retrieval working correctly!")
        return True
    else:
        print("❌ No results found - RAG retrieval may have issues")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_rag())
    sys.exit(0 if success else 1)
