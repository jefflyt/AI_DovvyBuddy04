"""
Token utilities for RAG and cost estimation.
"""

from __future__ import annotations

from typing import Optional

from app.services.rag.chunker import count_tokens as count_tokens_rag

GEMINI_INPUT_COST_PER_M_TOKEN = 0.15
GEMINI_OUTPUT_COST_PER_M_TOKEN = 0.60


def count_tokens(text: str) -> int:
    """
    Count tokens in text using tiktoken (Gemini approximation).

    Args:
        text: Text to count tokens for

    Returns:
        Token count
    """
    return count_tokens_rag(text)


def calculate_gemini_cost(
    prompt_tokens: Optional[int],
    completion_tokens: Optional[int],
) -> Optional[float]:
    """
    Calculate Gemini 2.5 Flash Lite cost in USD.

    Args:
        prompt_tokens: Prompt token count
        completion_tokens: Completion token count

    Returns:
        Cost in USD rounded to 4 decimals, or None if inputs missing
    """
    if prompt_tokens is None or completion_tokens is None:
        return None

    total_cost = (
        (prompt_tokens * GEMINI_INPUT_COST_PER_M_TOKEN)
        + (completion_tokens * GEMINI_OUTPUT_COST_PER_M_TOKEN)
    ) / 1_000_000

    return round(total_cost, 4)
