"""
Groq LLM provider implementation.

Uses Groq SDK for fast inference with Llama models.
"""

import logging
from typing import List, Optional

from groq import AsyncGroq
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


class GroqLLMProvider(LLMProvider):
    """LLM provider using Groq API."""

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        """
        Initialize Groq LLM provider.

        Args:
            api_key: Groq API key
            model: Model name (default: llama-3.3-70b-versatile)
            temperature: Default temperature (0.0-1.0)
            max_tokens: Default max tokens
        """
        if not api_key:
            raise ValueError("Groq API key is required")

        self.model = model
        self.default_temperature = temperature
        self.default_max_tokens = max_tokens

        # Initialize Groq client
        self.client = AsyncGroq(api_key=api_key)

        logger.info(f"Initialized GroqLLMProvider with model={model}")

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
        Generate a completion using Groq API.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (overrides default)
            max_tokens: Maximum tokens to generate (overrides default)
            **kwargs: Additional Groq-specific parameters

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

        # Convert messages to Groq format
        groq_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        try:
            # Call Groq API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=groq_messages,  # type: ignore[arg-type]
                temperature=temp,
                max_tokens=max_tok,
                **kwargs,
            )

            # Extract response
            content = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else None
            finish_reason = response.choices[0].finish_reason

            logger.info(
                f"Groq API call successful: tokens={tokens_used}, finish_reason={finish_reason}"
            )

            return LLMResponse(
                content=content,
                model=response.model,
                tokens_used=tokens_used,
                finish_reason=finish_reason,
            )

        except Exception as e:
            error_msg = str(e).lower()

            # Check for rate limit errors
            if "429" in error_msg or "rate limit" in error_msg:
                logger.warning(f"Rate limit hit: {e}")
                raise RateLimitError(str(e)) from e

            # Other errors
            logger.error(f"Groq API error: {e}")
            raise

    def get_model_name(self) -> str:
        """Get the name of the LLM model."""
        return self.model
