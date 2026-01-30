"""Response formatting utilities for chat responses."""

import logging

from app.core.config import settings
from app.prompts.safety import SAFETY_DISCLAIMER
from .mode_detector import ConversationMode

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """
    Formats chat responses with disclaimers, follow-ups, and greetings.
    
    Responsibilities:
    - Add safety disclaimers
    - Append follow-up questions
    - Generate welcome messages
    - Check for greeting messages
    """

    @staticmethod
    def is_greeting(message: str) -> bool:
        """
        Check if message is a common greeting.

        Args:
            message: User's message

        Returns:
            True if message is a greeting, False otherwise
        """
        greetings = {
            'hi', 'hello', 'hey', 'greetings', 'howdy', 
            'good morning', 'good afternoon', 'good evening'
        }
        normalized = message.strip().lower()
        return normalized in greetings

    @staticmethod
    def get_welcome_message() -> str:
        """
        Return friendly welcome message with capability overview.

        Returns:
            Welcome message string
        """
        return (
            "Hello! 👋 I'm DovvyBuddy, your AI diving assistant.\n\n"
            "I can help you with:\n"
            "🎓 Diving certifications and training\n"
            "🌊 Dive destinations and conditions\n"
            "⚠️ Safety procedures and best practices\n"
            "🤿 Equipment recommendations\n\n"
            "What would you like to know about diving?"
        )

    @staticmethod
    def add_safety_disclaimer(message: str) -> str:
        """
        Add safety disclaimer to message.

        Args:
            message: Original message

        Returns:
            Message with disclaimer appended
        """
        return f"{message}\n\n{SAFETY_DISCLAIMER}"

    @staticmethod
    def append_follow_up(message: str, follow_up_question: str) -> str:
        """
        Append follow-up question to response message.

        Args:
            message: Original response message
            follow_up_question: Follow-up question to append

        Returns:
            Message with follow-up question appended
        """
        if not follow_up_question:
            return message
        
        logger.info(f"Appending follow-up: {follow_up_question}")
        return f"{message}\n\n**{follow_up_question}**"

    @staticmethod
    def format_response(
        message: str,
        mode: ConversationMode,
        follow_up_question: str = None,
        include_disclaimer: bool = None,
    ) -> str:
        """
        Format a response with optional disclaimer and follow-up.

        Args:
            message: Base response message
            mode: Conversation mode
            follow_up_question: Optional follow-up question
            include_disclaimer: Override for disclaimer inclusion (defaults to settings)

        Returns:
            Formatted response message
        """
        formatted = message

        # Add safety disclaimer if needed
        if include_disclaimer is None:
            include_disclaimer = settings.include_safety_disclaimer
        
        if include_disclaimer and mode == ConversationMode.SAFETY:
            formatted = ResponseFormatter.add_safety_disclaimer(formatted)

        # Append follow-up question
        if follow_up_question:
            formatted = ResponseFormatter.append_follow_up(formatted, follow_up_question)

        return formatted
