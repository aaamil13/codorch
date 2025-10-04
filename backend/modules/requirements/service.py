"""Service layer for Requirements Module."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import APISpecification, Requirement, TechnologyRecommendation
from backend.modules.requirements.repository import (
    APISpecificationRepository,
    RequirementRepository,
    TechnologyRecommendationRepository,
)
from backend.modules.requirements.schemas import (
    APISpecificationCreate,
    APISpecificationUpdate,
    BatchValidationResponse,
    RequirementCreate,
    RequirementsReport,
    RequirementsSummary,
    RequirementUpdate,
    RequirementValidationResult,
    TechnologyRecommendationCreate,
    TechnologyRecommendationSummary,
    TechnologyRecommendationUpdate,
    ValidationIssue,
)


class RequirementsService:
    """Service for requirements business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.req_repo = RequirementRepository(session)
        self.tech_repo = TechnologyRecommendationRepository(session)
        self.api_repo = APISpecificationRepository(session)

    # ========================================================================
    # Requirement CRUD
    # ========================================================================

    async def create_requirement(self, data: RequirementCreate, created_by: UUID) -> Requirement:
        """Create new requirement."""
        requirement = Requirement(
            project_id=data.project_id,
            module_id=data.module_id,
            type=data.type,
            category=data.category,
            title=data.title,
            description=data.description,
            priority=data.priority,
            acceptance_criteria=data.acceptance_criteria,
            technical_specs=data.technical_specs,
            dependencies=data.dependencies,
            ai_generated=False,
            status="draft",
            created_by=created_by,
        )
        return await self.req_repo.create(requirement)

    async def get_requirement(self, requirement_id: UUID) -> Optional[Requirement]:
        """Get requirement by ID."""
        return await self.req_repo.get_by_id(requirement_id)

    async def list_requirements(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 100,
        type_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        priority_filter: Optional[str] = None,
        module_id: Optional[UUID] = None,
    ) -> Sequence[Requirement]:
        """List requirements with filters."""
        return await self.req_repo.get_by_project(
            project_id, skip, limit, type_filter, status_filter, priority_filter, module_id
        )

    async def get_module_requirements(self, module_id: UUID) -> Sequence[Requirement]:
        """Get requirements for a module."""
        return await self.req_repo.get_by_module(module_id)

    async def update_requirement(self, requirement_id: UUID, data: RequirementUpdate) -> Optional[Requirement]:
        """Update requirement."""
        requirement = await self.req_repo.get_by_id(requirement_id)
        if not requirement:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(requirement, field, value)

        return await self.req_repo.update(requirement)

    async def delete_requirement(self, requirement_id: UUID) -> bool:
        """Delete requirement."""
        requirement = await self.req_repo.get_by_id(requirement_id)
        if not requirement:
            return False

        await self.req_repo.delete(requirement)
        return True

    async def approve_requirement(self, requirement_id: UUID, approved_by: UUID) -> Optional[Requirement]:
        """Approve requirement."""
        requirement = await self.req_repo.get_by_id(requirement_id)
        if not requirement:
            return None

        return await self.req_repo.approve(requirement, approved_by)

    # ========================================================================
    # Validation
    # ========================================================================

    async def validate_requirement(self, requirement_id: UUID) -> Optional[RequirementValidationResult]:
        """Validate single requirement (AI validation)."""
        requirement = await self.req_repo.get_by_id(requirement_id)
        if not requirement:
            return None

        # AI validation will be implemented by AI agents
        # For now, return basic validation
        validation_result = self._basic_validation(requirement)

        # Store validation result
        requirement.ai_validation_result = validation_result.model_dump()
        await self.req_repo.update(requirement)

        return validation_result

    async def validate_batch(
        self, project_id: UUID, requirement_ids: Optional[List[UUID]] = None
    ) -> BatchValidationResponse:
        """Validate multiple requirements."""
        if requirement_ids:
            requirements: List[Requirement] = [] # Keep as List internally for manipulation
            for req_id in requirement_ids:
                req = await self.req_repo.get_by_id(req_id)
                if req:
                    requirements.append(req)
        else:
            requirements_sequence = await self.req_repo.get_by_project(project_id)
            requirements = list(requirements_sequence) # Convert Sequence to List for consistency

        results = []
        total_issues = 0
        critical_issues = 0

        for requirement in requirements:
            validation = self._basic_validation(requirement)
            results.append(validation)
            total_issues += len(validation.issues)
            critical_issues += sum(1 for issue in validation.issues if issue.severity == "critical")

            # Store validation result
            requirement.ai_validation_result = validation.model_dump()
            await self.req_repo.update(requirement)

        overall_score = sum(r.overall_score for r in results) / len(results) if results else 0.0

        return BatchValidationResponse(
            project_id=project_id,
            total_validated=len(results),
            results=results,
            overall_quality_score=overall_score,
            issues_count=total_issues,
            critical_issues_count=critical_issues,
        )

    def _basic_validation(self, requirement: Requirement) -> RequirementValidationResult:
        """Basic validation logic."""
        issues = []

        # Completeness check
        completeness_score = 10.0
        if not requirement.description or len(requirement.description) < 50:
            completeness_score -= 3.0
            issues.append(
                ValidationIssue(
                    type="completeness",
                    severity="warning",
                    message="Description is too short",
                    suggestion="Provide more detailed description (at least 50 characters)",
                )
            )

        if not requirement.acceptance_criteria or len(requirement.acceptance_criteria) == 0:
            completeness_score -= 3.0
            issues.append(
                ValidationIssue(
                    type="completeness",
                    severity="warning",
                    message="No acceptance criteria defined",
                    suggestion="Add specific acceptance criteria for this requirement",
                )
            )

        # Clarity check
        clarity_score = 8.0
        if "TODO" in requirement.description or "TBD" in requirement.description:
            clarity_score -= 2.0
            issues.append(
                ValidationIssue(
                    type="clarity",
                    severity="info",
                    message="Contains placeholder text (TODO/TBD)",
                    suggestion="Replace placeholders with specific details",
                )
            )

        # Consistency check
        consistency_score = 9.0

        # Feasibility check
        feasibility_score = 8.0

        overall_score = (completeness_score + clarity_score + consistency_score + feasibility_score) / 4

        return RequirementValidationResult(
            requirement_id=requirement.id,
            overall_score=overall_score,
            completeness_score=completeness_score,
            clarity_score=clarity_score,
            consistency_score=consistency_score,
            feasibility_score=feasibility_score,
            issues=issues,
            suggestions=[],
            is_valid=overall_score >= 7.0,
        )

    # ========================================================================
    # Technology Recommendations
    # ========================================================================

    async def create_technology_recommendation(self, data: TechnologyRecommendationCreate) -> TechnologyRecommendation:
        """Create technology recommendation."""
        recommendation = TechnologyRecommendation(
            project_id=data.project_id,
            module_id=data.module_id,
            technology_type=data.technology_type,
            name=data.name,
            version=data.version,
            reasoning=data.reasoning,
            suitability_score=data.suitability_score,
            popularity_score=data.popularity_score,
            learning_curve_score=data.learning_curve_score,
            ai_generated=True,
            alternatives=data.alternatives,
            status="suggested",
        )
        return await self.tech_repo.create(recommendation)

    async def get_technology_recommendation(self, recommendation_id: UUID) -> Optional[TechnologyRecommendation]:
        """Get technology recommendation by ID."""
        return await self.tech_repo.get_by_id(recommendation_id)

    async def list_technology_recommendations(
        self,
        project_id: UUID,
        technology_type: Optional[str] = None,
        status_filter: Optional[str] = None,
    ) -> Sequence[TechnologyRecommendation]:
        """List technology recommendations."""
        return await self.tech_repo.get_by_project(project_id, technology_type, status_filter)

    async def update_technology_recommendation(
        self, recommendation_id: UUID, data: TechnologyRecommendationUpdate
    ) -> Optional[TechnologyRecommendation]:
        """Update technology recommendation."""
        recommendation = await self.tech_repo.get_by_id(recommendation_id)
        if not recommendation:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(recommendation, field, value)

        return await self.tech_repo.update(recommendation)

    async def delete_technology_recommendation(self, recommendation_id: UUID) -> bool:
        """Delete technology recommendation."""
        recommendation = await self.tech_repo.get_by_id(recommendation_id)
        if not recommendation:
            return False

        await self.tech_repo.delete(recommendation)
        return True

    async def get_technology_summary(self, project_id: UUID) -> TechnologyRecommendationSummary:
        """Get technology recommendations summary."""
        recommendations = await self.tech_repo.get_by_project(project_id)
        by_type = await self.tech_repo.count_by_type(project_id)

        # Convert SQLAlchemy models to Pydantic response models
        from backend.modules.requirements.schemas import TechnologyRecommendationResponse
        recommendation_responses = [TechnologyRecommendationResponse.model_validate(r) for r in recommendations]

        return TechnologyRecommendationSummary(
            recommendations=recommendation_responses,
            total_count=len(recommendations),
            by_type=by_type,
        )

    # ========================================================================
    # API Specifications
    # ========================================================================

    async def create_api_specification(self, data: APISpecificationCreate) -> APISpecification:
        """Create API specification."""
        api_spec = APISpecification(
            requirement_id=data.requirement_id,
            method=data.method,
            path=data.path,
            description=data.description,
            request_schema=data.request_schema,
            response_schema=data.response_schema,
            error_codes=data.error_codes,
            authentication_required=data.authentication_required,
            rate_limit=data.rate_limit,
            examples=data.examples,
        )
        return await self.api_repo.create(api_spec)

    async def get_api_specification(self, api_spec_id: UUID) -> Optional[APISpecification]:
        """Get API specification by ID."""
        return await self.api_repo.get_by_id(api_spec_id)

    async def list_api_specifications(self, requirement_id: UUID) -> Sequence[APISpecification]:
        """List API specifications for requirement."""
        return await self.api_repo.get_by_requirement(requirement_id)

    async def update_api_specification(
        self, api_spec_id: UUID, data: APISpecificationUpdate
    ) -> Optional[APISpecification]:
        """Update API specification."""
        api_spec = await self.api_repo.get_by_id(api_spec_id)
        if not api_spec:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(api_spec, field, value)

        return await self.api_repo.update(api_spec)

    async def delete_api_specification(self, api_spec_id: UUID) -> bool:
        """Delete API specification."""
        api_spec = await self.api_repo.get_by_id(api_spec_id)
        if not api_spec:
            return False

        await self.api_repo.delete(api_spec)
        return True

    # ========================================================================
    # Reports & Analytics
    # ========================================================================

    async def get_requirements_summary(self, project_id: UUID) -> RequirementsSummary:
        """Get requirements summary."""
        requirements = await self.req_repo.get_by_project(project_id)

        by_type: dict[str, int] = {}
        by_status: dict[str, int] = {}
        by_priority: dict[str, int] = {}

        for req in requirements:
            by_type[req.type] = by_type.get(req.type, 0) + 1
            by_status[req.status] = by_status.get(req.status, 0) + 1
            by_priority[req.priority] = by_priority.get(req.priority, 0) + 1

        validated_count = await self.req_repo.get_validated_count(project_id)
        total_count = len(requirements)
        validation_coverage = (validated_count / total_count * 100) if total_count > 0 else 0.0

        return RequirementsSummary(
            total_count=total_count,
            by_type=by_type,
            by_status=by_status,
            by_priority=by_priority,
            validation_coverage=validation_coverage,
        )

    async def get_requirements_report(self, project_id: UUID) -> RequirementsReport:
        """Generate full requirements report."""
        requirements = await self.req_repo.get_by_project(project_id)
        technologies = await self.tech_repo.get_by_project(project_id)
        summary = await self.get_requirements_summary(project_id)

        # Convert SQLAlchemy models to Pydantic response models
        from backend.modules.requirements.schemas import RequirementResponse, TechnologyRecommendationResponse
        requirement_responses = [RequirementResponse.model_validate(r) for r in requirements]
        technology_responses = [TechnologyRecommendationResponse.model_validate(t) for t in technologies]

        # Count API specifications
        api_specs_count = 0
        for req in requirements:
            api_specs = await self.api_repo.get_by_requirement(req.id)
            api_specs_count += len(api_specs)

        return RequirementsReport(
            project_id=project_id,
            summary=summary,
            requirements=requirement_responses,
            technology_recommendations=technology_responses,
            api_specifications_count=api_specs_count,
            generated_at=datetime.utcnow(),
        )
