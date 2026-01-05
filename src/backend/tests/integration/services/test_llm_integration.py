"""
Integration tests for LLM providers.

Tests real API calls (marked as slow for CI).
"""

import pytest
import os

from app.services.llm import GroqLLMProvider, GeminiLLMProvider, LLMMessage


pytestmark = pytest.mark.slow


@pytest.fixture
def groq_api_key():
    """Get Groq API key from environment."""
    key = os.getenv("GROQ_API_KEY")
    if not key:
        pytest.skip("GROQ_API_KEY not set")
    return key


@pytest.fixture
def gemini_api_key():
    """Get Gemini API key from environment."""
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        pytest.skip("GEMINI_API_KEY not set")
    return key


@pytest.fixture
def groq_provider(groq_api_key):
    """Create real Groq LLM provider."""
    return GroqLLMProvider(api_key=groq_api_key)


@pytest.fixture
def gemini_provider(gemini_api_key):
    """Create real Gemini LLM provider."""
    return GeminiLLMProvider(api_key=gemini_api_key, model="gemini-2.0-flash")


@pytest.fixture
def test_messages():
    """Test messages."""
    return [
        LLMMessage(role="system", content="You are a helpful diving assistant."),
        LLMMessage(role="user", content="What is buoyancy control in one sentence?"),
    ]


@pytest.mark.asyncio
async def test_groq_generate(groq_provider, test_messages):
    """Test real Groq API call."""
    response = await groq_provider.generate(test_messages)

    assert response.content
    assert len(response.content) > 10
    assert response.model
    assert response.tokens_used is not None
    assert response.tokens_used > 0


@pytest.mark.asyncio
async def test_gemini_generate(gemini_provider, test_messages):
    """Test real Gemini API call."""
    response = await gemini_provider.generate(test_messages)

    assert response.content
    assert len(response.content) > 10
    assert response.model == "gemini-2.0-flash"


@pytest.mark.asyncio
async def test_groq_different_temperatures(groq_provider):
    """Test Groq with different temperatures."""
    messages = [
        LLMMessage(role="user", content="Say exactly: Hello"),
    ]

    # Temperature 0 (deterministic)
    response1 = await groq_provider.generate(messages, temperature=0.0)

    # Temperature 1 (creative)
    response2 = await groq_provider.generate(messages, temperature=1.0)

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
