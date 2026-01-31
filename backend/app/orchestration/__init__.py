"""
Orchestration system for DovvyBuddy chat.

Provides chat orchestration, session management, and mode detection.
"""

from .context_builder import ContextBuilder
from .emergency_detector_hybrid import EmergencyDetector
from .mode_detector import ConversationMode, ModeDetector  # ModeDetector deprecated - kept for ConversationMode enum
from .orchestrator import ChatOrchestrator
from .session_manager import SessionManager
from .types import ChatRequest, ChatResponse, SessionData

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
