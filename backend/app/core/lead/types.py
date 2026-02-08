"""Type definitions for lead capture system."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic import ConfigDict


class LeadType(str, Enum):
    """Lead type enumeration."""

    TRAINING = "training"
    TRIP = "trip"


class TrainingLeadData(BaseModel):
    """Training lead inquiry data."""

    name: str = Field(..., min_length=1, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Contact email address")
    phone: Optional[str] = Field(
        None, max_length=20, description="Contact phone number"
    )
    certification_level: Optional[str] = Field(
        None, max_length=50, description="Current certification level if any"
    )
    interested_certification: Optional[str] = Field(
        None, max_length=50, description="Desired certification"
    )
    preferred_location: Optional[str] = Field(
        None, max_length=100, description="Preferred training location"
    )
    message: Optional[str] = Field(
        None, max_length=2000, description="Additional notes or questions"
    )

    @field_validator("name", "message", mode="before")
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        """Strip leading/trailing whitespace from string fields."""
        return v.strip() if v else v


class TripLeadData(BaseModel):
    """Trip planning lead inquiry data."""

    name: str = Field(..., min_length=1, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Contact email address")
    phone: Optional[str] = Field(
        None, max_length=20, description="Contact phone number"
    )
    destination: Optional[str] = Field(
        None, max_length=100, description="Desired dive destination"
    )
    travel_dates: Optional[str] = Field(
        None, max_length=100, description="Preferred travel dates or timeframe"
    )
    group_size: Optional[int] = Field(
        None, ge=1, le=50, description="Number of travelers"
    )
    budget: Optional[str] = Field(
        None, max_length=50, description="Budget range or expectations"
    )
    message: Optional[str] = Field(
        None, max_length=2000, description="Additional notes or questions"
    )

    @field_validator("name", "message", mode="before")
    @classmethod
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        """Strip leading/trailing whitespace from string fields."""
        return v.strip() if v else v


class LeadPayload(BaseModel):
    """Combined request payload for lead submission."""

    type: LeadType = Field(..., description="Type of lead: training or trip")
    data: Union[TrainingLeadData, TripLeadData] = Field(
        ..., description="Lead-specific data"
    )
    session_id: Optional[UUID] = Field(
        None, description="Session ID for context enrichment"
    )

    @field_validator("data", mode="before")
    @classmethod
    def validate_data_type(cls, v: Any, info) -> Union[TrainingLeadData, TripLeadData]:
        """Validate that data matches the lead type."""
        if isinstance(v, dict):
            lead_type = info.data.get("type")
            if lead_type == LeadType.TRAINING:
                return TrainingLeadData(**v)
            elif lead_type == LeadType.TRIP:
                return TripLeadData(**v)
        # If v is already a TrainingLeadData or TripLeadData instance, return it
        if isinstance(v, (TrainingLeadData, TripLeadData)):
            return v
        # This should never happen due to Pydantic validation
        raise ValueError("Invalid data type")


class DiverProfile(BaseModel):
    """Session context diver profile data."""

    certification_level: Optional[str] = None
    experience_dives: Optional[int] = None
    interests: Optional[List[str]] = None
    fears: Optional[List[str]] = None


class LeadRecord(BaseModel):
    """Database record representation of a lead."""

    id: UUID = Field(..., description="Unique lead identifier")
    type: str = Field(..., description="Lead type: training or trip")
    diver_profile: Optional[Dict[str, Any]] = Field(
        None, description="Session context diver profile"
    )
    request_details: Dict[str, Any] = Field(
        ..., description="Lead-specific request data"
    )
    created_at: datetime = Field(..., description="Lead creation timestamp")
    model_config = ConfigDict(from_attributes=True)
