import uuid

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.base import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    source = Column(String, nullable=True)
    session_id = Column(UUID(as_uuid=True), nullable=True)
    metadata_ = Column(
        "metadata", JSONB, nullable=True
    )  # Use metadata_ to avoid SQLAlchemy conflict
    created_at = Column(DateTime(timezone=True), server_default=func.now())
