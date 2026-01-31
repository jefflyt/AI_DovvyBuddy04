"""
Conversation manager for intent classification, state extraction, and follow-up generation.

Uses lightweight LLM call with structured JSON output to handle conversation continuity.
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.services.llm.factory import create_llm_provider
from app.services.llm.types import LLMMessage

logger = logging.getLogger(__name__)


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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "cert_level": self.cert_level,
            "context_mode": self.context_mode,
            "location_known": self.location_known,
            "conditions_known": self.conditions_known,
            "last_intent": self.last_intent,
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
        )


@dataclass
class ConversationAnalysis:
    """Result of conversation analysis with LLM."""

    intent: IntentType
    state_updates: Dict[str, Any] = field(default_factory=dict)
    follow_up: Optional[str] = None
    bypass_followup: bool = False
    confidence: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/telemetry."""
        return {
            "intent": self.intent.value,
            "state_updates": self.state_updates,
            "follow_up": self.follow_up,
            "bypass_followup": self.bypass_followup,
            "confidence": self.confidence,
        }


class ConversationManager:
    """
    Manages conversation continuity through intent detection and follow-ups.
    
    Uses lightweight LLM call to:
    1. Classify user intent
    2. Extract session state updates naturally
    3. Generate contextual follow-up questions
    
    Implements confidence-based fallbacks and validation for safety.
    """

    # Intent-based follow-up templates (fallback if LLM fails or validation fails)
    FOLLOW_UP_TEMPLATES: Dict[IntentType, str] = {
        IntentType.INFO_LOOKUP: "Is this for learning, planning a dive, or just curious?",
        IntentType.DIVE_PLANNING: "Which destination are you considering?",
        IntentType.CONDITIONS: "What dates are you planning to dive?",
        IntentType.SKILL_EXPLANATION: "Are you preparing for a course or planning to use this skill?",
        IntentType.MARINE_LIFE: "Are you planning to dive somewhere specific to see this?",
        IntentType.GEAR: "Are you shopping for new equipment or troubleshooting?",
        IntentType.AGENCY_CERT: "Which certification level are you interested in?",
        IntentType.EMERGENCY_MEDICAL: None,  # No follow-up for emergencies
    }

    # Low confidence threshold - below this, force INFO_LOOKUP and skip state updates
    LOW_CONFIDENCE_THRESHOLD = 0.4

    def __init__(self):
        """Initialize conversation manager with LLM provider."""
        # Use fast, lightweight model for conversation management
        self.llm = create_llm_provider(
            provider_name="gemini",
            model="gemini-2.0-flash-exp",
            temperature=0.3,  # Lower temperature for more consistent structured output
            max_tokens=500,  # Short responses needed
        )

    async def analyze(
        self,
        message: str,
        history: List[Dict[str, str]],
        state: Optional[SessionState] = None,
    ) -> ConversationAnalysis:
        """
        Analyze message for intent, state updates, and follow-up.
        
        Args:
            message: User's message
            history: Conversation history (last 3-5 turns)
            state: Current session state
            
        Returns:
            ConversationAnalysis with intent, state updates, and follow-up
        """
        if state is None:
            state = SessionState()

        try:
            # Build LLM prompt with conversation context
            system_prompt = self._build_system_prompt(state)
            user_prompt = self._build_user_prompt(message, history)

            # Call LLM with structured output request
            messages = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_prompt),
            ]

            # Set 2-second timeout for conversation manager
            response = await self.llm.generate(messages, temperature=0.3, max_tokens=500)

            # Parse JSON response
            try:
                analysis_data = json.loads(response.content)
            except json.JSONDecodeError as e:
                logger.warning(f"LLM returned invalid JSON: {e}, using fallback")
                return self._fallback_analysis()

            # Extract with field-level fallbacks
            intent_str = analysis_data.get("intent", "INFO_LOOKUP")
            try:
                intent = IntentType(intent_str)
            except ValueError:
                logger.warning(f"Invalid intent '{intent_str}', using INFO_LOOKUP")
                intent = IntentType.INFO_LOOKUP

            state_updates = analysis_data.get("state_updates", {})
            if not isinstance(state_updates, dict):
                logger.warning("state_updates is not a dict, skipping")
                state_updates = {}

            follow_up = analysis_data.get("follow_up", "")
            confidence = analysis_data.get("confidence", 0.5)

            # Handle low confidence
            if confidence < self.LOW_CONFIDENCE_THRESHOLD:
                logger.info(
                    f"Low confidence ({confidence:.2f}), "
                    f"forcing INFO_LOOKUP, skipping state updates"
                )
                intent = IntentType.INFO_LOOKUP
                state_updates = {}
                # Use intent-based template instead of hardcoded generic question
                follow_up = self.FOLLOW_UP_TEMPLATES.get(IntentType.INFO_LOOKUP, "")

            # Validate follow-up
            validated_follow_up = self._validate_follow_up(follow_up, intent)

            return ConversationAnalysis(
                intent=intent,
                state_updates=state_updates,
                follow_up=validated_follow_up,
                bypass_followup=False,
                confidence=confidence,
            )

        except Exception as e:
            logger.error(f"Conversation analysis failed: {e}", exc_info=True)
            return self._fallback_analysis()

    def _build_system_prompt(self, state: SessionState) -> str:
        """Build system prompt for LLM with current session state."""
        return f"""You are a conversation analyzer for DovvyBuddy, a diving assistant chatbot.

Your task: Analyze the user's message and return a JSON object with:
1. "intent": One of {[e.value for e in IntentType]}
2. "state_updates": Dict with keys: cert_level, context_mode, location_known, conditions_known
3. "follow_up": Exactly ONE specific question to continue the conversation (max 100 chars)
4. "confidence": Float 0.0-1.0 indicating your confidence in the intent classification

**Current Session State:**
- cert_level: {state.cert_level or "unknown"}
- context_mode: {state.context_mode or "unknown"}
- location_known: {state.location_known}
- conditions_known: {state.conditions_known}

**Intent Classification Rules:**
- INFO_LOOKUP: General diving knowledge, definitions, explanations
- DIVE_PLANNING: Trip planning, destination selection, booking
- CONDITIONS: Weather, visibility, currents, seasonal patterns
- SKILL_EXPLANATION: Techniques, procedures, training requirements
- MARINE_LIFE: Species identification, behavior, best spots to see
- GEAR: Equipment recommendations, maintenance, troubleshooting
- AGENCY_CERT: Certification levels, prerequisites, training paths
- EMERGENCY_MEDICAL: Symptoms, injuries, medical emergencies (NEVER generate follow-up for this)

**State Extraction Rules:**
- Extract cert_level naturally: "I'm Open Water certified" → cert_level: "OW"
- Extract context_mode: "planning a trip" → context_mode: "planning"
- Set location_known: true if user mentions specific destination
- Set conditions_known: true if user discusses weather/visibility/currents

**Follow-up Generation Rules:**
- Must be exactly ONE question ending with ?
- Must be ≤ 100 characters
- Must NOT contain numbers (no "dive to 30m", no "site #3")
- Must NOT contain site names, depth references, or condition specifics
- Must advance planning OR fill critical missing session state
- Must be friendly and conversational, not interrogative
- For EMERGENCY_MEDICAL intent, return empty string for follow_up

**Output Format (JSON only, no markdown):**
{{
  "intent": "INFO_LOOKUP",
  "state_updates": {{"cert_level": "OW", "context_mode": "planning"}},
  "follow_up": "Which destination are you considering?",
  "confidence": 0.85
}}"""

    def _build_user_prompt(
        self,
        message: str,
        history: List[Dict[str, str]],
    ) -> str:
        """Build user prompt with message and conversation history."""
        # Include last 3 turns for context
        recent_history = history[-6:] if len(history) > 6 else history

        history_text = ""
        if recent_history:
            history_text = "\n**Recent Conversation:**\n"
            for turn in recent_history:
                role = turn.get("role", "user")
                content = turn.get("content", "")
                history_text += f"- {role}: {content[:100]}...\n"

        return f"""{history_text}

**Current User Message:**
{message}

Return JSON analysis:"""

    def _validate_follow_up(
        self,
        follow_up: str,
        intent: IntentType,
    ) -> Optional[str]:
        """
        Validate LLM-generated follow-up question.
        
        Falls back to template if validation fails.
        
        Args:
            follow_up: LLM-generated follow-up question
            intent: Detected intent
            
        Returns:
            Validated follow-up or template fallback
        """
        # No follow-up for emergencies
        if intent == IntentType.EMERGENCY_MEDICAL:
            return None

        if not follow_up or not follow_up.strip():
            logger.warning("Empty follow-up, using template")
            return self.FOLLOW_UP_TEMPLATES.get(intent)

        # Must end with ?
        if not follow_up.strip().endswith("?"):
            logger.warning("Follow-up missing ?, using template")
            return self.FOLLOW_UP_TEMPLATES.get(intent)

        # Must be ≤ 100 characters
        if len(follow_up) > 100:
            logger.warning(f"Follow-up too long ({len(follow_up)} chars), using template")
            return self.FOLLOW_UP_TEMPLATES.get(intent)

        # Must be exactly one question (single ?)
        if follow_up.count("?") > 1:
            logger.warning("Follow-up has multiple questions, using template")
            return self.FOLLOW_UP_TEMPLATES.get(intent)

        # Must not contain numbers
        if any(char.isdigit() for char in follow_up):
            logger.warning("Follow-up contains numbers, using template")
            return self.FOLLOW_UP_TEMPLATES.get(intent)

        # Passed all validations
        return follow_up.strip()

    def _fallback_analysis(self) -> ConversationAnalysis:
        """
        Return fallback analysis when LLM fails.
        
        Safest option: INFO_LOOKUP intent with template-based follow-up.
        """
        return ConversationAnalysis(
            intent=IntentType.INFO_LOOKUP,
            state_updates={},
            follow_up=self.FOLLOW_UP_TEMPLATES.get(IntentType.INFO_LOOKUP, ""),
            bypass_followup=False,
            confidence=0.0,
        )
