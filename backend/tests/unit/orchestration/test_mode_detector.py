"""
Unit tests for mode detector.
"""

import pytest

from app.orchestration.mode_detector import ConversationMode, ModeDetector


def test_certification_mode_detection():
    """Test certification mode detection."""
    detector = ModeDetector()

    queries = [
        "What is PADI Open Water certification?",
        "How do I become SSI certified?",
        "What are the requirements for Advanced Open Water?",
        "Can I take the rescue diver course?",
    ]

    for query in queries:
        mode = detector.detect_mode(query)
        assert mode == ConversationMode.CERTIFICATION, f"Failed for: {query}"


def test_trip_mode_detection():
    """Test trip mode detection."""
    detector = ModeDetector()

    queries = [
        "Best dive sites in Thailand",
        "Where should I go diving in December?",
        "Recommend a destination for wreck diving",
        "What are the top dive resorts in Maldives?",
    ]

    for query in queries:
        mode = detector.detect_mode(query)
        assert mode == ConversationMode.TRIP, f"Failed for: {query}"


def test_safety_mode_detection():
    """Test safety mode detection."""
    detector = ModeDetector()

    queries = [
        "Can I dive with a cold?",
        "Is it safe to dive with asthma?",
        "What are the medical requirements for diving?",
        "I have a heart condition, can I dive?",
        "What should I do in an emergency?",
    ]

    for query in queries:
        mode = detector.detect_mode(query)
        assert mode == ConversationMode.SAFETY, f"Failed for: {query}"


def test_general_mode_detection():
    """Test general mode detection."""
    detector = ModeDetector()

    queries = [
        "What is scuba diving?",
        "Tell me about diving equipment",
        "How deep can you dive?",
    ]

    for query in queries:
        mode = detector.detect_mode(query)
        assert mode == ConversationMode.GENERAL, f"Failed for: {query}"


def test_safety_priority():
    """Test that safety mode takes priority."""
    detector = ModeDetector()

    # Query with both trip and safety keywords
    query = "Best destinations for diving with asthma?"
    mode = detector.detect_mode(query)

    # Safety should take priority
    assert mode == ConversationMode.SAFETY


def test_context_based_detection():
    """Test mode detection with conversation history."""
    detector = ModeDetector()

    history = [
        {"role": "user", "content": "Tell me about PADI certifications"},
        {"role": "assistant", "content": "PADI offers various certification levels..."},
    ]

    # Ambiguous follow-up should use context
    mode = detector.detect_mode("What about Advanced?", history)
    assert mode == ConversationMode.CERTIFICATION


def test_empty_query():
    """Test handling of edge cases."""
    detector = ModeDetector()

    mode = detector.detect_mode("")
    assert mode == ConversationMode.GENERAL


def test_is_follow_up_question():
    """Test follow-up question detection."""
    detector = ModeDetector()

    history = [
        {"role": "user", "content": "Tell me about diving"},
        {"role": "assistant", "content": "Diving is..."},
    ]

    # Short questions are likely follow-ups
    assert detector.is_follow_up_question("And what else?", history) is True
    assert detector.is_follow_up_question("Tell me more", history) is True

    # Long standalone questions are not follow-ups
    long_query = "What are the best diving destinations in Southeast Asia?"
    assert detector.is_follow_up_question(long_query, history) is False

    # No history means not a follow-up
    assert detector.is_follow_up_question("What about that?", None) is False
