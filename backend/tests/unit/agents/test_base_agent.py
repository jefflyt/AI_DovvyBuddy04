"""
Unit tests for base agent functionality.
"""

import pytest

from app.agents.base import Agent, AgentResult
from app.agents.types import AgentCapability, AgentContext, AgentType


class MockAgent(Agent):
    """Mock agent for testing."""

    def __init__(self):
        super().__init__(
            agent_type=AgentType.GENERAL,
            name="Mock Agent",
            description="Test agent",
            capabilities=[AgentCapability.GENERAL_CONVERSATION],
        )

    async def execute(self, context: AgentContext) -> AgentResult:
        return AgentResult(
            response=f"Mock response to: {context.query}",
            agent_type=self.agent_type,
            confidence=0.9,
        )


@pytest.mark.asyncio
async def test_agent_execute():
    """Test agent execution."""
    agent = MockAgent()
    context = AgentContext(query="test query")

    result = await agent.execute(context)

    assert result is not None
    assert result.agent_type == AgentType.GENERAL
    assert "test query" in result.response
    assert result.confidence == 0.9


def test_agent_metadata():
    """Test agent metadata retrieval."""
    agent = MockAgent()
    metadata = agent.get_metadata()

    assert metadata["type"] == "general"
    assert metadata["name"] == "Mock Agent"
    assert metadata["description"] == "Test agent"
    assert "general_conversation" in metadata["capabilities"]


def test_agent_can_handle():
    """Test default can_handle implementation."""
    agent = MockAgent()
    context = AgentContext(query="any query")

    assert agent.can_handle(context) is True


@pytest.mark.asyncio
async def test_agent_error_handling():
    """Test agent error handling."""

    class ErrorAgent(Agent):
        def __init__(self):
            super().__init__(
                agent_type=AgentType.GENERAL,
                name="Error Agent",
                description="Test error handling",
                capabilities=[],
            )

        async def execute(self, context: AgentContext) -> AgentResult:
            raise ValueError("Test error")

    agent = ErrorAgent()
    context = AgentContext(query="test")

    # Error handling should return a fallback result
    result = await agent._handle_error(context, ValueError("Test error"))

    assert result is not None
    assert result.confidence == 0.0
    assert "error" in result.metadata
    assert "apologize" in result.response.lower()


def test_agent_result_dataclass():
    """Test AgentResult dataclass."""
    result = AgentResult(
        response="test response",
        agent_type=AgentType.CERTIFICATION,
        confidence=0.85,
        metadata={"key": "value"},
    )

    assert result.response == "test response"
    assert result.agent_type == AgentType.CERTIFICATION
    assert result.confidence == 0.85
    assert result.metadata["key"] == "value"


def test_agent_result_default_metadata():
    """Test AgentResult with default metadata."""
    result = AgentResult(
        response="test",
        agent_type=AgentType.TRIP,
    )

    assert result.metadata == {}
    assert result.confidence == 1.0
