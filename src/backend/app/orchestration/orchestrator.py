"""Chat orchestrator - main conversation controller."""

from __future__ import annotations

import logging
from typing import Any, AsyncGenerator, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.feature_flags import FeatureFlag, is_feature_enabled
from app.core.quota_manager import QuotaExceededError, get_quota_manager

from .agent_router import AgentRouter
from .context_builder import ContextBuilder
from .emergency_detector_hybrid import EmergencyDetector
from .gemini_orchestrator import GeminiOrchestrator
from .mode_detector import ConversationMode
from .response_formatter import ResponseFormatter
from .session_manager import SessionManager
from .types import ChatRequest, ChatResponse, IntentType, SessionData, SessionState

try:
    from app.adk import ADKNativeGraphOrchestrator, NativeTurnResult
except Exception:  # pragma: no cover - fallback for partially deployed environments
    ADKNativeGraphOrchestrator = None  # type: ignore[assignment]
    NativeTurnResult = Any  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class ChatOrchestrator:
    """Main orchestrator for chat conversations."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.session_manager = SessionManager(db_session)
        self.context_builder = ContextBuilder()
        self.agent_router = AgentRouter()
        self.response_formatter = ResponseFormatter()
        self.emergency_detector = EmergencyDetector()
        self.quota_manager = get_quota_manager()

        if not settings.enable_adk:
            raise RuntimeError("Google ADK orchestration is required. Set ENABLE_ADK=true.")
        if not settings.enable_agent_routing:
            raise RuntimeError(
                "Google ADK orchestration is required. Set ENABLE_AGENT_ROUTING=true."
            )

        self.native_graph_orchestrator: Optional[ADKNativeGraphOrchestrator] = None
        if (
            settings.enable_adk_native_graph
            and ADKNativeGraphOrchestrator is not None
        ):
            self.native_graph_orchestrator = ADKNativeGraphOrchestrator()
            logger.info(
                "Google ADK native graph enabled with model=%s",
                settings.adk_model,
            )

        # Legacy ADK router fallback remains available for staged rollout.
        self.orchestrator = GeminiOrchestrator()
        logger.info("Google ADK orchestration enabled with model=%s", settings.adk_model)

    @staticmethod
    def _route_to_mode(route: str) -> ConversationMode:
        route_mode_map = {
            "trip_specialist": ConversationMode.TRIP,
            "certification_specialist": ConversationMode.CERTIFICATION,
            "safety_specialist": ConversationMode.SAFETY,
            "general_retrieval_specialist": ConversationMode.GENERAL,
        }
        return route_mode_map.get(route, ConversationMode.GENERAL)

    @staticmethod
    def _route_to_agent_type(route: str) -> str:
        route_agent_map = {
            "trip_specialist": "trip",
            "certification_specialist": "certification",
            "safety_specialist": "safety",
            "general_retrieval_specialist": "retrieval",
        }
        return route_agent_map.get(route, "retrieval")

    @staticmethod
    def _mode_to_intent(mode: ConversationMode) -> str:
        if mode == ConversationMode.TRIP:
            return IntentType.DIVE_PLANNING.value
        if mode == ConversationMode.CERTIFICATION:
            return IntentType.AGENCY_CERT.value
        if mode == ConversationMode.SAFETY:
            return IntentType.EMERGENCY_MEDICAL.value
        return IntentType.INFO_LOOKUP.value

    @staticmethod
    def _normalize_legacy_target(route_name: str) -> str:
        # Backward compatibility with older ADK router tool names.
        legacy_map = {
            "trip_planner": "trip_specialist",
            "knowledge_base": "general_retrieval_specialist",
            "route_trip_specialist": "trip_specialist",
            "route_certification_specialist": "certification_specialist",
            "route_safety_specialist": "safety_specialist",
            "route_general_retrieval_specialist": "general_retrieval_specialist",
        }
        return legacy_map.get(route_name, route_name)

    def _quota_snapshot(self) -> Dict[str, Dict[str, Any]]:
        return self.quota_manager.snapshot_all()

    def _quota_exhausted_response(
        self,
        *,
        session_id: str,
        bucket: str,
        snapshot: Dict[str, Any],
    ) -> ChatResponse:
        return ChatResponse(
            message=(
                "I’ve reached the current daily AI usage limit for this service. "
                "Please try again later."
            ),
            session_id=session_id,
            agent_type="system",
            metadata={
                "mode": "quota_exhausted",
                "route_decision": {
                    "route": "general_retrieval_specialist",
                    "reason": "daily_quota_exhausted",
                    "confidence": 1.0,
                    "parameters": {},
                },
                "safety_classification": {
                    "classification": "non_medical",
                    "is_emergency": False,
                    "is_medical": False,
                },
                "policy_enforced": True,
                "quota_snapshot": {
                    **self._quota_snapshot(),
                    bucket: snapshot,
                },
            },
            follow_up_question=None,
        )

    async def _build_native_response(
        self,
        *,
        session: SessionData,
        request: ChatRequest,
        graph_result: NativeTurnResult,
    ) -> ChatResponse:
        mode = self._route_to_mode(graph_result.route_decision.route)
        agent_type = self._route_to_agent_type(graph_result.route_decision.route)

        response_message = await self.response_formatter.format_response(
            message=graph_result.message,
            mode=mode,
            follow_up_question=None,
            agent_type=agent_type,
            user_message=request.message,
            safety_classification=graph_result.safety_classification.classification,
        )

        await self._update_session_history(
            session.id,
            request.message,
            response_message,
        )

        metadata: Dict[str, Any] = {
            "mode": mode.value,
            "confidence": graph_result.route_decision.confidence,
            "has_rag": bool(graph_result.citations),
            "route_decision": graph_result.route_decision.to_dict(),
            "safety_classification": graph_result.safety_classification.to_dict(),
            "policy_enforced": graph_result.policy_validation.policy_enforced,
            "trace": graph_result.trace.to_dict(),
            "state_updates": graph_result.state_updates,
            "quota_snapshot": graph_result.quota_snapshot or self._quota_snapshot(),
        }
        if graph_result.citations:
            metadata["citations"] = graph_result.citations

        return ChatResponse(
            message=response_message,
            session_id=str(session.id),
            agent_type=agent_type,
            metadata=metadata,
            follow_up_question=None,
        )

    async def _handle_native_graph_turn(
        self,
        *,
        session: SessionData,
        request: ChatRequest,
        session_state: Optional[SessionState],
    ) -> Optional[ChatResponse]:
        if not self.native_graph_orchestrator:
            return None

        try:
            graph_result = await self.native_graph_orchestrator.run_turn(
                message=request.message,
                session_id=str(session.id),
                conversation_history=session.conversation_history,
                session_state=session_state.to_dict() if session_state else {},
                diver_profile=request.diver_profile or session.diver_profile,
            )
        except QuotaExceededError as exc:
            return self._quota_exhausted_response(
                session_id=str(session.id),
                bucket=exc.bucket,
                snapshot=exc.snapshot.to_dict(),
            )
        except Exception:
            logger.error("ADK native graph failed, falling back to legacy flow", exc_info=True)
            return None

        return await self._build_native_response(
            session=session,
            request=request,
            graph_result=graph_result,
        )

    async def _handle_emergency_precheck(
        self,
        *,
        session: SessionData,
        request: ChatRequest,
    ) -> Optional[ChatResponse]:
        if not (
            self.emergency_detector
            and is_feature_enabled(FeatureFlag.CONVERSATION_FOLLOWUP)
        ):
            return None

        is_emergency, emergency_response = await self.emergency_detector.detect_emergency(
            request.message,
            conversation_history=session.conversation_history,
        )
        if not is_emergency:
            return None

        logger.warning("Emergency detected for session %s", session.id)
        await self._update_session_history(
            session.id,
            request.message,
            emergency_response,
        )
        return ChatResponse(
            message=emergency_response,
            session_id=str(session.id),
            agent_type="emergency",
            metadata={
                "mode": "emergency",
                "emergency_detected": True,
                "route_decision": {
                    "route": "safety_specialist",
                    "reason": "emergency_precheck",
                    "confidence": 1.0,
                    "parameters": {},
                },
                "safety_classification": {
                    "classification": "emergency",
                    "is_emergency": True,
                    "is_medical": True,
                },
                "policy_enforced": True,
                "quota_snapshot": self._quota_snapshot(),
            },
            follow_up_question=None,
        )

    async def handle_chat(self, request: ChatRequest) -> ChatResponse:
        if not request.message or not request.message.strip():
            raise ValueError("Message cannot be empty")
        if len(request.message) > settings.max_message_length:
            raise ValueError(
                f"Message too long (max {settings.max_message_length} characters)"
            )

        if self.response_formatter.is_greeting(request.message):
            session = await self._get_or_create_session(request)
            welcome_message = self.response_formatter.get_welcome_message()
            await self._update_session_history(session.id, request.message, welcome_message)
            return ChatResponse(
                message=welcome_message,
                session_id=str(session.id),
                agent_type="general",
                metadata={"mode": "greeting", "quota_snapshot": self._quota_snapshot()},
            )

        session = await self._get_or_create_session(request)
        logger.info(
            "Processing chat session=%s message_length=%s",
            session.id,
            len(request.message),
        )

        emergency_response = await self._handle_emergency_precheck(
            session=session,
            request=request,
        )
        if emergency_response:
            return emergency_response

        session_state = (
            SessionState.from_dict(request.session_state)
            if request.session_state
            else None
        )

        native_response = await self._handle_native_graph_turn(
            session=session,
            request=request,
            session_state=session_state,
        )
        if native_response:
            logger.info(
                "Chat completed via ADK native graph session=%s agent=%s",
                session.id,
                native_response.agent_type,
            )
            return native_response

        if not self.orchestrator:
            raise RuntimeError("Google ADK orchestrator is unavailable")

        try:
            try:
                route_result = await self.orchestrator.route_request(
                    message=request.message,
                    history=session.conversation_history,
                    state=session_state,
                    session_id=str(session.id),
                )
            except QuotaExceededError:
                raise
            except Exception:
                logger.warning(
                    "ADK route request failed; falling back to general_retrieval_specialist",
                    exc_info=True,
                )
                route_result = {
                    "target_agent": "general_retrieval_specialist",
                    "parameters": {"reason": "router_fallback"},
                }

            raw_target = route_result.get("target_agent", "general_retrieval_specialist")
            target_route = self._normalize_legacy_target(raw_target)
            parameters = route_result.get("parameters", {})
            mode = self._route_to_mode(target_route)
            detected_intent = self._mode_to_intent(mode)

            state_updates: Dict[str, Any] = {
                "last_route": target_route,
            }
            if parameters.get("location"):
                state_updates["location_known"] = True

            agent = self.agent_router.select_agent(mode)
            if not agent:
                raise ValueError(f"No agent available for mode: {mode}")

            logger.info("Selected agent=%s mode=%s", agent.name, mode.value)
            context = await self.context_builder.build_context(
                query=request.message,
                conversation_history=session.conversation_history,
                diver_profile=request.diver_profile or session.diver_profile,
                use_rag=settings.enable_rag,
            )
            result = await agent.execute(context)
            sanitized_response = result.response

            citations: list[str] = []
            if context.rag_context and hasattr(context, "metadata"):
                if "rag_citations" in context.metadata:
                    citations = context.metadata["rag_citations"]
                elif "citations" in result.metadata:
                    citations = result.metadata["citations"]

            response_message = await self.response_formatter.format_response(
                message=sanitized_response,
                mode=mode,
                follow_up_question=None,
                agent_type=agent.name.lower(),
                user_message=request.message,
                safety_classification=(
                    "medical" if mode == ConversationMode.SAFETY else "non_medical"
                ),
            )

            await self._update_session_history(
                session.id,
                request.message,
                response_message,
            )

            response_metadata: Dict[str, Any] = {
                "mode": mode.value,
                "confidence": result.confidence,
                "has_rag": context.metadata.get("has_rag", False),
                "route_decision": {
                    "route": target_route,
                    "reason": parameters.get("reason", ""),
                    "confidence": result.confidence,
                    "parameters": parameters,
                },
                "safety_classification": {
                    "classification": (
                        "medical" if mode == ConversationMode.SAFETY else "non_medical"
                    ),
                    "is_emergency": False,
                    "is_medical": mode == ConversationMode.SAFETY,
                },
                "policy_enforced": False,
                "state_updates": state_updates,
                "detected_intent": detected_intent,
                "quota_snapshot": self._quota_snapshot(),
                **result.metadata,
            }
            if citations:
                response_metadata["citations"] = citations

            return ChatResponse(
                message=response_message,
                session_id=str(session.id),
                agent_type=result.agent_type.value,
                metadata=response_metadata,
                follow_up_question=None,
            )
        except QuotaExceededError as exc:
            return self._quota_exhausted_response(
                session_id=str(session.id),
                bucket=exc.bucket,
                snapshot=exc.snapshot.to_dict(),
            )

    async def stream_chat(
        self,
        request: ChatRequest,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat events for SSE transport."""
        if not request.message or not request.message.strip():
            yield {"type": "error", "content": "message_empty"}
            return
        if len(request.message) > settings.max_message_length:
            yield {
                "type": "error",
                "content": "message_too_long",
                "metadata": {"max": settings.max_message_length},
            }
            return

        if self.response_formatter.is_greeting(request.message):
            session = await self._get_or_create_session(request)
            welcome_message = self.response_formatter.get_welcome_message()
            await self._update_session_history(session.id, request.message, welcome_message)
            yield {
                "type": "final",
                "content": welcome_message,
                "metadata": {
                    "sessionId": str(session.id),
                    "agentType": "general",
                    "metadata": {
                        "mode": "greeting",
                        "quota_snapshot": self._quota_snapshot(),
                    },
                },
            }
            return

        session = await self._get_or_create_session(request)
        emergency_response = await self._handle_emergency_precheck(
            session=session,
            request=request,
        )
        if emergency_response:
            yield _stream_event("safety", emergency_response.metadata["safety_classification"])
            yield _stream_event(
                "final",
                emergency_response.message,
                {
                    "sessionId": emergency_response.session_id,
                    "agentType": emergency_response.agent_type,
                    "metadata": emergency_response.metadata,
                },
            )
            return

        session_state = (
            SessionState.from_dict(request.session_state)
            if request.session_state
            else None
        )

        if self.native_graph_orchestrator:
            async for native_event in self.native_graph_orchestrator.stream_turn(
                message=request.message,
                session_id=str(session.id),
                conversation_history=session.conversation_history,
                session_state=session_state.to_dict() if session_state else {},
                diver_profile=request.diver_profile or session.diver_profile,
            ):
                event_type = native_event.get("type")
                if event_type in {"route", "safety", "token", "citation"}:
                    yield native_event
                    continue

                if event_type == "error":
                    yield native_event
                    return

                if event_type == "final":
                    turn_result = native_event.get("turn_result")
                    if not turn_result:
                        yield {"type": "error", "content": "missing_turn_result"}
                        return

                    mode = self._route_to_mode(turn_result.route_decision.route)
                    agent_type = self._route_to_agent_type(turn_result.route_decision.route)
                    formatted_message = await self.response_formatter.format_response(
                        message=turn_result.message,
                        mode=mode,
                        follow_up_question=None,
                        agent_type=agent_type,
                        user_message=request.message,
                        safety_classification=turn_result.safety_classification.classification,
                    )
                    if formatted_message.startswith(turn_result.message):
                        tail = formatted_message[len(turn_result.message) :]
                        if tail:
                            yield {"type": "token", "content": tail}

                    await self._update_session_history(
                        session.id,
                        request.message,
                        formatted_message,
                    )
                    metadata: Dict[str, Any] = {
                        "mode": mode.value,
                        "confidence": turn_result.route_decision.confidence,
                        "has_rag": bool(turn_result.citations),
                        "route_decision": turn_result.route_decision.to_dict(),
                        "safety_classification": turn_result.safety_classification.to_dict(),
                        "policy_enforced": turn_result.policy_validation.policy_enforced,
                        "trace": turn_result.trace.to_dict(),
                        "state_updates": turn_result.state_updates,
                        "quota_snapshot": turn_result.quota_snapshot
                        or self._quota_snapshot(),
                    }
                    if turn_result.citations:
                        metadata["citations"] = turn_result.citations

                    yield _stream_event(
                        "final",
                        formatted_message,
                        {
                            "sessionId": str(session.id),
                            "agentType": agent_type,
                            "metadata": metadata,
                        },
                    )
                    return

            return

        # Legacy fallback (non-native graph): no post-hoc token splitting.
        response = await self.handle_chat(request)
        if response.metadata.get("route_decision"):
            yield _stream_event("route", response.metadata["route_decision"])
        if response.metadata.get("safety_classification"):
            yield _stream_event("safety", response.metadata["safety_classification"])
        for citation in response.metadata.get("citations", []):
            yield _stream_event("citation", citation)
        yield _stream_event(
            "final",
            response.message,
            {
                "sessionId": response.session_id,
                "agentType": response.agent_type,
                "metadata": response.metadata,
            },
        )

    async def _get_or_create_session(self, request: ChatRequest) -> SessionData:
        if request.session_id:
            session = await self.session_manager.get_session(request.session_id)
            if session:
                logger.debug("Using existing session: %s", request.session_id)
                return session
            logger.warning("Session not found: %s, creating new session", request.session_id)

        session = await self.session_manager.create_session(diver_profile=request.diver_profile)
        logger.info("Created new session: %s", session.id)
        return session

    async def _update_session_history(
        self,
        session_id: UUID,
        user_message: str,
        assistant_message: str,
    ) -> None:
        try:
            await self.session_manager.append_message(
                session_id=session_id,
                role="user",
                content=user_message,
            )
            await self.session_manager.append_message(
                session_id=session_id,
                role="assistant",
                content=assistant_message,
            )
            logger.debug("Updated session history: %s", session_id)
        except Exception:
            logger.error("Failed to update session history: %s", session_id, exc_info=True)

    async def get_session(self, session_id: str) -> Optional[SessionData]:
        return await self.session_manager.get_session(session_id)


def _stream_event(
    event_type: str,
    content: Any,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"type": event_type, "content": content}
    if metadata:
        payload["metadata"] = metadata
    return payload
