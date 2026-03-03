"""
Orchestration system for DovvyBuddy chat.

Provides chat orchestration, session management, and mode detection.
"""

from .mode_detector import ConversationMode, ModeDetector  # ModeDetector deprecated - kept for ConversationMode enum

__all__ = [
    "ChatOrchestrator",
    "SessionManager",
    "ModeDetector",  # Deprecated: ConversationManager provides better intent detection
    "ContextBuilder",
    "ConversationMode",
    "EmergencyDetector",
    "ChatRequest",
    "ChatResponse",
    "SessionData",
]


def __getattr__(name):
    if name == "ChatOrchestrator":
        from .orchestrator import ChatOrchestrator
        return ChatOrchestrator
    if name == "SessionManager":
        from .session_manager import SessionManager
        return SessionManager
    if name == "ContextBuilder":
        from .context_builder import ContextBuilder
        return ContextBuilder
    if name == "EmergencyDetector":
        from .emergency_detector_hybrid import EmergencyDetector
        return EmergencyDetector
    if name == "ChatRequest":
        from .types import ChatRequest
        return ChatRequest
    if name == "ChatResponse":
        from .types import ChatResponse
        return ChatResponse
    if name == "SessionData":
        from .types import SessionData
        return SessionData
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
