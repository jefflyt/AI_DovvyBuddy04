"""
Chat endpoint for conversation handling.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session as get_db_session
from app.orchestration import ChatOrchestrator
from app.orchestration.types import ChatRequest, ChatResponse

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatRequestPayload(BaseModel):
    """Request payload for chat endpoint."""

    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, alias="sessionId")
    diver_profile: Optional[dict] = Field(None, alias="diverProfile")

    class Config:
        populate_by_name = True


class ChatResponsePayload(BaseModel):
    """Response payload for chat endpoint."""

    message: str
    session_id: str = Field(..., alias="sessionId")
    agent_type: str = Field(..., alias="agentType")
    metadata: dict = {}

    class Config:
        populate_by_name = True


async def get_db():
    """Dependency to get database session."""
    session_maker = get_db_session()
    async with session_maker() as session:
        yield session


@router.post("/chat", response_model=ChatResponsePayload)
async def chat_endpoint(
    payload: ChatRequestPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle chat message and return response.

    Args:
        payload: Chat request with message and optional session_id
        db: Database session

    Returns:
        Chat response with message and session_id

    Raises:
        HTTPException: If request is invalid or processing fails
    """
    try:
        logger.info(f"🚀 CHAT ENDPOINT CALLED: message='{payload.message[:100]}...', session_id={payload.session_id}")
        
        # Create orchestrator
        orchestrator = ChatOrchestrator(db)

        # Build request
        request = ChatRequest(
            message=payload.message,
            session_id=payload.session_id,
            diver_profile=payload.diver_profile,
        )

        # Handle chat
        logger.info("📞 Calling orchestrator.handle_chat()")
        response = await orchestrator.handle_chat(request)
        logger.info(f"✅ Orchestrator returned response: {len(response.message)} chars")

        # Return response
        return ChatResponsePayload(
            message=response.message,
            session_id=response.session_id,
            agent_type=response.agent_type,
            metadata=response.metadata,
        )

    except ValueError as e:
        logger.warning(f"Invalid chat request: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Chat processing failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred processing your request. Please try again."
        )
