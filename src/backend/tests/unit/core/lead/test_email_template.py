"""Unit tests for email template builders."""

from datetime import datetime, timezone
from uuid import uuid4

from app.core.lead.email_template import (
    build_lead_email_html,
    build_lead_email_subject,
    build_lead_email_text,
)
from app.core.lead.types import LeadRecord


class TestEmailSubject:
    """Test email subject line builder."""

    def test_training_lead_subject(self):
        """Training lead subject includes type and name."""
        lead = LeadRecord(
            id=uuid4(),
            type="training",
            request_details={
                "name": "John Doe",
                "email": "john@example.com",
            },
            diver_profile=None,
            created_at=datetime.now(timezone.utc),
        )
        
        subject = build_lead_email_subject(lead)
        
        assert "[DovvyBuddy]" in subject
        assert "training" in subject.lower()
        assert "John Doe" in subject
        assert str(lead.id)[:8] in subject

    def test_trip_lead_subject(self):
        """Trip lead subject includes type and name."""
        lead = LeadRecord(
            id=uuid4(),
            type="trip",
            request_details={
                "name": "Jane Smith",
                "email": "jane@example.com",
            },
            diver_profile=None,
            created_at=datetime.now(timezone.utc),
        )
        
        subject = build_lead_email_subject(lead)
        
        assert "[DovvyBuddy]" in subject
        assert "trip" in subject.lower()
        assert "Jane Smith" in subject


class TestEmailHtml:
    """Test HTML email content builder."""

    def test_training_lead_html_minimal(self):
        """HTML includes all required sections for minimal training lead."""
        lead = LeadRecord(
            id=uuid4(),
            type="training",
            request_details={
                "name": "John Doe",
                "email": "john@example.com",
            },
            diver_profile=None,
            created_at=datetime.now(timezone.utc),
        )
        
        html = build_lead_email_html(lead)
        
        # Check for required sections
        assert "John Doe" in html
        assert "john@example.com" in html
        assert "Training Inquiry" in html
        assert str(lead.id) in html
        assert "Contact Information" in html
        
        # Check HTML structure
        assert "<!DOCTYPE html>" in html
        assert "<html>" in html
        assert "</html>" in html

    def test_training_lead_html_complete(self):
        """HTML includes all fields for complete training lead."""
        lead = LeadRecord(
            id=uuid4(),
            type="training",
            request_details={
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "certification_level": "Open Water",
                "interested_certification": "Advanced Open Water",
                "preferred_location": "Bali, Indonesia",
                "message": "Looking to get certified next month",
            },
            diver_profile=None,
            created_at=datetime.now(timezone.utc),
        )
        
        html = build_lead_email_html(lead)
        
        assert "+1234567890" in html
        assert "Open Water" in html
        assert "Advanced Open Water" in html
        assert "Bali, Indonesia" in html
        assert "Looking to get certified next month" in html

    def test_trip_lead_html_complete(self):
        """HTML includes all fields for complete trip lead."""
        lead = LeadRecord(
            id=uuid4(),
            type="trip",
            request_details={
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "+9876543210",
                "destination": "Maldives",
                "travel_dates": "June 2026",
                "group_size": 4,
                "budget": "$5000-$7000 per person",
                "message": "Looking for liveaboard options",
            },
            diver_profile=None,
            created_at=datetime.now(timezone.utc),
        )
        
        html = build_lead_email_html(lead)
        
        assert "Trip Planning Request" in html
        assert "Jane Smith" in html
        assert "Maldives" in html
        assert "June 2026" in html
        assert "4 travelers" in html
        assert "$5000-$7000 per person" in html
        assert "Looking for liveaboard options" in html

    def test_diver_profile_section(self):
        """HTML includes diver profile section when available."""
        lead = LeadRecord(
            id=uuid4(),
            type="training",
            request_details={
                "name": "John Doe",
                "email": "john@example.com",
            },
            diver_profile={
                "certification_level": "Open Water",
                "experience_dives": 25,
                "interests": ["wreck diving", "photography"],
                "fears": ["deep water", "strong currents"],
            },
            created_at=datetime.now(timezone.utc),
        )
        
        html = build_lead_email_html(lead)
        
        assert "Diver Profile" in html
        assert "25 dives" in html
        assert "wreck diving" in html
        assert "photography" in html
        assert "deep water" in html
        assert "strong currents" in html


class TestEmailText:
    """Test plain text email content builder."""

    def test_training_lead_text_minimal(self):
        """Plain text includes all required sections for minimal training lead."""
        lead = LeadRecord(
            id=uuid4(),
            type="training",
            request_details={
                "name": "John Doe",
                "email": "john@example.com",
            },
            diver_profile=None,
            created_at=datetime.now(timezone.utc),
        )
        
        text = build_lead_email_text(lead)
        
        assert "DOVVYBUDDY" in text
        assert "John Doe" in text
        assert "john@example.com" in text
        assert "Training Inquiry" in text
        assert str(lead.id) in text
        assert "CONTACT INFORMATION" in text

    def test_trip_lead_text_complete(self):
        """Plain text includes all fields for complete trip lead."""
        lead = LeadRecord(
            id=uuid4(),
            type="trip",
            request_details={
                "name": "Jane Smith",
                "email": "jane@example.com",
                "destination": "Maldives",
                "travel_dates": "June 2026",
                "group_size": 4,
                "message": "Looking for liveaboard options",
            },
            diver_profile=None,
            created_at=datetime.now(timezone.utc),
        )
        
        text = build_lead_email_text(lead)
        
        assert "Trip Planning Request" in text
        assert "Jane Smith" in text
        assert "Maldives" in text
        assert "June 2026" in text
        assert "4 travelers" in text
        assert "Looking for liveaboard options" in text

    def test_diver_profile_section_text(self):
        """Plain text includes diver profile section when available."""
        lead = LeadRecord(
            id=uuid4(),
            type="training",
            request_details={
                "name": "John Doe",
                "email": "john@example.com",
            },
            diver_profile={
                "certification_level": "Open Water",
                "experience_dives": 25,
            },
            created_at=datetime.now(timezone.utc),
        )
        
        text = build_lead_email_text(lead)
        
        assert "DIVER PROFILE" in text
        assert "Open Water" in text
        assert "25 dives" in text
