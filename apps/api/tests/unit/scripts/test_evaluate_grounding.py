"""Unit tests for grounding evaluation script."""

from scripts.evaluate_grounding import evaluate_cases


def test_evaluate_cases_metrics():
    cases = [
        {
            "id": "grounded",
            "answer": "Open Water depth limit is 18 meters.",
            "citations": ["content/certifications/open-water.md"],
            "safety_flags": {"is_emergency": False},
        },
        {
            "id": "unsupported",
            "answer": "This site has 30 meter visibility year round.",
            "citations": [],
            "safety_flags": {"is_emergency": False},
        },
        {
            "id": "non_factual",
            "answer": "What destination are you planning for?",
            "citations": [],
            "safety_flags": {"is_emergency": False},
        },
    ]

    result = evaluate_cases(cases)

    assert result["total_cases"] == 3
    assert result["factual_cases"] == 2
    assert result["citation_rate"] == 0.5
    assert result["unsupported_claim_rate"] == 0.5


def test_evaluate_cases_quality_thresholds():
    cases = [
        {
            "id": "grounded_1",
            "answer": "Advanced Open Water is recommended before 30 meter depth dives.",
            "citations": ["content/certifications/aow.md"],
            "safety_flags": {"is_emergency": False},
        },
        {
            "id": "grounded_2",
            "answer": "Tiger Reef has strong current and is usually for experienced divers.",
            "citations": ["content/destinations/Malaysia-Tioman/tioman-tiger-reef.md"],
            "safety_flags": {"is_emergency": False},
        },
        {
            "id": "ungrounded",
            "answer": "This destination has 40 meter visibility year round.",
            "citations": [],
            "safety_flags": {"is_emergency": False},
        },
    ]

    result = evaluate_cases(cases)
    assert result["citation_rate"] >= 0.6
    assert result["unsupported_claim_rate"] <= 0.4
