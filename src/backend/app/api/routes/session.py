"""
Session endpoints for managing conversation sessions.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.orchestration import ChatOrchestrator

router = APIRouter()
logger = logging.getLogger(__name__)


class SessionResponse(BaseModel):
    """Response model for session data."""

    id: str
    conversation_history: List[Dict[str, str]]
    diver_profile: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@router.get("/sessions")
async def list_sessions():
    """
    List sessions endpoint (placeholder).

    TODO: Implement session listing with pagination
    """
    return {"sessions": []}


@router.post("/sessions")
async def create_session(payload: dict):
    """
    Create session endpoint (placeholder).

    Note: Sessions are auto-created in chat endpoint.
    This endpoint is for explicit session creation if needed.
    """
    # Placeholder: would create session using SessionRepository
    return {"id": "placeholder", "data": payload}


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get session by ID.

    Args:
        session_id: Session UUID string
        db: Database session

    Returns:
        Session data with conversation history

    Raises:
        HTTPException: If session not found
    """
    try:
        orchestrator = ChatOrchestrator(db)
        session = await orchestrator.get_session(session_id)

        if not session:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Session not found: {session_id}",
                    "code": "SESSION_NOT_FOUND",
                },
            )

        # Format response
        return SessionResponse(
            id=str(session.id),
            conversation_history=session.conversation_history,
            diver_profile=session.diver_profile,
            created_at=session.created_at.isoformat() if session.created_at else None,
            updated_at=session.updated_at.isoformat() if session.updated_at else None,
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to retrieve session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "An error occurred retrieving the session",
                "code": "INTERNAL_ERROR",
            },
        )
