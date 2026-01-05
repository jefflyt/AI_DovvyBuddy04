import uuid

from sqlalchemy import Column, DateTime, Float, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

from app.db.base import Base


class ContentEmbedding(Base):
    __tablename__ = "content_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_path = Column(String, nullable=False)
    chunk_text = Column(Text, nullable=False)
    # Storing embeddings as an ARRAY of FLOAT for now (pgvector integration can be added later)
    embedding = Column(ARRAY(Float), nullable=True)
    metadata_ = Column(
        "metadata", JSONB, nullable=True
    )  # Use metadata_ to avoid SQLAlchemy conflict
    created_at = Column(DateTime(timezone=True), server_default=func.now())
