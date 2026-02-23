"""003 align content_embeddings.embedding with pgvector

Revision ID: 003_pgvector_embedding_column
Revises: 002_update_leads
Create Date: 2026-02-23 00:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "003_pgvector_embedding_column"
down_revision = "002_update_leads"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ensure pgvector is available before casting embedding column.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = 'content_embeddings'
                  AND column_name = 'embedding'
                  AND udt_name <> 'vector'
            ) THEN
                ALTER TABLE content_embeddings
                ALTER COLUMN embedding TYPE vector(768)
                USING embedding::vector(768);
            END IF;
        END$$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = 'content_embeddings'
                  AND column_name = 'embedding'
                  AND udt_name = 'vector'
            ) THEN
                ALTER TABLE content_embeddings
                ALTER COLUMN embedding TYPE real[]
                USING embedding::real[];
            END IF;
        END$$;
        """
    )
