"""004 change embedding dimension to 768

Revision ID: 004_embedding_dimension_768
Revises: 003_pgvector_embedding_column
Create Date: 2026-02-23 12:00:00.000000

Changes the content_embeddings.embedding column from vector(3072) to vector(768)
to support text-embedding-004 embeddings (Google's recommended model with Matryoshka support).
This migration WILL DROP existing data in the embedding column - run data clearing script first.

**CRITICAL: Run data clearing script before applying this migration:**
  cd /path/to/project
  .venv/bin/python src/backend/scripts/clear_embeddings.py

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '004_embedding_dimension_768'
down_revision = '003_pgvector_embedding_column'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Change embedding column from vector(3072) to vector(768)
    # Note: Using text-embedding-004 which produces 768-dimensional embeddings
    # This model supports Matryoshka truncation for flexible dimensionality
    # DESTRUCTIVE: This will drop existing embeddings - ensure backup/clearing was done
    op.execute("""
        ALTER TABLE content_embeddings
        ALTER COLUMN embedding DROP NOT NULL
    """)

    op.execute("""
        UPDATE content_embeddings
        SET embedding = NULL
        WHERE embedding IS NOT NULL
    """)

    op.execute("""
        ALTER TABLE content_embeddings 
        ALTER COLUMN embedding TYPE vector(768)
        USING NULL::vector(768)
    """)
    
    # Now we CAN create an HNSW index since 768 < 2000 dimension limit
    # HNSW is recommended for high-recall similarity search
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_content_embeddings_hnsw 
        ON content_embeddings 
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)
    
    # Note: m=16 provides good recall/speed tradeoff
    # ef_construction=64 is moderate build time vs. recall quality


def downgrade() -> None:
    # Drop the HNSW index first
    op.execute("DROP INDEX IF EXISTS idx_content_embeddings_hnsw")
    
    # Revert embedding column from vector(768) back to vector(3072)
    # DESTRUCTIVE: This will drop existing embeddings
    op.execute("""
        ALTER TABLE content_embeddings 
        ALTER COLUMN embedding TYPE vector(3072)
        USING embedding::vector(3072)
    """)

