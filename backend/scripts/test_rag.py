"""
Manual test script for RAG pipeline.

Usage:
    python -m scripts.test_rag "What certifications do I need for Tioman?"
    python -m scripts.test_rag --top-k 3 "What is PADI Open Water?"
"""

import asyncio
import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.rag import RAGPipeline
from app.db.session import init_db


async def main():
    """Test RAG pipeline."""
    parser = argparse.ArgumentParser(description="Test RAG pipeline")
    parser.add_argument("query", help="The query to retrieve context for")
    parser.add_argument(
        "--top-k", type=int, default=5, help="Number of chunks to retrieve (default: 5)"
    )
    parser.add_argument(
        "--min-similarity",
        type=float,
        default=0.0,
        help="Minimum similarity threshold (default: 0.0)",
    )
    parser.add_argument(
        "--doc-type", help="Filter by document type (e.g., 'faq', 'certification')"
    )
    parser.add_argument("--destination", help="Filter by destination (e.g., 'Tioman')")

    args = parser.parse_args()

    print(f"\n=== Testing RAG Pipeline ===")
    print(f"Query: {args.query}")
    print(f"Top-K: {args.top_k}")
    print(f"Min similarity: {args.min_similarity}")
    if args.doc_type:
        print(f"Doc type filter: {args.doc_type}")
    if args.destination:
        print(f"Destination filter: {args.destination}")
    print()

    # Initialize database
    try:
        print("Initializing database...")
        await init_db()
        print("✓ Database initialized\n")
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("\nMake sure DATABASE_URL is set in your environment.")
        sys.exit(1)

    # Create RAG pipeline
    try:
        pipeline = RAGPipeline()
        print(f"RAG pipeline created (enabled: {pipeline.enabled})\n")
    except Exception as e:
        print(f"Error creating RAG pipeline: {e}")
        print("\nMake sure GEMINI_API_KEY is set in your environment.")
        sys.exit(1)

    # Build filters
    filters = {}
    if args.doc_type:
        filters["doc_type"] = args.doc_type
    if args.destination:
        filters["destination"] = args.destination

    # Retrieve context
    try:
        print("Retrieving context...\n")
        context = await pipeline.retrieve_context(
            args.query,
            top_k=args.top_k,
            min_similarity=args.min_similarity,
            filters=filters if filters else None,
        )

        print(f"=== Results ({len(context.results)} chunks) ===\n")

        if not context.results:
            print("No results found.")
            print("\nPossible reasons:")
            print("  - Database has no embeddings yet")
            print("  - Query doesn't match any content")
            print("  - Filters are too restrictive")
            print("  - Min similarity threshold is too high")
        else:
            for i, result in enumerate(context.results, 1):
                print(f"--- Chunk {i} (similarity: {result.similarity:.4f}) ---")
                print(f"ID: {result.chunk_id}")
                print(f"Metadata: {result.metadata}")
                print(f"Text: {result.text[:200]}...")
                if len(result.text) > 200:
                    print(f"  (truncated, full length: {len(result.text)} chars)")
                print()

            print("\n=== Formatted Context ===")
            print(context.formatted_context[:500])
            if len(context.formatted_context) > 500:
                print(f"\n... (truncated, full length: {len(context.formatted_context)} chars)")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
