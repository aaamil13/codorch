"""Repository pattern for Research Module."""

from typing import Optional
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload

from backend.db.models import ResearchFinding, ResearchMessage, ResearchSession


class ResearchSessionRepository:
    """Repository for ResearchSession model."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def create(self, session: ResearchSession) -> ResearchSession:
        """Create a new research session."""
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def get_by_id(self, session_id: UUID) -> Optional[ResearchSession]:
        """Get research session by ID."""
        result = await self.db.execute(
            select(ResearchSession)
            .options(
                joinedload(ResearchSession.messages),
                joinedload(ResearchSession.findings),
            )
            .filter(ResearchSession.id == session_id)
        )
        return result.scalars().first()

    async def get_by_project(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> list[ResearchSession]:
        """Get research sessions by project ID."""
        query = select(ResearchSession).filter(ResearchSession.project_id == project_id)

        if status:
            query = query.filter(ResearchSession.status == status)

        result = await self.db.execute(query.order_by(desc(ResearchSession.updated_at)).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_by_goal(self, goal_id: UUID) -> list[ResearchSession]:
        """Get research sessions by goal ID."""
        result = await self.db.execute(
            select(ResearchSession)
            .filter(ResearchSession.goal_id == goal_id)
            .order_by(desc(ResearchSession.created_at))
        )
        return list(result.scalars().all())

    async def get_by_opportunity(self, opportunity_id: UUID) -> list[ResearchSession]:
        """Get research sessions by opportunity ID."""
        result = await self.db.execute(
            select(ResearchSession)
            .filter(ResearchSession.opportunity_id == opportunity_id)
            .order_by(desc(ResearchSession.created_at))
        )
        return list(result.scalars().all())

    async def update(self, session: ResearchSession) -> ResearchSession:
        """Update research session."""
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def delete(self, session: ResearchSession) -> None:
        """Delete research session (cascade deletes messages and findings)."""
        await self.db.delete(session)
        await self.db.commit()

    async def count_by_project(self, project_id: UUID) -> int:
        """Count research sessions for a project."""
        result = await self.db.execute(
            select(func.count(ResearchSession.id)).filter(ResearchSession.project_id == project_id)
        )
        return result.scalar_one()

    async def get_active_sessions(self, user_id: UUID) -> list[ResearchSession]:
        """Get all active sessions for a user."""
        result = await self.db.execute(
            select(ResearchSession)
            .filter(
                ResearchSession.created_by == user_id,
                ResearchSession.status == "active",
            )
            .order_by(desc(ResearchSession.updated_at))
        )
        return list(result.scalars().all())


class ResearchMessageRepository:
    """Repository for ResearchMessage model."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def create(self, message: ResearchMessage) -> ResearchMessage:
        """Create a new research message."""
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_by_id(self, message_id: UUID) -> Optional[ResearchMessage]:
        """Get research message by ID."""
        result = await self.db.execute(select(ResearchMessage).filter(ResearchMessage.id == message_id))
        return result.scalars().first()

    async def get_by_session(
        self,
        session_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ResearchMessage]:
        """Get messages for a research session."""
        result = await self.db.execute(
            select(ResearchMessage)
            .filter(ResearchMessage.session_id == session_id)
            .order_by(ResearchMessage.created_at)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_by_session(self, session_id: UUID) -> int:
        """Count messages in a session."""
        result = await self.db.execute(
            select(func.count(ResearchMessage.id)).filter(ResearchMessage.session_id == session_id)
        )
        return result.scalar_one()

    async def get_latest_messages(self, session_id: UUID, limit: int = 10) -> list[ResearchMessage]:
        """Get latest N messages from a session."""
        result = await self.db.execute(
            select(ResearchMessage)
            .filter(ResearchMessage.session_id == session_id)
            .order_by(desc(ResearchMessage.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())


class ResearchFindingRepository:
    """Repository for ResearchFinding model."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def create(self, finding: ResearchFinding) -> ResearchFinding:
        """Create a new research finding."""
        self.db.add(finding)
        await self.db.commit()
        await self.db.refresh(finding)
        return finding

    async def get_by_id(self, finding_id: UUID) -> Optional[ResearchFinding]:
        """Get research finding by ID."""
        result = await self.db.execute(select(ResearchFinding).filter(ResearchFinding.id == finding_id))
        return result.scalars().first()

    async def get_by_session(
        self,
        session_id: UUID,
        finding_type: Optional[str] = None,
    ) -> list[ResearchFinding]:
        """Get findings for a research session."""
        query = select(ResearchFinding).filter(ResearchFinding.session_id == session_id)

        if finding_type:
            query = query.filter(ResearchFinding.finding_type == finding_type)

        result = await self.db.execute(query.order_by(desc(ResearchFinding.created_at)))
        return list(result.scalars().all())

    async def get_by_project(
        self,
        project_id: UUID,
        finding_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[ResearchFinding]:
        """Get findings for all sessions in a project."""
        query = select(ResearchFinding).join(ResearchSession).filter(ResearchSession.project_id == project_id)

        if finding_type:
            query = query.filter(ResearchFinding.finding_type == finding_type)

        result = await self.db.execute(query.order_by(desc(ResearchFinding.created_at)).limit(limit))
        return list(result.scalars().all())

    async def update(self, finding: ResearchFinding) -> ResearchFinding:
        """Update research finding."""
        await self.db.commit()
        await self.db.refresh(finding)
        return finding

    async def delete(self, finding: ResearchFinding) -> None:
        """Delete research finding."""
        await self.db.delete(finding)
        await self.db.commit()

    async def count_by_session(self, session_id: UUID) -> int:
        """Count findings in a session."""
        result = await self.db.execute(
            select(func.count(ResearchFinding.id)).filter(ResearchFinding.session_id == session_id)
        )
        return result.scalar_one()

    async def count_by_type(self, session_id: UUID) -> dict[str, int]:
        """Count findings by type in a session."""
        result = await self.db.execute(
            select(
                ResearchFinding.finding_type,
                func.count(ResearchFinding.id),
            )
            .filter(ResearchFinding.session_id == session_id)
            .group_by(ResearchFinding.finding_type)
        )
        return {finding_type: count for finding_type, count in result.all()}

    async def get_high_confidence_findings(
        self,
        session_id: UUID,
        min_confidence: float = 0.7,
        limit: int = 10,
    ) -> list[ResearchFinding]:
        """Get high-confidence findings."""
        result = await self.db.execute(
            select(ResearchFinding)
            .filter(
                ResearchFinding.session_id == session_id,
                ResearchFinding.confidence_score >= min_confidence,
            )
            .order_by(desc(ResearchFinding.confidence_score))
            .limit(limit)
        )
        return list(result.scalars().all())
