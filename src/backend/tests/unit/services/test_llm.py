"""
Unit tests for LLM providers.

Tests LLM generation with mocked API calls.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.llm import GroqLLMProvider, GeminiLLMProvider, LLMMessage, LLMResponse
from app.services.llm.factory import create_llm_provider


@pytest.fixture
def groq_provider():
    """Create a Groq LLM provider with mocked API."""
    return GroqLLMProvider(api_key="test-key")


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


class TestGroqLLMProvider:
    """Test Groq LLM provider."""

    def test_initialization(self):
        """Test provider initialization."""
        provider = GroqLLMProvider(api_key="test-key", model="llama-3.3-70b-versatile")
        assert provider.model == "llama-3.3-70b-versatile"
        assert provider.default_temperature == 0.7
        assert provider.default_max_tokens == 2048

    def test_initialization_without_api_key(self):
        """Test that initialization fails without API key."""
        with pytest.raises(ValueError, match="API key is required"):
            GroqLLMProvider(api_key="")

    @pytest.mark.asyncio
    async def test_generate_success(self, groq_provider, test_messages):
        """Test successful generation."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello! How can I help you?"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "llama-3.3-70b-versatile"
        mock_response.usage = MagicMock()
        mock_response.usage.total_tokens = 50

        with patch.object(
            groq_provider.client.chat.completions, "create", new=AsyncMock(return_value=mock_response)
        ):
            result = await groq_provider.generate(test_messages)

            assert isinstance(result, LLMResponse)
            assert result.content == "Hello! How can I help you?"
            assert result.model == "llama-3.3-70b-versatile"
            assert result.tokens_used == 50
            assert result.finish_reason == "stop"

    @pytest.mark.asyncio
    async def test_generate_empty_messages_raises(self, groq_provider):
        """Test that empty messages raise ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            await groq_provider.generate([])

    @pytest.mark.asyncio
    async def test_generate_with_custom_params(self, groq_provider, test_messages):
        """Test generation with custom temperature and max_tokens."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.model = "llama-3.3-70b-versatile"
        mock_response.usage = None

        with patch.object(
            groq_provider.client.chat.completions, "create", new=AsyncMock(return_value=mock_response)
        ) as mock_create:
            result = await groq_provider.generate(
                test_messages, temperature=0.5, max_tokens=1000
            )

            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args.kwargs
            assert call_kwargs["temperature"] == 0.5
            assert call_kwargs["max_tokens"] == 1000

    def test_get_model_name(self, groq_provider):
        """Test get_model_name method."""
        assert groq_provider.get_model_name() == "llama-3.3-70b-versatile"


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
    def test_create_groq_provider(self, mock_settings):
        """Test creating Groq provider."""
        mock_settings.default_llm_provider = "groq"
        mock_settings.groq_api_key = "test-groq-key"
        mock_settings.default_llm_model = "llama-3.3-70b-versatile"
        mock_settings.llm_temperature = 0.7
        mock_settings.llm_max_tokens = 2048

        provider = create_llm_provider()

        assert isinstance(provider, GroqLLMProvider)
        assert provider.model == "llama-3.3-70b-versatile"

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
    def test_create_provider_unknown_raises(self, mock_settings):
        """Test that unknown provider raises ValueError."""
        mock_settings.default_llm_provider = "unknown"

        with pytest.raises(ValueError, match="Unknown LLM provider"):
            create_llm_provider()
