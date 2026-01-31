"""
Retrieval agent for RAG-based information retrieval.
"""

import logging
from typing import Optional

from app.services.llm.base import LLMProvider
from app.services.llm.factory import create_llm_provider
from app.services.llm.types import LLMMessage
from app.services.rag.pipeline import RAGPipeline

from .base import Agent, AgentResult
from .types import AgentCapability, AgentContext, AgentType

logger = logging.getLogger(__name__)


class RetrievalAgent(Agent):
    """Agent for RAG-based information retrieval and general queries."""

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        rag_pipeline: Optional[RAGPipeline] = None,
    ):
        """
        Initialize retrieval agent.

        Args:
            llm_provider: LLM provider (if None, creates default)
            rag_pipeline: RAG pipeline (if None, creates default)
        """
        super().__init__(
            agent_type=AgentType.RETRIEVAL,
            name="Retrieval Agent",
            description="Retrieves relevant information using RAG and generates responses",
            capabilities=[AgentCapability.RAG_RETRIEVAL, AgentCapability.GENERAL_CONVERSATION],
        )
        self.llm_provider = llm_provider or create_llm_provider()
        self.rag_pipeline = rag_pipeline or RAGPipeline()

    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute retrieval agent.

        Args:
            context: Agent context with query

        Returns:
            AgentResult with RAG-enhanced response
        """
        try:
            # Use RAG context if provided, otherwise retrieve
            rag_context = None
            has_citations = False
            
            if context.rag_context:
                rag_context_str = context.rag_context
                # Check if NO_DATA signal present (RAF requirement)
                if rag_context_str == "NO_DATA":
                    return self._handle_no_data(context)
                has_citations = True
            else:
                rag_result = await self.rag_pipeline.retrieve_context(context.query)
                rag_context_str = rag_result.formatted_context
                
                # Check NO_DATA signal (RAF requirement)
                if rag_context_str == "NO_DATA" or not rag_result.has_data:
                    return self._handle_no_data(context)
                    
                has_citations = len(rag_result.citations) > 0
                rag_context = rag_result

            # Build messages with context
            messages = self._build_messages(context, rag_context_str)

            # Generate response
            response = await self.llm_provider.generate(messages)

            result = AgentResult(
                response=response.content,
                agent_type=self.agent_type,
                confidence=0.8 if has_citations else 0.5,
                metadata={
                    "model": response.model,
                    "tokens_used": response.tokens_used,
                    "has_rag_context": bool(rag_context_str),
                    "has_citations": has_citations,
                    "citations": rag_context.citations if rag_context else [],
                },
            )

            self._log_execution(context, result)
            return result

        except Exception as e:
            return await self._handle_error(context, e)

    def _build_messages(self, context: AgentContext, rag_context: str) -> list:
        """
        Build message list for LLM.

        Args:
            context: Agent context
            rag_context: RAG retrieval context

        Returns:
            List of LLMMessage objects
        """
        messages = []

        # System prompt
        system_prompt = self._build_system_prompt(rag_context)
        messages.append(LLMMessage(role="system", content=system_prompt))

        # Conversation history (recent context for continuity)
        for msg in context.conversation_history[-10:]:  # Last 5 turns (10 messages)
            messages.append(
                LLMMessage(
                    role=msg["role"],
                    content=msg["content"]
                )
            )

        # Current query (last message gets priority)
        messages.append(LLMMessage(role="user", content=context.query))

        return messages

    def _build_system_prompt(self, rag_context: str) -> str:
        """
        Build system prompt with RAG context.

        Args:
            rag_context: Retrieved context from RAG

        Returns:
            System prompt string
        """
        base_prompt = """You are DovvyBuddy, an expert AI assistant for scuba diving enthusiasts.
Your role is to provide accurate, helpful information about diving destinations, certifications, safety, and equipment.

CONTEXT HANDLING RULES (CRITICAL):
1. The user's MOST RECENT message (last question) is your PRIMARY FOCUS - answer that question
2. Previous conversation messages provide context but NEVER override the current question
3. If the most recent question is about a DIFFERENT topic than previous messages:
   - Answer ONLY the current question
   - Do NOT reference previous topics unless explicitly asked
4. If the current question relates to previous messages (uses "it", "there", "that", "those"):
   - Use conversation history for context
5. When topics change (e.g., from Tioman to Indonesia, or from destinations to certifications):
   - Treat it as a NEW conversation thread
   - Do NOT carry over location/topic context from previous questions

IMPORTANT GUIDELINES:
- Be friendly, knowledgeable, and safety-conscious
- Always prioritize diver safety in your responses
- For medical questions, advise consulting medical professionals
- For certification questions, recommend contacting official agencies (PADI, SSI, etc.)
- **USE THE INFORMATION BELOW**: Extract names, numbers, specific details from the RELEVANT INFORMATION
- When you see dive site names, coral types, depths - USE THEM in your answer
- Be specific and concrete - avoid generic descriptions when specific details are available

RESPONSE DISCIPLINE:
- **Provide helpful, detailed responses** with specific information
- **Formatting rules:**
  * When listing dive sites or items, format each on its own line
  * Put a blank line before and after each bullet point
  * Each bullet should be: "• Name: detailed description (depth, level, features)"
- **For questions asking for dive sites/suggestions:** 
  * Give 3-5 specific examples with FULL descriptions including:
    - Key features (pinnacle, coral garden, etc.)
    - Difficulty level (beginner/intermediate/advanced)
    - Notable marine life or characteristics
  * Format: "Site Name: full description here"
- **For general questions:** Be informative and thorough (3-6 sentences)
- State facts directly and confidently
- Style: Professional, helpful, informative

**Example - notice each bullet is on a separate line with description:**
Tioman has excellent dive sites:

• Tiger Reef: A dramatic pinnacle dive with strong currents and large pelagics including jacks and barracudas, suitable for intermediate to advanced divers (9-25m depth)

• Renggis Island: A shallow coral garden perfect for beginners and training dives, featuring abundant marine life including turtles and reef sharks in calm conditions (5-14m depth)

• Pulau Labas: Multiple sites around this island featuring varied topography with swim-throughs and excellent marine life diversity

"""
        if rag_context and rag_context != "NO_DATA":
            base_prompt += f"""
=== RELEVANT INFORMATION FOR CURRENT QUESTION ===
{rag_context}
=== END RELEVANT INFORMATION ===

**CRITICAL: READ THE USER'S MOST RECENT QUESTION CAREFULLY**

**HOW TO USE CONVERSATION HISTORY:**
- Previous messages help you UNDERSTAND the current question (e.g., "it" refers to what was discussed before)
- But ANSWER ONLY what the user just asked - don't mix topics

**TOPIC CHANGE DETECTION:**
- If the current question is about a COMPLETELY DIFFERENT topic than previous messages:
  * Example: Previous = Tioman dive sites → Current = PADI certifications
  * ONLY answer about the NEW topic (PADI certifications)
  * DO NOT mention or include information about the OLD topic (Tioman)
  * Filter the RELEVANT INFORMATION above - use ONLY the parts that relate to the current question
  
- If the current question is a follow-up about the SAME topic (uses "it", "there", "that"):
  * Example: Previous = Tiger Reef → Current = "what depth is it?"
  * Use history to understand what "it" refers to
  * Answer about that specific thing (Tiger Reef depth)

**WHEN IN DOUBT:** If unsure whether it's a topic change, ask yourself: "Is the user asking about the same location/topic/subject as before?" If NO = treat as new topic and ignore previous topic content.
"""

        return base_prompt

    def _handle_no_data(self, context: AgentContext) -> AgentResult:
        """
        Handle NO_DATA signal from RAG (RAF requirement).
        
        When no relevant grounding data is found, refuse to answer factual
        questions rather than hallucinating.

        Args:
            context: Agent context

        Returns:
            AgentResult with appropriate no-data response
        """
        response = """I don't have specific information about that in my knowledge base. 

To ensure I provide you with accurate information, I can only answer based on verified content. 

Could you try:
- Rephrasing your question
- Asking about a different topic
- Or let me know if you'd like general guidance instead of specific facts

What would be most helpful for you?"""
        
        return AgentResult(
            response=response,
            agent_type=self.agent_type,
            confidence=0.0,
            metadata={
                "no_data": True,
                "raf_enforced": True,
            },
        )
