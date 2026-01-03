"""
Session manager for conversation persistence.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.repositories.session_repository import SessionRepository

from .types import SessionData

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages conversation sessions and history."""

    def __init__(self, db_session: AsyncSession):
        """
        Initialize session manager.

        Args:
            db_session: Database session
        """
        self.db_session = db_session
        self.repository = SessionRepository(db_session)

    async def create_session(
        self,
        diver_profile: Optional[dict] = None
    ) -> SessionData:
        """
        Create a new session.

        Args:
            diver_profile: Optional diver profile data

        Returns:
            SessionData with new session ID
        """
        session_id = uuid.uuid4()
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=settings.session_expiry_hours)

        session_obj = {
            "id": session_id,
            "conversation_history": [],
            "diver_profile": diver_profile,
            "created_at": now,
            "expires_at": expires_at,
        }

        db_session = await self.repository.create(session_obj)

        logger.info(f"Created new session: {session_id}")

        return SessionData(
            id=db_session.id,
            conversation_history=[],
            diver_profile=diver_profile,
            created_at=db_session.created_at,
            updated_at=db_session.updated_at,
        )

    async def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Get existing session by ID.

        Args:
            session_id: UUID string of session

        Returns:
            SessionData if found, None otherwise
        """
        try:
            session_uuid = UUID(session_id)
        except (ValueError, AttributeError):
            logger.warning(f"Invalid session ID format: {session_id}")
            return None

        db_session = await self.repository.get(session_uuid)

        if not db_session:
            logger.warning(f"Session not found: {session_id}")
            return None

        # Check if expired
        if hasattr(db_session, 'expires_at') and db_session.expires_at:
            if datetime.utcnow() > db_session.expires_at:
                logger.info(f"Session expired: {session_id}")
                return None

        return SessionData(
            id=db_session.id,
            conversation_history=db_session.conversation_history or [],
            diver_profile=db_session.diver_profile,
            created_at=db_session.created_at,
            updated_at=db_session.updated_at,
        )

    async def update_session(
        self,
        session_id: UUID,
        conversation_history: list,
        diver_profile: Optional[dict] = None
    ):
        """
        Update session with new conversation history.

        Args:
            session_id: Session UUID
            conversation_history: Updated conversation history
            diver_profile: Optional updated diver profile
        """
        db_session = await self.repository.get(session_id)

        if not db_session:
            logger.error(f"Cannot update non-existent session: {session_id}")
            return

        # Trim history if too long
        if len(conversation_history) > settings.max_conversation_history:
            conversation_history = conversation_history[-settings.max_conversation_history:]
            logger.info(f"Trimmed session history to {settings.max_conversation_history} messages")

        # Update fields
        db_session.conversation_history = conversation_history
        if diver_profile:
            db_session.diver_profile = diver_profile
        db_session.updated_at = datetime.utcnow()

        await self.db_session.commit()
        await self.db_session.refresh(db_session)

        logger.debug(f"Updated session: {session_id}")

    async def append_message(
        self,
        session_id: UUID,
        role: str,
        content: str
    ):
        """
        Append a message to session history.

        Args:
            session_id: Session UUID
            role: Message role (user/assistant)
            content: Message content
        """
        db_session = await self.repository.get(session_id)

        if not db_session:
            logger.error(f"Cannot append to non-existent session: {session_id}")
            return

        history = db_session.conversation_history or []
        history.append({"role": role, "content": content})

        # Trim if needed
        if len(history) > settings.max_conversation_history:
            history = history[-settings.max_conversation_history:]

        db_session.conversation_history = history
        db_session.updated_at = datetime.utcnow()

        await self.db_session.commit()

        logger.debug(f"Appended message to session {session_id}: {role}")
