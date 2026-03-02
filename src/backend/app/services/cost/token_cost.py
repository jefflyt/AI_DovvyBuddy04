"""Token usage and Gemini cost estimation utilities."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import re
from typing import Optional

try:
    import tiktoken
except Exception:  # pragma: no cover - optional dependency in constrained test envs
    tiktoken = None

# Gemini 2.5 Flash-Lite estimate (USD per 1M tokens)
GEMINI_INPUT_COST_PER_M_TOKEN = 0.15
GEMINI_OUTPUT_COST_PER_M_TOKEN = 0.60
TOKENS_PER_CHAR_ESTIMATE = 0.25
logger = logging.getLogger(__name__)


class _FallbackTokenizer:
    """Deterministic tokenizer used if tiktoken model metadata is unavailable."""

    def encode(self, text: str) -> list[str]:
        return re.findall(r"\w+|[^\w\s]", text or "")


_TOKENIZER = None


def _get_tokenizer():
    global _TOKENIZER
    if _TOKENIZER is not None:
        return _TOKENIZER

    if tiktoken is not None:
        try:
            _TOKENIZER = tiktoken.encoding_for_model("gpt-3.5-turbo")
        except Exception as exc:  # pragma: no cover - fallback path
            logger.warning("tiktoken model lookup failed, using fallback tokenizer: %s", exc)
            _TOKENIZER = _FallbackTokenizer()
    else:
        _TOKENIZER = _FallbackTokenizer()
    return _TOKENIZER


@dataclass(frozen=True)
class TokenUsage:
    """Structured token usage counters."""

    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
        }


@dataclass(frozen=True)
class CostUsage:
    """Structured cost usage counters."""

    cost_usd_estimate: Optional[float] = None

    def to_dict(self) -> dict:
        return {"cost_usd_estimate": self.cost_usd_estimate}


def count_tokens(text: str) -> int:
    """Count tokens with local tokenizer fallback."""
    tokenizer = _get_tokenizer()
    return len(tokenizer.encode(text))


def estimate_tokens_from_text(text: str) -> int:
    """Cheap token estimate when full tokenization is unnecessary."""
    if not text:
        return 1
    return max(1, int(len(text) * TOKENS_PER_CHAR_ESTIMATE))


def calculate_gemini_cost(
    prompt_tokens: Optional[int],
    completion_tokens: Optional[int],
) -> Optional[float]:
    """
    Estimate Gemini generation cost in USD.

    Returns None when usage metadata is unavailable.
    """
    if prompt_tokens is None or completion_tokens is None:
        return None

    total_cost = (
        (prompt_tokens * GEMINI_INPUT_COST_PER_M_TOKEN)
        + (completion_tokens * GEMINI_OUTPUT_COST_PER_M_TOKEN)
    ) / 1_000_000

    return round(total_cost, 6)
