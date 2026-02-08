import uuid

from sqlalchemy import Column, Computed, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID, TSVECTOR
from pgvector.sqlalchemy import Vector

from app.db.base import Base


class ContentEmbedding(Base):
    __tablename__ = "content_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_path = Column(String, nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_text_tsv = Column(TSVECTOR, Computed("to_tsvector('english', chunk_text)", persisted=True))  # Full-text search column (database-generated)
    # Store embeddings using pgvector
    embedding = Column(Vector(768), nullable=True)
    metadata_ = Column(
        "metadata", JSONB, nullable=True
    )  # Use metadata_ to avoid SQLAlchemy conflict
    created_at = Column(DateTime(timezone=True), server_default=func.now())
