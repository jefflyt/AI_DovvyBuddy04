"""ADK-native multi-agent orchestration graph."""

import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

from app.core.config import settings

from .tools import ADKToolbox
from .types import (
    AgentTurnTrace,
    NativeTurnResult,
    PolicyValidationResult,
    RouteDecision,
    RouteName,
    SafetyClassification,
)

logger = logging.getLogger(__name__)


class ADKNativeGraphOrchestrator:
    """Coordinator + specialist ADK graph for one chat turn."""

    def __init__(self):
        self.api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("Gemini API key is required for ADK native graph")
        os.environ["GOOGLE_API_KEY"] = self.api_key

        self.model_name = settings.adk_model
        self.app_name = "dovvybuddy_adk_graph"
        self.user_id = "backend-native-graph"

        self.tools = ADKToolbox()

        self.router_agent = self._build_router_agent()
        self.router_runner = InMemoryRunner(
            agent=self.router_agent,
            app_name=f"{self.app_name}_router",
        )

        self.specialist_agents = self._build_specialist_agents()
        self.specialist_runners: Dict[str, InMemoryRunner] = {
            name: InMemoryRunner(
                agent=agent,
                app_name=f"{self.app_name}_{name}",
            )
            for name, agent in self.specialist_agents.items()
        }

    def _build_router_agent(self) -> LlmAgent:
        return LlmAgent(
            name="dovvy_orchestrator",
            model=Gemini(model=self.model_name),
            instruction=(
                "You are DovvyBuddy's coordinator. "
                "Call exactly one route tool based on user intent:\n"
                "- route_trip_specialist: destinations, sites, planning\n"
                "- route_certification_specialist: PADI/SSI training and cert pathways\n"
                "- route_safety_specialist: medical or safety concerns\n"
                "- route_general_retrieval_specialist: general diving knowledge\n"
                "Always include a short reason."
            ),
            tools=[
                self.route_trip_specialist,
                self.route_certification_specialist,
                self.route_general_retrieval_specialist,
                self.route_safety_specialist,
            ],
            generate_content_config=types.GenerateContentConfig(temperature=0.0),
        )

    def _build_specialist_agents(self) -> Dict[str, LlmAgent]:
        common_tools = [
            self.tools.session_context_tool,
            self.tools.rag_search_tool,
            self.tools.safety_classification_tool,
            self.tools.response_policy_tool,
        ]
        specialist_model = Gemini(model=self.model_name)

        return {
            "trip_specialist": LlmAgent(
                name="trip_specialist",
                model=specialist_model,
                instruction=(
                    "You are DovvyBuddy trip specialist. "
                    "For factual destination/site claims, call rag_search_tool first. "
                    "Keep answers practical and end with one forward-moving follow-up question."
                ),
                tools=common_tools,
                generate_content_config=types.GenerateContentConfig(temperature=0.4),
            ),
            "certification_specialist": LlmAgent(
                name="certification_specialist",
                model=specialist_model,
                instruction=(
                    "You are DovvyBuddy certification specialist for PADI/SSI pathways. "
                    "Ground factual requirements via rag_search_tool before answering."
                ),
                tools=common_tools,
                generate_content_config=types.GenerateContentConfig(temperature=0.3),
            ),
            "general_retrieval_specialist": LlmAgent(
                name="general_retrieval_specialist",
                model=specialist_model,
                instruction=(
                    "You handle general diving Q&A. "
                    "Use rag_search_tool for factual claims and avoid speculation."
                ),
                tools=common_tools,
                generate_content_config=types.GenerateContentConfig(temperature=0.3),
            ),
            "safety_specialist": LlmAgent(
                name="safety_specialist",
                model=specialist_model,
                instruction=(
                    "You provide conservative diving safety guidance. "
                    "Do not diagnose. Encourage professional medical advice for health concerns."
                ),
                tools=common_tools,
                generate_content_config=types.GenerateContentConfig(temperature=0.2),
            ),
        }

    async def _ensure_session(
        self,
        runner: InMemoryRunner,
        *,
        session_id: str,
        state: Optional[Dict[str, Any]] = None,
    ) -> None:
        session = await runner.session_service.get_session(
            app_name=runner.app_name,
            user_id=self.user_id,
            session_id=session_id,
        )
        if not session:
            await runner.session_service.create_session(
                app_name=runner.app_name,
                user_id=self.user_id,
                session_id=session_id,
                state=state or {},
            )

    @staticmethod
    def _extract_text(event) -> str:
        content = getattr(event, "content", None)
        if not content or not getattr(content, "parts", None):
            return ""
        parts = []
        for part in content.parts:
            text = getattr(part, "text", None)
            if text:
                parts.append(text)
        return "".join(parts).strip()

    async def _route_request(
        self,
        *,
        message: str,
        history: List[Dict[str, str]],
        session_id: str,
        session_state: Optional[Dict[str, Any]],
    ) -> Tuple[RouteDecision, List[str]]:
        await self._ensure_session(
            self.router_runner,
            session_id=session_id,
            state=session_state or {},
        )

        prompt = message
        if history:
            history_str = "\n".join(
                f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                for msg in history[-3:]
            )
            prompt = f"Recent history:\n{history_str}\n\nUser request:\n{message}"

        user_message = types.Content(role="user", parts=[types.Part(text=prompt)])

        called_tools: List[str] = []
        route = RouteDecision(route="general_retrieval_specialist", reason="default")
        async for event in self.router_runner.run_async(
            user_id=self.user_id,
            session_id=session_id,
            new_message=user_message,
        ):
            function_calls = event.get_function_calls()
            for call in function_calls:
                called_tools.append(call.name)
                args = dict(call.args) if call.args else {}
                mapped_route = self._map_route_tool_to_specialist(call.name)
                if mapped_route:
                    route = RouteDecision(
                        route=mapped_route,
                        reason=args.get("reason", ""),
                        confidence=0.85,
                        parameters=args,
                    )
                    return route, called_tools

        return route, called_tools

    async def _run_specialist(
        self,
        *,
        route: RouteName,
        message: str,
        session_id: str,
        session_state: Optional[Dict[str, Any]],
    ) -> Tuple[str, List[str]]:
        runner = self.specialist_runners[route]
        await self._ensure_session(runner, session_id=session_id, state=session_state or {})

        user_message = types.Content(role="user", parts=[types.Part(text=message)])

        response_text = ""
        called_tools: List[str] = []
        async for event in runner.run_async(
            user_id=self.user_id,
            session_id=session_id,
            new_message=user_message,
        ):
            function_calls = event.get_function_calls()
            for call in function_calls:
                called_tools.append(call.name)

            text = self._extract_text(event)
            if text:
                response_text = text

            if event.is_final_response() and text:
                response_text = text

        return response_text, called_tools

    @staticmethod
    def _map_route_tool_to_specialist(tool_name: str) -> Optional[RouteName]:
        route_map = {
            "route_trip_specialist": "trip_specialist",
            "route_certification_specialist": "certification_specialist",
            "route_general_retrieval_specialist": "general_retrieval_specialist",
            "route_safety_specialist": "safety_specialist",
        }
        return route_map.get(tool_name)

    async def run_turn(
        self,
        *,
        message: str,
        session_id: str,
        conversation_history: List[Dict[str, str]],
        session_state: Optional[Dict[str, Any]] = None,
        diver_profile: Optional[Dict[str, Any]] = None,
    ) -> NativeTurnResult:
        started = time.perf_counter()
        self.tools.set_turn_context(
            session_id=session_id,
            message=message,
            history=conversation_history,
            session_state=session_state,
            diver_profile=diver_profile,
        )

        safety_started = time.perf_counter()
        safety_data = await self.tools.safety_classification_tool(
            message=message,
            history=conversation_history,
        )
        safety_latency_ms = (time.perf_counter() - safety_started) * 1000
        safety_classification = SafetyClassification(
            classification=safety_data["classification"],
            is_emergency=safety_data["is_emergency"],
            is_medical=safety_data["is_medical"],
        )

        route_started = time.perf_counter()
        route_decision, route_tools_called = await self._route_request(
            message=message,
            history=conversation_history,
            session_id=session_id,
            session_state=session_state,
        )
        route_latency_ms = (time.perf_counter() - route_started) * 1000

        specialist_started = time.perf_counter()
        specialist_response, specialist_tools_called = await self._run_specialist(
            route=route_decision.route,
            message=message,
            session_id=session_id,
            session_state=session_state,
        )
        specialist_latency_ms = (time.perf_counter() - specialist_started) * 1000

        citations = self.tools.last_rag_result.citations
        if not specialist_response:
            specialist_response = (
                "I’m sorry, I couldn’t generate a complete answer right now. "
                "Please try rephrasing your question."
            )

        policy_data = self.tools.response_policy_tool(
            answer=specialist_response,
            citations=citations,
            safety_flags=safety_data,
        )
        policy_validation = PolicyValidationResult(
            is_allowed=policy_data["is_allowed"],
            policy_enforced=policy_data["policy_enforced"],
            reason=policy_data["reason"],
            should_append_uncertainty=policy_data["should_append_uncertainty"],
        )

        response_message = specialist_response
        if policy_validation.should_append_uncertainty:
            response_message = (
                f"{specialist_response}\n\n"
                "I don’t have enough verified sources to fully ground that answer yet. "
                "If you can share more specifics, I can narrow it down."
            )

        total_latency_ms = (time.perf_counter() - started) * 1000
        trace = AgentTurnTrace(
            tools_called=route_tools_called + specialist_tools_called,
            citations_count=len(citations),
            safety_label=safety_classification.classification,
            route=route_decision.route,
            latency_ms={
                "safety_classification_ms": safety_latency_ms,
                "route_ms": route_latency_ms,
                "specialist_ms": specialist_latency_ms,
                "total_ms": total_latency_ms,
            },
        )

        state_updates: Dict[str, Any] = {
            "last_route": route_decision.route,
            "medical_flag": safety_classification.is_medical,
            "citations_used": bool(citations),
        }
        location = route_decision.parameters.get("location")
        if location:
            state_updates["location_known"] = True

        return NativeTurnResult(
            message=response_message,
            route_decision=route_decision,
            citations=citations,
            safety_classification=safety_classification,
            policy_validation=policy_validation,
            state_updates=state_updates,
            trace=trace,
        )

    def route_trip_specialist(
        self,
        query: str,
        reason: str = "",
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "route": "trip_specialist",
            "query": query,
            "reason": reason,
            "location": location,
        }

    def route_certification_specialist(
        self,
        query: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        return {
            "route": "certification_specialist",
            "query": query,
            "reason": reason,
        }

    def route_general_retrieval_specialist(
        self,
        query: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        return {
            "route": "general_retrieval_specialist",
            "query": query,
            "reason": reason,
        }

    def route_safety_specialist(
        self,
        query: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        return {
            "route": "safety_specialist",
            "query": query,
            "reason": reason,
        }
