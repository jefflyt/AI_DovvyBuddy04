"""Integration tests for lead API endpoint."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from app.core.lead.types import LeadType
from app.core.config import settings
from app.main import app


@pytest.fixture
def mock_resend():
    """Mock Resend API client."""
    with patch("app.api.routes.lead.resend") as mock:
        mock.emails.send = MagicMock(return_value={"id": "email-123"})
        yield mock


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = AsyncMock()
    return session


@pytest.fixture(autouse=True)
def configure_lead_settings(monkeypatch):
    """Ensure lead email configuration is present for tests."""
    monkeypatch.setattr(settings, "resend_api_key", "test-key")
    monkeypatch.setattr(settings, "lead_email_to", "leads@example.com")


class TestLeadEndpoint:
    """Test POST /api/leads endpoint."""

    @pytest.mark.asyncio
    async def test_create_training_lead_success(self, mock_resend):
        """Successful training lead creation returns 201 with lead ID."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "type": "training",
                "data": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+1234567890",
                    "certification_level": "Open Water",
                    "interested_certification": "Advanced Open Water",
                },
            }
            
            with patch("app.api.routes.lead.capture_and_deliver_lead") as mock_capture:
                mock_lead_record = MagicMock()
                mock_lead_record.id = uuid4()
                mock_capture.return_value = mock_lead_record
                
                response = await client.post("/api/leads", json=payload)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert "lead_id" in data

    @pytest.mark.asyncio
    async def test_create_trip_lead_success(self, mock_resend):
        """Successful trip lead creation returns 201 with lead ID."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "type": "trip",
                "data": {
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                    "destination": "Maldives",
                    "travel_dates": "June 2026",
                    "group_size": 4,
                },
            }
            
            with patch("app.api.routes.lead.capture_and_deliver_lead") as mock_capture:
                mock_lead_record = MagicMock()
                mock_lead_record.id = uuid4()
                mock_capture.return_value = mock_lead_record
                
                response = await client.post("/api/leads", json=payload)
        
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.asyncio
    async def test_missing_name_returns_400(self):
        """Missing required name field returns 400 validation error."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "type": "training",
                "data": {
                    "email": "john@example.com",
                },
            }
            
            response = await client.post("/api/leads", json=payload)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_invalid_email_returns_400(self):
        """Invalid email format returns 422 validation error."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "type": "training",
                "data": {
                    "name": "John Doe",
                    "email": "not-an-email",
                },
            }
            
            response = await client.post("/api/leads", json=payload)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_missing_type_returns_400(self):
        """Missing type field returns 400 validation error."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "data": {
                    "name": "John Doe",
                    "email": "john@example.com",
                },
            }
            
            response = await client.post("/api/leads", json=payload)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_invalid_json_returns_422(self):
        """Invalid JSON body returns 422 error."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/leads",
                content="not valid json",
                headers={"Content-Type": "application/json"},
            )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_message_too_long_returns_400(self):
        """Message exceeding max length returns 422 validation error."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "type": "training",
                "data": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "message": "A" * 2001,
                },
            }
            
            response = await client.post("/api/leads", json=payload)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_trip_group_size_validation(self):
        """Trip lead with invalid group size returns 422."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "type": "trip",
                "data": {
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                    "group_size": 0,  # Invalid: must be >= 1
                },
            }
            
            response = await client.post("/api/leads", json=payload)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_lead_with_session_id(self, mock_resend):
        """Lead with session_id is processed successfully."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            session_id = str(uuid4())
            payload = {
                "type": "training",
                "data": {
                    "name": "John Doe",
                    "email": "john@example.com",
                },
                "session_id": session_id,
            }
            
            with patch("app.api.routes.lead.capture_and_deliver_lead") as mock_capture:
                mock_lead_record = MagicMock()
                mock_lead_record.id = uuid4()
                mock_capture.return_value = mock_lead_record
                
                response = await client.post("/api/leads", json=payload)
        
        assert response.status_code == status.HTTP_201_CREATED
