"""API endpoints for Architecture Module."""

from typing import Annotated, Optional, List, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai_agents.architecture_team import ArchitectureTeam
from backend.api.deps import get_current_user, get_db
from backend.db.models import User
from backend.modules.architecture.schemas import (
    ArchitectureGenerationRequest,
    ArchitectureGenerationResponse,
    ArchitectureModuleCreate,
    ArchitectureModuleResponse,
    ArchitectureModuleUpdate,
    ArchitectureRuleCreate,
    ArchitectureRuleResponse,
    ArchitectureRuleUpdate,
    ArchitectureValidationResponse,
    ComplexityAnalysisResponse,
    ImpactAnalysisRequest,
    ImpactAnalysisResponse,
    ModuleDependencyCreate,
    ModuleDependencyResponse,
    ModuleDependencyUpdate,
    SharedModulesResponse,
)
from backend.modules.architecture.service import ArchitectureService

router = APIRouter()


# ============================================================================
# Architecture Generation
# ============================================================================


@router.post(
    "/projects/{project_id}/architecture/generate",
    response_model=ArchitectureGenerationResponse,
)
async def generate_architecture(
    project_id: UUID,
    request: ArchitectureGenerationRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ArchitectureGenerationResponse:
    """Generate architecture using AI team."""
    # Get goals and opportunities from database
    from backend.modules.goals.repository import GoalRepository
    from backend.modules.opportunities.repository import OpportunityRepository

    goal_repo = GoalRepository(db)
    opp_repo = OpportunityRepository(db)

    goals_data = []
    for goal_id in request.goal_ids:
        goal = await goal_repo.get_by_id(goal_id)
        if goal:
            goals_data.append(
                {
                    "title": goal.title,
                    "description": goal.description,
                    "category": goal.category,
                }
            )

    opportunities_data = []
    for opp_id in request.opportunity_ids:
        opp = await opp_repo.get_by_id(opp_id)
        if opp:
            opportunities_data.append(
                {
                    "title": opp.title,
                    "description": opp.description,
                    "category": opp.category,
                }
            )

    # Generate architecture with AI
    team = ArchitectureTeam()
    result = await team.generate_architecture(
        goals=goals_data,
        opportunities=opportunities_data,
        style=request.architectural_style,
    )

    # Create modules in database
    service = ArchitectureService(db)
    proposal = result["proposal"]
    created_modules = []
    module_name_to_id = {}

    # Create all modules first
    for module_data in proposal["modules"]:
        module_create = ArchitectureModuleCreate(
            project_id=project_id,
            name=module_data["name"],
            description=module_data["description"],
            module_type=module_data["module_type"],
            level=module_data["level"],
            module_metadata={
                "technologies": module_data.get("technologies", []),
                "patterns": module_data.get("patterns", []),
            },
        )

        # Mark as AI generated
        module = await service.create_module(module_create)
        module.ai_generated = True
        module.generation_reasoning = proposal.get("reasoning")
        await db.commit()

        created_modules.append(module)
        module_name_to_id[module.name] = module.id

    # Create dependencies
    created_dependencies = []
    for dep_data in proposal["dependencies"]:
        from_id = module_name_to_id.get(dep_data["from_module"])
        to_id = module_name_to_id.get(dep_data["to_module"])

        if from_id and to_id:
            try:
                dep_create = ModuleDependencyCreate(
                    project_id=project_id,
                    from_module_id=from_id,
                    to_module_id=to_id,
                    dependency_type=dep_data["dependency_type"],
                    description=dep_data.get("reason"),
                )
                dep = await service.create_dependency(dep_create)
                created_dependencies.append(dep)
            except ValueError:
                # Skip if dependency validation fails
                pass

    # Create suggested rules (optional)
    created_rules = []

    return ArchitectureGenerationResponse(
        modules=[ArchitectureModuleResponse.model_validate(m) for m in created_modules],
        dependencies=[ModuleDependencyResponse.model_validate(d) for d in created_dependencies],
        rules=created_rules,
        architectural_style=proposal["architectural_style"],
        reasoning=proposal["reasoning"],
        overall_score=result["review"]["overall_score"],
    )


# ============================================================================
# Module CRUD
# ============================================================================


@router.post("/architecture/modules", response_model=ArchitectureModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module(
    data: ArchitectureModuleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ArchitectureModuleResponse:
    """Create a new architecture module."""
    service = ArchitectureService(db)
    module = await service.create_module(data)
    return ArchitectureModuleResponse.model_validate(module)


@router.get("/projects/{project_id}/architecture", response_model=list[ArchitectureModuleResponse])
async def list_modules(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[UUID] = None,
    module_type: Optional[str] = None,
    status_filter: Optional[str] = None,
) -> list[ArchitectureModuleResponse]:
    """List architecture modules for a project."""
    service = ArchitectureService(db)
    modules = await service.list_modules(
        project_id=project_id,
        skip=skip,
        limit=limit,
        parent_id=parent_id,
        module_type=module_type,
        status=status_filter,
    )
    return [ArchitectureModuleResponse.model_validate(m) for m in modules]


@router.get("/architecture/modules/{module_id}", response_model=ArchitectureModuleResponse)
async def get_module(
    module_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ArchitectureModuleResponse:
    """Get architecture module by ID."""
    service = ArchitectureService(db)
    module = await service.get_module(module_id)

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found",
        )

    return ArchitectureModuleResponse.model_validate(module)


@router.put("/architecture/modules/{module_id}", response_model=ArchitectureModuleResponse)
async def update_module(
    module_id: UUID,
    data: ArchitectureModuleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ArchitectureModuleResponse:
    """Update architecture module."""
    service = ArchitectureService(db)
    module = await service.update_module(module_id, data)

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found",
        )

    return ArchitectureModuleResponse.model_validate(module)


@router.delete("/architecture/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete architecture module."""
    service = ArchitectureService(db)
    success = await service.delete_module(module_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found",
        )


@router.post("/architecture/modules/{module_id}/approve", response_model=ArchitectureModuleResponse)
async def approve_module(
    module_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ArchitectureModuleResponse:
    """Approve architecture module."""
    service = ArchitectureService(db)
    module = await service.approve_module(module_id, current_user)

    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found",
        )

    return ArchitectureModuleResponse.model_validate(module)


# ============================================================================
# Dependency Management
# ============================================================================


@router.post(
    "/architecture/dependencies",
    response_model=ModuleDependencyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_dependency(
    data: ModuleDependencyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ModuleDependencyResponse:
    """Create a module dependency."""
    service = ArchitectureService(db)

    try:
        dependency = await service.create_dependency(data)
        return ModuleDependencyResponse.model_validate(dependency)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/projects/{project_id}/architecture/dependencies", response_model=list[ModuleDependencyResponse])
async def list_dependencies(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    dependency_type: Optional[str] = None,
) -> list[ModuleDependencyResponse]:
    """List dependencies for a project."""
    service = ArchitectureService(db)
    dependencies = await service.list_dependencies(
        project_id=project_id,
        dependency_type=dependency_type,
    )
    return [ModuleDependencyResponse.model_validate(d) for d in dependencies]


@router.delete("/architecture/dependencies/{dependency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dependency(
    dependency_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a module dependency."""
    service = ArchitectureService(db)
    success = await service.delete_dependency(dependency_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependency not found",
        )


# ============================================================================
# Validation
# ============================================================================


@router.get("/projects/{project_id}/architecture/validate", response_model=ArchitectureValidationResponse)
async def validate_architecture(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ArchitectureValidationResponse:
    """Validate architecture for issues."""
    service = ArchitectureService(db)
    return await service.validate_architecture(project_id)


# ============================================================================
# Rules Management
# ============================================================================


@router.post("/architecture/rules", response_model=ArchitectureRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    data: ArchitectureRuleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ArchitectureRuleResponse:
    """Create an architecture rule."""
    service = ArchitectureService(db)
    rule = await service.create_rule(data)
    return ArchitectureRuleResponse.model_validate(rule)


@router.get("/projects/{project_id}/architecture/rules", response_model=list[ArchitectureRuleResponse])
async def list_rules(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    level: Optional[str] = None,
    rule_type: Optional[str] = None,
    active_only: bool = True,
) -> list[ArchitectureRuleResponse]:
    """List architecture rules for a project."""
    service = ArchitectureService(db)
    rules = await service.list_rules(
        project_id=project_id,
        level=level,
        rule_type=rule_type,
        active_only=active_only,
    )
    return [ArchitectureRuleResponse.model_validate(r) for r in rules]


@router.put("/architecture/rules/{rule_id}", response_model=ArchitectureRuleResponse)
async def update_rule(
    rule_id: UUID,
    data: ArchitectureRuleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ArchitectureRuleResponse:
    """Update an architecture rule."""
    service = ArchitectureService(db)
    rule = await service.update_rule(rule_id, data)

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found",
        )

    return ArchitectureRuleResponse.model_validate(rule)


@router.delete("/architecture/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete an architecture rule."""
    service = ArchitectureService(db)
    success = await service.delete_rule(rule_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found",
        )


# ============================================================================
# Analysis
# ============================================================================


@router.get("/projects/{project_id}/architecture/complexity", response_model=ComplexityAnalysisResponse)
async def get_complexity_analysis(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ComplexityAnalysisResponse:
    """Get complexity analysis for architecture."""
    service = ArchitectureService(db)
    return await service.analyze_complexity(project_id)


@router.post("/projects/{project_id}/architecture/impact-analysis", response_model=ImpactAnalysisResponse)
async def get_impact_analysis(
    project_id: UUID,
    request: ImpactAnalysisRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ImpactAnalysisResponse:
    """Analyze impact of changes to a module."""
    service = ArchitectureService(db)

    try:
        return await service.analyze_impact(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ============================================================================
# Shared Modules
# ============================================================================


@router.get("/projects/{project_id}/architecture/shared-modules", response_model=SharedModulesResponse)
async def get_shared_modules(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SharedModulesResponse:
    """Get shared modules (used by multiple modules)."""
    service = ArchitectureService(db)
    return await service.get_shared_modules(project_id)


# ============================================================================
# RefMemTree Advanced Features API Endpoints
# ============================================================================


@router.get("/modules/{module_id}/impact-analysis-advanced", response_model=dict)
async def analyze_module_impact_advanced(
    module_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    change_type: str = "update",
):
    """
    ADVANCED RefMemTree: Analyze change impact with dependency tracking.

    Uses RefMemTree's internal dependency tracking for deeper analysis:
    - Propagation paths
    - Coupling strength analysis
    - Critical dependency identification
    """
    service = ArchitectureService(db)
    return service.analyze_module_change_impact_advanced(module_id, change_type)


@router.post("/modules/{module_id}/simulate-change", response_model=dict)
async def simulate_module_change(
    module_id: UUID,
    proposed_changes: dict,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    ADVANCED RefMemTree: Simulate changes before applying.

    Simulates proposed change and returns:
    - Risk level (low/medium/high/critical)
    - Success probability
    - Side effects
    - Affected modules

    Use case: "What if I change this module's type?"
    """
    service = ArchitectureService(db)
    return service.simulate_module_change(module_id, proposed_changes)


@router.get("/modules/{module_id}/dependency-analysis", response_model=dict)
async def get_dependency_analysis(
    module_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    ADVANCED RefMemTree: Comprehensive dependency analysis.

    Provides:
    - Dependency chain depth
    - Coupling scores
    - Criticality assessment (how many modules depend on this)
    - Indirect dependency analysis
    """
    service = ArchitectureService(db)
    return service.get_dependency_analysis_advanced(module_id)


@router.get("/modules/{module_id}/rule-validation", response_model=dict)
async def validate_module_rules(
    module_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    ADVANCED RefMemTree: Validate against architecture rules.

    Checks module compliance with:
    - Naming conventions
    - Dependency constraints
    - Layer rules
    - Custom architecture rules
    """
    service = ArchitectureService(db)
    return service.validate_module_rules(module_id)


# ============================================================================
# AI Governor - Safe AI Plan Execution
# ============================================================================


@router.post("/projects/{project_id}/execute-ai-plan", response_model=dict)
async def execute_ai_architecture_plan(
    project_id: UUID,
    plan: List[Dict],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    dry_run: bool = False,
):
    """
    Execute AI-generated architecture plan using AI Governor.

    ⭐ Uses REAL RefMemTree AIGovernor.execute_refactoring_plan()

    This is THE endpoint that makes AI architecture generation SAFE!

    Features:
    - Validates plan before execution
    - Creates snapshot for rollback
    - Atomic execution (all-or-nothing)
    - Auto-rollback on failure
    - Syncs to PostgreSQL after success

    Args:
        project_id: Project UUID
        plan: AI-generated plan (list of actions)
        dry_run: If True, simulates without applying

    Returns:
        Execution result with status, created nodes, rollback info
    """
    from backend.core.ai_governor import execute_ai_plan

    result = await execute_ai_plan(project_id, plan, db, dry_run=dry_run)

    return result
