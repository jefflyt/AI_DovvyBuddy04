"""
Type definitions for orchestration system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID


@dataclass
class ChatRequest:
    """Request for chat endpoint."""

    message: str
    session_id: Optional[str] = None
    diver_profile: Optional[Dict[str, Any]] = None
    session_state: Optional[Dict[str, Any]] = None  # PR6.2: Session state from localStorage


@dataclass
class ChatResponse:
    """Response from chat endpoint."""

    message: str
    session_id: str
    agent_type: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    follow_up_question: Optional[str] = None  # PR6.2: Follow-up for conversation continuity


@dataclass
class SessionData:
    """Session data structure."""

    id: UUID
    conversation_history: List[Dict[str, str]]
    diver_profile: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def add_message(self, role: str, content: str):
        """Add a message to conversation history."""
        self.conversation_history.append({"role": role, "content": content})

    def get_last_n_messages(self, n: int) -> List[Dict[str, str]]:
        """Get last N messages from history."""
        return self.conversation_history[-n:] if self.conversation_history else []
