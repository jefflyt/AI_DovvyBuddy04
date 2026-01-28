from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.session import Session as SessionModel


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
