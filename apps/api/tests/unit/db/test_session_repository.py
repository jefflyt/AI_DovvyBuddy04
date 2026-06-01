"""
Unit tests for SessionRepository.list_sessions.
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.infrastructure.db.repositories.session_repository import SessionRepository


class TestSessionRepositoryListSessions:
    """Test SessionRepository.list_sessions pagination."""

    @pytest.mark.asyncio
    async def test_list_sessions_returns_items_and_total(self):
        """list_sessions returns (items, total) ordered by created_at desc."""
        mock_items = [
            MagicMock(
                id=uuid4(),
                conversation_history=[
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there"},
                ],
                diver_profile=None,
                created_at=MagicMock(isoformat=MagicMock(return_value="2026-05-14T10:00:00")),
                updated_at=MagicMock(isoformat=MagicMock(return_value="2026-05-14T11:00:00")),
            ),
            MagicMock(
                id=uuid4(),
                conversation_history=[
                    {"role": "user", "content": "What about Tioman?"},
                ],
                diver_profile={"level": "AOW"},
                created_at=MagicMock(isoformat=MagicMock(return_value="2026-05-13T10:00:00")),
                updated_at=None,
            ),
        ]

        mock_session = AsyncMock()
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 42
        mock_items_result = MagicMock()
        mock_items_result.scalars.return_value.all.return_value = mock_items

        # First execute returns count, second returns items
        mock_session.execute = AsyncMock(
            side_effect=[mock_count_result, mock_items_result]
        )

        repo = SessionRepository(mock_session)
        items, total = await repo.list_sessions(offset=0, limit=20)

        assert total == 42
        assert len(items) == 2
        assert items[0].conversation_history[0]["content"] == "Hello"

    @pytest.mark.asyncio
    async def test_list_sessions_empty(self):
        """list_sessions returns empty list when no sessions exist."""
        mock_session = AsyncMock()
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 0
        mock_items_result = MagicMock()
        mock_items_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(
            side_effect=[mock_count_result, mock_items_result]
        )

        repo = SessionRepository(mock_session)
        items, total = await repo.list_sessions(offset=0, limit=20)

        assert total == 0
        assert items == []
