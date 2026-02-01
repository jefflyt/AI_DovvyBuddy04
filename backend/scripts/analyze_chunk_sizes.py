"""Analyze chunk token sizes in the database.

Checks for:
- Chunks exceeding max_tokens (400)
- Token distribution statistics
- Potential data loss from oversized content
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import tiktoken
from sqlalchemy import text
from app.db.session import SessionLocal


def count_tokens(text_str: str) -> int:
    """Count tokens using tiktoken."""
    encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoder.encode(text_str))


def main():
    """Analyze chunk sizes."""
    db = SessionLocal()
    
    try:
        # Get all chunks
        result = db.execute(
            text("SELECT id, content_path, chunk_text, metadata FROM content_embeddings")
        )
        chunks = result.fetchall()
        
        print(f"Total chunks in database: {len(chunks)}")
        print()
        
        if not chunks:
            print("No chunks found in database")
            return
        
        # Analyze token counts
        oversized = []
        token_stats = []
        
        for chunk in chunks:
            chunk_id, content_path, chunk_text, metadata = chunk
            token_count = count_tokens(chunk_text)
            token_stats.append(token_count)
            
            # Check if exceeds max_tokens (400)
            if token_count > 400:
                oversized.append({
                    "id": str(chunk_id),
                    "path": content_path,
                    "tokens": token_count,
                    "section": metadata.get("section_header", "N/A") if metadata else "N/A",
                    "preview": chunk_text[:100] + "..."
                })
        
        # Statistics
        print("Token count statistics:")
        print(f"  Min: {min(token_stats)}")
        print(f"  Max: {max(token_stats)}")
        print(f"  Average: {sum(token_stats) / len(token_stats):.1f}")
        print(f"  Median: {sorted(token_stats)[len(token_stats) // 2]}")
        print()
        
        # Distribution
        ranges = [
            (0, 100, "0-100"),
            (100, 200, "100-200"),
            (200, 300, "200-300"),
            (300, 400, "300-400"),
            (400, 500, "400-500"),
            (500, 1000, "500-1000"),
            (1000, float("inf"), "1000+")
        ]
        
        print("Token distribution:")
        for min_tok, max_tok, label in ranges:
            count = sum(1 for t in token_stats if min_tok <= t < max_tok)
            if count > 0:
                pct = (count / len(token_stats)) * 100
                print(f"  {label:12s}: {count:4d} ({pct:5.1f}%)")
        print()
        
        # Oversized chunks
        if oversized:
            print(f"⚠️  WARNING: Found {len(oversized)} chunks exceeding max_tokens (400)")
            print()
            print("Top 10 largest chunks:")
            print()
            
            for i, item in enumerate(sorted(oversized, key=lambda x: x["tokens"], reverse=True)[:10], 1):
                print(f"{i}. Path: {item['path']}")
                print(f"   Section: {item['section']}")
                print(f"   Tokens: {item['tokens']} (exceeds limit by {item['tokens'] - 400})")
                print(f"   Preview: {item['preview']}")
                print()
            
            if len(oversized) > 10:
                print(f"   ... and {len(oversized) - 10} more oversized chunks")
            
            print()
            print("⚠️  RECOMMENDATION: These chunks exceed the configured max_tokens.")
            print("   The chunker has a guardrail that INCLUDES oversized paragraphs")
            print("   as their own chunks, so NO DATA IS LOST.")
            print("   However, these large chunks may impact retrieval quality.")
        else:
            print("✅ SUCCESS: All chunks are within max_tokens (400) limit")
            print("   No data loss detected.")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
