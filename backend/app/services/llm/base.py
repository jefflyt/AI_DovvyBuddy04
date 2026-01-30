"""
Base interface for LLM providers.

Defines the contract that all LLM providers must implement.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from .types import LLMMessage, LLMResponse


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate a completion for the given messages.

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            LLMResponse with generated content

        Raises:
            ValueError: If messages are invalid
            Exception: If API call fails after retries
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name of the LLM model.

        Returns:
            String model name
        """
        pass

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Default implementation uses rough approximation.
        Subclasses can override with provider-specific tokenizers.

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        # Rough approximation: ~4 chars per token
        return len(text) // 4
