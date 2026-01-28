from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.lead import Lead


class LeadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, lead_data: dict) -> Lead:
        """Create a new lead record.
        
        Args:
            lead_data: Dictionary containing lead fields (type, diver_profile, request_details)
            
        Returns:
            Created Lead model instance
        """
        db_obj = Lead(**lead_data)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get(self, lead_id: UUID) -> Optional[Lead]:
        """Retrieve a lead by ID.
        
        Args:
            lead_id: UUID of the lead to retrieve
            
        Returns:
            Lead model instance if found, None otherwise
        """
        q = select(Lead).where(Lead.id == lead_id)
        res = await self.session.execute(q)
        return res.scalars().first()
