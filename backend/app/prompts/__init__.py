"""
Prompt templates for DovvyBuddy agents.

Provides system prompts and templates for different conversation modes.
"""

from .certification import CERTIFICATION_SYSTEM_PROMPT
from .safety import SAFETY_DISCLAIMER, SAFETY_SYSTEM_PROMPT
from .system import BASE_SYSTEM_PROMPT
from .templates import render_template
from .trip import TRIP_SYSTEM_PROMPT

__all__ = [
    "BASE_SYSTEM_PROMPT",
    "CERTIFICATION_SYSTEM_PROMPT",
    "TRIP_SYSTEM_PROMPT",
    "SAFETY_SYSTEM_PROMPT",
    "SAFETY_DISCLAIMER",
    "render_template",
]
