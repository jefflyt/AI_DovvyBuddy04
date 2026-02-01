"""
Trip agent for destination and dive site recommendations.
"""

import logging
from typing import Optional

from app.services.llm.base import LLMProvider
from app.services.llm.factory import create_llm_provider
from app.services.llm.types import LLMMessage

from .base import Agent, AgentResult
from .types import AgentCapability, AgentContext, AgentType

logger = logging.getLogger(__name__)


class TripAgent(Agent):
    """Agent for handling trip planning and destination queries."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """
        Initialize trip agent.

        Args:
            llm_provider: LLM provider (if None, creates default)
        """
        super().__init__(
            agent_type=AgentType.TRIP,
            name="Trip Agent",
            description="Provides destination recommendations and dive site information",
            capabilities=[AgentCapability.DESTINATION_RECOMMENDATION],
        )
        self.llm_provider = llm_provider or create_llm_provider()

    def get_tool_definition(self) -> dict:
        """Define trip planning tool for Gemini."""
        return {
            "name": "trip_planner",
            "description": "Plan a diving trip, recommend destinations, or find dive sites.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string", 
                        "description": "The user's trip-related request"
                    },
                    "location": {
                        "type": "string",
                        "description": "Specific location mentioned, or null"
                    }
                },
                "required": ["query"]
            }
        }

    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute trip agent.

        Args:
            context: Agent context with query

        Returns:
            AgentResult with destination recommendations
        """
        try:
            messages = self._build_messages(context)
            response = await self.llm_provider.generate(messages)

            result = AgentResult(
                response=response.content,
                agent_type=self.agent_type,
                confidence=0.9,
                metadata={
                    "model": response.model,
                    "tokens_used": response.tokens_used,
                },
            )

            self._log_execution(context, result)
            return result

        except Exception as e:
            return await self._handle_error(context, e)

    def _build_messages(self, context: AgentContext) -> list:
        """Build message list for LLM."""
        messages = []

        # System prompt with MAXIMUM STRICTNESS + EXAMPLES
        system_prompt = """You are DovvyBuddy's Trip Planning Expert.

🚨 CRITICAL RAG ENFORCEMENT 🚨

YOU MUST FOLLOW THESE RULES OR YOUR RESPONSE WILL BE REJECTED:

1. **ONLY USE THE "Destination Information" SECTION BELOW**
   - Every single fact, dive site name, depth, marine life mention MUST come from that text
   - If you cannot find specific information in that text, say "I don't have specific details about X in my knowledge base"

2. **LIST SPECIFIC DIVE SITES BY NAME**
   - DO: "• Tiger Reef: Dramatic pinnacle at 9-25m (intermediate to advanced)"
   - DON'T: "shallow coral gardens" or "deeper pinnacles"
   - You MUST list at least 3-5 specific site names if they exist in the text

3. **FORBIDDEN PHRASES** (These will cause instant failure):
   - "shallow coral gardens" (unless this exact phrase with a specific NAME appears in text)
   - "deeper pinnacles" (unless this exact phrase with a specific NAME appears in text)  
   - "drift dives" (unless a specific SITE is named as a drift dive in text)
   - Any generic category without a specific dive site name

4. **LEAD CAPTURE**
   - ALWAYS end with: "I can help you plan this! When are you thinking of going?"

EXAMPLE RESPONSES:

❌ WRONG (Generic, no specific names):
"Tioman offers shallow coral gardens perfect for beginners, deeper pinnacles for advanced divers, and drift dives for those seeking adventure."

✅ CORRECT (Specific sites with details from text):
"Tioman Island has fantastic dive sites for all levels:

• Renggis Island: Shallow coral garden perfect for training dives and beginners
• Tiger Reef: Dramatic pinnacle with strong currents and large pelagics (intermediate to advanced)
• Pulau Labas: Multiple sites with varied topography around a rocky island
• Pulau Chebeh: Submerged rocks with good macro life
• Batu Malang: Deep pinnacle with excellent visibility (advanced)

I can help you plan this! When are you thinking of going?"

VERIFICATION CHECKLIST (Check before responding):
□ Did I list specific dive site NAMES (not categories)?
□ Is every fact directly from the "Destination Information" below?
□ Did I avoid generic summaries?
□ Did I format with bullet points showing: Site Name: Description?

If you cannot find 3+ specific dive site names in the Destination Information, explicitly say:
"I have general information about [destination] but not a detailed list of specific dive sites in my current knowledge base."
"""

        # Add diver profile context if available
        if context.diver_profile:
            cert_level = context.diver_profile.get("certification_level", "unknown")
            experience = context.diver_profile.get("dive_count", "unknown")
            system_prompt += f"\n\nDIVER PROFILE: Certification: {cert_level}, Experience: {experience} dives"

        messages.append(LLMMessage(role="system", content=system_prompt))

        # Conversation history
        for msg in context.conversation_history[-10:]:
            messages.append(LLMMessage(role=msg["role"], content=msg["content"]))

        # Current query with RAG context
        query_text = context.query
        
        # CRITICAL: Log whether RAG context exists
        if context.rag_context:
            logger.info(f"✅ TripAgent: RAG context EXISTS (length: {len(context.rag_context)} chars)")
            logger.debug(f"RAG context preview: {context.rag_context[:200]}...")
            query_text = f"""Destination Information:
{context.rag_context}

Question: {context.query}"""
        else:
            logger.error(f"❌ TripAgent: NO RAG context provided! This will cause hallucination.")
            # Force NO_DATA response if no context
            query_text = f"NO_DATA\n\nQuestion: {context.query}"

        messages.append(LLMMessage(role="user", content=query_text))

        return messages
