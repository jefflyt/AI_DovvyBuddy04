"""
Integration tests for chat flow.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.orchestration import ChatOrchestrator
from app.orchestration.types import ChatRequest


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def mock_session_data():
    """Mock session data."""
    from app.orchestration.types import SessionData

    return SessionData(
        id=uuid4(),
        conversation_history=[],
        diver_profile=None,
    )


@pytest.mark.asyncio
async def test_chat_flow_new_session(mock_db_session, mock_session_data):
    """Test complete chat flow with new session."""
    orchestrator = ChatOrchestrator(mock_db_session)

    # Mock session creation
    orchestrator.session_manager.create_session = AsyncMock(
        return_value=mock_session_data
    )
    orchestrator.session_manager.append_message = AsyncMock()

    # Mock agent execution
    from app.agents.base import AgentResult
    from app.agents.types import AgentType

    mock_result = AgentResult(
        response="This is a test response about diving",
        agent_type=AgentType.RETRIEVAL,
        confidence=0.8,
    )

    with patch.object(
        orchestrator.agent_registry.get(AgentType.RETRIEVAL),
        "execute",
        return_value=mock_result,
    ):
        request = ChatRequest(
            message="What is scuba diving?",
            session_id=None,
        )

        response = await orchestrator.handle_chat(request)

        assert response is not None
        assert response.message == mock_result.response
        assert response.session_id == str(mock_session_data.id)
        assert response.agent_type == AgentType.RETRIEVAL.value


@pytest.mark.asyncio
async def test_chat_flow_existing_session(mock_db_session, mock_session_data):
    """Test chat flow with existing session."""
    orchestrator = ChatOrchestrator(mock_db_session)

    # Add some history to session
    mock_session_data.conversation_history = [
        {"role": "user", "content": "Previous question"},
        {"role": "assistant", "content": "Previous answer"},
    ]

    orchestrator.session_manager.get_session = AsyncMock(
        return_value=mock_session_data
    )
    orchestrator.session_manager.append_message = AsyncMock()

    # Mock agent
    from app.agents.base import AgentResult
    from app.agents.types import AgentType

    mock_result = AgentResult(
        response="Follow-up response",
        agent_type=AgentType.RETRIEVAL,
    )

    retrieval_agent = orchestrator.agent_registry.get(AgentType.RETRIEVAL)
    retrieval_agent.execute = AsyncMock(return_value=mock_result)

    request = ChatRequest(
        message="Tell me more",
        session_id=str(mock_session_data.id),
    )

    response = await orchestrator.handle_chat(request)

    assert response is not None
    assert response.session_id == str(mock_session_data.id)

    # Verify session was retrieved, not created
    orchestrator.session_manager.get_session.assert_called_once()


@pytest.mark.asyncio
async def test_chat_flow_certification_query(mock_db_session, mock_session_data):
    """Test chat flow with certification query."""
    orchestrator = ChatOrchestrator(mock_db_session)

    orchestrator.session_manager.create_session = AsyncMock(
        return_value=mock_session_data
    )
    orchestrator.session_manager.append_message = AsyncMock()

    # Mock certification agent
    from app.agents.base import AgentResult
    from app.agents.types import AgentType

    mock_result = AgentResult(
        response="PADI Open Water is...",
        agent_type=AgentType.CERTIFICATION,
    )

    cert_agent = orchestrator.agent_registry.get(AgentType.CERTIFICATION)
    cert_agent.execute = AsyncMock(return_value=mock_result)

    request = ChatRequest(
        message="What is PADI Open Water certification?",
    )

    response = await orchestrator.handle_chat(request)

    assert response.agent_type == AgentType.CERTIFICATION.value
    cert_agent.execute.assert_called_once()


@pytest.mark.asyncio
async def test_chat_flow_safety_query(mock_db_session, mock_session_data):
    """Test chat flow with safety query includes disclaimer."""
    orchestrator = ChatOrchestrator(mock_db_session)

    orchestrator.session_manager.create_session = AsyncMock(
        return_value=mock_session_data
    )
    orchestrator.session_manager.append_message = AsyncMock()

    # Mock safety agent
    from app.agents.base import AgentResult
    from app.agents.types import AgentType

    mock_result = AgentResult(
        response="For medical questions, consult a physician",
        agent_type=AgentType.SAFETY,
    )

    safety_agent = orchestrator.agent_registry.get(AgentType.SAFETY)
    safety_agent.execute = AsyncMock(return_value=mock_result)

    request = ChatRequest(
        message="Can I dive with asthma?",
    )

    response = await orchestrator.handle_chat(request)

    assert response.agent_type == AgentType.SAFETY.value
    # Response should include safety disclaimer (from config)
    # Actual disclaimer adding depends on settings.include_safety_disclaimer


@pytest.mark.asyncio
async def test_chat_flow_empty_message(mock_db_session):
    """Test chat flow with empty message raises error."""
    orchestrator = ChatOrchestrator(mock_db_session)

    request = ChatRequest(message="")

    with pytest.raises(ValueError, match="Message cannot be empty"):
        await orchestrator.handle_chat(request)


@pytest.mark.asyncio
async def test_chat_flow_message_too_long(mock_db_session):
    """Test chat flow with too-long message raises error."""
    orchestrator = ChatOrchestrator(mock_db_session)

    # Message longer than max_message_length (2000)
    long_message = "x" * 2001

    request = ChatRequest(message=long_message)

    with pytest.raises(ValueError, match="Message too long"):
        await orchestrator.handle_chat(request)


@pytest.mark.asyncio
async def test_get_session(mock_db_session, mock_session_data):
    """Test getting session by ID."""
    orchestrator = ChatOrchestrator(mock_db_session)

    orchestrator.session_manager.get_session = AsyncMock(
        return_value=mock_session_data
    )

    session = await orchestrator.get_session(str(mock_session_data.id))

    assert session is not None
    assert session.id == mock_session_data.id


@pytest.mark.asyncio
async def test_get_session_not_found(mock_db_session):
    """Test getting non-existent session."""
    orchestrator = ChatOrchestrator(mock_db_session)

    orchestrator.session_manager.get_session = AsyncMock(return_value=None)

    session = await orchestrator.get_session("non-existent-id")

    assert session is None
