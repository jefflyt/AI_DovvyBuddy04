import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class DiveSite(Base):
    __tablename__ = "dive_sites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destination_id = Column(UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    min_certification_level = Column(String, nullable=True)  # e.g., "OW", "AOW", "Rescue"
    min_logged_dives = Column(Integer, nullable=True)
    difficulty_band = Column(String, nullable=True)  # e.g., "beginner", "intermediate", "advanced"
    access_type = Column(String, nullable=True)  # e.g., "shore", "boat"
    data_quality = Column(String, nullable=True)  # e.g., "verified", "compiled", "anecdotal"
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
