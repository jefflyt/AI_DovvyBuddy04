"""Contract tests for versioned specialist prompts."""

from app.prompts.specialists_v1 import (
    GROUNDING_CONTRACT,
    LEGACY_CERTIFICATION_SYSTEM_PROMPT,
    LEGACY_SAFETY_SYSTEM_PROMPT,
    LEGACY_TRIP_SYSTEM_PROMPT,
    NATIVE_CERTIFICATION_SPECIALIST_PROMPT,
    NATIVE_GENERAL_SPECIALIST_PROMPT,
    NATIVE_SAFETY_SPECIALIST_PROMPT,
    NATIVE_TRIP_SPECIALIST_PROMPT,
    ROUTER_SYSTEM_PROMPT,
)


def test_router_prompt_declares_all_routes():
    assert "route_trip_specialist" in ROUTER_SYSTEM_PROMPT
    assert "route_certification_specialist" in ROUTER_SYSTEM_PROMPT
    assert "route_safety_specialist" in ROUTER_SYSTEM_PROMPT
    assert "route_general_retrieval_specialist" in ROUTER_SYSTEM_PROMPT


def test_native_specialists_include_grounding_contract():
    assert GROUNDING_CONTRACT in NATIVE_TRIP_SPECIALIST_PROMPT
    assert GROUNDING_CONTRACT in NATIVE_CERTIFICATION_SPECIALIST_PROMPT
    assert GROUNDING_CONTRACT in NATIVE_GENERAL_SPECIALIST_PROMPT


def test_safety_prompt_mentions_medical_boundary():
    assert "Do not diagnose" in NATIVE_SAFETY_SPECIALIST_PROMPT
    assert "medical advice" in NATIVE_SAFETY_SPECIALIST_PROMPT.lower()
    assert "never diagnose" in LEGACY_SAFETY_SYSTEM_PROMPT.lower()


def test_legacy_prompts_block_internal_source_leakage():
    assert "Never mention internal context" in LEGACY_TRIP_SYSTEM_PROMPT
    assert "Never mention internal context" in LEGACY_CERTIFICATION_SYSTEM_PROMPT
