"""
Unit tests for ConversationManager.

Tests LLM-based intent classification, state extraction, and follow-up generation with mocking.
"""

import json
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.orchestration.conversation_manager import (
    ConversationAnalysis,
    ConversationManager,
    IntentType,
    SessionState,
)
from app.services.llm.types import LLMResponse


@pytest.fixture
def mock_llm():
    """Create mock LLM provider."""
    llm = AsyncMock()
    return llm


@pytest.fixture
def manager_with_mock_llm(mock_llm):
    """Create ConversationManager with mocked LLM."""
    with patch(
        "app.orchestration.conversation_manager.create_llm_provider",
        return_value=mock_llm,
    ):
        manager = ConversationManager()
        manager.llm = mock_llm
        return manager


class TestIntentClassification:
    """Test intent classification with mocked LLM responses."""

    @pytest.mark.asyncio
    async def test_dive_planning_intent(self, manager_with_mock_llm, mock_llm):
        """Should classify DIVE_PLANNING intent."""
        mock_llm.generate.return_value = LLMResponse(
            content=json.dumps({
                "intent": "DIVE_PLANNING",
                "state_updates": {"context_mode": "planning"},
                "follow_up": "Which destination are you considering?",
                "confidence": 0.9,
            }),
            model="test-model",
        )

        analysis = await manager_with_mock_llm.analyze(
            message="I want to plan a dive trip to Malaysia",
            history=[],
            state=SessionState(),
        )

        assert analysis.intent == IntentType.DIVE_PLANNING
        assert analysis.confidence == 0.9
        assert "destination" in analysis.follow_up.lower()

    @pytest.mark.asyncio
    async def test_info_lookup_intent(self, manager_with_mock_llm, mock_llm):
        """Should classify INFO_LOOKUP intent."""
        mock_llm.generate.return_value = LLMResponse(
            content=json.dumps({
                "intent": "INFO_LOOKUP",
                "state_updates": {},
                "follow_up": "Is this for learning or planning?",
                "confidence": 0.85,
            }),
            model="test-model",
        )

        analysis = await manager_with_mock_llm.analyze(
            message="What is a DSMB?",
            history=[],
            state=SessionState(),
        )

        assert analysis.intent == IntentType.INFO_LOOKUP
        assert analysis.confidence == 0.85

    @pytest.mark.asyncio
    async def test_agency_cert_intent(self, manager_with_mock_llm, mock_llm):
        """Should classify AGENCY_CERT intent."""
        mock_llm.generate.return_value = LLMResponse(
            content=json.dumps({
                "intent": "AGENCY_CERT",
                "state_updates": {"context_mode": "learning"},
                "follow_up": "Which certification level are you interested in?",
                "confidence": 0.88,
            }),
            model="test-model",
        )

        analysis = await manager_with_mock_llm.analyze(
            message="Tell me about Open Water certification",
            history=[],
            state=SessionState(),
        )

        assert analysis.intent == IntentType.AGENCY_CERT


class TestStateExtraction:
    """Test session state extraction from LLM."""

    @pytest.mark.asyncio
    async def test_cert_level_extraction(self, manager_with_mock_llm, mock_llm):
        """Should extract cert_level from message."""
        mock_llm.generate.return_value = LLMResponse(
            content=json.dumps({
                "intent": "INFO_LOOKUP",
                "state_updates": {"cert_level": "OW"},
                "follow_up": "What would you like to know?",
                "confidence": 0.9,
            }),
            model="test-model",
        )

        analysis = await manager_with_mock_llm.analyze(
            message="I'm Open Water certified",
            history=[],
            state=SessionState(),
        )

        assert analysis.state_updates.get("cert_level") == "OW"

    @pytest.mark.asyncio
    async def test_context_mode_extraction(self, manager_with_mock_llm, mock_llm):
        """Should extract context_mode from message."""
        mock_llm.generate.return_value = LLMResponse(
            content=json.dumps({
                "intent": "DIVE_PLANNING",
                "state_updates": {"context_mode": "planning", "location_known": True},
                "follow_up": "When are you planning to go?",
                "confidence": 0.92,
            }),
            model="test-model",
        )

        analysis = await manager_with_mock_llm.analyze(
            message="I'm planning a trip to Tioman",
            history=[],
            state=SessionState(),
        )

        assert analysis.state_updates.get("context_mode") == "planning"
        assert analysis.state_updates.get("location_known") is True

    @pytest.mark.asyncio
    async def test_multiple_state_updates(self, manager_with_mock_llm, mock_llm):
        """Should extract multiple state fields."""
        mock_llm.generate.return_value = LLMResponse(
            content=json.dumps({
                "intent": "DIVE_PLANNING",
                "state_updates": {
                    "cert_level": "AOW",
                    "context_mode": "planning",
                    "location_known": True,
                },
                "follow_up": "What dates work for you?",
                "confidence": 0.9,
            }),
            model="test-model",
        )

        analysis = await manager_with_mock_llm.analyze(
            message="I'm AOW certified and want to dive in Sipadan",
            history=[],
            state=SessionState(),
        )

        assert analysis.state_updates.get("cert_level") == "AOW"
        assert analysis.state_updates.get("context_mode") == "planning"
        assert analysis.state_updates.get("location_known") is True


class TestFollowUpGeneration:
    """Test follow-up question generation and validation."""

    @pytest.mark.asyncio
    async def test_valid_follow_up(self, manager_with_mock_llm, mock_llm):
        """Should accept valid follow-up question."""
        mock_llm.generate.return_value = LLMResponse(
            content=json.dumps({
                "intent": "INFO_LOOKUP",
                "state_updates": {},
                "follow_up": "Is this for learning or planning?",
                "confidence": 0.85,
            }),
            model="test-model",
        )

        analysis = await manager_with_mock_llm.analyze(
            message="What is nitrox?",
            history=[],
            state=SessionState(),
        )

        assert analysis.follow_up == "Is this for learning or planning?"

    @pytest.mark.asyncio
    async def test_follow_up_too_long_fallback(self, manager_with_mock_llm, mock_llm):
        """Should fall back to template if follow-up too long."""
        mock_llm.generate.return_value = LLMResponse(
            content=json.dumps({
                "intent": "INFO_LOOKUP",
                "state_updates": {},
                "follow_up": "This is a really long follow-up question that exceeds the 100 character limit and should be rejected by validation?",
                "confidence": 0.85,
            }),
            model="test-model",
        )

        analysis = await manager_with_mock_llm.analyze(
            message="What is nitrox?",
            history=[],
            state=SessionState(),
        )

        # Should fall back to template
        assert len(analysis.follow_up) <= 100
        assert "?" in analysis.follow_up

    @pytest.mark.asyncio
    async def test_follow_up_missing_question_mark_fallback(self, manager_with_mock_llm, mock_llm):
        """Should fall back to template if follow-up missing ?."""
        mock_llm.generate.return_value = LLMResponse(
            content=json.dumps({
                "intent": "INFO_LOOKUP",
                "state_updates": {},
                "follow_up": "Tell me more about your diving experience",
                "confidence": 0.85,
            }),
            model="test-model",
        )

        analysis = await manager_with_mock_llm.analyze(
            message="What is a DSMB?",
            history=[],
            state=SessionState(),
        )

        # Should fall back to template (which has ?)
        assert analysis.follow_up.endswith("?")

    @pytest.mark.asyncio
    async def test_follow_up_contains_numbers_fallback(self, manager_with_mock_llm, mock_llm):
        """Should fall back to template if follow-up contains numbers."""
        mock_llm.generate.return_value = LLMResponse(
            content=json.dumps({
                "intent": "DIVE_PLANNING",
                "state_updates": {},
                "follow_up": "Would you like to dive to 30m depth?",
                "confidence": 0.85,
            }),
            model="test-model",
        )

        analysis = await manager_with_mock_llm.analyze(
            message="Where should I dive?",
            history=[],
            state=SessionState(),
        )

        # Should fall back to template (no numbers)
        assert not any(char.isdigit() for char in analysis.follow_up)

    @pytest.mark.asyncio
    async def test_no_follow_up_for_emergency(self, manager_with_mock_llm, mock_llm):
        """Should return None for EMERGENCY_MEDICAL intent."""
        mock_llm.generate.return_value = LLMResponse(
            content=json.dumps({
                "intent": "EMERGENCY_MEDICAL",
                "state_updates": {},
                "follow_up": "",
                "confidence": 0.95,
            }),
            model="test-model",
        )

        analysis = await manager_with_mock_llm.analyze(
            message="Emergency message",  # Note: actual emergency detection is keyword-based
            history=[],
            state=SessionState(),
        )

        # Validation should return None for emergency intent
        assert analysis.follow_up is None or analysis.follow_up == ""


class TestConfidenceHandling:
    """Test confidence-based fallback behavior."""

    @pytest.mark.asyncio
    async def test_low_confidence_forces_info_lookup(self, manager_with_mock_llm, mock_llm):
        """Should force INFO_LOOKUP intent when confidence < 0.4."""
        mock_llm.generate.return_value = LLMResponse(
            content=json.dumps({
                "intent": "DIVE_PLANNING",
                "state_updates": {"cert_level": "AOW"},
                "follow_up": "Which destination?",
                "confidence": 0.3,  # Low confidence
            }),
            model="test-model",
        )

        analysis = await manager_with_mock_llm.analyze(
            message="Ambiguous message",
            history=[],
            state=SessionState(),
        )

        assert analysis.intent == IntentType.INFO_LOOKUP
        assert analysis.confidence == 0.3
        assert analysis.state_updates == {}  # State updates skipped

    @pytest.mark.asyncio
    async def test_normal_confidence_uses_detected_intent(self, manager_with_mock_llm, mock_llm):
        """Should use detected intent when confidence >= 0.4."""
        mock_llm.generate.return_value = LLMResponse(
            content=json.dumps({
                "intent": "DIVE_PLANNING",
                "state_updates": {"context_mode": "planning"},
                "follow_up": "Which destination?",
                "confidence": 0.75,
            }),
            model="test-model",
        )

        analysis = await manager_with_mock_llm.analyze(
            message="I want to plan a dive",
            history=[],
            state=SessionState(),
        )

        assert analysis.intent == IntentType.DIVE_PLANNING
        assert analysis.state_updates.get("context_mode") == "planning"


class TestErrorHandling:
    """Test error handling and fallbacks."""

    @pytest.mark.asyncio
    async def test_llm_timeout_fallback(self, manager_with_mock_llm, mock_llm):
        """Should return fallback analysis on LLM timeout."""
        mock_llm.generate.side_effect = TimeoutError("LLM timeout")

        analysis = await manager_with_mock_llm.analyze(
            message="Test message",
            history=[],
            state=SessionState(),
        )

        assert analysis.intent == IntentType.INFO_LOOKUP
        assert analysis.confidence == 0.0
        assert analysis.follow_up is not None

    @pytest.mark.asyncio
    async def test_invalid_json_fallback(self, manager_with_mock_llm, mock_llm):
        """Should return fallback analysis on invalid JSON."""
        mock_llm.generate.return_value = LLMResponse(
            content="This is not JSON",
            model="test-model",
        )

        analysis = await manager_with_mock_llm.analyze(
            message="Test message",
            history=[],
            state=SessionState(),
        )

        assert analysis.intent == IntentType.INFO_LOOKUP
        assert analysis.confidence == 0.0

    @pytest.mark.asyncio
    async def test_missing_intent_field_fallback(self, manager_with_mock_llm, mock_llm):
        """Should use INFO_LOOKUP if intent field missing."""
        mock_llm.generate.return_value = LLMResponse(
            content=json.dumps({
                # Intent field missing
                "state_updates": {},
                "follow_up": "What can I help with?",
                "confidence": 0.8,
            }),
            model="test-model",
        )

        analysis = await manager_with_mock_llm.analyze(
            message="Test message",
            history=[],
            state=SessionState(),
        )

        assert analysis.intent == IntentType.INFO_LOOKUP

    @pytest.mark.asyncio
    async def test_invalid_state_updates_type(self, manager_with_mock_llm, mock_llm):
        """Should skip state_updates if not a dict."""
        mock_llm.generate.return_value = LLMResponse(
            content=json.dumps({
                "intent": "INFO_LOOKUP",
                "state_updates": "not a dict",  # Invalid type
                "follow_up": "What can I help with?",
                "confidence": 0.8,
            }),
            model="test-model",
        )

        analysis = await manager_with_mock_llm.analyze(
            message="Test message",
            history=[],
            state=SessionState(),
        )

        assert analysis.state_updates == {}


class TestSessionStateDataclass:
    """Test SessionState dataclass methods."""

    def test_to_dict(self):
        """Should convert to dict."""
        state = SessionState(
            cert_level="OW",
            context_mode="planning",
            location_known=True,
            conditions_known=False,
            last_intent="DIVE_PLANNING",
        )

        result = state.to_dict()

        assert result["cert_level"] == "OW"
        assert result["context_mode"] == "planning"
        assert result["location_known"] is True
        assert result["conditions_known"] is False
        assert result["last_intent"] == "DIVE_PLANNING"

    def test_from_dict(self):
        """Should create from dict."""
        data = {
            "cert_level": "AOW",
            "context_mode": "learning",
            "location_known": False,
            "conditions_known": True,
            "last_intent": "INFO_LOOKUP",
        }

        state = SessionState.from_dict(data)

        assert state.cert_level == "AOW"
        assert state.context_mode == "learning"
        assert state.location_known is False
        assert state.conditions_known is True
        assert state.last_intent == "INFO_LOOKUP"

    def test_from_dict_with_missing_fields(self):
        """Should handle missing fields gracefully."""
        data = {"cert_level": "OW"}

        state = SessionState.from_dict(data)

        assert state.cert_level == "OW"
        assert state.context_mode is None
        assert state.location_known is False
        assert state.conditions_known is False
