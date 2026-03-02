"""
Google ADK orchestrator for semantic routing.

Uses Google ADK's LlmAgent + Runner pattern to route user queries to
the appropriate specialist tool.
"""

import logging
import os
from typing import Dict, List, Optional, Any
from uuid import uuid4

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

from app.core.config import settings
from app.core.quota_manager import QuotaExceededError, get_quota_manager
from app.orchestration.types import SessionState
from app.services.cost.token_cost import estimate_tokens_from_text

logger = logging.getLogger(__name__)


class GeminiOrchestrator:
    """
    Orchestrates conversation flow using Gemini Function Calling.
    
    Acts as a router that translates user intent into specific agent calls.
    """
    
    def __init__(self):
        """Initialize ADK runner with routing tools."""
        self.api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("Gemini API key not found. Google ADK orchestrator cannot start.")
        os.environ["GOOGLE_API_KEY"] = self.api_key

        self.model_name = settings.adk_model
        self.app_name = "dovvybuddy_orchestrator"
        self.user_id = "backend-orchestrator"
        self.quota_manager = get_quota_manager()

        self.agent = LlmAgent(
            name="dovvy_router",
            model=Gemini(model=self.model_name),
            instruction="""You are the DovvyBuddy routing coordinator.
Route each turn by calling exactly ONE tool:
- route_trip_specialist: destination, site, conditions, trip planning
- route_certification_specialist: certification pathways and prerequisites
- route_safety_specialist: medical or safety risk concerns
- route_general_retrieval_specialist: all other general diving knowledge
Return concise structured arguments and include reason.
""",
            tools=[
                self.route_trip_specialist,
                self.route_certification_specialist,
                self.route_general_retrieval_specialist,
                self.route_safety_specialist,
            ],
            generate_content_config=types.GenerateContentConfig(temperature=0.0),
        )
        self.runner = InMemoryRunner(agent=self.agent, app_name=self.app_name)

    def route_trip_specialist(
        self,
        query: str,
        reason: str = "",
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "target_agent": "trip_specialist",
            "parameters": {"query": query, "reason": reason, "location": location},
        }

    def route_certification_specialist(
        self,
        query: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        return {
            "target_agent": "certification_specialist",
            "parameters": {"query": query, "reason": reason},
        }

    def route_safety_specialist(
        self,
        query: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        return {
            "target_agent": "safety_specialist",
            "parameters": {"query": query, "reason": reason},
        }

    def route_general_retrieval_specialist(
        self,
        query: str,
        reason: str = "",
        topic: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "target_agent": "general_retrieval_specialist",
            "parameters": {"query": query, "reason": reason, "topic": topic},
        }

    async def _ensure_session(self, *, session_id: str, state: Optional[SessionState]) -> None:
        existing = await self.runner.session_service.get_session(
            app_name=self.app_name,
            user_id=self.user_id,
            session_id=session_id,
        )
        if existing:
            return

        await self.runner.session_service.create_session(
            app_name=self.app_name,
            user_id=self.user_id,
            session_id=session_id,
            state=state.to_dict() if state else {},
        )
        
    async def route_request(
        self, 
        message: str, 
        history: List[Dict[str, str]], 
        state: Optional[SessionState] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Route request to an agent via Google ADK tool calling.
        """
        try:
            prompt_context = ""
            if history:
                prompt_context = "Recent History:\n" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-3:]]) + "\n\n"

            full_prompt = prompt_context + f"User Request: {message}"

            resolved_session_id = session_id or f"legacy-{uuid4()}"
            await self._ensure_session(session_id=resolved_session_id, state=state)

            estimated_tokens = estimate_tokens_from_text(full_prompt) + 128
            await self.quota_manager.reserve(
                "text_generation",
                estimated_tokens,
                wait_for_capacity=True,
            )

            user_message = types.Content(role="user", parts=[types.Part(text=full_prompt)])

            async for event in self.runner.run_async(
                user_id=self.user_id,
                session_id=resolved_session_id,
                new_message=user_message,
            ):
                function_calls = event.get_function_calls()
                if function_calls:
                    function_call = function_calls[0]
                    logger.info(
                        "📍 ADK router decision: %s (args: %s)",
                        function_call.name,
                        function_call.args,
                    )
                    target_map = {
                        "route_trip_specialist": "trip_specialist",
                        "route_certification_specialist": "certification_specialist",
                        "route_safety_specialist": "safety_specialist",
                        "route_general_retrieval_specialist": "general_retrieval_specialist",
                    }
                    return {
                        "target_agent": target_map.get(function_call.name, function_call.name),
                        "parameters": dict(function_call.args) if function_call.args else {},
                    }

            logger.error("Google ADK router did not produce a function call")
            raise RuntimeError("Google ADK router did not produce a function call")

        except QuotaExceededError:
            raise
        except Exception as e:
            logger.error(f"ADK orchestration failed: {e}", exc_info=True)
            raise RuntimeError("Google ADK orchestration failed") from e
