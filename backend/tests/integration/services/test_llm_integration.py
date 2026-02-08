"""
Integration tests for LLM providers.

Tests real API calls (marked as slow for CI).
"""

import pytest
import os

from app.core.config import settings
from app.services.llm import GeminiLLMProvider, LLMMessage


pytestmark = pytest.mark.slow


@pytest.fixture
def gemini_api_key():
    """Get Gemini API key from environment."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        pytest.skip("GEMINI_API_KEY not set")
    return key


@pytest.fixture
def gemini_provider(gemini_api_key):
    """Create real Gemini LLM provider."""
    return GeminiLLMProvider(api_key=gemini_api_key, model=settings.default_llm_model)


@pytest.fixture
def test_messages():
    """Test messages."""
    return [
        LLMMessage(role="system", content="You are a helpful diving assistant."),
        LLMMessage(role="user", content="What is buoyancy control in one sentence?"),
    ]


@pytest.mark.asyncio
async def test_gemini_generate(gemini_provider, test_messages):
    """Test real Gemini API call."""
    response = await gemini_provider.generate(test_messages)

    assert response.content
    assert len(response.content) > 10
    assert response.model == settings.default_llm_model


@pytest.mark.asyncio
async def test_gemini_usage_metadata_fields(gemini_provider, test_messages):
    """Test token usage fields are populated when usage_metadata is available."""
    response = await gemini_provider.generate(test_messages)

    if response.tokens_used is None:
        pytest.skip("Gemini usage_metadata not returned")

    assert response.prompt_tokens is not None
    assert response.completion_tokens is not None
    assert response.cost_usd is not None


@pytest.mark.asyncio
async def test_gemini_different_temperatures(gemini_provider):
    """Test Gemini with different temperatures."""
    messages = [
        LLMMessage(role="user", content="Say exactly: Hello"),
    ]

    # Temperature 0 (deterministic)
    response1 = await gemini_provider.generate(messages, temperature=0.0)

    # Temperature 1 (creative)
    response2 = await gemini_provider.generate(messages, temperature=1.0)

    assert response1.content
    assert response2.content
    # Both should respond, but content may differ


@pytest.mark.asyncio
async def test_gemini_conversation(gemini_provider):
    """Test Gemini with multi-turn conversation."""
    messages = [
        LLMMessage(role="system", content="You are a diving assistant."),
        LLMMessage(role="user", content="What is PADI?"),
        LLMMessage(role="assistant", content="PADI is a diving certification organization."),
        LLMMessage(role="user", content="What does it stand for?"),
    ]

    response = await gemini_provider.generate(messages)

    assert response.content
    assert "professional" in response.content.lower() or "association" in response.content.lower()
