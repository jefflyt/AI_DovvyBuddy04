"""
Unit tests for system and RAG prompts.
"""

from app.prompts.rag import NO_RAG_PROMPT, RAG_SYSTEM_PROMPT
from app.prompts.system import BASE_SYSTEM_PROMPT, GENERAL_SYSTEM_PROMPT
from app.services.rag.chunker import count_tokens


def test_rag_prompt_token_count():
    prompt = RAG_SYSTEM_PROMPT.format(context="Sample verified context.")
    assert count_tokens(prompt) <= 250


def test_no_rag_prompt_token_count():
    assert count_tokens(NO_RAG_PROMPT) <= 40


def test_base_prompt_token_count():
    assert count_tokens(BASE_SYSTEM_PROMPT) <= 180


def test_general_prompt_token_count():
    assert count_tokens(GENERAL_SYSTEM_PROMPT) <= 30


def test_prompts_contain_safety_disclaimers():
    base_lower = BASE_SYSTEM_PROMPT.lower()
    general_lower = GENERAL_SYSTEM_PROMPT.lower()
    assert "medical" in base_lower
    assert "medical" in general_lower
    assert "qualified" in base_lower or "professionals" in base_lower


def test_prompts_contain_rag_adherence_rules():
    rag_lower = RAG_SYSTEM_PROMPT.lower()
    assert "verified information" in rag_lower
    assert "use only" in rag_lower


def test_no_rag_prompt_has_fallback_message():
    no_rag_lower = NO_RAG_PROMPT.lower()
    assert "general guidance" in no_rag_lower
    assert "rephrase" in no_rag_lower
