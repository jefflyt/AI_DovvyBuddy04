"""
Gemini Orchestrator using Native Function Calling (Google ADK Pattern).

Uses Gemini 2.5 Flash Lite to semantically route user queries to the appropriate agent
by defining agents as "tools" and letting the model decide which tool to call.
"""

import logging
import os
from typing import Dict, List, Optional, Any
import json

"""
Gemini Orchestrator using Native Function Calling (Google ADK Pattern).

Uses Gemini 2.5 Flash Lite to semantically route user queries to the appropriate agent
by defining agents as "tools" and letting the model decide which tool to call.
"""

import logging
import os
from typing import Dict, List, Optional, Any
import json

import google.genai as genai
from google.genai import types

from app.core.config import settings
from app.orchestration.types import IntentType, SessionState
from app.services.rag.token_utils import calculate_gemini_cost

logger = logging.getLogger(__name__)

class GeminiOrchestrator:
    """
    Orchestrates conversation flow using Gemini Function Calling.
    
    Acts as a router that translates user intent into specific agent calls.
    """

    ROUTING_SYSTEM_INSTRUCTION = """Route user queries to specialist agents.

RULES:
- Location/destination/sites/trip -> trip_planner
- Safety/certification/equipment/marine life -> knowledge_base

You MUST call a tool. Use exact query in args.
"""
    
    def __init__(self):
        """Initialize Gemini model with tool definitions."""
        self.api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("Gemini API key not found. Orchestrator will fail.")
            
        # Initialize the client (New SDK)
        self.client = genai.Client(api_key=self.api_key)
        
        # Tool Definitions (Schema for New SDK)
        self.tools = [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name="trip_planner",
                        description="Plan a diving trip, recommend destinations, or find dive sites. Use for 'Where can I go?', 'Best diving in Bali', 'sites suitable for beginners'.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                                "query": types.Schema(
                                    type="STRING",
                                    description="The user's trip-related request"
                                ),
                                "location": types.Schema(
                                    type="STRING",
                                    description="Specific location mentioned, or null"
                                )
                            },
                            required=["query"]
                        )
                    ),
                    types.FunctionDeclaration(
                        name="knowledge_base",
                        description="Retrieve information about diving certifications, safety, equipment, marine life, or general FAQs. Use for 'What is PADI?', 'Is it safe to fly?', 'What gear do I need?'.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                                "query": types.Schema(
                                    type="STRING",
                                    description="The user's question"
                                ),
                                "topic": types.Schema(
                                    type="STRING",
                                    description="The general topic (e.g., 'safety', 'equipment', 'certification')"
                                )
                            },
                            required=["query"]
                        )
                    )
                ]
            )
        ]

        self.model_name = "gemini-2.5-flash-lite"
        
    async def route_request(
        self, 
        message: str, 
        history: List[Dict[str, str]], 
        state: Optional[SessionState] = None
    ) -> Dict[str, Any]:
        """
        Route the request to the appropriate agent using Gemini Function Calling.
        """
        try:
            heuristic_route = self._quick_route_heuristic(message)
            if heuristic_route:
                logger.info(
                    "Routing heuristic: target_agent=%s, prompt_tokens=0, completion_tokens=0, total_tokens=0, cost_usd=0",
                    heuristic_route["target_agent"],
                )
                return heuristic_route

            # Construct chat history for context
            # New SDK format involves Content/Part objects, but text strings usually work for simple cases.
            # To be robust, we'll format conversation history into a single turn with context if needed, 
            # or just rely on the model seeing the current query given this is a router.
            # Routing is usually stateless or just needs immediate context.
            
            prompt_context = ""
            if history:
                prompt_context = "Recent History:\n" + "\n".join([f"{msg['role']}: {msg['content']}" for msg in history[-3:]]) + "\n\n"
            
            full_prompt = prompt_context + f"User Request: {message}"

            # Prepare Generation Config
            config = types.GenerateContentConfig(
                temperature=0.0, # Deterministic for routing
                tools=self.tools,
                tool_config=types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(
                        mode="ANY" # FORCE the model to call a function
                    )
                ),
                system_instruction=self.ROUTING_SYSTEM_INSTRUCTION,
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=config
            )

            usage_metadata = getattr(response, "usage_metadata", None)
            prompt_tokens = getattr(usage_metadata, "prompt_token_count", None)
            completion_tokens = getattr(usage_metadata, "candidates_token_count", None)
            total_tokens = getattr(usage_metadata, "total_token_count", None)
            cost_usd = calculate_gemini_cost(prompt_tokens, completion_tokens)

            if usage_metadata is None:
                logger.warning("Routing response missing usage_metadata")

            logger.info(
                "Routing LLM complete: model=%s, prompt_tokens=%s, completion_tokens=%s, total_tokens=%s, cost_usd=%s",
                self.model_name,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                cost_usd,
            )

            # Parse Response
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        fc = part.function_call
                        logger.info(f"📍 Router decision: {fc.name} (args: {fc.args})")
                        return {
                            "target_agent": fc.name,
                            "parameters": dict(fc.args) if fc.args else {}
                        }
            
            # Fallback
            logger.warning("Gemini Orchestrator provided no function call, defaulting to retrieval.")
            return {
                "target_agent": "knowledge_base",
                "parameters": {"query": message}
            }
            
        except Exception as e:
            logger.error(f"Orchestration failed: {e}", exc_info=True)
            return {
                "target_agent": "knowledge_base",
                "parameters": {"query": message}
            }

    def _quick_route_heuristic(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Lightweight heuristic routing for obvious cases.

        Returns:
            Dict with target_agent/parameters, or None if ambiguous.
        """
        if not message or not message.strip():
            return None

        normalized = message.lower()

        trip_keywords = [
            "where can i dive",
            "best sites",
            "dive sites",
            "destination",
            "plan trip",
            "plan a trip",
            "itinerary",
            "where to dive",
        ]

        info_keywords = [
            "certification",
            "padi",
            "ssi",
            "equipment",
            "gear",
            "safety",
            "nitrox",
            "buoyancy",
            "what is",
        ]

        if any(keyword in normalized for keyword in trip_keywords):
            return {
                "target_agent": "trip_planner",
                "parameters": {"query": message},
            }

        if any(keyword in normalized for keyword in info_keywords):
            return {
                "target_agent": "knowledge_base",
                "parameters": {"query": message},
            }

        return None
