"""
Chat endpoint for conversation handling.
"""

import json
import logging
from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from app.core.rate_limit import limiter
from app.core.security import validate_message_safety

from app.db.session import get_db
from app.orchestration import ChatOrchestrator
from app.orchestration.types import ChatRequest, ChatResponse

router = APIRouter()
logger = logging.getLogger(__name__)


def _sse_data(event_type: str, content: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
    payload: Dict[str, Any] = {"type": event_type, "content": content}
    if metadata:
        payload["metadata"] = metadata
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


class ChatRequestPayload(BaseModel):
    """Request payload for chat endpoint."""

    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, alias="sessionId")
    diver_profile: Optional[dict] = Field(None, alias="diverProfile")
    session_state: Optional[dict] = Field(None, alias="sessionState")  # PR6.1

    model_config = ConfigDict(populate_by_name=True)


class ChatResponsePayload(BaseModel):
    """Response payload for chat endpoint."""

    message: str
    session_id: str = Field(..., alias="sessionId")
    agent_type: str = Field(..., alias="agentType")
    metadata: dict = {}
    follow_up_question: Optional[str] = Field(None, alias="followUpQuestion")  # PR6.2

    model_config = ConfigDict(populate_by_name=True)


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


@router.post("/chat/stream")
@limiter.limit("20/minute")
async def chat_stream_endpoint(
    request: Request,
    payload: ChatRequestPayload,
    db: AsyncSession = Depends(get_db),
):
    """
    Stream chat response as SSE events.

    Event types:
    - route
    - safety
    - token
    - citation
    - final
    - error
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            clean_message, security_error = validate_message_safety(payload.message)
            if security_error:
                yield _sse_data("error", "security_validation_failed", {"detail": security_error})
                return

            orchestrator = ChatOrchestrator(db)
            chat_request = ChatRequest(
                message=clean_message,
                session_id=payload.session_id,
                diver_profile=payload.diver_profile,
                session_state=payload.session_state,
            )
            response = await orchestrator.handle_chat(chat_request)

            route_info = response.metadata.get("route_decision")
            if route_info:
                yield _sse_data("route", route_info)

            safety_info = response.metadata.get("safety_classification")
            if safety_info:
                yield _sse_data("safety", safety_info)

            for token in response.message.split():
                yield _sse_data("token", f"{token} ")

            for citation in response.metadata.get("citations", []):
                yield _sse_data("citation", citation)

            yield _sse_data(
                "final",
                response.message,
                {
                    "sessionId": response.session_id,
                    "agentType": response.agent_type,
                    "metadata": response.metadata,
                },
            )

        except Exception as exc:
            logger.error("Stream chat processing failed: %s", exc, exc_info=True)
            yield _sse_data("error", "stream_processing_failed", {"detail": str(exc)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
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
