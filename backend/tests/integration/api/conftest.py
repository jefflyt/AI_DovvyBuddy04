"""Pytest fixtures for integration tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4


@pytest.fixture(autouse=True)
def mock_database():
    """Mock database session for all tests."""
    from app.db.session import get_db
    from app.main import app
    
    async def mock_get_db():
        """Mock database session generator."""
        mock_session = AsyncMock()
        
        # Mock execute method for database queries
        mock_result = MagicMock()
        mock_lead = MagicMock()
        mock_lead.id = uuid4()
        mock_lead.type = "training"
        mock_lead.request_details = {}
        mock_lead.diver_profile = None
        mock_lead.created_at = MagicMock()
        
        mock_result.scalar_one.return_value = mock_lead
        mock_session.execute.return_value = mock_result
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        yield mock_session
    
    # Override the dependency
    app.dependency_overrides[get_db] = mock_get_db
    
    yield
    
    # Clean up
    app.dependency_overrides.clear()


