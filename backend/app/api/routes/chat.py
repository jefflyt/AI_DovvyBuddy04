"""
Chat endpoint for conversation handling.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rate_limit import limiter
from app.core.security import validate_message_safety

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
    session_state: Optional[dict] = Field(None, alias="sessionState")  # PR6.1

    class Config:
        populate_by_name = True


class ChatResponsePayload(BaseModel):
    """Response payload for chat endpoint."""

    message: str
    session_id: str = Field(..., alias="sessionId")
    agent_type: str = Field(..., alias="agentType")
    metadata: dict = {}
    follow_up_question: Optional[str] = Field(None, alias="followUpQuestion")  # PR6.2

    class Config:
        populate_by_name = True


async def get_db():
    """Dependency to get database session."""
    session_maker = get_db_session()
    async with session_maker() as session:
        yield session


@router.post("/chat", response_model=ChatResponsePayload)
@limiter.limit("20/minute")
async def chat_endpoint(
    request: Request,
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
        
        # Security validation: sanitize and detect injection attempts
        clean_message, security_error = validate_message_safety(payload.message)
        
        if security_error:
            logger.warning(f"Security validation failed for message: {payload.message[:100]}")
            raise HTTPException(status_code=400, detail=security_error)
        
        # Create orchestrator
        orchestrator = ChatOrchestrator(db)

        # Build request with sanitized message
        chat_request = ChatRequest(
            message=clean_message,
            session_id=payload.session_id,
            diver_profile=payload.diver_profile,
            session_state=payload.session_state,  # PR6.2
        )

        # Handle chat
        logger.info("📞 Calling orchestrator.handle_chat()")
        response = await orchestrator.handle_chat(chat_request)
        logger.info(f"✅ Orchestrator returned response: {len(response.message)} chars")

        # Return response
        return ChatResponsePayload(
            message=response.message,
            session_id=response.session_id,
            agent_type=response.agent_type,
            metadata=response.metadata,
            follow_up_question=response.follow_up_question,  # PR6.2
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


# Debug endpoint to test RAG directly in-server
@router.get("/debug/rag")
async def debug_rag_endpoint(q: str = "Where can I dive in Tioman?"):
    """Debug endpoint to test RAG pipeline in running server."""
    from app.core.config import settings
    from app.services.rag.pipeline import RAGPipeline
    
    pipeline = RAGPipeline()
    
    result = {
        "settings.enable_rag": settings.enable_rag,
        "settings.gemini_api_key_set": bool(settings.gemini_api_key),
        "pipeline.enabled": pipeline.enabled,
        "query": q,
    }
    
    try:
        context = await pipeline.retrieve_context(q)
        result["results_count"] = len(context.results)
        result["has_data"] = context.has_data
        if context.results:
            result["top_results"] = [
                {
                    "similarity": r.similarity,
                    "text_preview": r.text[:200]
                }
                for r in context.results[:3]
            ]
        else:
            result["top_results"] = []
            result["formatted_context"] = context.formatted_context
    except Exception as e:
        result["error"] = str(e)
        import traceback
        result["traceback"] = traceback.format_exc()
    
    return result
