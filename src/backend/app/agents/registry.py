"""
Agent registry and factory for managing agent instances.
"""

import logging
from typing import Dict, Optional

from .base import Agent
from .certification import CertificationAgent
from .retrieval import RetrievalAgent
from .safety import SafetyAgent
from .trip import TripAgent
from .types import AgentType

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry for managing agent instances."""

    def __init__(self):
        """Initialize agent registry."""
        self._agents: Dict[AgentType, Agent] = {}
        self._initialized = False

    def initialize(self):
        """
        Initialize all agents.

        Creates instances of all agent types and registers them.
        """
        if self._initialized:
            logger.warning("AgentRegistry already initialized")
            return

        logger.info("Initializing agent registry...")

        # Create and register agents
        self.register(CertificationAgent())
        self.register(TripAgent())
        self.register(SafetyAgent())
        self.register(RetrievalAgent())

        self._initialized = True
        logger.info(f"Agent registry initialized with {len(self._agents)} agents")

    def register(self, agent: Agent):
        """
        Register an agent.

        Args:
            agent: Agent instance to register
        """
        self._agents[agent.agent_type] = agent
        logger.debug(f"Registered agent: {agent.name} ({agent.agent_type.value})")

    def get(self, agent_type: AgentType) -> Optional[Agent]:
        """
        Get agent by type.

        Args:
            agent_type: Type of agent to retrieve

        Returns:
            Agent instance or None if not found
        """
        if not self._initialized:
            self.initialize()

        return self._agents.get(agent_type)

    def get_all(self) -> Dict[AgentType, Agent]:
        """
        Get all registered agents.

        Returns:
            Dictionary of agent type to agent instance
        """
        if not self._initialized:
            self.initialize()

        return self._agents.copy()

    def get_by_name(self, name: str) -> Optional[Agent]:
        """
        Get agent by type name (string).

        Args:
            name: Agent type name (e.g., "certification", "trip")

        Returns:
            Agent instance or None if not found
        """
        if not self._initialized:
            self.initialize()

        try:
            agent_type = AgentType(name.lower())
            return self.get(agent_type)
        except ValueError:
            logger.warning(f"Unknown agent type: {name}")
            return None

    def list_agents(self) -> list:
        """
        List all registered agents with metadata.

        Returns:
            List of agent metadata dictionaries
        """
        if not self._initialized:
            self.initialize()

        return [agent.get_metadata() for agent in self._agents.values()]


# Global agent registry instance
_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """
    Get the global agent registry instance.

    Returns:
        AgentRegistry singleton
    """
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
        _registry.initialize()
    return _registry


def create_agent(agent_type: AgentType) -> Agent:
    """
    Factory function to create agent instances.

    Args:
        agent_type: Type of agent to create

    Returns:
        New agent instance

    Raises:
        ValueError: If agent type is unknown
    """
    if agent_type == AgentType.CERTIFICATION:
        return CertificationAgent()
    elif agent_type == AgentType.TRIP:
        return TripAgent()
    elif agent_type == AgentType.SAFETY:
        return SafetyAgent()
    elif agent_type == AgentType.RETRIEVAL:
        return RetrievalAgent()
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")
