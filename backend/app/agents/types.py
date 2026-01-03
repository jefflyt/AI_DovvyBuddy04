"""
Type definitions for agent system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class AgentType(str, Enum):
    """Type of agent for conversation handling."""

    CERTIFICATION = "certification"
    TRIP = "trip"
    SAFETY = "safety"
    RETRIEVAL = "retrieval"
    GENERAL = "general"


class AgentCapability(str, Enum):
    """Capabilities that agents can provide."""

    CERTIFICATION_GUIDANCE = "certification_guidance"
    DESTINATION_RECOMMENDATION = "destination_recommendation"
    SAFETY_DISCLAIMER = "safety_disclaimer"
    RAG_RETRIEVAL = "rag_retrieval"
    GENERAL_CONVERSATION = "general_conversation"


@dataclass
class AgentContext:
    """Context provided to agents for processing queries."""

    query: str
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    diver_profile: Optional[Dict[str, Any]] = None
    rag_context: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_last_user_message(self) -> Optional[str]:
        """Get the last user message from history."""
        for msg in reversed(self.conversation_history):
            if msg.get("role") == "user":
                return msg.get("content")
        return None

    def get_conversation_length(self) -> int:
        """Get number of messages in conversation."""
        return len(self.conversation_history)
