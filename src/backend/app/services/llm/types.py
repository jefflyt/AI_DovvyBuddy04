"""
Type definitions for LLM services.
"""

from dataclasses import dataclass
from typing import Literal, Optional


@dataclass
class LLMMessage:
    """A message in a conversation."""

    role: Literal["system", "user", "assistant"]
    content: str


@dataclass
class LLMResponse:
    """Response from an LLM provider."""

    content: str
    model: str
    tokens_used: Optional[int] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    finish_reason: Optional[str] = None
