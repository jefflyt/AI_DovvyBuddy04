from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.lead import Lead


class LeadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, obj: dict) -> Lead:
        db_obj = Lead(**obj)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get(self, id_) -> Optional[Lead]:
        q = select(Lead).where(Lead.id == id_)
        res = await self.session.execute(q)
        return res.scalars().first()
