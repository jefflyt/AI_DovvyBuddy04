"""
Manual test script for embedding generation.

Usage:
    python -m scripts.test_embeddings "What is PADI Open Water?"
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embeddings import create_embedding_provider_from_env


async def main():
    """Test embedding generation."""
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.test_embeddings <text>")
        print('Example: python -m scripts.test_embeddings "What is PADI Open Water?"')
        sys.exit(1)

    text = sys.argv[1]

    print(f"\n=== Testing Embedding Generation ===")
    print(f"Text: {text}\n")

    # Create provider
    try:
        provider = create_embedding_provider_from_env()
        print(f"Provider: {provider.__class__.__name__}")
        print(f"Model: {provider.get_model_name()}")
        print(f"Dimension: {provider.get_dimension()}\n")
    except Exception as e:
        print(f"Error creating provider: {e}")
        print("\nMake sure GEMINI_API_KEY is set in your environment.")
        sys.exit(1)

    # Generate embedding
    try:
        print("Generating embedding...")
        embedding = await provider.embed_text(text)

        print(f"✓ Success!")
        print(f"Embedding length: {len(embedding)}")
        print(f"First 10 values: {embedding[:10]}")
        print(f"Min value: {min(embedding):.6f}")
        print(f"Max value: {max(embedding):.6f}")
        print(f"Mean value: {sum(embedding) / len(embedding):.6f}")

        # Test cache if available
        if hasattr(provider, "cache") and provider.cache:
            stats = provider.cache.get_stats()
            print(f"\nCache stats: {stats}")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
