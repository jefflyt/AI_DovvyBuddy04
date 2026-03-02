"""
Gemini LLM provider implementation.

Uses Google's Generative AI API for text generation.
"""

import asyncio
import logging
from typing import List, Optional, Tuple

import google.genai as genai
from google.genai import types
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.core.quota_manager import QuotaExceededError, get_quota_manager
from app.services.cost.token_cost import (
    calculate_gemini_cost,
    estimate_tokens_from_text,
)
from app.services.llm.base import LLMProvider, LLMResponse
from app.services.llm.types import LLMMessage

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""
    pass


class GeminiLLMProvider(LLMProvider):
    """Google Gemini LLM provider implementation."""

    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ):
        """
        Initialize Gemini LLM provider.
        """
        if not api_key:
            raise ValueError("Gemini API key is required")

        self.api_key = api_key
        self.model = model or settings.default_llm_model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Create Gemini Client (New SDK)
        self.client = genai.Client(api_key=api_key)
        self.quota_manager = get_quota_manager()

        logger.info(f"Initialized GeminiLLMProvider with model={self.model} (New SDK)")

    def _messages_to_gemini_format(
        self, messages: List[LLMMessage]
    ) -> Tuple[Optional[str], str]:
        """Convert messages to Gemini format."""
        
        # New SDK supports chat history better, but for single-turn compatible interface:
        system_instruction = None
        user_messages = []

        for msg in messages:
            if msg.role == "system":
                system_instruction = msg.content
            elif msg.role == "user":
                user_messages.append(msg.content)
            elif msg.role == "assistant":
                # For basic generation, we might skip or append. 
                # For true chat, we'd build a history list. 
                # Keeping it simple for now as per previous implementation:
                pass

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
        """Generate completion using Gemini API (New SDK)."""
        if not messages:
            raise ValueError("Messages cannot be empty")

        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        system_instruction, user_prompt = self._messages_to_gemini_format(messages)
        estimated_tokens = estimate_tokens_from_text(
            f"{system_instruction or ''}{user_prompt}"
        ) + max(1, int(max_tok))

        try:
            quota_decision = await self.quota_manager.reserve(
                "text_generation",
                estimated_tokens,
                wait_for_capacity=True,
            )
            if quota_decision.wait_seconds > 0:
                logger.info(
                    "Quota backpressure applied bucket=%s wait=%.3fs",
                    quota_decision.bucket,
                    quota_decision.wait_seconds,
                )

            # New SDK usage: client.models.generate_content
            config = types.GenerateContentConfig(
                temperature=temp,
                max_output_tokens=max_tok,
                system_instruction=system_instruction,
            )
            
            # Run in executor
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.model,
                    contents=user_prompt,
                    config=config
                ),
            )

            # Extract content
            content = response.text if response.text else ""
            
            # Finish reason in new SDK
            finish_reason = "unknown"
            if response.candidates and response.candidates[0].finish_reason:
                finish_reason = response.candidates[0].finish_reason

            usage_metadata = getattr(response, "usage_metadata", None)
            prompt_tokens = getattr(usage_metadata, "prompt_token_count", None)
            completion_tokens = getattr(usage_metadata, "candidates_token_count", None)
            total_tokens = getattr(usage_metadata, "total_token_count", None)
            estimated_cost = calculate_gemini_cost(prompt_tokens, completion_tokens)

            logger.info(f"Gemini API call successful (New SDK): len={len(content)}")

            return LLMResponse(
                content=content,
                model=self.model,
                tokens_used=total_tokens,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost_usd=estimated_cost,
                finish_reason=str(finish_reason),
            )

        except QuotaExceededError:
            raise

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
