"""
Gemini LLM provider implementation.

Uses Google's Generative AI API for text generation.
"""

import asyncio
import logging
from typing import List, Optional, Tuple

from google import genai
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

        # Create Gemini client
        self.client = genai.Client(api_key=api_key)

        logger.info(f"Initialized GeminiLLMProvider with model={model}")

    def _messages_to_gemini_format(
        self, messages: List[LLMMessage]
    ) -> Tuple[Optional[str], str]:
        """
        Convert messages to Gemini format.

        Gemini's generate_content expects a simple string prompt when using system_instruction.

        Args:
            messages: List of LLMMessage objects

        Returns:
            Tuple of (system_instruction, user_prompt)
        """
        system_instruction = None
        user_messages = []

        for msg in messages:
            if msg.role == "system":
                # Gemini uses system_instruction parameter
                system_instruction = msg.content
            elif msg.role == "user":
                user_messages.append(msg.content)
            elif msg.role == "assistant":
                # For now, skip assistant messages in prompt
                # Multi-turn conversation would need chat session
                pass

        # Combine user messages into single prompt
        user_prompt = "\n\n".join(user_messages) if user_messages else ""

        return system_instruction, user_prompt

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
        system_instruction, user_prompt = self._messages_to_gemini_format(messages)

        try:
            # Prepare config
            config = {
                "temperature": temp,
                "max_output_tokens": max_tok,
            }
            
            # Add system instruction if provided
            if system_instruction:
                config["system_instruction"] = system_instruction
                
            config.update(kwargs)

            # Run synchronous API call in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.model,
                    contents=user_prompt,
                    config=config,
                ),
            )

            # Extract response
            content = response.text if hasattr(response, "text") else ""
            finish_reason = (
                response.candidates[0].finish_reason.name
                if hasattr(response, "candidates") and response.candidates
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
