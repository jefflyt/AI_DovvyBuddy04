"""
Unit tests for token utilities.
"""

from app.services.rag.token_utils import calculate_gemini_cost, count_tokens
from app.services.rag.chunker import count_tokens as count_tokens_chunker


def test_token_counting_utility_matches_chunker():
    text = "Diving in Tioman is great for beginners."
    assert count_tokens(text) == count_tokens_chunker(text)


def test_cost_calculation():
    # (100k * 0.15 + 50k * 0.60) / 1M = 0.045
    cost = calculate_gemini_cost(100_000, 50_000)
    assert cost == 0.045


def test_cost_calculation_edge_cases():
    assert calculate_gemini_cost(None, 100) is None
    assert calculate_gemini_cost(100, None) is None
    assert calculate_gemini_cost(0, 0) == 0.0
