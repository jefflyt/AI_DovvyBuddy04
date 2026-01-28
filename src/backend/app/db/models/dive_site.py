import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.base import Base


class DiveSite(Base):
    __tablename__ = "dive_sites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    destination_id = Column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # New fields added in schema migration (2026-01-01)
    dive_site_id = Column(String, unique=True, nullable=False)  # Unique identifier from content
    difficulty_rating = Column(Integer, nullable=True)  # 1-5 scale
    depth_min_m = Column(Float, nullable=True)  # Minimum depth in meters
    depth_max_m = Column(Float, nullable=True)  # Maximum depth in meters
    tags = Column(JSONB, nullable=True)  # JSON array of tags
    last_updated = Column(DateTime(timezone=True), nullable=True)  # Content last updated date
    
    # Original fields
    min_certification_level = Column(String, nullable=True)  # e.g., "OW", "AOW", "Rescue"
    min_logged_dives = Column(Integer, nullable=True)
    difficulty_band = Column(String, nullable=True)  # e.g., "beginner", "intermediate", "advanced"
    access_type = Column(String, nullable=True)  # e.g., "shore", "boat"
    data_quality = Column(String, nullable=True)  # e.g., "verified", "compiled", "anecdotal"
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)  # Auto-update timestamp
