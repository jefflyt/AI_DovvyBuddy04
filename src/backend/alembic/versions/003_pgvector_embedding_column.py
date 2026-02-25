"""003 add pgvector embedding column

Revision ID: 003_pgvector_embedding_column
Revises: 002_update_leads
Create Date: 2026-02-23 00:00:00.000000

Changes the content_embeddings.embedding column from ARRAY(Float) to vector(3072)
to support gemini-embedding-001 embeddings. No index created due to pgvector's
2000-dimension limit for IVFFlat/HNSW indexes.

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY

# revision identifiers, used by Alembic.
revision = '003_pgvector_embedding_column'
down_revision = '002_update_leads'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Change embedding column from ARRAY(Float) to vector(3072)
    # Note: Using gemini-embedding-001 which produces 3072-dimensional embeddings
    # Cannot create IVFFlat/HNSW index due to pgvector 2000-dimension limit
    op.execute("""
        ALTER TABLE content_embeddings 
        ALTER COLUMN embedding TYPE vector(3072)
        USING embedding::vector(3072)
    """)
    
    # Note: No index created due to pgvector 2000-dimension limit for IVFFlat/HNSW
    # Sequential scan will be used for similarity searches
    # Consider GraphRAG or vector-specialized database for large-scale deployments


def downgrade() -> None:
    # Revert embedding column from vector(3072) back to ARRAY(Float)
    op.execute("""
        ALTER TABLE content_embeddings 
        ALTER COLUMN embedding TYPE float[]
        USING embedding::float[]
    """)
    
    # Note: We don't drop the vector extension in case other tables use it
    # op.execute('DROP EXTENSION IF EXISTS vector')
