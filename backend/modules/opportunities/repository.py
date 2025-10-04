"""Opportunity repository for database operations."""

from typing import List, Optional, Sequence
from uuid import UUID

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Opportunity


class OpportunityRepository:
    """Repository pattern for Opportunity entity."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository with asynchronous database session."""
        self.db = db

    async def create(self, opportunity: Opportunity) -> Opportunity:
        """Create new opportunity."""
        self.db.add(opportunity)
        await self.db.commit()
        await self.db.refresh(opportunity)
        return opportunity

    async def get_by_id(self, opportunity_id: UUID) -> Optional[Opportunity]:
        """Get opportunity by ID."""
        result = await self.db.execute(select(Opportunity).filter(Opportunity.id == opportunity_id))
        return result.scalars().first()

    async def get_by_project(self, project_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[Opportunity]:
        """Get all opportunities for a project."""
        result = await self.db.execute(
            select(Opportunity)
            .filter(Opportunity.project_id == project_id)
            .order_by(desc(Opportunity.score))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_goal(self, goal_id: UUID) -> Sequence[Opportunity]:
        """Get opportunities related to a goal."""
        result = await self.db.execute(
            select(Opportunity).filter(Opportunity.goal_id == goal_id).order_by(desc(Opportunity.score))
        )
        return result.scalars().all()

    async def get_by_status(self, project_id: UUID, status: str) -> Sequence[Opportunity]:
        """Get opportunities by status."""
        result = await self.db.execute(
            select(Opportunity)
            .filter(and_(Opportunity.project_id == project_id, Opportunity.status == status))
            .order_by(desc(Opportunity.score))
        )
        return result.scalars().all()

    async def get_ai_generated(self, project_id: UUID) -> Sequence[Opportunity]:
        """Get AI-generated opportunities."""
        result = await self.db.execute(
            select(Opportunity)
            .filter(and_(Opportunity.project_id == project_id, Opportunity.ai_generated == True))  # noqa: E712
            .order_by(desc(Opportunity.score))
        )
        return result.scalars().all()

    async def get_top_scored(self, project_id: UUID, limit: int = 10) -> Sequence[Opportunity]:
        """Get top-scored opportunities."""
        result = await self.db.execute(
            select(Opportunity)
            .filter(Opportunity.project_id == project_id)
            .filter(Opportunity.score.isnot(None))
            .order_by(desc(Opportunity.score))
            .limit(limit)
        )
        return result.scalars().all()

    async def update(self, opportunity: Opportunity) -> Opportunity:
        """Update opportunity."""
        await self.db.commit()
        await self.db.refresh(opportunity)
        return opportunity

    async def delete(self, opportunity: Opportunity) -> None:
        """Delete opportunity."""
        await self.db.delete(opportunity)
        await self.db.commit()

    async def count_by_project(self, project_id: UUID) -> int:
        """Count opportunities in a project."""
        result = await self.db.execute(select(func.count()).filter(Opportunity.project_id == project_id))
        return result.scalar_one()

    async def get_multiple_by_ids(self, opportunity_ids: List[UUID]) -> Sequence[Opportunity]:
        """Get multiple opportunities by IDs."""
        result = await self.db.execute(select(Opportunity).filter(Opportunity.id.in_(opportunity_ids)))
        return result.scalars().all()
