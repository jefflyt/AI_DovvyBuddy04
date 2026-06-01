"""
Session endpoints for managing conversation sessions.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.orchestration import ChatOrchestrator
from app.infrastructure.db.repositories.session_repository import SessionRepository
from app.infrastructure.db.session import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


class SessionSummary(BaseModel):
    """Summary item for session listing."""

    id: str
    first_message_preview: Optional[str] = None
    message_count: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SessionListResponse(BaseModel):
    """Paginated session list response."""

    sessions: List[SessionSummary]
    total: int
    offset: int
    limit: int


class SessionResponse(BaseModel):
    """Response model for session data."""

    id: str
    conversation_history: List[Dict[str, str]]
    diver_profile: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """
    List sessions with pagination (newest first).

    Args:
        db: Database session
        offset: Number of sessions to skip
        limit: Maximum sessions to return (1-100)

    Returns:
        Paginated list of session summaries with total count
    """
    try:
        repository = SessionRepository(db)
        items, total = await repository.list_sessions(offset=offset, limit=limit)

        sessions = []
        for item in items:
            history = item.conversation_history or []
            first_user_msg = next(
                (m for m in history if m.get("role") == "user"), None
            )
            sessions.append(
                SessionSummary(
                    id=str(item.id),
                    first_message_preview=(
                        first_user_msg.get("content", "")[:200]
                        if first_user_msg
                        else None
                    ),
                    message_count=len(history),
                    created_at=item.created_at.isoformat() if item.created_at else None,
                    updated_at=item.updated_at.isoformat() if item.updated_at else None,
                )
            )

        return SessionListResponse(
            sessions=sessions,
            total=total,
            offset=offset,
            limit=limit,
        )

    except Exception as e:
        logger.error(f"Failed to list sessions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "An error occurred listing sessions",
                "code": "INTERNAL_ERROR",
            },
        ) from e


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
    db: AsyncSession = Depends(get_db),
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
        ) from e
