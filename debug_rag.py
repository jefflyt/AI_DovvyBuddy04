#!/usr/bin/env python
"""Debug script to test RAG pipeline components directly."""
import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.core.config import settings
from app.db.session import init_db, get_session
from app.services.embeddings import create_embedding_provider_from_env
from app.services.rag.pipeline import RAGPipeline
from app.db.models.content_embedding import ContentEmbedding
from sqlalchemy import select, func


async def main():
    print("=" * 60)
    print("RAG PIPELINE DIAGNOSTIC")
    print("=" * 60)
    
    # 1. Check Config
    print(f"\n[1] CONFIGURATION:")
    print(f"  - ENABLE_RAG: {settings.enable_rag}")
    print(f"  - DATABASE_URL: {settings.database_url[:50]}...")
    print(f"  - GEMINI_API_KEY: {'SET' if settings.gemini_api_key else 'MISSING!'}")
    print(f"  - RAG_TOP_K: {settings.rag_top_k}")
    print(f"  - RAG_MIN_SIMILARITY: {settings.rag_min_similarity}")
    
    # 2. Check DB Connection
    print(f"\n[2] DATABASE CONNECTION:")
    try:
        await init_db()
        session_maker = get_session()
        async with session_maker() as session:
            result = await session.execute(select(func.count()).select_from(ContentEmbedding))
            count = result.scalar()
            print(f"  ✅ Connected! content_embedding table has {count} rows.")
            
            # Check pgvector extension
            pgvector_check = await session.execute(
                select(func.count()).select_from(
                    select(ContentEmbedding.embedding).limit(1).subquery()
                )
            )
            print(f"  ✅ pgvector extension working.")
            
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return
    
    # 3. Check Embedding Provider
    print(f"\n[3] EMBEDDING PROVIDER:")
    try:
        provider = create_embedding_provider_from_env()
        print(f"  ✅ Provider initialized: {type(provider).__name__}")
        
        test_embedding = await provider.embed_text("test query")
        print(f"  ✅ Embedding generated: length={len(test_embedding)}")
    except Exception as e:
        print(f"  ❌ Embedding error: {e}")
        return
    
    # 4. Test RAG Retrieval
    print(f"\n[4] RAG RETRIEVAL TEST:")
    try:
        pipeline = RAGPipeline()
        print(f"  - Pipeline enabled: {pipeline.enabled}")
        
        query = "Where can I dive in Tioman?"
        print(f"  - Query: '{query}'")
        
        context = await pipeline.retrieve_context(query)
        print(f"  - Results: {len(context.results)}")
        print(f"  - Has Data: {context.has_data}")
        
        if context.results:
            print(f"  ✅ TOP 3 RESULTS:")
            for i, r in enumerate(context.results[:3]):
                print(f"    [{i+1}] similarity={r.similarity:.3f}, text={r.text[:80]}...")
        else:
            print(f"  ⚠️  NO RESULTS FOUND!")
            print(f"\n  Possible causes:")
            print(f"    1. No content with 'Tioman' in database")
            print(f"    2. Similarity threshold ({settings.rag_min_similarity}) too high")
            print(f"    3. Embedding model mismatch (ingested vs. query)")
            
            # Check if ANY content exists
            async with session_maker() as session:
                sample = await session.execute(
                    select(ContentEmbedding.content_path, ContentEmbedding.chunk_text)
                    .limit(3)
                )
                rows = sample.all()
                if rows:
                    print(f"\n  ℹ️  Sample content in DB:")
                    for row in rows:
                        print(f"    - {row.content_path}: {row.chunk_text[:60]}...")
                else:
                    print(f"\n  ❌ DATABASE IS EMPTY! Run content ingestion first.")
                    
    except Exception as e:
        print(f"  ❌ RAG error: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
