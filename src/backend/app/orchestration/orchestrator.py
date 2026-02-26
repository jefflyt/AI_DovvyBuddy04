"""
Chat orchestrator - main conversation controller.
"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.feature_flags import FeatureFlag, is_feature_enabled

from .agent_router import AgentRouter
from .context_builder import ContextBuilder
from .gemini_orchestrator import GeminiOrchestrator
from .emergency_detector_hybrid import EmergencyDetector
from .mode_detector import ConversationMode
from .response_formatter import ResponseFormatter
from .session_manager import SessionManager
from .types import ChatRequest, ChatResponse, SessionData, IntentType, SessionState

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
        self.context_builder = ContextBuilder()
        self.agent_router = AgentRouter()
        self.response_formatter = ResponseFormatter()
        
        self.emergency_detector = EmergencyDetector()

        if not settings.enable_adk:
            raise RuntimeError(
                "Google ADK orchestration is required. Set ENABLE_ADK=true."
            )

        if not settings.enable_agent_routing:
            raise RuntimeError(
                "Google ADK orchestration is required. Set ENABLE_AGENT_ROUTING=true."
            )

        self.orchestrator = GeminiOrchestrator()
        logger.info(f"Google ADK orchestration enabled with model={settings.adk_model}")

    @staticmethod
    def _intent_to_mode(intent: IntentType) -> ConversationMode:
        """Map ConversationManager intent to ConversationMode for agent routing."""
        intent_mode_map = {
            IntentType.AGENCY_CERT: ConversationMode.CERTIFICATION,
            IntentType.DIVE_PLANNING: ConversationMode.TRIP,
            IntentType.EMERGENCY_MEDICAL: ConversationMode.SAFETY,
            IntentType.SKILL_EXPLANATION: ConversationMode.GENERAL,
            IntentType.MARINE_LIFE: ConversationMode.GENERAL,
            IntentType.GEAR: ConversationMode.GENERAL,
            IntentType.CONDITIONS: ConversationMode.GENERAL,
            IntentType.INFO_LOOKUP: ConversationMode.GENERAL,
        }
        return intent_mode_map.get(intent, ConversationMode.GENERAL)

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
        if self.response_formatter.is_greeting(request.message):
            session = await self._get_or_create_session(request)
            welcome_message = self.response_formatter.get_welcome_message()
            
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

        # PR6.1: Check for emergency FIRST (safety-critical, hybrid detection)
        follow_up_question = None
        state_updates = {}
        detected_intent = None
        
        if is_feature_enabled(FeatureFlag.CONVERSATION_FOLLOWUP) and self.emergency_detector:
            # Use hybrid detection: keywords for speed + LLM for ambiguous cases
            is_emergency, emergency_response = await self.emergency_detector.detect_emergency(
                request.message,
                conversation_history=session.conversation_history
            )
            
            if is_emergency:
                # Emergency detected: bypass conversation manager, return safety response
                logger.warning(f"Emergency detected for session {session.id}")
                
                await self._update_session_history(
                    session.id,
                    request.message,
                    emergency_response
                )
                
                return ChatResponse(
                    message=emergency_response,
                    session_id=str(session.id),
                    agent_type="emergency",
                    metadata={"mode": "emergency", "emergency_detected": True},
                    follow_up_question=None,  # No follow-up for emergencies
                )
        
        
        # PR6.1: Run orchestrator for intent + state BEFORE agent execution
        mode = ConversationMode.GENERAL  # Default mode
        detected_intent = None
        session_state = None
        
        if not self.orchestrator:
            raise RuntimeError("Google ADK orchestrator is unavailable")

        # Parse session state from request
        if request.session_state:
            session_state = SessionState.from_dict(request.session_state)

        # Route request using Gemini Function Calling (ADK pattern)
        route_result = await self.orchestrator.route_request(
            message=request.message,
            history=session.conversation_history,
            state=session_state,
        )

        target_agent = route_result.get("target_agent")
        parameters = route_result.get("parameters", {})

        logger.info(f"Gemini routed to: {target_agent} with params: {parameters}")

        # Map Gemini Agent -> Conversation Mode
        if target_agent == "trip_planner":
            mode = ConversationMode.TRIP
            detected_intent = IntentType.DIVE_PLANNING.value

            # Extract location state if present
            if "location" in parameters and parameters["location"]:
                state_updates["location_known"] = True
        else:
            # Default / knowledge_base
            mode = ConversationMode.GENERAL
            detected_intent = IntentType.INFO_LOOKUP.value

        # Select agent
        agent = self.agent_router.select_agent(mode)

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

        # PR6.2: Sanitize response to remove any leaked RAG mentions
        # DISABLED: This was too aggressive and removed valid phrases like "the information provided"
        # which caused confusing responses. Agent prompts should handle this instead.
        # sanitized_response = self.response_formatter.sanitize_response(result.response)
        sanitized_response = result.response  # Use original response
        
        # PR6.1: Follow-up generation (Simplified for now - can be re-added to GeminiOrchestrator later)
        # For now, we rely on the Agent's response or simple rules.
        follow_up_question = None
        # We could implement a simple follow-up generator here if needed, 
        # but for clean architecture we rely on the specific agents or a dedicated call.
        pass
        
        # PR6.2: Extract citations from context (if RAG was used)
        citations = []
        if context.rag_context and hasattr(context, 'metadata'):
            # Try to get citations from context metadata (if available from RAG pipeline)
            if 'rag_citations' in context.metadata:
                citations = context.metadata['rag_citations']
            # Also check result metadata for citations
            elif 'citations' in result.metadata:
                citations = result.metadata['citations']
        
        # Log response discipline check
        response_length = len(sanitized_response)
        estimated_tokens = response_length // 4  # Rough estimate: 1 token ≈ 4 chars
        violations = []
        
        # Check for discipline violations
        forbidden_terms = ["provided context", "source:", "document", "retrieval", "according to"]
        for term in forbidden_terms:
            if term.lower() in sanitized_response.lower():
                violations.append(term)
        
        if violations or estimated_tokens > 120:
            logger.warning(
                "Response discipline check",
                extra={
                    "session_id": str(session.id),
                    "agent_type": agent.name,
                    "response_length": response_length,
                    "estimated_tokens": estimated_tokens,
                    "has_rag_mentions": len(violations) > 0,
                    "violations": violations,
                    "exceeds_token_limit": estimated_tokens > 120,
                }
            )

        # Format response with disclaimer and follow-up
        response_message = await self.response_formatter.format_response(
            message=sanitized_response,
            mode=mode,
            follow_up_question=follow_up_question,
            agent_type=agent.name.lower(),  # Pass agent type for disclaimer logic
            user_message=request.message,  # Pass original message for medical keyword detection
        )

        # Update session history
        await self._update_session_history(
            session.id,
            request.message,
            response_message
        )

        # Build response
        response_metadata = {
            "mode": mode.value,
            "confidence": result.confidence,
            "has_rag": context.metadata.get("has_rag", False),
            **result.metadata,
        }
        
        # PR6.2: Add citations to metadata (not visible in response text)
        if citations:
            response_metadata["citations"] = citations
        
        # PR6.1: Add conversation metadata
        if detected_intent:
            response_metadata["detected_intent"] = detected_intent
        if state_updates:
            response_metadata["state_updates"] = state_updates
        
        response = ChatResponse(
            message=response_message,
            session_id=str(session.id),
            agent_type=result.agent_type.value,
            metadata=response_metadata,
            follow_up_question=follow_up_question,
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

        except Exception:
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

