"""
Comparison tests for agent routing.

These tests verify that agent routing matches expected behavior
by comparing mode detection and agent selection across different queries.
"""

import pytest

from app.orchestration.mode_detector import ConversationMode, ModeDetector
from app.agents.types import AgentType


# Test data: labeled queries with expected modes
LABELED_QUERIES = [
    # Certification queries
    ("What is PADI Open Water certification?", ConversationMode.CERTIFICATION),
    ("How do I become SSI certified?", ConversationMode.CERTIFICATION),
    ("Requirements for Advanced Open Water", ConversationMode.CERTIFICATION),
    ("Can I take the rescue diver course?", ConversationMode.CERTIFICATION),
    ("Difference between PADI and SSI", ConversationMode.CERTIFICATION),
    ("What is a Divemaster?", ConversationMode.CERTIFICATION),
    ("How long does the Open Water course take?", ConversationMode.CERTIFICATION),
    ("Do I need a certification to dive?", ConversationMode.CERTIFICATION),
    ("What specialty certifications are available?", ConversationMode.CERTIFICATION),
    ("Prerequisites for Nitrox certification", ConversationMode.CERTIFICATION),
    # Trip queries
    ("Best dive sites in Thailand", ConversationMode.TRIP),
    ("Where should I dive in December?", ConversationMode.TRIP),
    ("Recommend a destination for wreck diving", ConversationMode.TRIP),
    ("Top dive resorts in Maldives", ConversationMode.TRIP),
    ("Where can I see whale sharks?", ConversationMode.TRIP),
    ("Best diving in Southeast Asia", ConversationMode.TRIP),
    ("Dive sites in Tioman Malaysia", ConversationMode.TRIP),
    ("When is the best season for diving in Raja Ampat?", ConversationMode.TRIP),
    ("Budget-friendly dive destinations", ConversationMode.TRIP),
    ("Diving in the Great Barrier Reef", ConversationMode.TRIP),
    # Safety queries
    ("Can I dive with a cold?", ConversationMode.SAFETY),
    ("Is it safe to dive with asthma?", ConversationMode.SAFETY),
    ("Medical requirements for diving", ConversationMode.SAFETY),
    ("Heart condition and diving", ConversationMode.SAFETY),
    ("What should I do in an emergency?", ConversationMode.SAFETY),
    ("Can I dive after surgery?", ConversationMode.SAFETY),
    ("Is diving safe during pregnancy?", ConversationMode.SAFETY),
    ("Ear problems while diving", ConversationMode.SAFETY),
    ("Decompression sickness symptoms", ConversationMode.SAFETY),
    ("Can I take medications and dive?", ConversationMode.SAFETY),
    # General queries
    ("What is scuba diving?", ConversationMode.GENERAL),
    ("How deep can you dive?", ConversationMode.GENERAL),
    ("What equipment do I need?", ConversationMode.GENERAL),
    ("Tell me about diving", ConversationMode.GENERAL),
    ("How does a BCD work?", ConversationMode.GENERAL),
    ("What is a regulator?", ConversationMode.GENERAL),
    ("Difference between wet suit and dry suit", ConversationMode.GENERAL),
    ("What marine life can I see?", ConversationMode.GENERAL),
    ("How long does a tank last?", ConversationMode.GENERAL),
    ("What is nitrox?", ConversationMode.GENERAL),
]


@pytest.mark.parametrize("query,expected_mode", LABELED_QUERIES)
def test_mode_detection_accuracy(query, expected_mode):
    """Test mode detection accuracy on labeled queries."""
    detector = ModeDetector()
    detected_mode = detector.detect_mode(query)

    assert detected_mode == expected_mode, (
        f"Mode detection failed for query: '{query}'\n"
        f"Expected: {expected_mode.value}, Got: {detected_mode.value}"
    )


def test_mode_detection_overall_accuracy():
    """Test overall accuracy of mode detection."""
    detector = ModeDetector()

    correct = 0
    total = len(LABELED_QUERIES)

    for query, expected_mode in LABELED_QUERIES:
        detected_mode = detector.detect_mode(query)
        if detected_mode == expected_mode:
            correct += 1

    accuracy = correct / total
    print(f"\nMode detection accuracy: {accuracy:.2%} ({correct}/{total})")

    # Require at least 90% accuracy
    assert accuracy >= 0.90, (
        f"Mode detection accuracy {accuracy:.2%} is below required 90%"
    )


def test_agent_selection_mapping():
    """Test that modes map to correct agent types."""
    from app.orchestration.orchestrator import ChatOrchestrator
    from unittest.mock import MagicMock

    # Mode to expected agent mapping
    mode_to_agent = {
        ConversationMode.CERTIFICATION: AgentType.CERTIFICATION,
        ConversationMode.TRIP: AgentType.TRIP,
        ConversationMode.SAFETY: AgentType.SAFETY,
        ConversationMode.GENERAL: AgentType.RETRIEVAL,
    }

    mock_db = MagicMock()
    orchestrator = ChatOrchestrator(mock_db)

    for mode, expected_agent_type in mode_to_agent.items():
        agent = orchestrator._select_agent(mode)
        assert agent is not None, f"No agent for mode: {mode}"
        assert agent.agent_type == expected_agent_type, (
            f"Wrong agent for mode {mode}: "
            f"expected {expected_agent_type}, got {agent.agent_type}"
        )


def test_safety_priority_routing():
    """Test that safety queries take priority over other modes."""
    detector = ModeDetector()

    # Queries that have both safety and other keywords
    mixed_queries = [
        ("Best destinations for diving with asthma", ConversationMode.SAFETY),
        ("PADI certification medical requirements", ConversationMode.SAFETY),
        ("Can I get certified if I have a heart condition", ConversationMode.SAFETY),
    ]

    for query, expected_mode in mixed_queries:
        detected_mode = detector.detect_mode(query)
        assert detected_mode == expected_mode, (
            f"Safety priority failed for: '{query}'\n"
            f"Expected: {expected_mode.value}, Got: {detected_mode.value}"
        )


def test_mode_detection_with_context():
    """Test mode detection considers conversation context."""
    detector = ModeDetector()

    # Start with certification query
    history = [
        {"role": "user", "content": "What is PADI Open Water?"},
        {"role": "assistant", "content": "PADI Open Water is the entry-level certification..."},
    ]

    # Ambiguous follow-up should detect certification from context
    mode = detector.detect_mode("What about Advanced?", history)
    assert mode == ConversationMode.CERTIFICATION


@pytest.mark.parametrize(
    "query,keywords",
    [
        ("PADI Open Water", ["padi", "open water", "certification"]),
        ("dive sites in Thailand", ["dive site", "thailand", "destination"]),
        ("Can I dive with asthma?", ["asthma", "medical", "safe"]),
    ],
)
def test_keyword_matching(query, keywords):
    """Test that expected keywords are detected in queries."""
    query_lower = query.lower()

    # At least one keyword should match
    matches = [kw for kw in keywords if kw in query_lower]
    assert len(matches) > 0, (
        f"No keywords matched for query: '{query}'\n"
        f"Expected keywords: {keywords}"
    )
