"""
Unit tests for LLM providers.

Tests LLM generation with mocked API calls.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.llm import GeminiLLMProvider, LLMMessage, LLMResponse
from app.services.llm.factory import create_llm_provider


@pytest.fixture
def gemini_provider():
    """Create a Gemini LLM provider with mocked API."""
    with patch("google.genai.Client"):
        provider = GeminiLLMProvider(api_key="test-key")
        return provider


@pytest.fixture
def test_messages():
    """Test messages."""
    return [
        LLMMessage(role="system", content="You are a helpful assistant."),
        LLMMessage(role="user", content="Hello!"),
    ]


class TestGeminiLLMProvider:
    """Test Gemini LLM provider."""

    def test_initialization(self):
        """Test provider initialization."""
        with patch("google.genai.Client"):
            provider = GeminiLLMProvider(api_key="test-key", model="gemini-2.0-flash")
            assert provider.model == "gemini-2.0-flash"
            assert provider.default_temperature == 0.7
            assert provider.default_max_tokens == 2048

    def test_initialization_without_api_key(self):
        """Test that initialization fails without API key."""
        with pytest.raises(ValueError, match="API key is required"):
            GeminiLLMProvider(api_key="")

    def test_messages_to_gemini_format(self, gemini_provider):
        """Test message format conversion."""
        messages = [
            LLMMessage(role="system", content="You are helpful."),
            LLMMessage(role="user", content="Hello"),
            LLMMessage(role="assistant", content="Hi there!"),
            LLMMessage(role="user", content="How are you?"),
        ]

        system_instruction, conversation = gemini_provider._messages_to_gemini_format(
            messages
        )

        assert system_instruction == "You are helpful."
        assert len(conversation) == 3
        assert conversation[0]["role"] == "user"
        assert conversation[1]["role"] == "model"  # assistant -> model
        assert conversation[2]["role"] == "user"

    @pytest.mark.asyncio
    async def test_generate_empty_messages_raises(self, gemini_provider):
        """Test that empty messages raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await gemini_provider.generate([])

    def test_get_model_name(self, gemini_provider):
        """Test get_model_name method."""
        assert gemini_provider.get_model_name() == "gemini-2.0-flash"


class TestLLMFactory:
    """Test LLM provider factory."""

    @patch("app.core.config.settings")
    @patch("google.genai.Client")
    def test_create_gemini_provider(self, mock_client, mock_settings):
        """Test creating Gemini provider."""
        mock_settings.default_llm_provider = "gemini"
        mock_settings.gemini_api_key = "test-gemini-key"
        mock_settings.default_llm_model = "gemini-2.0-flash"
        mock_settings.llm_temperature = 0.7
        mock_settings.llm_max_tokens = 2048

        provider = create_llm_provider()

        assert isinstance(provider, GeminiLLMProvider)
        assert provider.model == "gemini-2.0-flash"

    @patch("app.core.config.settings")
    @patch("google.genai.Client")
    def test_create_groq_provider_fallback(self, mock_client, mock_settings):
        """Test that Groq provider request falls back to Gemini."""
        mock_settings.default_llm_provider = "groq"
        mock_settings.gemini_api_key = "test-gemini-key"
        mock_settings.llm_temperature = 0.7
        mock_settings.llm_max_tokens = 2048

        provider = create_llm_provider(provider_name="groq")

        # Should fallback to Gemini
        assert isinstance(provider, GeminiLLMProvider)

    @patch("app.services.llm.factory.settings")
    def test_create_provider_unknown_raises(self, mock_settings):
        """Test that unknown provider raises ValueError."""
        mock_settings.default_llm_provider = "unknown"
        mock_settings.llm_temperature = 0.7
        mock_settings.llm_max_tokens = 2048

        with pytest.raises(ValueError, match="Unknown LLM provider"):
            create_llm_provider()
