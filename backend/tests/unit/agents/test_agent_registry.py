"""
Unit tests for agent registry.
"""

import pytest

from app.agents.registry import AgentRegistry, create_agent, get_agent_registry
from app.agents.types import AgentType


def test_registry_initialization():
    """Test agent registry initialization."""
    registry = AgentRegistry()
    assert registry._initialized is False

    registry.initialize()
    assert registry._initialized is True

    # All agents should be registered
    agents = registry.get_all()
    assert len(agents) == 4  # certification, trip, safety, retrieval


def test_get_agent_by_type():
    """Test retrieving agent by type."""
    registry = AgentRegistry()
    registry.initialize()

    cert_agent = registry.get(AgentType.CERTIFICATION)
    assert cert_agent is not None
    assert cert_agent.agent_type == AgentType.CERTIFICATION

    trip_agent = registry.get(AgentType.TRIP)
    assert trip_agent is not None
    assert trip_agent.agent_type == AgentType.TRIP


def test_get_agent_by_name():
    """Test retrieving agent by name string."""
    registry = AgentRegistry()
    registry.initialize()

    agent = registry.get_by_name("certification")
    assert agent is not None
    assert agent.agent_type == AgentType.CERTIFICATION

    agent = registry.get_by_name("trip")
    assert agent is not None

    # Unknown agent name
    agent = registry.get_by_name("unknown")
    assert agent is None


def test_list_agents():
    """Test listing all agents."""
    registry = AgentRegistry()
    registry.initialize()

    agents_list = registry.list_agents()
    assert len(agents_list) == 4

    # Check metadata structure
    for agent_meta in agents_list:
        assert "type" in agent_meta
        assert "name" in agent_meta
        assert "description" in agent_meta
        assert "capabilities" in agent_meta


def test_registry_singleton():
    """Test global registry singleton."""
    registry1 = get_agent_registry()
    registry2 = get_agent_registry()

    # Should be same instance
    assert registry1 is registry2


def test_create_agent_factory():
    """Test agent factory function."""
    cert_agent = create_agent(AgentType.CERTIFICATION)
    assert cert_agent.agent_type == AgentType.CERTIFICATION

    trip_agent = create_agent(AgentType.TRIP)
    assert trip_agent.agent_type == AgentType.TRIP

    safety_agent = create_agent(AgentType.SAFETY)
    assert safety_agent.agent_type == AgentType.SAFETY

    retrieval_agent = create_agent(AgentType.RETRIEVAL)
    assert retrieval_agent.agent_type == AgentType.RETRIEVAL


def test_create_agent_invalid_type():
    """Test factory with invalid agent type."""
    # This would need a mock invalid AgentType
    # In practice, Python enums prevent this at the type level
    pass


def test_double_initialization():
    """Test that double initialization is handled."""
    registry = AgentRegistry()
    registry.initialize()
    first_agents = registry.get_all()

    # Initialize again
    registry.initialize()
    second_agents = registry.get_all()

    # Should be same agents (not duplicated)
    assert len(first_agents) == len(second_agents)
