"""Agent routing logic for conversation handling."""

import logging
from typing import Optional

from app.agents.registry import get_agent_registry
from app.agents.types import AgentType
from app.core.config import settings

from .mode_detector import ConversationMode

logger = logging.getLogger(__name__)


class AgentRouter:
    """
    Routes conversation modes to appropriate agents.
    
    Responsibilities:
    - Map conversation modes to agent types
    - Handle agent selection with fallbacks
    - Manage agent registry access
    """

    # Mode to agent type mapping
    MODE_TO_AGENT = {
        ConversationMode.CERTIFICATION: AgentType.CERTIFICATION,
        ConversationMode.TRIP: AgentType.TRIP,
        ConversationMode.SAFETY: AgentType.SAFETY,
        ConversationMode.GENERAL: AgentType.RETRIEVAL,
    }

    def __init__(self):
        """Initialize agent router with agent registry."""
        self.agent_registry = get_agent_registry()

    def select_agent(self, mode: ConversationMode) -> Optional[object]:
        """
        Select agent based on conversation mode.

        Args:
            mode: Detected conversation mode

        Returns:
            Agent instance or None

        Raises:
            ValueError: If no fallback agent available
        """
        if not settings.enable_agent_routing:
            # Fallback to retrieval agent
            return self._get_fallback_agent()

        # Map mode to agent type
        agent_type = self.MODE_TO_AGENT.get(mode, AgentType.RETRIEVAL)
        agent = self.agent_registry.get(agent_type)

        # Fallback to retrieval if agent not found
        if not agent:
            logger.warning(f"Agent not found for {agent_type}, using retrieval")
            agent = self._get_fallback_agent()

        return agent

    def _get_fallback_agent(self) -> Optional[object]:
        """
        Get fallback agent (retrieval agent).

        Returns:
            Retrieval agent instance or None
        """
        return self.agent_registry.get(AgentType.RETRIEVAL)
