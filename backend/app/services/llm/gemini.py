"""
Gemini LLM provider implementation.

Uses Google's Generative AI API for text generation.
"""

import asyncio
import logging
from typing import List, Optional, Tuple

import google.generativeai as genai
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings

from .base import LLMProvider
from .types import LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""

    pass


class GeminiLLMProvider(LLMProvider):
    """LLM provider using Google's Gemini API."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        """
        Initialize Gemini LLM provider.

        Args:
            api_key: Google API key
            model: Model name (default: gemini-2.0-flash per copilot-instructions.md)
            temperature: Default temperature (0.0-1.0)
            max_tokens: Default max tokens
        """
        if not api_key:
            raise ValueError("Gemini API key is required")

        self.model = model
        self.default_temperature = temperature
        self.default_max_tokens = max_tokens

        # Configure Gemini
        genai.configure(api_key=api_key)

        logger.info(f"Initialized GeminiLLMProvider with model={model}")

    def _messages_to_gemini_format(
        self, messages: List[LLMMessage]
    ) -> Tuple[Optional[str], List[dict]]:
        """
        Convert messages to Gemini format.

        Gemini uses system_instruction + conversation history format.

        Args:
            messages: List of LLMMessage objects

        Returns:
            Tuple of (system_instruction, conversation_messages)
        """
        system_instruction = None
        conversation = []

        for msg in messages:
            if msg.role == "system":
                # Gemini uses system_instruction parameter
                system_instruction = msg.content
            else:
                # Map role: "assistant" -> "model" for Gemini
                role = "model" if msg.role == "assistant" else "user"
                conversation.append({"role": role, "parts": [msg.content]})

        return system_instruction, conversation

    @retry(
        stop=stop_after_attempt(settings.llm_max_retries),
        wait=wait_exponential(
            multiplier=settings.llm_retry_delay,
            min=settings.llm_retry_delay,
            max=10,
        ),
        retry=retry_if_exception_type(RateLimitError),
        reraise=True,
    )
    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate a completion using Gemini API.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (overrides default)
            max_tokens: Maximum tokens to generate (overrides default)
            **kwargs: Additional Gemini-specific parameters

        Returns:
            LLMResponse with generated content

        Raises:
            ValueError: If messages are invalid
            RateLimitError: If rate limit is hit (will trigger retry)
            Exception: If API call fails
        """
        if not messages:
            raise ValueError("Messages cannot be empty")

        # Use defaults if not specified
        temp = temperature if temperature is not None else self.default_temperature
        max_tok = max_tokens if max_tokens is not None else self.default_max_tokens

        # Convert messages to Gemini format
        system_instruction, conversation = self._messages_to_gemini_format(messages)

        try:
            # Create model with configuration
            generation_config = genai.GenerationConfig(
                temperature=temp,
                max_output_tokens=max_tok,
                **kwargs,
            )

            model = genai.GenerativeModel(
                model_name=self.model,
                generation_config=generation_config,
                system_instruction=system_instruction,
            )

            # Run synchronous API call in thread pool
            loop = asyncio.get_event_loop()

            # If conversation history exists, use chat
            if len(conversation) > 1:
                chat = model.start_chat(history=conversation[:-1])  # type: ignore[arg-type]
                response = await loop.run_in_executor(
                    None,
                    lambda: chat.send_message(conversation[-1]["parts"][0]),
                )
            else:
                # Single message
                response = await loop.run_in_executor(
                    None,
                    lambda: model.generate_content(conversation[0]["parts"][0]),
                )

            # Extract response
            content = response.text if hasattr(response, "text") else ""
            finish_reason = (
                response.candidates[0].finish_reason.name
                if response.candidates
                else None
            )

            logger.info(f"Gemini API call successful: finish_reason={finish_reason}")

            return LLMResponse(
                content=content,
                model=self.model,
                tokens_used=None,  # Gemini doesn't return token count in all cases
                finish_reason=finish_reason,
            )

        except Exception as e:
            error_msg = str(e).lower()

            # Check for rate limit errors
            if "429" in error_msg or "rate limit" in error_msg or "quota" in error_msg:
                logger.warning(f"Rate limit hit: {e}")
                raise RateLimitError(str(e)) from e

            # Other errors
            logger.error(f"Gemini API error: {e}")
            raise

    def get_model_name(self) -> str:
        """Get the name of the LLM model."""
        return self.model
