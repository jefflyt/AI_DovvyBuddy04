"""
Mode detection for conversation routing.
"""

import logging
import re
from enum import Enum
from typing import List, Optional

logger = logging.getLogger(__name__)


class ConversationMode(str, Enum):
    """Conversation mode for agent routing."""

    CERTIFICATION = "certification"
    TRIP = "trip"
    SAFETY = "safety"
    GENERAL = "general"


class ModeDetector:
    """Detects conversation mode from user query."""

    # Keywords for each mode
    CERTIFICATION_KEYWORDS = [
        "certification", "certified", "certificate", "padi", "ssi", "naui",
        "open water", "advanced", "rescue", "divemaster", "instructor",
        "course", "training", "license", "qualify", "requirements", "prerequisites"
    ]

    TRIP_KEYWORDS = [
        "destination", "trip", "travel", "visit", "dive site", "where to dive",
        "best place", "recommend", "location", "country", "island", "reef",
        "wreck", "season", "when to go", "book", "resort", "liveaboard"
    ]

    SAFETY_KEYWORDS = [
        "medical", "health", "safe", "safety", "condition", "disease", "illness",
        "medication", "doctor", "physician", "cold", "flu", "asthma", "diabetes",
        "heart", "lung", "ear", "sinus", "pregnant", "injury", "emergency",
        "accident", "dcs", "decompression", "barotrauma", "risk"
    ]

    def detect_mode(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> ConversationMode:
        """
        Detect conversation mode from query.

        Args:
            query: User query to analyze
            conversation_history: Previous conversation for context

        Returns:
            ConversationMode enum value
        """
        query_lower = query.lower()

        # Score each mode
        scores = {
            ConversationMode.SAFETY: self._score_keywords(query_lower, self.SAFETY_KEYWORDS),
            ConversationMode.CERTIFICATION: self._score_keywords(query_lower, self.CERTIFICATION_KEYWORDS),
            ConversationMode.TRIP: self._score_keywords(query_lower, self.TRIP_KEYWORDS),
        }

        # Safety takes priority (highest weight)
        if scores[ConversationMode.SAFETY] > 0:
            logger.info(f"Mode detected: SAFETY (score={scores[ConversationMode.SAFETY]})")
            return ConversationMode.SAFETY

        # Find highest scoring mode
        max_score = max(scores.values())
        
        if max_score == 0:
            # No keywords matched, check context
            if conversation_history:
                context_mode = self._detect_from_context(conversation_history)
                if context_mode:
                    logger.info(f"Mode detected from context: {context_mode.value}")
                    return context_mode

            logger.info("Mode detected: GENERAL (no keywords matched)")
            return ConversationMode.GENERAL

        # Return mode with highest score
        for mode, score in scores.items():
            if score == max_score:
                logger.info(f"Mode detected: {mode.value} (score={score})")
                return mode

        return ConversationMode.GENERAL

    def _score_keywords(self, query: str, keywords: List[str]) -> int:
        """
        Score query based on keyword matches.

        Args:
            query: Lowercased query string
            keywords: List of keywords to match

        Returns:
            Score (number of keyword matches)
        """
        score = 0
        for keyword in keywords:
            if keyword in query:
                score += 1
        return score

    def _detect_from_context(
        self,
        conversation_history: List[Dict[str, str]]
    ) -> Optional[ConversationMode]:
        """
        Detect mode from conversation context.

        Args:
            conversation_history: Previous messages

        Returns:
            ConversationMode if detected from context, None otherwise
        """
        # Look at last few messages for context
        recent_messages = conversation_history[-3:] if len(conversation_history) >= 3 else conversation_history

        for msg in reversed(recent_messages):
            if msg.get("role") == "user":
                content = msg.get("content", "").lower()
                
                # Check each mode
                if self._score_keywords(content, self.CERTIFICATION_KEYWORDS) > 0:
                    return ConversationMode.CERTIFICATION
                if self._score_keywords(content, self.TRIP_KEYWORDS) > 0:
                    return ConversationMode.TRIP
                if self._score_keywords(content, self.SAFETY_KEYWORDS) > 0:
                    return ConversationMode.SAFETY

        return None

    def is_follow_up_question(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> bool:
        """
        Detect if query is a follow-up question.

        Args:
            query: User query
            conversation_history: Previous conversation

        Returns:
            True if appears to be follow-up
        """
        if not conversation_history or len(conversation_history) < 2:
            return False

        query_lower = query.lower()
        
        # Follow-up indicators
        follow_up_indicators = [
            "what about", "how about", "and", "also", "more", "else",
            "can you", "tell me more", "explain", "what if", "but"
        ]

        # Short query often indicates follow-up
        if len(query.split()) <= 5:
            return True

        return any(indicator in query_lower for indicator in follow_up_indicators)
