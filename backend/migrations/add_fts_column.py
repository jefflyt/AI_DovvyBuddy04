"""Add full-text search column to content_embedding table.

This migration adds a tsvector column for PostgreSQL full-text search
to enable hybrid search (keyword + semantic).
"""
from sqlalchemy import text
from app.db.session import SessionLocal


def upgrade():
    """Add FTS column and index."""
    db = SessionLocal()
    try:
        print("Adding full-text search column...")
        
        # Add tsvector column (generated from chunk_text)
        db.execute(text("""
            ALTER TABLE content_embeddings 
            ADD COLUMN IF NOT EXISTS chunk_text_tsv tsvector 
            GENERATED ALWAYS AS (to_tsvector('english', chunk_text)) STORED
        """))
        
        print("Creating GIN index for FTS...")
        
        # Create GIN index for fast full-text search
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_content_embeddings_fts 
            ON content_embeddings USING GIN(chunk_text_tsv)
        """))
        
        db.commit()
        print("✓ Migration completed successfully")
        print("  - Added chunk_text_tsv column")
        print("  - Created idx_content_embeddings_fts index")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        db.close()


def downgrade():
    """Remove FTS column and index."""
    db = SessionLocal()
    try:
        print("Removing FTS index...")
        db.execute(text("DROP INDEX IF EXISTS idx_content_embeddings_fts"))
        
        print("Removing FTS column...")
        db.execute(text("ALTER TABLE content_embeddings DROP COLUMN IF EXISTS chunk_text_tsv"))
        
        db.commit()
        print("✓ Rollback completed successfully")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Rollback failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
