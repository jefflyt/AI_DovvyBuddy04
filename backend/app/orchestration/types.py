"""
Shared types for orchestration layer to avoid circular imports.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

@dataclass
class SessionData:
    """Session data model for internal use."""
    id: UUID
    conversation_history: List[Dict[str, str]]
    created_at: datetime
    updated_at: datetime
    diver_profile: Optional[Dict[str, Any]] = None

@dataclass
class ChatRequest:
    """Internal chat request model."""
    message: str
    session_id: Optional[str] = None
    diver_profile: Optional[Dict[str, Any]] = None
    session_state: Optional[Dict[str, Any]] = None

@dataclass
class ChatResponse:
    """Internal chat response model."""
    message: str
    session_id: str
    agent_type: str
    metadata: Dict[str, Any]
    follow_up_question: Optional[str] = None

class IntentType(str, Enum):
    """Conversation intent types for agent routing."""

    INFO_LOOKUP = "INFO_LOOKUP"  # General diving knowledge
    DIVE_PLANNING = "DIVE_PLANNING"  # Trip planning, destination selection
    CONDITIONS = "CONDITIONS"  # Weather, visibility, currents
    SKILL_EXPLANATION = "SKILL_EXPLANATION"  # Techniques, procedures
    MARINE_LIFE = "MARINE_LIFE"  # Species identification, behavior
    GEAR = "GEAR"  # Equipment recommendations, maintenance
    AGENCY_CERT = "AGENCY_CERT"  # Certification levels, training
    EMERGENCY_MEDICAL = "EMERGENCY_MEDICAL"  # Safety-critical situations


@dataclass
class SessionState:
    """Session state tracking for personalized follow-ups."""

    cert_level: Optional[str] = None  # "OW", "AOW", "DM", "Instructor", "unknown"
    context_mode: Optional[str] = None  # "learning", "planning", "briefing", "curiosity"
    location_known: bool = False
    conditions_known: bool = False
    last_intent: Optional[str] = None
    asked_follow_ups: List[str] = field(default_factory=list)  # Track asked questions to avoid repetition

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "cert_level": self.cert_level,
            "context_mode": self.context_mode,
            "location_known": self.location_known,
            "conditions_known": self.conditions_known,
            "last_intent": self.last_intent,
            "asked_follow_ups": self.asked_follow_ups,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionState":
        """Create from dictionary."""
        return cls(
            cert_level=data.get("cert_level"),
            context_mode=data.get("context_mode"),
            location_known=data.get("location_known", False),
            conditions_known=data.get("conditions_known", False),
            last_intent=data.get("last_intent"),
            asked_follow_ups=data.get("asked_follow_ups", []),
        )
