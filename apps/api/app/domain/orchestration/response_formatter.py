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
        # Visual separator + icon + question for better readability
        return f"{message}\n\n─────\n💬 {follow_up_question}"

    @staticmethod
    async def format_response(
        message: str,
        mode: ConversationMode,
        follow_up_question: str = None,
        include_disclaimer: bool = None,
        agent_type: str = None,
        user_message: str = None,
        safety_classification: str = None,
    ) -> str:
        """
        Format a response with optional disclaimer and follow-up.

        Args:
            message: Base response message
            mode: Conversation mode
            follow_up_question: Optional follow-up question
            include_disclaimer: Override for disclaimer inclusion (defaults to settings)
            agent_type: Agent that generated response (for disclaimer logic)
            user_message: Original user message (retained for compatibility)
            safety_classification: One of emergency|medical|non_medical

        Returns:
            Formatted response message
        """
        formatted = message

        # Add safety disclaimer ONLY for medical/health-related content
        if include_disclaimer is None:
            include_disclaimer = settings.include_safety_disclaimer
        
        # Use upstream safety classification when available to avoid duplicate
        # classifier calls in formatter stage.
        is_medical_query = (
            safety_classification in {"medical", "emergency"}
            if safety_classification
            else mode == ConversationMode.SAFETY
        )
        
        # Add disclaimer for genuinely medical queries (must be medical AND safety context)
        # This prevents non-medical dive site/destination queries from showing medical disclaimers
        should_add_disclaimer = include_disclaimer and (
            (mode == ConversationMode.SAFETY and is_medical_query) or  # Safety mode WITH medical content
            (agent_type == "emergency")  # Always show for emergency agent
        )
        
        if should_add_disclaimer:
            formatted = ResponseFormatter.add_safety_disclaimer(formatted)

        # Append follow-up question
        if follow_up_question:
            formatted = ResponseFormatter.append_follow_up(formatted, follow_up_question)

        return formatted

    @staticmethod
    def sanitize_response(response: str) -> str:
        """
        Remove any leaked RAG/source references from response text.
        
        Strips common patterns that expose internal system behavior:
        - "according to the context"
        - "based on the provided information"
        - "from the documentation"
        - "[Source: ...]" brackets
        - "provided context"
        - "retrieved document"
        - "in the document"
        
        This is a defensive layer in case agent prompts fail to comply.
        
        Args:
            response: Original response text
            
        Returns:
            Sanitized response with RAG mentions removed
        """
        import re
        
        if not response:
            return response
        
        sanitized = response
        
        # Patterns to remove (case-insensitive)
        # Match full phrases with context, being careful with word boundaries
        patterns = [
            r'\baccording to\s+(the\s+)?(provided\s+|retrieved\s+)?(context|information|document|documentation)\b,?\s*',
            r'\bbased on\s+(the\s+)?(provided\s+|retrieved\s+)?(context|information|document|documentation)\b,?\s*',
            r'\bfrom\s+(the\s+)?(provided\s+|retrieved\s+)?(context|information|document|documentation)\b,?\s*',
            r'\bin\s+(the\s+)?(provided\s+|retrieved\s+)?(context|document|documentation)\b,?\s*',
            r'\bthe\s+(provided\s+|retrieved\s+)?(context|document|documentation)\s+(shows?|states?|indicates?|mentions?|says?)\b,?\s*',
            r'\[Source:.*?\]',  # Remove bracketed source citations
            r'\(Source:.*?\)',  # Remove parenthetical source citations
        ]
        
        for pattern in patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE)
        
        # Clean up extra whitespace and punctuation artifacts
        sanitized = re.sub(r'\s+', ' ', sanitized)  # Multiple spaces to single
        sanitized = re.sub(r'\s+([.,!?])', r'\1', sanitized)  # Space before punctuation
        sanitized = re.sub(r'([.,!?])\s*\1+', r'\1', sanitized)  # Duplicate punctuation
        sanitized = re.sub(r'^[.,!?]\s*', '', sanitized)  # Leading punctuation
        sanitized = sanitized.strip()
        
        # Log if sanitization made changes
        if sanitized != response:
            logger.warning(
                f"Response sanitization removed RAG mentions: "
                f"original_length={len(response)}, "
                f"sanitized_length={len(sanitized)}"
            )
        
        return sanitized
