"""API endpoints for Opportunity Engine."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.api.deps import get_current_user, get_db
from backend.db.models import Project, User
from backend.modules.opportunities.schemas import (
    OpportunityCompareRequest,
    OpportunityCreate,
    OpportunityGenerateRequest,
    OpportunityGenerateResponse,
    OpportunityResponse,
    OpportunityUpdate,
)
from backend.modules.opportunities.service import OpportunityService

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.post("/projects/{project_id}/opportunities", response_model=OpportunityResponse)
def create_opportunity(
    project_id: UUID,
    opportunity_data: OpportunityCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OpportunityResponse:
    """Create a new opportunity."""
    # Verify project ownership
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    service = OpportunityService(db)
    try:
        opportunity = service.create_opportunity(project_id, opportunity_data)
        return OpportunityResponse.model_validate(opportunity)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/projects/{project_id}/opportunities", response_model=list[OpportunityResponse])
def list_opportunities(
    project_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[OpportunityResponse]:
    """List opportunities for a project."""
    # Verify project ownership
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    service = OpportunityService(db)
    opportunities = service.list_opportunities(project_id, skip, limit)
    return [OpportunityResponse.model_validate(opp) for opp in opportunities]


@router.get("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
def get_opportunity(
    opportunity_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OpportunityResponse:
    """Get opportunity details."""
    service = OpportunityService(db)
    opportunity = service.get_opportunity(opportunity_id)

    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    # Verify ownership
    project = db.query(Project).filter(Project.id == opportunity.project_id).first()
    if not project or project.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return OpportunityResponse.model_validate(opportunity)


@router.put("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
def update_opportunity(
    opportunity_id: UUID,
    opportunity_update: OpportunityUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OpportunityResponse:
    """Update an opportunity."""
    service = OpportunityService(db)
    opportunity = service.get_opportunity(opportunity_id)

    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    # Verify ownership
    project = db.query(Project).filter(Project.id == opportunity.project_id).first()
    if not project or project.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    try:
        updated = service.update_opportunity(opportunity_id, opportunity_update)
        return OpportunityResponse.model_validate(updated)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/opportunities/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opportunity(
    opportunity_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete an opportunity."""
    service = OpportunityService(db)
    opportunity = service.get_opportunity(opportunity_id)

    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    # Verify ownership
    project = db.query(Project).filter(Project.id == opportunity.project_id).first()
    if not project or project.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    try:
        service.delete_opportunity(opportunity_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/projects/{project_id}/opportunities/generate", response_model=OpportunityGenerateResponse
)
async def generate_opportunities(
    project_id: UUID,
    request: OpportunityGenerateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OpportunityGenerateResponse:
    """
    Generate opportunities using AI Team.

    This endpoint triggers the AI Team workflow:
    1. Creative Generator (high creativity)
    2. Structured Generator (practical focus)
    3. Analyzer (analyzes all ideas)
    4. Supervisor (makes final decisions)
    """
    # Verify project ownership
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    service = OpportunityService(db)
    try:
        result = await service.generate_opportunities(project_id, request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI generation failed: {str(e)}",
        )


@router.get("/projects/{project_id}/opportunities/top", response_model=list[OpportunityResponse])
def get_top_opportunities(
    project_id: UUID,
    limit: int = 10,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[OpportunityResponse]:
    """Get top-scored opportunities."""
    # Verify project ownership
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if project.created_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    service = OpportunityService(db)
    opportunities = service.get_top_opportunities(project_id, limit)
    return [OpportunityResponse.model_validate(opp) for opp in opportunities]


@router.post("/opportunities/compare")
def compare_opportunities(
    request: OpportunityCompareRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Compare multiple opportunities."""
    service = OpportunityService(db)

    # Verify ownership for all opportunities
    for opp_id in request.opportunity_ids:
        opportunity = service.get_opportunity(opp_id)
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Opportunity {opp_id} not found",
            )

        project = db.query(Project).filter(Project.id == opportunity.project_id).first()
        if not project or project.created_by != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    try:
        comparison = service.compare_opportunities(request.opportunity_ids)
        return comparison
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
