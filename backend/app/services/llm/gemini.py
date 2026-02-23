"""
Gemini LLM provider implementation.

Uses Google's Generative AI API for text generation.
"""

import asyncio
import logging
import time
from collections import deque
from typing import Deque, List, Optional, Tuple

import google.genai as genai
from google.genai import types
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.services.llm.base import LLMProvider, LLMResponse
from app.services.llm.types import LLMMessage
from app.services.rag.token_utils import calculate_gemini_cost

logger = logging.getLogger(__name__)

TOKENS_PER_CHAR_ESTIMATE = 0.25


class RateLimitError(Exception):
    """Raised when API rate limit is exceeded."""
    pass


class _LLMRateLimiter:
    """Sliding-window rate limiter for RPM/TPM/RPD constraints."""

    def __init__(
        self,
        rpm_limit: int,
        tpm_limit: int,
        rpd_limit: int,
        window_seconds: int,
    ) -> None:
        self.rpm_limit = rpm_limit
        self.tpm_limit = tpm_limit
        self.rpd_limit = rpd_limit
        self.window_seconds = window_seconds
        self._lock = asyncio.Lock()
        self._events: Deque[Tuple[float, int]] = deque()
        self._daily_events: Deque[float] = deque()

    def _prune(self, now: float) -> None:
        while self._events and now - self._events[0][0] >= self.window_seconds:
            self._events.popleft()
        while self._daily_events and now - self._daily_events[0] >= 86400:
            self._daily_events.popleft()

    def _current_usage(self, now: float) -> Tuple[int, int, int]:
        self._prune(now)
        tokens_used = sum(tokens for _, tokens in self._events)
        return len(self._events), tokens_used, len(self._daily_events)

    def _time_until_tokens_available(self, now: float, needed_tokens: int) -> float:
        if needed_tokens <= 0:
            return 0.0

        running = 0
        for timestamp, tokens in self._events:
            running += tokens
            if running >= needed_tokens:
                return max(0.0, (timestamp + self.window_seconds) - now)
        return 0.0

    async def wait_for_slot(self, request_tokens: int) -> None:
        async with self._lock:
            while True:
                now = time.time()
                request_count, tokens_used, daily_count = self._current_usage(now)

                under_rpm = request_count < self.rpm_limit
                under_tpm = (tokens_used + request_tokens) <= self.tpm_limit
                under_rpd = daily_count < self.rpd_limit

                if under_rpm and under_tpm and under_rpd:
                    self._events.append((now, request_tokens))
                    self._daily_events.append(now)
                    return

                wait_for_rpm = 0.0
                if not under_rpm and self._events:
                    wait_for_rpm = (self._events[0][0] + self.window_seconds) - now

                required_tokens = (tokens_used + request_tokens) - self.tpm_limit
                wait_for_tpm = self._time_until_tokens_available(now, required_tokens)

                wait_for_rpd = 0.0
                if not under_rpd and self._daily_events:
                    wait_for_rpd = (self._daily_events[0] + 86400) - now

                sleep_for = max(0.0, wait_for_rpm, wait_for_tpm, wait_for_rpd)
                if sleep_for > 0:
                    await asyncio.sleep(sleep_for)
                else:
                    await asyncio.sleep(0.01)

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

        self.rate_limiter = _LLMRateLimiter(
            rpm_limit=settings.llm_rpm_limit,
            tpm_limit=settings.llm_tpm_limit,
            rpd_limit=settings.llm_rpd_limit,
            window_seconds=settings.llm_rate_window_seconds,
        )

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

        # Estimate tokens for rate limiting
        request_tokens = self._estimate_tokens(system_instruction, user_prompt, max_tok)
        await self.rate_limiter.wait_for_slot(request_tokens)

        try:
            # New SDK usage: client.models.generate_content
            config = types.GenerateContentConfig(
                temperature=temp,
                max_output_tokens=max_tok,
                system_instruction=system_instruction,
            )
            
            # Run in executor
            loop = asyncio.get_event_loop()
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
            cost_usd = calculate_gemini_cost(prompt_tokens, completion_tokens)

            if usage_metadata is None:
                logger.warning("Gemini API response missing usage_metadata")

            logger.info(
                "LLM generation complete: model=%s, finish_reason=%s, prompt_tokens=%s, completion_tokens=%s, total_tokens=%s, cost_usd=%s",
                self.model,
                finish_reason,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                cost_usd,
            )

            return LLMResponse(
                content=content,
                model=self.model,
                tokens_used=total_tokens,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost_usd=cost_usd,
                finish_reason=str(finish_reason),
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

    def _estimate_tokens(
        self, system_instruction: Optional[str], user_prompt: str, max_tokens: int
    ) -> int:
        """Estimate total tokens (input + output) for rate limiting."""
        input_text = (system_instruction or "") + user_prompt
        input_tokens = max(1, int(len(input_text) * TOKENS_PER_CHAR_ESTIMATE))
        return input_tokens + max_tokens
