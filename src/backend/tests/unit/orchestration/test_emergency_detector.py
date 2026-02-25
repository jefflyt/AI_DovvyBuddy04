"""
Unit tests for EmergencyDetector.

Tests keyword-based emergency detection with symptom + first-person context.
"""

import pytest

from app.orchestration.emergency_detector import EmergencyDetector


@pytest.fixture
def detector():
    """Create EmergencyDetector instance for testing."""
    return EmergencyDetector()


class TestEmergencyDetection:
    """Test emergency detection with symptom + first-person context."""

    def test_emergency_chest_pain_first_person(self, detector):
        """Should detect emergency: symptom + first-person."""
        assert detector.is_emergency("I have chest pain after diving") is True

    def test_emergency_dizzy_first_person(self, detector):
        """Should detect emergency: symptom + first-person."""
        assert detector.is_emergency("I feel dizzy and numb") is True

    def test_emergency_breathing_difficulty_first_person(self, detector):
        """Should detect emergency: symptom + first-person."""
        assert detector.is_emergency("I can't breathe properly") is True

    def test_emergency_my_symptom(self, detector):
        """Should detect emergency: possessive first-person."""
        assert detector.is_emergency("my chest hurts after the dive") is True

    def test_emergency_during_dive(self, detector):
        """Should detect emergency: symptom + dive context."""
        assert detector.is_emergency("chest pain during diving") is True

    def test_emergency_post_dive(self, detector):
        """Should detect emergency: symptom + post-dive context."""
        assert detector.is_emergency("numbness after dive") is True

    def test_no_emergency_educational_query(self, detector):
        """Should NOT detect emergency: educational query without first-person."""
        assert detector.is_emergency("What is decompression sickness?") is False

    def test_no_emergency_symptom_explanation(self, detector):
        """Should NOT detect emergency: asking about symptoms."""
        assert detector.is_emergency("Can you explain DCS symptoms?") is False

    def test_no_emergency_learning_about_safety(self, detector):
        """Should NOT detect emergency: learning context."""
        assert detector.is_emergency("Tell me about chest pain in diving") is False

    def test_no_emergency_general_question(self, detector):
        """Should NOT detect emergency: general question."""
        assert detector.is_emergency("Where should I dive in Malaysia?") is False

    def test_no_emergency_symptom_without_context(self, detector):
        """Should NOT detect emergency: symptom alone without first-person or dive context."""
        assert detector.is_emergency("chest pain is a symptom of DCS") is False

    def test_no_emergency_certification_question(self, detector):
        """Should NOT detect emergency: certification question."""
        assert detector.is_emergency("What is Open Water certification?") is False

    def test_case_insensitive_matching(self, detector):
        """Should detect emergency: case-insensitive."""
        assert detector.is_emergency("I HAVE CHEST PAIN AFTER DIVING") is True
        assert detector.is_emergency("i feel dizzy") is True

    def test_symptom_in_longer_message(self, detector):
        """Should detect emergency: symptom in longer context with first-person."""
        message = (
            "I went diving yesterday and now I have chest pain. "
            "It started about 2 hours after I surfaced. Should I be worried?"
        )
        assert detector.is_emergency(message) is True

    def test_third_person_no_emergency(self, detector):
        """Should NOT detect emergency: third-person (not first-person)."""
        assert detector.is_emergency("My friend has chest pain") is False
        assert detector.is_emergency("The diver experienced numbness") is False

    def test_multiple_symptoms(self, detector):
        """Should detect emergency: multiple symptoms with first-person."""
        assert detector.is_emergency("I have chest pain and numbness") is True

    def test_emergency_response_message(self, detector):
        """Should return proper emergency response message."""
        response = detector.get_emergency_response()
        
        # Should contain key safety information
        assert "⚠️" in response
        assert "EMERGENCY" in response.upper()
        assert "911" in response or "112" in response
        assert "DAN" in response
        assert "+1-919-684-9111" in response
        assert "oxygen" in response.lower()


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_message(self, detector):
        """Should handle empty message."""
        assert detector.is_emergency("") is False

    def test_whitespace_only(self, detector):
        """Should handle whitespace-only message."""
        assert detector.is_emergency("   \n\t  ") is False

    def test_partial_symptom_match(self, detector):
        """Should match symptom keywords within larger words."""
        # "dizzy" should match even in "I'm feeling dizzy"
        assert detector.is_emergency("I'm feeling dizzy after diving") is True

    def test_symptom_at_end(self, detector):
        """Should detect symptom at end of message."""
        assert detector.is_emergency("After diving, I have chest pain") is True

    def test_symptom_at_beginning(self, detector):
        """Should detect symptom at beginning of message."""
        assert detector.is_emergency("Chest pain is what I'm experiencing after dive") is True

    def test_multiple_first_person_indicators(self, detector):
        """Should detect with multiple first-person indicators."""
        assert detector.is_emergency("I think my chest pain is getting worse") is True

    def test_contraction_im(self, detector):
        """Should detect contraction forms."""
        assert detector.is_emergency("I'm feeling numb after diving") is True
        assert detector.is_emergency("I've got chest pain") is True
