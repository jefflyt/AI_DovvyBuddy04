from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.session import Session as SessionModel


class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, session_obj: dict) -> SessionModel:
        db_obj = SessionModel(**session_obj)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get(self, id_) -> Optional[SessionModel]:
        q = select(SessionModel).where(SessionModel.id == id_)
        res = await self.session.execute(q)
        return res.scalars().first()

    async def list_sessions(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> Tuple[List[SessionModel], int]:
        """List sessions ordered by creation date (newest first) with total count."""
        # Get total count
        count_q = select(func.count()).select_from(SessionModel)
        count_res = await self.session.execute(count_q)
        total = count_res.scalar() or 0

        # Get paginated sessions
        q = (
            select(SessionModel)
            .order_by(SessionModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        res = await self.session.execute(q)
        items = list(res.scalars().all())

        return items, total
