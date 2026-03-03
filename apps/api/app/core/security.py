"""
Security utilities for DovvyBuddy.

Provides input sanitization, prompt injection detection, and other security features.
"""

import logging
import re
from typing import Optional

import bleach

logger = logging.getLogger(__name__)

# Patterns that indicate potential prompt injection attempts
INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|above|prior)\s+(instructions|prompts|rules)",
    r"ignore\s+all\s+previous\s+(instructions|prompts|rules)",
    r"disregard\s+(previous|all|above|prior)\s+(instructions|prompts|rules)",
    r"disregard\s+all\s+previous\s+(instructions|prompts|rules)",
    r"forget\s+(previous|all|above|everything|your)\s+(instructions|prompts|rules|training)",
    r"system\s+(prompt|instruction|message)",
    r"reveal\s+your\s+(instructions|prompt|rules|system)",
    r"what\s+(are|is)\s+your\s+(instructions|prompt|rules|system)",
    r"you\s+are\s+now\s+(a|an)",
    r"pretend\s+(to\s+be|you\s+are)",
    r"act\s+as\s+(a|an|if)",
    r"roleplay\s+as",
    r"simulate\s+(a|an|being)",
    r"jailbreak",
    r"<script",
    r"javascript:",
    r"onerror=",
    r"onclick=",
]

# Compiled patterns for performance
COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in INJECTION_PATTERNS]


def sanitize_input(text: str) -> str:
    """
    Remove HTML tags and scripts from user input.
    
    Prevents XSS attacks by stripping all HTML elements.
    
    Args:
        text: Raw user input
        
    Returns:
        Sanitized text with HTML removed
    """
    if not text:
        return text

    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove all HTML tags, keep only text
    sanitized = bleach.clean(
        text,
        tags=[],  # Allow no HTML tags
        strip=True,  # Strip tags instead of escaping
        strip_comments=True,
    )
    
    # Log if sanitization made changes
    if sanitized != text:
        logger.warning(
            f"Input sanitization removed HTML: "
            f"original_length={len(text)}, sanitized_length={len(sanitized)}"
        )
    
    return sanitized


def detect_injection_attempt(text: str) -> Optional[str]:
    """
    Detect potential prompt injection attempts in user input.
    
    Checks for suspicious patterns that indicate attempts to:
    - Override system instructions
    - Change the AI's role or behavior
    - Reveal system prompts
    - Execute scripts or code
    
    Args:
        text: User input to analyze
        
    Returns:
        Warning message if injection detected, None otherwise
    """
    if not text:
        return None
    
    text_lower = text.lower()
    
    for pattern in COMPILED_PATTERNS:
        match = pattern.search(text)
        if match:
            matched_text = match.group()
            logger.warning(
                f"Potential prompt injection detected: pattern='{pattern.pattern}' "
                f"matched='{matched_text}' input_preview='{text[:100]}...'"
            )
            
            return (
                "Your message contains patterns that could indicate a security concern. "
                "Please rephrase your question in a straightforward way. "
                "I'm here to help with diving-related questions!"
            )
    
    return None


def validate_message_safety(message: str) -> tuple[str, Optional[str]]:
    """
    Comprehensive safety validation of user message.
    
    Combines sanitization and injection detection into a single check.
    
    Args:
        message: Raw user message
        
    Returns:
        Tuple of (sanitized_message, error_message)
        If error_message is not None, the request should be rejected
    """
    # First sanitize HTML/scripts
    clean_message = sanitize_input(message)
    
    # Then check for injection attempts
    injection_warning = detect_injection_attempt(clean_message)
    
    if injection_warning:
        return clean_message, injection_warning
    
    return clean_message, None
