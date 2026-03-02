"""Integration tests for chat streaming endpoint."""

import json
from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_chat_stream_emits_orchestrator_events_in_order():
    events = [
        {"type": "route", "content": {"route": "trip_specialist"}},
        {"type": "safety", "content": {"classification": "non_medical"}},
        {"type": "token", "content": "Hello "},
        {"type": "token", "content": "diver"},
        {"type": "citation", "content": "content/destinations/tioman.md"},
        {
            "type": "final",
            "content": "Hello diver",
            "metadata": {
                "sessionId": "session-1",
                "agentType": "trip",
                "metadata": {"route_decision": {"route": "trip_specialist"}},
            },
        },
    ]

    async def fake_stream_chat(_request):
        for event in events:
            yield event

    mock_orchestrator = MagicMock()
    mock_orchestrator.stream_chat = fake_stream_chat

    with patch("app.api.routes.chat.ChatOrchestrator", return_value=mock_orchestrator):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            async with client.stream(
                "POST",
                "/api/chat/stream",
                json={"message": "Plan a dive trip"},
            ) as response:
                assert response.status_code == 200
                payloads = []
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        payloads.append(json.loads(line[6:]))

    assert [payload["type"] for payload in payloads] == [
        "route",
        "safety",
        "token",
        "token",
        "citation",
        "final",
    ]
    assert payloads[-1]["content"] == "Hello diver"

