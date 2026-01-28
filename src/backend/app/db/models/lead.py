import uuid

from sqlalchemy import Column, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.base import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String, nullable=False)  # 'training' or 'trip'
    diver_profile = Column(JSONB, nullable=True)  # Session context diver profile
    request_details = Column(JSONB, nullable=False)  # Lead-specific request data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
