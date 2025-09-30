"""Repository pattern for Requirements Module."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.db.models import APISpecification, Requirement, TechnologyRecommendation


class RequirementRepository:
    """Repository for Requirement operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, requirement: Requirement) -> Requirement:
        """Create a new requirement."""
        self.session.add(requirement)
        await self.session.commit()
        await self.session.refresh(requirement)
        return requirement

    async def get_by_id(self, requirement_id: UUID) -> Optional[Requirement]:
        """Get requirement by ID."""
        result = await self.session.execute(
            select(Requirement)
            .where(Requirement.id == requirement_id)
            .options(selectinload(Requirement.api_specifications))
        )
        return result.scalar_one_or_none()

    async def get_by_project(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 100,
        type_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        priority_filter: Optional[str] = None,
        module_id: Optional[UUID] = None,
    ) -> list[Requirement]:
        """Get requirements by project with filters."""
        query = select(Requirement).where(Requirement.project_id == project_id)

        if type_filter:
            query = query.where(Requirement.type == type_filter)
        if status_filter:
            query = query.where(Requirement.status == status_filter)
        if priority_filter:
            query = query.where(Requirement.priority == priority_filter)
        if module_id:
            query = query.where(Requirement.module_id == module_id)

        query = query.offset(skip).limit(limit).order_by(Requirement.created_at.desc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_module(self, module_id: UUID) -> list[Requirement]:
        """Get requirements by module."""
        result = await self.session.execute(
            select(Requirement)
            .where(Requirement.module_id == module_id)
            .order_by(Requirement.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, requirement: Requirement) -> Requirement:
        """Update requirement."""
        await self.session.commit()
        await self.session.refresh(requirement)
        return requirement

    async def delete(self, requirement: Requirement) -> None:
        """Delete requirement."""
        await self.session.delete(requirement)
        await self.session.commit()

    async def approve(self, requirement: Requirement, approved_by: UUID) -> Requirement:
        """Approve requirement."""
        from datetime import datetime

        requirement.status = "approved"
        requirement.approved_by = approved_by
        requirement.approved_at = datetime.utcnow()
        return await self.update(requirement)

    async def count_by_project(self, project_id: UUID) -> int:
        """Count requirements by project."""
        result = await self.session.execute(
            select(Requirement).where(Requirement.project_id == project_id)
        )
        return len(list(result.scalars().all()))

    async def get_validated_count(self, project_id: UUID) -> int:
        """Count validated requirements."""
        result = await self.session.execute(
            select(Requirement).where(
                Requirement.project_id == project_id, Requirement.ai_validation_result.isnot(None)
            )
        )
        return len(list(result.scalars().all()))


class TechnologyRecommendationRepository:
    """Repository for TechnologyRecommendation operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, recommendation: TechnologyRecommendation) -> TechnologyRecommendation:
        """Create technology recommendation."""
        self.session.add(recommendation)
        await self.session.commit()
        await self.session.refresh(recommendation)
        return recommendation

    async def get_by_id(self, recommendation_id: UUID) -> Optional[TechnologyRecommendation]:
        """Get recommendation by ID."""
        result = await self.session.execute(
            select(TechnologyRecommendation).where(TechnologyRecommendation.id == recommendation_id)
        )
        return result.scalar_one_or_none()

    async def get_by_project(
        self,
        project_id: UUID,
        technology_type: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> list[TechnologyRecommendation]:
        """Get recommendations by project."""
        query = select(TechnologyRecommendation).where(TechnologyRecommendation.project_id == project_id)

        if technology_type:
            query = query.where(TechnologyRecommendation.technology_type == technology_type)
        if status_filter:
            query = query.where(TechnologyRecommendation.status == status_filter)

        query = query.order_by(TechnologyRecommendation.suitability_score.desc())

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_module(self, module_id: UUID) -> list[TechnologyRecommendation]:
        """Get recommendations by module."""
        result = await self.session.execute(
            select(TechnologyRecommendation)
            .where(TechnologyRecommendation.module_id == module_id)
            .order_by(TechnologyRecommendation.suitability_score.desc())
        )
        return list(result.scalars().all())

    async def update(self, recommendation: TechnologyRecommendation) -> TechnologyRecommendation:
        """Update recommendation."""
        await self.session.commit()
        await self.session.refresh(recommendation)
        return recommendation

    async def delete(self, recommendation: TechnologyRecommendation) -> None:
        """Delete recommendation."""
        await self.session.delete(recommendation)
        await self.session.commit()

    async def count_by_type(self, project_id: UUID) -> dict[str, int]:
        """Count recommendations by type."""
        result = await self.session.execute(
            select(TechnologyRecommendation).where(TechnologyRecommendation.project_id == project_id)
        )
        recommendations = list(result.scalars().all())

        counts: dict[str, int] = {}
        for rec in recommendations:
            counts[rec.technology_type] = counts.get(rec.technology_type, 0) + 1

        return counts


class APISpecificationRepository:
    """Repository for APISpecification operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, api_spec: APISpecification) -> APISpecification:
        """Create API specification."""
        self.session.add(api_spec)
        await self.session.commit()
        await self.session.refresh(api_spec)
        return api_spec

    async def get_by_id(self, api_spec_id: UUID) -> Optional[APISpecification]:
        """Get API spec by ID."""
        result = await self.session.execute(
            select(APISpecification).where(APISpecification.id == api_spec_id)
        )
        return result.scalar_one_or_none()

    async def get_by_requirement(self, requirement_id: UUID) -> list[APISpecification]:
        """Get API specs by requirement."""
        result = await self.session.execute(
            select(APISpecification)
            .where(APISpecification.requirement_id == requirement_id)
            .order_by(APISpecification.created_at.desc())
        )
        return list(result.scalars().all())

    async def update(self, api_spec: APISpecification) -> APISpecification:
        """Update API specification."""
        await self.session.commit()
        await self.session.refresh(api_spec)
        return api_spec

    async def delete(self, api_spec: APISpecification) -> None:
        """Delete API specification."""
        await self.session.delete(api_spec)
        await self.session.commit()

    async def count_by_requirement(self, requirement_id: UUID) -> int:
        """Count API specs for requirement."""
        result = await self.session.execute(
            select(APISpecification).where(APISpecification.requirement_id == requirement_id)
        )
        return len(list(result.scalars().all()))