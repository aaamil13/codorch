"""Goal repository for database operations."""

from typing import List, Optional, Sequence
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from backend.db.models import Goal
from backend.modules.goals.schemas import GoalCreate, GoalUpdate


class GoalRepository:
    """Repository pattern for Goal entity."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize repository with asynchronous database session."""
        self.db = db

    async def create(self, goal_data: GoalCreate, project_id: UUID) -> Goal:
        """Create new goal."""
        db_goal = Goal(**goal_data.model_dump(), project_id=project_id)
        self.db.add(db_goal)
        await self.db.commit()
        await self.db.refresh(db_goal)
        return db_goal

    async def get_by_id(self, goal_id: UUID) -> Optional[Goal]:
        """Get goal by ID."""
        result = await self.db.execute(select(Goal).filter(Goal.id == goal_id))
        return result.scalars().first()

    async def get_by_id_with_subgoals(self, goal_id: UUID) -> Optional[Goal]:
        """Get goal by ID with subgoals loaded."""
        result = await self.db.execute(select(Goal).options(joinedload(Goal.subgoals)).filter(Goal.id == goal_id))
        return result.scalars().first()

    async def get_by_project(self, project_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[Goal]:
        """Get all goals for a project."""
        result = await self.db.execute(select(Goal).filter(Goal.project_id == project_id).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_root_goals(self, project_id: UUID) -> Sequence[Goal]:
        """Get root goals (goals without parent) for a project."""
        result = await self.db.execute(
            select(Goal).filter(
                and_(
                    Goal.project_id == project_id,
                    Goal.parent_goal_id.is_(None),
                )
            )
        )
        return result.scalars().all()

    async def get_subgoals(self, parent_goal_id: UUID) -> Sequence[Goal]:
        """Get all subgoals of a parent goal."""
        result = await self.db.execute(select(Goal).filter(Goal.parent_goal_id == parent_goal_id))
        return result.scalars().all()

    async def update(self, goal_id: UUID, update_data: GoalUpdate) -> Optional[Goal]:
        """Update goal."""
        goal = await self.get_by_id(goal_id)
        if not goal:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(goal, key, value)

        await self.db.commit()
        await self.db.refresh(goal)
        return goal

    async def delete(self, goal_id: UUID) -> bool:
        """Delete goal."""
        goal = await self.get_by_id(goal_id)
        if not goal:
            return False
        await self.db.delete(goal)
        await self.db.commit()
        return True

    async def count_by_project(self, project_id: UUID) -> int:
        """Count goals in a project."""
        result = await self.db.execute(select(func.count()).filter(Goal.project_id == project_id))
        return result.scalar_one()

    async def get_by_status(self, project_id: UUID, status: str) -> Sequence[Goal]:
        """Get goals by status."""
        result = await self.db.execute(select(Goal).filter(and_(Goal.project_id == project_id, Goal.status == status)))
        return result.scalars().all()
