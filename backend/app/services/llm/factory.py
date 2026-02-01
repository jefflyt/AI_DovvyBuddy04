"""
Factory for creating LLM provider instances.

Provides convenient methods to create providers from configuration.
"""

import logging
from typing import Optional

from app.core.config import settings

from .base import LLMProvider
from .gemini import GeminiLLMProvider

logger = logging.getLogger(__name__)


def create_llm_provider(
    provider_name: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
) -> LLMProvider:
    """
    Create an LLM provider instance.

    Args:
        provider_name: Name of the provider ("groq" or "gemini", default: from settings)
        api_key: API key (if None, uses from settings)
        model: Model name (if None, uses from settings)
        temperature: Temperature (if None, uses from settings)
        max_tokens: Max tokens (if None, uses from settings)

    Returns:
        LLMProvider instance

    Raises:
        ValueError: If provider is unknown or API key is missing
    """
    provider = (provider_name or settings.default_llm_provider).lower()
    temp = temperature if temperature is not None else settings.llm_temperature
    max_tok = max_tokens if max_tokens is not None else settings.llm_max_tokens

    if provider == "groq":
        # Groq is deprecated - fallback to Gemini
        logger.warning(f"Groq provider no longer supported - using Gemini instead")
        return create_llm_provider(provider_name=settings.default_llm_provider, api_key=api_key, model=model, temperature=temperature, max_tokens=max_tokens)

    elif provider == "gemini":
        key = api_key or settings.gemini_api_key
        if not key:
            raise ValueError("Gemini API key is required (GEMINI_API_KEY env var)")

        # Use default from config as single source of truth
        model_name = model or settings.default_llm_model
        logger.info(f"Creating Gemini LLM provider with model={model_name}")
        return GeminiLLMProvider(
            api_key=key,
            model=model_name,
            temperature=temp,
            max_tokens=max_tok,
        )

    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


def create_llm_provider_from_env() -> LLMProvider:
    """
    Create an LLM provider from environment configuration.

    Returns:
        LLMProvider instance configured from settings

    Raises:
        ValueError: If configuration is invalid
    """
    return create_llm_provider()
