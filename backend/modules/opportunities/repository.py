"""Opportunity repository for database operations."""

from typing import Optional
from uuid import UUID

from sqlalchemy import and_, desc
from sqlalchemy.orm import Session

from backend.db.models import Opportunity


class OpportunityRepository:
    """Repository pattern for Opportunity entity."""

    def __init__(self, db: Session) -> None:
        """Initialize repository with database session."""
        self.db = db

    def create(self, opportunity: Opportunity) -> Opportunity:
        """Create new opportunity."""
        self.db.add(opportunity)
        self.db.commit()
        self.db.refresh(opportunity)
        return opportunity

    def get_by_id(self, opportunity_id: UUID) -> Optional[Opportunity]:
        """Get opportunity by ID."""
        return self.db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()

    def get_by_project(self, project_id: UUID, skip: int = 0, limit: int = 100) -> list[Opportunity]:
        """Get all opportunities for a project."""
        return (
            self.db.query(Opportunity)
            .filter(Opportunity.project_id == project_id)
            .order_by(desc(Opportunity.score))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_goal(self, goal_id: UUID) -> list[Opportunity]:
        """Get opportunities related to a goal."""
        return self.db.query(Opportunity).filter(Opportunity.goal_id == goal_id).order_by(desc(Opportunity.score)).all()

    def get_by_status(self, project_id: UUID, status: str) -> list[Opportunity]:
        """Get opportunities by status."""
        return (
            self.db.query(Opportunity)
            .filter(and_(Opportunity.project_id == project_id, Opportunity.status == status))
            .order_by(desc(Opportunity.score))
            .all()
        )

    def get_ai_generated(self, project_id: UUID) -> list[Opportunity]:
        """Get AI-generated opportunities."""
        return (
            self.db.query(Opportunity)
            .filter(and_(Opportunity.project_id == project_id, Opportunity.ai_generated == True))  # noqa: E712
            .order_by(desc(Opportunity.score))
            .all()
        )

    def get_top_scored(self, project_id: UUID, limit: int = 10) -> list[Opportunity]:
        """Get top-scored opportunities."""
        return (
            self.db.query(Opportunity)
            .filter(Opportunity.project_id == project_id)
            .filter(Opportunity.score.isnot(None))
            .order_by(desc(Opportunity.score))
            .limit(limit)
            .all()
        )

    def update(self, opportunity: Opportunity) -> Opportunity:
        """Update opportunity."""
        self.db.commit()
        self.db.refresh(opportunity)
        return opportunity

    def delete(self, opportunity: Opportunity) -> None:
        """Delete opportunity."""
        self.db.delete(opportunity)
        self.db.commit()

    def count_by_project(self, project_id: UUID) -> int:
        """Count opportunities in a project."""
        return self.db.query(Opportunity).filter(Opportunity.project_id == project_id).count()

    def get_multiple_by_ids(self, opportunity_ids: list[UUID]) -> list[Opportunity]:
        """Get multiple opportunities by IDs."""
        return self.db.query(Opportunity).filter(Opportunity.id.in_(opportunity_ids)).all()
