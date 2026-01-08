"""Lead service layer for capture and delivery orchestration."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.lead.email_template import (
    build_lead_email_html,
    build_lead_email_subject,
    build_lead_email_text,
)
from app.core.lead.types import DiverProfile, LeadPayload, LeadRecord
from app.db.models.lead import Lead
from app.db.repositories.lead_repository import LeadRepository
from app.db.repositories.session_repository import SessionRepository

logger = logging.getLogger(__name__)


async def capture_lead(
    db: AsyncSession,
    payload: LeadPayload,
    diver_profile: Optional[DiverProfile] = None,
) -> LeadRecord:
    """Capture a lead to the database.
    
    Args:
        db: Database session
        payload: Validated lead payload
        diver_profile: Optional diver profile from session context
        
    Returns:
        Created lead record
        
    Raises:
        Exception: If database operation fails
    """
    logger.info(f"Capturing {payload.type} lead")
    
    try:
        # Prepare lead data for database
        lead_data = {
            "type": payload.type.value,
            "request_details": payload.data.model_dump(exclude_none=False),
            "diver_profile": diver_profile.model_dump() if diver_profile else None,
        }
        
        # Create lead record
        lead_repo = LeadRepository(db)
        db_lead = await lead_repo.create(lead_data)
        
        # Convert to LeadRecord
        lead_record = LeadRecord(
            id=db_lead.id,
            type=db_lead.type,
            diver_profile=db_lead.diver_profile,
            request_details=db_lead.request_details,
            created_at=db_lead.created_at,
        )
        
        logger.info(f"Lead captured successfully: {lead_record.id}")
        return lead_record
        
    except Exception as e:
        logger.error(f"Failed to capture lead: {str(e)}", exc_info=True)
        raise


async def deliver_lead(lead: LeadRecord, resend_client, config) -> None:
    """Deliver a lead notification via email using Resend.
    
    Args:
        lead: Lead record to deliver
        resend_client: Resend API client instance
        config: Application settings with email configuration
        
    Raises:
        Exception: If email delivery fails (non-critical, logged but not raised)
    """
    logger.info(f"Delivering lead notification: {lead.id}")
    
    try:
        # Build email content
        subject = build_lead_email_subject(lead)
        html_body = build_lead_email_html(lead)
        text_body = build_lead_email_text(lead)
        
        # Get email configuration
        from_email = getattr(config, "lead_email_from", "leads@dovvybuddy.com")
        to_email = config.lead_email_to
        reply_to = lead.request_details.get("email")
        
        # Send email via Resend
        response = resend_client.emails.send({
            "from": from_email,
            "to": to_email,
            "reply_to": reply_to,
            "subject": subject,
            "html": html_body,
            "text": text_body,
        })
        
        logger.info(f"Lead notification delivered successfully: {lead.id}, email_id: {response.get('id')}")
        
    except Exception as e:
        # Log error but don't raise - lead is already persisted
        logger.error(
            f"Failed to deliver lead notification for {lead.id}: {str(e)}",
            exc_info=True,
        )


async def capture_and_deliver_lead(
    db: AsyncSession,
    payload: LeadPayload,
    session_id: Optional[UUID],
    resend_client,
    config,
) -> LeadRecord:
    """Orchestrate lead capture and delivery.
    
    This is the main entry point for lead processing. It:
    1. Fetches diver profile from session if session_id provided
    2. Captures lead to database
    3. Delivers lead notification via email (fire-and-forget)
    
    Args:
        db: Database session
        payload: Validated lead payload
        session_id: Optional session ID for context enrichment
        resend_client: Resend API client instance
        config: Application settings
        
    Returns:
        Created lead record
        
    Raises:
        Exception: If lead capture fails (delivery failures are logged but not raised)
    """
    logger.info(
        f"Processing {payload.type} lead"
        + (f" with session {session_id}" if session_id else "")
    )
    
    # Fetch diver profile from session if available
    diver_profile = None
    if session_id:
        try:
            session_repo = SessionRepository(db)
            session_obj = await session_repo.get(session_id)
            if session_obj and session_obj.diver_profile:
                diver_profile = DiverProfile(**session_obj.diver_profile)
                logger.info(f"Enriching lead with session context: {session_id}")
        except Exception as e:
            logger.warning(f"Failed to fetch session context: {str(e)}")
            # Continue without session context
    
    # Capture lead to database
    lead_record = await capture_lead(db, payload, diver_profile)
    
    # Deliver lead notification (fire-and-forget, errors logged)
    try:
        await deliver_lead(lead_record, resend_client, config)
    except Exception as e:
        # Already logged in deliver_lead, continue
        pass
    
    logger.info(f"Lead processing complete: {lead_record.id}")
    return lead_record
