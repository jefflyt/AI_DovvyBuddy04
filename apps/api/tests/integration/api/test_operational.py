"""Operational endpoint tests."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.main import app


class _SessionContext:
    def __init__(self, session):
        self._session = session

    async def __aenter__(self):
        return self._session

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_health_endpoint_reports_healthy():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_ready_endpoint_reports_ready_when_dependencies_are_configured():
    mock_session = AsyncMock()

    def fake_session_factory():
        return _SessionContext(mock_session)

    with patch("app.main.get_session", return_value=fake_session_factory), patch.object(
        settings,
        "gemini_api_key",
        "test-key",
    ), patch.object(settings, "environment", "development"), patch.object(
        settings,
        "resend_api_key",
        "",
    ), patch.object(settings, "lead_email_to", ""):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["checks"]["database"] == "ok"
    assert response.json()["checks"]["llm"] == "configured"


@pytest.mark.asyncio
async def test_ready_endpoint_requires_lead_capture_in_production():
    mock_session = AsyncMock()

    def fake_session_factory():
        return _SessionContext(mock_session)

    with patch("app.main.get_session", return_value=fake_session_factory), patch.object(
        settings,
        "gemini_api_key",
        "test-key",
    ), patch.object(settings, "environment", "production"), patch.object(
        settings,
        "resend_api_key",
        "",
    ), patch.object(settings, "lead_email_to", ""):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert response.json()["checks"]["lead_capture"] == "missing"
