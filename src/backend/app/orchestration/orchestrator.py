"""
Chat orchestrator - main conversation controller.
"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.registry import get_agent_registry
from app.agents.types import AgentContext, AgentType
from app.core.config import settings

from .context_builder import ContextBuilder
from .mode_detector import ConversationMode, ModeDetector
from .session_manager import SessionManager
from .types import ChatRequest, ChatResponse, SessionData

logger = logging.getLogger(__name__)


class ChatOrchestrator:
    """
    Main orchestrator for chat conversations.
    
    Coordinates:
    - Session management
    - Mode detection
    - Agent selection
    - Context building
    - Response generation
    """

    def __init__(self, db_session: AsyncSession):
        """
        Initialize chat orchestrator.

        Args:
            db_session: Database session for persistence
        """
        self.db_session = db_session
        self.session_manager = SessionManager(db_session)
        self.mode_detector = ModeDetector()
        self.context_builder = ContextBuilder()
        self.agent_registry = get_agent_registry()

    async def handle_chat(self, request: ChatRequest) -> ChatResponse:
        """
        Handle a chat request.

        Args:
            request: ChatRequest with message and optional session_id

        Returns:
            ChatResponse with reply and session_id

        Raises:
            ValueError: If message is invalid
        """
        # Validate message
        if not request.message or not request.message.strip():
            raise ValueError("Message cannot be empty")

        if len(request.message) > settings.max_message_length:
            raise ValueError(
                f"Message too long (max {settings.max_message_length} characters)"
            )

        # Handle common greetings with friendly welcome
        if self._is_greeting(request.message):
            session = await self._get_or_create_session(request)
            welcome_message = self._get_welcome_message()
            
            await self._update_session_history(
                session.id,
                request.message,
                welcome_message
            )
            
            return ChatResponse(
                message=welcome_message,
                session_id=str(session.id),
                agent_type="general",
                metadata={"mode": "greeting"},
            )

        # Get or create session
        session = await self._get_or_create_session(request)

        logger.info(
            f"Processing chat: session={session.id}, "
            f"message_length={len(request.message)}"
        )

        # Detect conversation mode
        mode = self.mode_detector.detect_mode(
            request.message,
            session.conversation_history
        )

        # Select agent
        agent = self._select_agent(mode)

        if not agent:
            raise ValueError(f"No agent available for mode: {mode}")

        logger.info(f"Selected agent: {agent.name} for mode: {mode.value}")

        # Build context
        logger.info(f"🔧 Building context with use_rag={settings.enable_rag}")
        context = await self.context_builder.build_context(
            query=request.message,
            conversation_history=session.conversation_history,
            diver_profile=request.diver_profile or session.diver_profile,
            use_rag=settings.enable_rag,
        )
        logger.info(f"📦 Context built: has_rag={context.metadata.get('has_rag')}, rag_context_length={len(context.rag_context) if context.rag_context else 0}")

        # Execute agent
        result = await agent.execute(context)

        # Add safety disclaimer if needed
        response_message = result.response
        if settings.include_safety_disclaimer and mode == ConversationMode.SAFETY:
            response_message = self._add_safety_disclaimer(response_message)

        # Update session history
        await self._update_session_history(
            session.id,
            request.message,
            response_message
        )

        # Build response
        response = ChatResponse(
            message=response_message,
            session_id=str(session.id),
            agent_type=result.agent_type.value,
            metadata={
                "mode": mode.value,
                "confidence": result.confidence,
                "has_rag": context.metadata.get("has_rag", False),
                **result.metadata,
            },
        )

        logger.info(
            f"Chat completed: session={session.id}, "
            f"agent={agent.name}, "
            f"response_length={len(response_message)}"
        )

        return response

    async def _get_or_create_session(
        self,
        request: ChatRequest
    ) -> SessionData:
        """
        Get existing session or create new one.

        Args:
            request: Chat request

        Returns:
            SessionData (existing or newly created)
        """
        if request.session_id:
            session = await self.session_manager.get_session(request.session_id)
            if session:
                logger.debug(f"Using existing session: {request.session_id}")
                return session
            else:
                logger.warning(
                    f"Session not found: {request.session_id}, creating new session"
                )

        # Create new session
        session = await self.session_manager.create_session(
            diver_profile=request.diver_profile
        )
        logger.info(f"Created new session: {session.id}")
        return session

    def _select_agent(self, mode: ConversationMode) -> Optional[object]:
        """
        Select agent based on conversation mode.

        Args:
            mode: Detected conversation mode

        Returns:
            Agent instance or None
        """
        if not settings.enable_agent_routing:
            # Fallback to retrieval agent
            return self.agent_registry.get(AgentType.RETRIEVAL)

        # Map mode to agent type
        mode_to_agent = {
            ConversationMode.CERTIFICATION: AgentType.CERTIFICATION,
            ConversationMode.TRIP: AgentType.TRIP,
            ConversationMode.SAFETY: AgentType.SAFETY,
            ConversationMode.GENERAL: AgentType.RETRIEVAL,
        }

        agent_type = mode_to_agent.get(mode, AgentType.RETRIEVAL)
        agent = self.agent_registry.get(agent_type)

        # Fallback to retrieval if agent not found
        if not agent:
            logger.warning(f"Agent not found for {agent_type}, using retrieval")
            agent = self.agent_registry.get(AgentType.RETRIEVAL)

        return agent

    def _add_safety_disclaimer(self, message: str) -> str:
        """
        Add safety disclaimer to message.

        Args:
            message: Original message

        Returns:
            Message with disclaimer appended
        """
        from app.prompts.safety import SAFETY_DISCLAIMER

        return f"{message}\n\n{SAFETY_DISCLAIMER}"

    async def _update_session_history(
        self,
        session_id: UUID,
        user_message: str,
        assistant_message: str
    ):
        """
        Update session with new messages.

        Args:
            session_id: Session UUID
            user_message: User's message
            assistant_message: Assistant's response
        """
        try:
            # Append user message
            await self.session_manager.append_message(
                session_id=session_id,
                role="user",
                content=user_message
            )

            # Append assistant message
            await self.session_manager.append_message(
                session_id=session_id,
                role="assistant",
                content=assistant_message
            )

            logger.debug(f"Updated session history: {session_id}")

        except Exception as e:
            logger.error(
                f"Failed to update session history: {session_id}",
                exc_info=True
            )
            # Don't fail the request if history update fails
            pass

    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Get session by ID.

        Args:
            session_id: Session UUID string

        Returns:
            SessionData if found, None otherwise
        """
        return await self.session_manager.get_session(session_id)

    def _is_greeting(self, message: str) -> bool:
        """
        Check if message is a common greeting.

        Args:
            message: User's message

        Returns:
            True if message is a greeting, False otherwise
        """
        greetings = {'hi', 'hello', 'hey', 'greetings', 'howdy', 'good morning', 'good afternoon', 'good evening'}
        normalized = message.strip().lower()
        return normalized in greetings

    def _get_welcome_message(self) -> str:
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
