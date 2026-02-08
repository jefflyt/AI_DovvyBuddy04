"""
Unit tests for GeminiOrchestrator routing heuristics and prompt size.
"""

from unittest.mock import patch

from app.orchestration.gemini_orchestrator import GeminiOrchestrator
from app.services.rag.chunker import count_tokens


def test_routing_prompt_token_count():
    assert count_tokens(GeminiOrchestrator.ROUTING_SYSTEM_INSTRUCTION) <= 70


def test_heuristic_routing_trip():
    with patch("google.genai.Client"):
        orchestrator = GeminiOrchestrator()
    result = orchestrator._quick_route_heuristic("Where can I dive in Bali?")
    assert result is not None
    assert result["target_agent"] == "trip_planner"


def test_heuristic_routing_info():
    with patch("google.genai.Client"):
        orchestrator = GeminiOrchestrator()
    result = orchestrator._quick_route_heuristic("What is a BCD?")
    assert result is not None
    assert result["target_agent"] == "knowledge_base"


def test_heuristic_routing_ambiguous():
    with patch("google.genai.Client"):
        orchestrator = GeminiOrchestrator()
    result = orchestrator._quick_route_heuristic("Tell me about diving")
    assert result is None
