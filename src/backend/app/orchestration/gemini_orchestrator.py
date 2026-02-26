"""
Google ADK orchestrator for semantic routing.

Uses Google ADK's LlmAgent + Runner pattern to route user queries to
the appropriate specialist tool.
"""

import logging
import os
from typing import Dict, List, Optional, Any

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

from app.core.config import settings
from app.orchestration.types import SessionState

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

        self.agent = LlmAgent(
            name="dovvy_router",
            model=Gemini(model=self.model_name),
            instruction="""You are the DovvyBuddy router.
Route requests by calling exactly one tool:
- Use trip_planner for location-based dive planning requests.
- Use knowledge_base for all certification, safety, equipment, marine life, and general queries.
Always call a tool and include the user's original request in query.
""",
            tools=[self.trip_planner, self.knowledge_base],
            generate_content_config=types.GenerateContentConfig(temperature=0.0),
        )
        self.runner = InMemoryRunner(agent=self.agent, app_name=self.app_name)

    def trip_planner(self, query: str, location: Optional[str] = None) -> Dict[str, Any]:
        return {"target_agent": "trip_planner", "parameters": {"query": query, "location": location}}

    def knowledge_base(self, query: str, topic: Optional[str] = None) -> Dict[str, Any]:
        return {"target_agent": "knowledge_base", "parameters": {"query": query, "topic": topic}}
        
    async def route_request(
        self, 
        message: str, 
        history: List[Dict[str, str]], 
        state: Optional[SessionState] = None
    ) -> Dict[str, Any]:
        """
        Route request to an agent via Google ADK tool calling.
        """
        try:
            prompt_context = ""
            if history:
                prompt_context = "Recent History:\n" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-3:]]) + "\n\n"

            full_prompt = prompt_context + f"User Request: {message}"

            session = await self.runner.session_service.create_session(
                app_name=self.app_name,
                user_id=self.user_id,
            )
            user_message = types.Content(role="user", parts=[types.Part(text=full_prompt)])

            async for event in self.runner.run_async(
                user_id=self.user_id,
                session_id=session.id,
                new_message=user_message,
            ):
                function_calls = event.get_function_calls()
                if function_calls:
                    function_call = function_calls[0]
                    logger.info(f"📍 ADK router decision: {function_call.name} (args: {function_call.args})")
                    return {
                        "target_agent": function_call.name,
                        "parameters": dict(function_call.args) if function_call.args else {},
                    }

            logger.error("Google ADK router did not produce a function call")
            raise RuntimeError("Google ADK router did not produce a function call")

        except Exception as e:
            logger.error(f"ADK orchestration failed: {e}", exc_info=True)
            raise RuntimeError("Google ADK orchestration failed") from e
