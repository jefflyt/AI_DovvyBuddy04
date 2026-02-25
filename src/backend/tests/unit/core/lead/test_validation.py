"""Unit tests for lead type validation."""

import pytest
from pydantic import ValidationError

from app.core.lead.types import (
    LeadPayload,
    LeadType,
    TrainingLeadData,
    TripLeadData,
)


class TestTrainingLeadData:
    """Test TrainingLeadData validation."""

    def test_valid_training_lead_minimal(self):
        """Valid training lead with only required fields passes validation."""
        data = TrainingLeadData(
            name="John Doe",
            email="john@example.com",
        )
        assert data.name == "John Doe"
        assert data.email == "john@example.com"
        assert data.phone is None
        assert data.certification_level is None

    def test_valid_training_lead_complete(self):
        """Valid training lead with all fields passes validation."""
        data = TrainingLeadData(
            name="John Doe",
            email="john@example.com",
            phone="+1234567890",
            certification_level="Open Water",
            interested_certification="Advanced Open Water",
            preferred_location="Bali, Indonesia",
            message="Looking to get certified next month",
        )
        assert data.name == "John Doe"
        assert data.email == "john@example.com"
        assert data.phone == "+1234567890"
        assert data.certification_level == "Open Water"

    def test_missing_name_fails(self):
        """Missing name field fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            TrainingLeadData(email="john@example.com")
        
        errors = exc_info.value.errors()
        assert any(err["loc"] == ("name",) for err in errors)

    def test_missing_email_fails(self):
        """Missing email field fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            TrainingLeadData(name="John Doe")
        
        errors = exc_info.value.errors()
        assert any(err["loc"] == ("email",) for err in errors)

    def test_invalid_email_format_fails(self):
        """Invalid email format fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            TrainingLeadData(
                name="John Doe",
                email="not-an-email",
            )
        
        errors = exc_info.value.errors()
        assert any(err["loc"] == ("email",) for err in errors)

    def test_empty_name_fails(self):
        """Empty name string fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            TrainingLeadData(
                name="",
                email="john@example.com",
            )
        
        errors = exc_info.value.errors()
        assert any(err["loc"] == ("name",) for err in errors)

    def test_name_too_long_fails(self):
        """Name exceeding max length fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            TrainingLeadData(
                name="A" * 101,
                email="john@example.com",
            )
        
        errors = exc_info.value.errors()
        assert any(err["loc"] == ("name",) for err in errors)

    def test_message_too_long_fails(self):
        """Message exceeding max length fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            TrainingLeadData(
                name="John Doe",
                email="john@example.com",
                message="A" * 2001,
            )
        
        errors = exc_info.value.errors()
        assert any(err["loc"] == ("message",) for err in errors)

    def test_whitespace_trimming(self):
        """Leading/trailing whitespace is trimmed from string fields."""
        data = TrainingLeadData(
            name="  John Doe  ",
            email="john@example.com",
            message="  Looking to get certified  ",
        )
        assert data.name == "John Doe"
        assert data.message == "Looking to get certified"


class TestTripLeadData:
    """Test TripLeadData validation."""

    def test_valid_trip_lead_minimal(self):
        """Valid trip lead with only required fields passes validation."""
        data = TripLeadData(
            name="Jane Smith",
            email="jane@example.com",
        )
        assert data.name == "Jane Smith"
        assert data.email == "jane@example.com"
        assert data.destination is None

    def test_valid_trip_lead_complete(self):
        """Valid trip lead with all fields passes validation."""
        data = TripLeadData(
            name="Jane Smith",
            email="jane@example.com",
            phone="+9876543210",
            destination="Maldives",
            travel_dates="June 2026",
            group_size=4,
            budget="$5000-$7000 per person",
            message="Looking for liveaboard options",
        )
        assert data.name == "Jane Smith"
        assert data.destination == "Maldives"
        assert data.group_size == 4

    def test_group_size_validation(self):
        """Group size must be between 1 and 50."""
        # Valid group size
        data = TripLeadData(
            name="Jane Smith",
            email="jane@example.com",
            group_size=10,
        )
        assert data.group_size == 10

        # Group size too small
        with pytest.raises(ValidationError):
            TripLeadData(
                name="Jane Smith",
                email="jane@example.com",
                group_size=0,
            )

        # Group size too large
        with pytest.raises(ValidationError):
            TripLeadData(
                name="Jane Smith",
                email="jane@example.com",
                group_size=51,
            )

    def test_whitespace_trimming(self):
        """Leading/trailing whitespace is trimmed from string fields."""
        data = TripLeadData(
            name="  Jane Smith  ",
            email="jane@example.com",
            message="  Looking for liveaboard  ",
        )
        assert data.name == "Jane Smith"
        assert data.message == "Looking for liveaboard"


class TestLeadPayload:
    """Test LeadPayload validation."""

    def test_valid_training_payload(self):
        """Valid training lead payload passes validation."""
        payload = LeadPayload(
            type=LeadType.TRAINING,
            data={
                "name": "John Doe",
                "email": "john@example.com",
            },
        )
        assert payload.type == LeadType.TRAINING
        assert isinstance(payload.data, TrainingLeadData)

    def test_valid_trip_payload(self):
        """Valid trip lead payload passes validation."""
        payload = LeadPayload(
            type=LeadType.TRIP,
            data={
                "name": "Jane Smith",
                "email": "jane@example.com",
            },
        )
        assert payload.type == LeadType.TRIP
        assert isinstance(payload.data, TripLeadData)

    def test_payload_with_session_id(self):
        """Payload with session_id is valid."""
        from uuid import uuid4
        
        session_id = uuid4()
        payload = LeadPayload(
            type=LeadType.TRAINING,
            data={
                "name": "John Doe",
                "email": "john@example.com",
            },
            session_id=session_id,
        )
        assert payload.session_id == session_id

    def test_missing_type_fails(self):
        """Payload without type field fails validation."""
        with pytest.raises(ValidationError):
            LeadPayload(
                data={
                    "name": "John Doe",
                    "email": "john@example.com",
                }
            )

    def test_missing_data_fails(self):
        """Payload without data field fails validation."""
        with pytest.raises(ValidationError):
            LeadPayload(type=LeadType.TRAINING)
