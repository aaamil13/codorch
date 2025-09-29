"""Goal repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from backend.db.models import Goal


class GoalRepository:
    """Repository pattern for Goal entity."""

    def __init__(self, db: Session) -> None:
        """Initialize repository with database session."""
        self.db = db

    def create(self, goal: Goal) -> Goal:
        """Create new goal."""
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def get_by_id(self, goal_id: UUID) -> Optional[Goal]:
        """Get goal by ID."""
        return self.db.query(Goal).filter(Goal.id == goal_id).first()

    def get_by_id_with_subgoals(self, goal_id: UUID) -> Optional[Goal]:
        """Get goal by ID with subgoals loaded."""
        return (
            self.db.query(Goal)
            .options(joinedload(Goal.subgoals))
            .filter(Goal.id == goal_id)
            .first()
        )

    def get_by_project(
        self, project_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Goal]:
        """Get all goals for a project."""
        return (
            self.db.query(Goal)
            .filter(Goal.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_root_goals(self, project_id: UUID) -> list[Goal]:
        """Get root goals (goals without parent) for a project."""
        return (
            self.db.query(Goal)
            .filter(
                and_(
                    Goal.project_id == project_id,
                    Goal.parent_goal_id.is_(None),
                )
            )
            .all()
        )

    def get_subgoals(self, parent_goal_id: UUID) -> list[Goal]:
        """Get all subgoals of a parent goal."""
        return self.db.query(Goal).filter(Goal.parent_goal_id == parent_goal_id).all()

    def update(self, goal: Goal) -> Goal:
        """Update goal."""
        self.db.commit()
        self.db.refresh(goal)
        return goal

    def delete(self, goal: Goal) -> None:
        """Delete goal."""
        self.db.delete(goal)
        self.db.commit()

    def count_by_project(self, project_id: UUID) -> int:
        """Count goals in a project."""
        return self.db.query(Goal).filter(Goal.project_id == project_id).count()

    def get_by_status(self, project_id: UUID, status: str) -> list[Goal]:
        """Get goals by status."""
        return (
            self.db.query(Goal)
            .filter(and_(Goal.project_id == project_id, Goal.status == status))
            .all()
        )
