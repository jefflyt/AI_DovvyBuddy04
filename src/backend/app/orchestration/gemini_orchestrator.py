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

logger = logging.getLogger(__name__)

class GeminiOrchestrator:
    """
    Orchestrates conversation flow using Gemini Function Calling.
    
    Acts as a router that translates user intent into specific agent calls.
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
                system_instruction="""You are the DovvyBuddy Orchestrator.
Your job is to route the user's request to the correct specialist agent.

ROUTING RULES:
- If the user mentions a LOCATION (e.g., "Bali", "Tioman", "Phuket") -> `trip_planner`.
- "Where can I dive..." / "Best sites in..." -> `trip_planner`.
- "Recommend a dive shop..." -> `trip_planner`.
- "Plan a trip..." -> `trip_planner`.
- EVERYTHING ELSE (Safety, Certifications, Marine Life, Equipment) -> `knowledge_base`.

CRITICAL:
- You MUST call a tool.
- "Where can I dive in Tioman?" -> Call `trip_planner(query="Where can I dive in Tioman?", location="Tioman")`
""",
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=config
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
