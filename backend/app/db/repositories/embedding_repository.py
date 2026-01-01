from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.content_embedding import ContentEmbedding


class EmbeddingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, obj: dict) -> ContentEmbedding:
        db_obj = ContentEmbedding(**obj)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def list_all(self, limit: int = 100) -> List[ContentEmbedding]:
        q = select(ContentEmbedding).limit(limit)
        res = await self.session.execute(q)
        return res.scalars().all()
