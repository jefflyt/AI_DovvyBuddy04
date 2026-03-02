"""Unit tests for ADK shared tools."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.adk.tools import ADKToolbox
from app.services.rag.types import RAGContext, RetrievalResult


class _MockEmergencyDetector:
    def __init__(self, is_emergency: bool = False):
        self.is_emergency = is_emergency

    async def detect_emergency(self, message, conversation_history=None):
        return self.is_emergency, "Emergency response"


class _MockMedicalDetector:
    def __init__(self, is_medical: bool = False):
        self.is_medical = is_medical

    async def is_medical_query(self, message):
        return self.is_medical


@pytest.mark.asyncio
async def test_rag_search_tool_returns_contract():
    rag_context = RAGContext(
        query="tioman",
        results=[
            RetrievalResult(
                chunk_id="1",
                text="Tioman has sites from 9m to 25m.",
                similarity=0.91,
                metadata={"content_path": "content/destinations/tioman.md"},
            )
        ],
        formatted_context="Tioman has sites from 9m to 25m.",
        citations=["content/destinations/tioman.md"],
        has_data=True,
    )
    mock_rag_pipeline = SimpleNamespace(retrieve_context=AsyncMock(return_value=rag_context))

    toolbox = ADKToolbox(
        rag_pipeline=mock_rag_pipeline,
        emergency_detector=_MockEmergencyDetector(),
        medical_detector=_MockMedicalDetector(),
    )
    toolbox.set_turn_context(session_id="s1", message="Where to dive?", history=[])

    result = await toolbox.rag_search_tool("Where to dive in Tioman?")

    assert result["has_data"] is True
    assert result["citations"] == ["content/destinations/tioman.md"]
    assert len(result["chunks"]) == 1


@pytest.mark.asyncio
async def test_safety_classification_emergency_precedence():
    toolbox = ADKToolbox(
        rag_pipeline=SimpleNamespace(retrieve_context=AsyncMock()),
        emergency_detector=_MockEmergencyDetector(is_emergency=True),
        medical_detector=_MockMedicalDetector(is_medical=False),
    )
    toolbox.set_turn_context(session_id="s1", message="I have chest pain", history=[])

    result = await toolbox.safety_classification_tool("I have chest pain after diving")

    assert result["classification"] == "emergency"
    assert result["is_emergency"] is True
    assert result["is_medical"] is True


@pytest.mark.asyncio
async def test_session_context_tool_uses_turn_state():
    toolbox = ADKToolbox(
        rag_pipeline=SimpleNamespace(retrieve_context=AsyncMock()),
        emergency_detector=_MockEmergencyDetector(),
        medical_detector=_MockMedicalDetector(),
    )
    toolbox.set_turn_context(
        session_id="s123",
        message="hello",
        history=[{"role": "user", "content": "hi"}],
        session_state={"last_route": "trip_specialist"},
        diver_profile={"certification_level": "AOW"},
    )

    result = toolbox.session_context_tool()

    assert result["session_id"] == "s123"
    assert result["session_state"]["last_route"] == "trip_specialist"
    assert result["diver_profile"]["certification_level"] == "AOW"


def test_response_policy_enforces_citations_for_factual_claim():
    toolbox = ADKToolbox(
        rag_pipeline=SimpleNamespace(retrieve_context=AsyncMock()),
        emergency_detector=_MockEmergencyDetector(),
        medical_detector=_MockMedicalDetector(),
    )

    response = toolbox.response_policy_tool(
        answer="The minimum certification required is Advanced Open Water at 18 meters depth.",
        citations=[],
        safety_flags={"is_emergency": False},
    )

    assert response["policy_enforced"] is True
    assert response["should_append_uncertainty"] is True
    assert response["reason"] == "missing_citations_for_factual_claim"


def test_response_policy_allows_grounded_or_non_factual_answers():
    toolbox = ADKToolbox(
        rag_pipeline=SimpleNamespace(retrieve_context=AsyncMock()),
        emergency_detector=_MockEmergencyDetector(),
        medical_detector=_MockMedicalDetector(),
    )

    grounded = toolbox.response_policy_tool(
        answer="The minimum certification required is Advanced Open Water at 18 meters depth.",
        citations=["content/certifications/aow.md"],
        safety_flags={"is_emergency": False},
    )
    conversational = toolbox.response_policy_tool(
        answer="Could you share your certification level first?",
        citations=[],
        safety_flags={"is_emergency": False},
    )

    assert grounded["policy_enforced"] is False
    assert conversational["policy_enforced"] is False
