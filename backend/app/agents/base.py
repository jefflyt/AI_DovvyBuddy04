"""
Base agent interface and common functionality.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from .types import AgentCapability, AgentContext, AgentType

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Result from agent execution."""

    response: str
    agent_type: AgentType
    confidence: float = 1.0
    metadata: dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class Agent(ABC):
    """Abstract base class for all agents."""

    def __init__(
        self,
        agent_type: AgentType,
        name: str,
        description: str,
        capabilities: List[AgentCapability],
    ):
        """
        Initialize agent.

        Args:
            agent_type: Type of agent
            name: Human-readable agent name
            description: Description of agent's purpose
            capabilities: List of capabilities this agent provides
        """
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.logger = logging.getLogger(f"agent.{agent_type.value}")

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute agent logic to handle the query.

        Args:
            context: Agent context with query and conversation history

        Returns:
            AgentResult with response and metadata

        Raises:
            ValueError: If context is invalid
            Exception: If agent execution fails
        """
        pass

    def can_handle(self, context: AgentContext) -> bool:
        """
        Check if this agent can handle the given context.

        Default implementation always returns True.
        Subclasses can override for more sophisticated routing.

        Args:
            context: Agent context to evaluate

        Returns:
            True if agent can handle, False otherwise
        """
        return True

    def get_metadata(self) -> dict:
        """
        Get agent metadata.

        Returns:
            Dictionary with agent information
        """
        return {
            "type": self.agent_type.value,
            "name": self.name,
            "description": self.description,
            "capabilities": [c.value for c in self.capabilities],
        }

    def get_tool_definition(self) -> dict:
        """
        Get the tool definition for Gemini Function Calling.
        
        Using Google Generative AI SDK format.
        Subclasses should override this to provide specific parameter schemas.
        """
        return {
            "name": self.agent_type.value,
            "description": self.description,
            "parameters": {
                "type": "object", 
                "properties": {
                    "query": {"type": "string", "description": "User query"}
                },
                "required": ["query"]
            }
        }

    def _log_execution(self, context: AgentContext, result: AgentResult):
        """
        Log agent execution for debugging.

        Args:
            context: Agent context that was processed
            result: Result produced by agent
        """
        metadata = result.metadata or {}
        self.logger.info(
            "Agent executed: query='%s...', confidence=%.2f, response_length=%s, tokens_used=%s, prompt_tokens=%s, completion_tokens=%s, cost_usd=%s, rag_tokens=%s, history_messages=%s",
            context.query[:50],
            result.confidence,
            len(result.response),
            metadata.get("tokens_used"),
            metadata.get("prompt_tokens"),
            metadata.get("completion_tokens"),
            metadata.get("cost_usd"),
            context.metadata.get("rag_tokens"),
            len(context.conversation_history),
        )

    async def _handle_error(self, context: AgentContext, error: Exception) -> AgentResult:
        """
        Handle errors during agent execution.

        Args:
            context: Agent context being processed
            error: Exception that occurred

        Returns:
            Fallback AgentResult with error message
        """
        self.logger.error(
            f"Error in {self.name}: {str(error)}",
            exc_info=True
        )
        
        return AgentResult(
            response=(
                "I apologize, but I encountered an error processing your request. "
                "Please try rephrasing your question or ask something else."
            ),
            agent_type=self.agent_type,
            confidence=0.0,
            metadata={"error": str(error), "error_type": type(error).__name__},
        )
