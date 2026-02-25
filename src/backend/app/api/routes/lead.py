import logging
from typing import Optional
from uuid import UUID

import resend
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.lead import capture_and_deliver_lead
from app.core.lead.types import LeadPayload
from app.db.session import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize Resend client
resend.api_key = settings.resend_api_key


class LeadResponse(BaseModel):
    """Response model for successful lead capture."""

    success: bool = True
    lead_id: UUID


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str
    code: str
    details: Optional[list] = None


@router.post(
    "/leads",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def create_lead(
    payload: LeadPayload,
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    """Create a new lead and deliver notification via email.
    
    This endpoint accepts training or trip lead inquiries, validates the data,
    persists to database, and sends email notification to configured recipient.
    
    Args:
        payload: Lead payload with type (training/trip) and associated data
        db: Database session (injected)
        
    Returns:
        LeadResponse with success status and lead ID
        
    Raises:
        HTTPException: 400 for validation errors, 500 for server errors
    """
    try:
        # Validate required email configuration
        if not settings.resend_api_key:
            logger.error("RESEND_API_KEY not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Email service not configured",
                    "code": "CONFIG_ERROR",
                },
            )
        
        if not settings.lead_email_to:
            logger.error("LEAD_EMAIL_TO not configured")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "Lead delivery email not configured",
                    "code": "CONFIG_ERROR",
                },
            )
        
        # Extract session_id if provided
        session_id = payload.session_id
        
        # Process lead (capture + deliver)
        lead_record = await capture_and_deliver_lead(
            db=db,
            payload=payload,
            session_id=session_id,
            resend_client=resend,
            config=settings,
        )
        
        logger.info(f"Lead created successfully: {lead_record.id}")
        
        return LeadResponse(lead_id=lead_record.id)
        
    except ValidationError as e:
        logger.warning(f"Lead validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Validation failed",
                "code": "VALIDATION_ERROR",
                "details": [
                    {"field": err["loc"][-1], "message": err["msg"]}
                    for err in e.errors()
                ],
            },
        )
        
    except Exception as e:
        logger.error(f"Failed to create lead: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to capture lead",
                "code": "DB_ERROR" if "database" in str(e).lower() else "UNKNOWN",
            },
        )
