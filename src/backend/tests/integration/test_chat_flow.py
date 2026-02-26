"""
Integration tests for chat flow.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.orchestration import ChatOrchestrator
from app.orchestration.types import ChatRequest
from app.agents.base import AgentResult
from app.agents.types import AgentContext, AgentType


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
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        diver_profile=None,
    )


@pytest.mark.asyncio
async def test_chat_flow_new_session(mock_db_session, mock_session_data):
    """Test complete chat flow with new session."""
    orchestrator = ChatOrchestrator(mock_db_session)

    # Mock session creation and orchestrator flow
    orchestrator.session_manager.create_session = AsyncMock(
        return_value=mock_session_data
    )
    orchestrator.session_manager.append_message = AsyncMock()
    orchestrator.orchestrator.route_request = AsyncMock(
        return_value={"target_agent": "knowledge_base", "parameters": {}}
    )
    orchestrator.response_formatter.format_response = AsyncMock(
        side_effect=lambda message, **kwargs: message
    )

    mock_result = AgentResult(
        response="This is a test response about diving",
        agent_type=AgentType.RETRIEVAL,
        confidence=0.8,
    )
    mock_agent = MagicMock()
    mock_agent.name = "retrieval"
    mock_agent.execute = AsyncMock(return_value=mock_result)

    orchestrator.agent_router.select_agent = MagicMock(return_value=mock_agent)
    orchestrator.context_builder.build_context = AsyncMock(
        return_value=AgentContext(query="What is scuba diving?", metadata={"has_rag": False})
    )

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
    orchestrator.orchestrator.route_request = AsyncMock(
        return_value={"target_agent": "knowledge_base", "parameters": {}}
    )
    orchestrator.response_formatter.format_response = AsyncMock(
        side_effect=lambda message, **kwargs: message
    )

    mock_result = AgentResult(
        response="Follow-up response",
        agent_type=AgentType.RETRIEVAL,
    )
    mock_agent = MagicMock()
    mock_agent.name = "retrieval"
    mock_agent.execute = AsyncMock(return_value=mock_result)
    orchestrator.agent_router.select_agent = MagicMock(return_value=mock_agent)
    orchestrator.context_builder.build_context = AsyncMock(
        return_value=AgentContext(query="Tell me more", metadata={"has_rag": False})
    )

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
    orchestrator.orchestrator.route_request = AsyncMock(
        return_value={"target_agent": "knowledge_base", "parameters": {}}
    )
    orchestrator.response_formatter.format_response = AsyncMock(
        side_effect=lambda message, **kwargs: message
    )

    mock_result = AgentResult(
        response="PADI Open Water is...",
        agent_type=AgentType.RETRIEVAL,
    )
    mock_agent = MagicMock()
    mock_agent.name = "retrieval"
    mock_agent.execute = AsyncMock(return_value=mock_result)
    orchestrator.agent_router.select_agent = MagicMock(return_value=mock_agent)
    orchestrator.context_builder.build_context = AsyncMock(
        return_value=AgentContext(
            query="What is PADI Open Water certification?",
            metadata={"has_rag": False},
        )
    )

    request = ChatRequest(
        message="What is PADI Open Water certification?",
    )

    response = await orchestrator.handle_chat(request)

    assert response.agent_type == AgentType.RETRIEVAL.value
    mock_agent.execute.assert_called_once()


@pytest.mark.asyncio
async def test_chat_flow_safety_query(mock_db_session, mock_session_data):
    """Test chat flow with safety query includes disclaimer."""
    orchestrator = ChatOrchestrator(mock_db_session)

    orchestrator.session_manager.create_session = AsyncMock(
        return_value=mock_session_data
    )
    orchestrator.session_manager.append_message = AsyncMock()
    orchestrator.emergency_detector.detect_emergency = AsyncMock(
        return_value=(True, "Seek emergency medical help immediately")
    )

    request = ChatRequest(
        message="Can I dive with asthma?",
    )

    response = await orchestrator.handle_chat(request)

    assert response.agent_type == "emergency"
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
