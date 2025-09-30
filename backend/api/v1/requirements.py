"""API endpoints for Requirements Module (Module 5)."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user, get_session
from backend.db.models import User
from backend.modules.requirements.schemas import (
    APISpecificationCreate,
    APISpecificationResponse,
    APISpecificationUpdate,
    BatchValidationRequest,
    BatchValidationResponse,
    RequirementCreate,
    RequirementResponse,
    RequirementsReport,
    RequirementsSummary,
    RequirementUpdate,
    RequirementValidationRequest,
    RequirementValidationResult,
    TechnologyRecommendationCreate,
    TechnologyRecommendationRequest,
    TechnologyRecommendationResponse,
    TechnologyRecommendationSummary,
    TechnologyRecommendationUpdate,
)
from backend.modules.requirements.service import RequirementsService
from backend.ai_agents.requirements_team import RequirementsTeam

router = APIRouter(prefix="/requirements", tags=["requirements"])


# ============================================================================
# Requirements CRUD
# ============================================================================


@router.post("", response_model=RequirementResponse, status_code=status.HTTP_201_CREATED)
async def create_requirement(
    data: RequirementCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Create new requirement."""
    service = RequirementsService(session)
    requirement = await service.create_requirement(data, current_user.id)
    return requirement


@router.get("/projects/{project_id}", response_model=list[RequirementResponse])
async def list_requirements(
    project_id: UUID,
    skip: int = 0,
    limit: int = 100,
    type_filter: Optional[str] = None,
    status_filter: Optional[str] = None,
    priority_filter: Optional[str] = None,
    module_id: Optional[UUID] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List requirements for a project."""
    service = RequirementsService(session)
    requirements = await service.list_requirements(
        project_id, skip, limit, type_filter, status_filter, priority_filter, module_id
    )
    return requirements


@router.get("/modules/{module_id}", response_model=list[RequirementResponse])
async def list_module_requirements(
    module_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get requirements for a specific module."""
    service = RequirementsService(session)
    requirements = await service.get_module_requirements(module_id)
    return requirements


@router.get("/{requirement_id}", response_model=RequirementResponse)
async def get_requirement(
    requirement_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get requirement by ID."""
    service = RequirementsService(session)
    requirement = await service.get_requirement(requirement_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return requirement


@router.put("/{requirement_id}", response_model=RequirementResponse)
async def update_requirement(
    requirement_id: UUID,
    data: RequirementUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Update requirement."""
    service = RequirementsService(session)
    requirement = await service.update_requirement(requirement_id, data)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return requirement


@router.delete("/{requirement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_requirement(
    requirement_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete requirement."""
    service = RequirementsService(session)
    success = await service.delete_requirement(requirement_id)
    if not success:
        raise HTTPException(status_code=404, detail="Requirement not found")


@router.post("/{requirement_id}/approve", response_model=RequirementResponse)
async def approve_requirement(
    requirement_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Approve requirement."""
    service = RequirementsService(session)
    requirement = await service.approve_requirement(requirement_id, current_user.id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return requirement


# ============================================================================
# AI Validation
# ============================================================================


@router.post("/{requirement_id}/validate", response_model=RequirementValidationResult)
async def validate_requirement(
    requirement_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Validate single requirement with AI."""
    service = RequirementsService(session)
    
    # Get requirement
    requirement = await service.get_requirement(requirement_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    # Run AI validation
    result = await RequirementsTeam.full_analysis_workflow(
        requirement.title,
        requirement.description,
        requirement.type,
        requirement.acceptance_criteria or [],
    )
    
    # Store validation result
    requirement.ai_validation_result = result
    await service.req_repo.update(requirement)
    
    # Convert to validation result
    analysis = result["analysis"]
    validation = result["validation"]
    
    return RequirementValidationResult(
        requirement_id=requirement_id,
        overall_score=result["overall_score"],
        completeness_score=analysis.completeness_score,
        clarity_score=analysis.clarity_score,
        consistency_score=analysis.consistency_score,
        feasibility_score=analysis.feasibility_score,
        issues=[
            {
                "type": issue.get("type", "general"),
                "severity": issue.get("severity", "info"),
                "message": issue.get("message", ""),
                "suggestion": issue.get("suggestion"),
            }
            for issue in analysis.issues
        ],
        suggestions=analysis.suggestions,
        is_valid=validation.is_valid,
    )


@router.post("/projects/{project_id}/validate-batch", response_model=BatchValidationResponse)
async def validate_batch(
    project_id: UUID,
    data: BatchValidationRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Validate multiple requirements."""
    service = RequirementsService(session)
    result = await service.validate_batch(project_id, data.requirement_ids)
    return result


@router.get("/{requirement_id}/suggestions", response_model=dict)
async def get_suggestions(
    requirement_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get AI suggestions for improving requirement."""
    service = RequirementsService(session)
    requirement = await service.get_requirement(requirement_id)
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    return {
        "requirement_id": requirement_id,
        "suggestions": requirement.ai_suggestions or [],
        "validation_result": requirement.ai_validation_result,
    }


# ============================================================================
# Technology Recommendations
# ============================================================================


@router.post(
    "/projects/{project_id}/technology-recommendations/generate",
    response_model=TechnologyRecommendationSummary,
)
async def generate_technology_recommendations(
    project_id: UUID,
    data: TechnologyRecommendationRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Generate technology recommendations using AI."""
    service = RequirementsService(session)
    
    # Get requirements
    if data.requirements:
        requirements = []
        for req_id in data.requirements:
            req = await service.get_requirement(req_id)
            if req:
                requirements.append({
                    "type": req.type,
                    "title": req.title,
                    "description": req.description,
                })
    else:
        all_reqs = await service.list_requirements(project_id)
        requirements = [
            {"type": r.type, "title": r.title, "description": r.description}
            for r in all_reqs[:20]  # Limit to 20
        ]
    
    # Get module name if module_id provided
    module_name = "General"
    if data.module_id:
        # Would get from architecture module
        module_name = f"Module {data.module_id}"
    
    # Generate recommendations
    tech_recs = await RequirementsTeam.technology_recommendation_workflow(
        requirements,
        module_name,
        data.preferences,
    )
    
    # Save recommendations to database
    saved_recs = []
    for rec in tech_recs.recommendations:
        tech_data = TechnologyRecommendationCreate(
            project_id=project_id,
            module_id=data.module_id,
            technology_type=rec.get("technology_type", "library"),
            name=rec.get("name", ""),
            version=rec.get("version"),
            reasoning=rec.get("reasoning", ""),
            suitability_score=rec.get("suitability_score", 5.0),
            popularity_score=rec.get("popularity_score"),
            learning_curve_score=rec.get("learning_curve_score"),
            alternatives=[],
        )
        saved_rec = await service.create_technology_recommendation(tech_data)
        saved_recs.append(saved_rec)
    
    by_type: dict[str, int] = {}
    for rec in saved_recs:
        by_type[rec.technology_type] = by_type.get(rec.technology_type, 0) + 1
    
    return TechnologyRecommendationSummary(
        recommendations=saved_recs,
        total_count=len(saved_recs),
        by_type=by_type,
    )


@router.get(
    "/projects/{project_id}/technology-recommendations",
    response_model=list[TechnologyRecommendationResponse],
)
async def list_technology_recommendations(
    project_id: UUID,
    technology_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List technology recommendations."""
    service = RequirementsService(session)
    recommendations = await service.list_technology_recommendations(
        project_id, technology_type, status_filter
    )
    return recommendations


@router.get("/technology-recommendations/{recommendation_id}", response_model=TechnologyRecommendationResponse)
async def get_technology_recommendation(
    recommendation_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get technology recommendation by ID."""
    service = RequirementsService(session)
    recommendation = await service.get_technology_recommendation(recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Technology recommendation not found")
    return recommendation


@router.put("/technology-recommendations/{recommendation_id}", response_model=TechnologyRecommendationResponse)
async def update_technology_recommendation(
    recommendation_id: UUID,
    data: TechnologyRecommendationUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Update technology recommendation."""
    service = RequirementsService(session)
    recommendation = await service.update_technology_recommendation(recommendation_id, data)
    if not recommendation:
        raise HTTPException(status_code=404, detail="Technology recommendation not found")
    return recommendation


@router.delete("/technology-recommendations/{recommendation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_technology_recommendation(
    recommendation_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete technology recommendation."""
    service = RequirementsService(session)
    success = await service.delete_technology_recommendation(recommendation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Technology recommendation not found")


# ============================================================================
# API Specifications
# ============================================================================


@router.post("/api-specifications", response_model=APISpecificationResponse, status_code=status.HTTP_201_CREATED)
async def create_api_specification(
    data: APISpecificationCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Create API specification."""
    service = RequirementsService(session)
    api_spec = await service.create_api_specification(data)
    return api_spec


@router.get("/requirements/{requirement_id}/api-specifications", response_model=list[APISpecificationResponse])
async def list_api_specifications(
    requirement_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """List API specifications for a requirement."""
    service = RequirementsService(session)
    api_specs = await service.list_api_specifications(requirement_id)
    return api_specs


@router.get("/api-specifications/{api_spec_id}", response_model=APISpecificationResponse)
async def get_api_specification(
    api_spec_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get API specification by ID."""
    service = RequirementsService(session)
    api_spec = await service.get_api_specification(api_spec_id)
    if not api_spec:
        raise HTTPException(status_code=404, detail="API specification not found")
    return api_spec


@router.put("/api-specifications/{api_spec_id}", response_model=APISpecificationResponse)
async def update_api_specification(
    api_spec_id: UUID,
    data: APISpecificationUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Update API specification."""
    service = RequirementsService(session)
    api_spec = await service.update_api_specification(api_spec_id, data)
    if not api_spec:
        raise HTTPException(status_code=404, detail="API specification not found")
    return api_spec


@router.delete("/api-specifications/{api_spec_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_specification(
    api_spec_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete API specification."""
    service = RequirementsService(session)
    success = await service.delete_api_specification(api_spec_id)
    if not success:
        raise HTTPException(status_code=404, detail="API specification not found")


# ============================================================================
# Reports & Analytics
# ============================================================================


@router.get("/projects/{project_id}/summary", response_model=RequirementsSummary)
async def get_requirements_summary(
    project_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get requirements summary for a project."""
    service = RequirementsService(session)
    summary = await service.get_requirements_summary(project_id)
    return summary


@router.get("/projects/{project_id}/report", response_model=RequirementsReport)
async def get_requirements_report(
    project_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Generate full requirements report."""
    service = RequirementsService(session)
    report = await service.get_requirements_report(project_id)
    return report