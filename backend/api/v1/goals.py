"""Goal endpoints for Module 1."""

from typing import Annotated, Optional, Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_active_user
from backend.core.schemas import MessageResponse
from backend.db.base import get_db
from backend.db.models import User
from backend.modules.goals.schemas import (
    GoalAnalysisRequest,
    GoalAnalysisResponse,
    GoalCreate,
    GoalDecomposeRequest,
    GoalDecomposeResponse,
    GoalResponse,
    GoalUpdate,
    GoalWithSubgoals,
)
from backend.modules.goals.service import GoalService

router = APIRouter()


async def get_goal_service(db: AsyncSession = Depends(get_db)) -> GoalService:
    """Get goal service dependency."""
    return GoalService(db)


@router.post(
    "/projects/{project_id}/goals",
    response_model=GoalResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_goal(
    project_id: UUID,
    goal_data: GoalCreate,
    service: GoalService = Depends(get_goal_service),
    current_user: User = Depends(get_current_active_user),
) -> GoalResponse:
    """Create new goal for project."""
    try:
        goal = await service.create_goal(project_id, goal_data)
        return GoalResponse.model_validate(goal)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/projects/{project_id}/goals", response_model=list[GoalResponse])
async def list_goals(
    project_id: UUID,
    skip: int = 0,
    limit: int = 100,
    root_only: bool = False,
    service: GoalService = Depends(get_goal_service),
    current_user: User = Depends(get_current_active_user),
) -> Sequence[GoalResponse]:
    """List goals for project."""
    if root_only:
        goals = await service.list_root_goals(project_id)
    else:
        goals = await service.list_goals(project_id, skip, limit)

    return [GoalResponse.model_validate(goal) for goal in goals]


@router.get("/goals/{goal_id}", response_model=GoalWithSubgoals)
async def get_goal(
    goal_id: UUID,
    include_subgoals: bool = True,
    service: GoalService = Depends(get_goal_service),
    current_user: User = Depends(get_current_active_user),
) -> GoalWithSubgoals:
    """Get goal by ID."""
    if include_subgoals:
        goal = await service.get_goal_with_subgoals(goal_id)
    else:
        goal = await service.get_goal(goal_id)

    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

    # Convert subgoals to response format
    subgoals = [GoalResponse.model_validate(sg) for sg in goal.subgoals]

    response = GoalWithSubgoals.model_validate(goal)
    response.subgoals = subgoals

    return response


@router.put("/goals/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: UUID,
    goal_update: GoalUpdate,
    service: GoalService = Depends(get_goal_service),
    current_user: User = Depends(get_current_active_user),
) -> GoalResponse:
    """Update goal."""
    try:
        goal = await service.update_goal(goal_id, goal_update)
        return GoalResponse.model_validate(goal)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/goals/{goal_id}", response_model=MessageResponse)
async def delete_goal(
    goal_id: UUID,
    service: GoalService = Depends(get_goal_service),
    current_user: User = Depends(get_current_active_user),
) -> MessageResponse:
    """Delete goal."""
    try:
        await service.delete_goal(goal_id)
        return MessageResponse(message="Goal deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/goals/{goal_id}/analyze", response_model=GoalAnalysisResponse)
async def analyze_goal(
    goal_id: UUID,
    request: GoalAnalysisRequest = GoalAnalysisRequest(
        include_suggestions=False, include_metrics=False, include_subgoals=False
    ),
    service: GoalService = Depends(get_goal_service),
    current_user: User = Depends(get_current_active_user),
) -> GoalAnalysisResponse:
    """
    Analyze goal with AI.

    Performs SMART validation and provides feedback and suggestions.
    """
    try:
        result = await service.analyze_goal(goal_id, request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/goals/{goal_id}/decompose", response_model=GoalDecomposeResponse)
async def decompose_goal(
    goal_id: UUID,
    request: GoalDecomposeRequest = GoalDecomposeRequest(num_subgoals=0, include_metrics=False),
    service: GoalService = Depends(get_goal_service),
    current_user: User = Depends(get_current_active_user),
) -> GoalDecomposeResponse:
    """
    Decompose goal into subgoals.

    AI generates suggested subgoals based on the main goal.
    """
    try:
        result = await service.decompose_goal(goal_id, request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
