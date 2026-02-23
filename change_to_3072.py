#!/usr/bin/env python3
"""Change content_embeddings.embedding from vector(768) to vector(3072) without index"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src/backend'))

from app.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    # Drop existing embedding index (HNSW or IVFFlat)
    print("Checking for existing vector indexes...")
    result = db.execute(text(
        "SELECT indexname FROM pg_indexes WHERE tablename='content_embeddings' AND indexname LIKE '%vector%'"
    ))
    indexes_found = False
    for row in result:
        indexes_found = True
        print(f"  Dropping index: {row[0]}")
        db.execute(text(f"DROP INDEX IF EXISTS {row[0]}"))
    if not indexes_found:
        print("  No vector indexes found")
    
    # Alter column type
    print("Changing column to vector(3072)...")
    db.execute(text("ALTER TABLE content_embeddings ALTER COLUMN embedding TYPE vector(3072)"))
    
    # Commit changes
    db.commit()
    print("✓ Database changed to vector(3072) (no index - will use sequential scan)")
    print("  Note: Index creation skipped due to pgvector 2000-dimension limit")
    
except Exception as e:
    db.rollback()
    print(f"✗ Error: {e}")
    sys.exit(1)
finally:
    db.close()
