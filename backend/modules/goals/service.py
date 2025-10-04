"""Goal service layer."""

from typing import Optional, Sequence, Any, Dict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai_agents.goal_analyst import GoalAnalystAgent
from backend.db.models import Goal, Project
from backend.modules.goals.repository import GoalRepository
from backend.modules.goals.schemas import (
    GoalAnalysisRequest,
    GoalAnalysisResponse,
    GoalCreate,
    GoalDecomposeRequest,
    GoalDecomposeResponse,
    GoalUpdate,
)
from backend.modules.goals.smart_validator import SMARTValidator


class GoalService:
    """Service layer for Goal operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize service."""
        self.db = db
        self.repository = GoalRepository(db)
        self.validator = SMARTValidator()
        self.ai_agent = GoalAnalystAgent()

    async def create_goal(self, project_id: UUID, goal_data: GoalCreate) -> Goal:
        """
        Create new goal.

        Args:
            project_id: Project ID
            goal_data: Goal creation data

        Returns:
            Created goal
        """
        # Verify project exists
        project_result = await self.db.execute(select(Project).filter(Project.id == project_id))
        project = project_result.scalars().first()
        if not project:
            raise ValueError("Project not found")

        # Verify parent goal if specified
        if goal_data.parent_goal_id:
            parent = await self.repository.get_by_id(goal_data.parent_goal_id)
            if not parent or parent.project_id != project_id:
                raise ValueError("Parent goal not found or belongs to different project")

        # Create goal via repository
        created_goal = await self.repository.create(goal_data, project_id)

        # Perform SMART validation and update
        validation_result = self.validator.validate_goal(
            title=created_goal.title,
            description=created_goal.description,
            category=created_goal.category,
            target_date=created_goal.target_date,
            metrics=created_goal.metrics,
        )

        # Set validation scores
        update_data = GoalUpdate(
            specific_score=validation_result["specific_score"],
            measurable_score=validation_result["measurable_score"],
            achievable_score=validation_result["achievable_score"],
            relevant_score=validation_result["relevant_score"],
            time_bound_score=validation_result["time_bound_score"],
            overall_smart_score=validation_result["overall_smart_score"],
            is_smart_validated=bool(validation_result["is_smart_compliant"]),
        )
        
        updated_goal = await self.repository.update(created_goal.id, update_data)
        if updated_goal is None:
             raise ValueError("Failed to update goal after creation.") # Should not happen
        return updated_goal

    async def get_goal(self, goal_id: UUID) -> Optional[Goal]:
        """Get goal by ID."""
        return await self.repository.get_by_id(goal_id)

    async def get_goal_with_subgoals(self, goal_id: UUID) -> Optional[Goal]:
        """Get goal with subgoals."""
        return await self.repository.get_by_id_with_subgoals(goal_id)

    async def list_goals(self, project_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[Goal]:
        """List goals for project."""
        return await self.repository.get_by_project(project_id, skip, limit)

    async def list_root_goals(self, project_id: UUID) -> Sequence[Goal]:
        """List root goals (no parent) for project."""
        return await self.repository.get_root_goals(project_id)

    async def update_goal(self, goal_id: UUID, goal_update: GoalUpdate) -> Goal:
        """
        Update goal.

        Args:
            goal_id: Goal ID
            goal_update: Update data

        Returns:
            Updated goal
        """
        goal = await self.repository.get_by_id(goal_id)
        if not goal:
            raise ValueError("Goal not found")

        # Update fields
        if goal_update.title is not None:
            goal.title = goal_update.title
        if goal_update.description is not None:
            goal.description = goal_update.description
        if goal_update.category is not None:
            goal.category = goal_update.category
        if goal_update.target_date is not None:
            goal.target_date = goal_update.target_date
        if goal_update.priority is not None:
            goal.priority = goal_update.priority
        if goal_update.status is not None:
            goal.status = goal_update.status
        if goal_update.completion_percentage is not None:
            goal.completion_percentage = goal_update.completion_percentage
        if goal_update.metrics is not None:
            goal.metrics = {"metrics": [m.model_dump() for m in goal_update.metrics]}

        # Re-validate if key fields changed
        if any(
            [
                goal_update.title,
                goal_update.description,
                goal_update.target_date,
                goal_update.metrics,
            ]
        ):
            validation_result = self.validator.validate_goal(
                title=goal.title,
                description=goal.description,
                category=goal.category,
                target_date=goal.target_date,
                metrics=goal.metrics,
            )

            goal.specific_score = validation_result["specific_score"]
            goal.measurable_score = validation_result["measurable_score"]
            goal.achievable_score = validation_result["achievable_score"]
            goal.relevant_score = validation_result["relevant_score"]
            goal.time_bound_score = validation_result["time_bound_score"]
            goal.overall_smart_score = validation_result["overall_smart_score"]
            goal.is_smart_validated = validation_result["is_smart_compliant"] # type: ignore

        updated_goal = await self.repository.update(goal_id, goal_update)
        if updated_goal is None:
            raise ValueError("Goal not found during update")
        return updated_goal

    async def delete_goal(self, goal_id: UUID) -> None:
        """Delete goal."""
        goal = await self.repository.get_by_id(goal_id)
        if not goal:
            raise ValueError("Goal not found")

        await self.repository.delete(goal_id)

    async def analyze_goal(self, goal_id: UUID, request: GoalAnalysisRequest) -> GoalAnalysisResponse:
        """
        Analyze goal with AI.

        Args:
            goal_id: Goal ID
            request: Analysis request options

        Returns:
            Analysis result
        """
        goal = await self.repository.get_by_id(goal_id)
        if not goal:
            raise ValueError("Goal not found")

        # Run AI analysis
        ai_result = await self.ai_agent.analyze_goal(
            title=goal.title,
            description=goal.description,
            category=goal.category,
            target_date=str(goal.target_date) if goal.target_date else None,
        )

        # Get suggested metrics if requested
        suggested_metrics = []
        if request.include_metrics:
            metrics_result = await self.ai_agent.suggest_metrics(
                title=goal.title, description=goal.description, category=goal.category
            )
            suggested_metrics = metrics_result

        # Get suggested subgoals if requested
        suggested_subgoals = []
        if request.include_subgoals:
            subgoals_result = await self.ai_agent.decompose_goal(
                title=goal.title, description=goal.description, num_subgoals=3
            )
            suggested_subgoals = [s.title for s in subgoals_result]

        # Store AI feedback in goal
        update_data = GoalUpdate(
            ai_feedback={
                "feedback": ai_result.overall_feedback,
                "strengths": ai_result.strengths,
                "weaknesses": ai_result.weaknesses,
            },
            ai_suggestions=ai_result.suggestions,
        )
        await self.repository.update(goal.id, update_data)

        # Build response
        from backend.modules.goals.schemas import AIFeedback, SMARTScores, MetricDefinition # Import MetricDefinition

        response = GoalAnalysisResponse(
            goal_id=goal.id,
            smart_scores=SMARTScores(
                specific_score=goal.specific_score or 0.0,
                measurable_score=goal.measurable_score or 0.0,
                achievable_score=goal.achievable_score or 0.0,
                relevant_score=goal.relevant_score or 0.0,
                time_bound_score=goal.time_bound_score or 0.0,
                overall_smart_score=goal.overall_smart_score or 0.0,
            ),
            feedback=AIFeedback(
                feedback=ai_result.overall_feedback,
                suggestions=ai_result.suggestions,
                strengths=ai_result.strengths,
                weaknesses=ai_result.weaknesses,
            ),
            suggested_metrics=[MetricDefinition.model_validate(m) for m in suggested_metrics], # Convert MetricSuggestion to MetricDefinition
            suggested_subgoals=suggested_subgoals,
            is_smart_compliant=goal.is_smart_validated,
        )

        return response

    async def decompose_goal(self, goal_id: UUID, request: GoalDecomposeRequest) -> GoalDecomposeResponse:
        """
        Decompose goal into subgoals.

        Args:
            goal_id: Goal ID
            request: Decomposition request

        Returns:
            Suggested subgoals
        """
        goal = await self.repository.get_by_id(goal_id)
        if not goal:
            raise ValueError("Goal not found")

        # Run AI decomposition
        subgoals = await self.ai_agent.decompose_goal(
            title=goal.title, description=goal.description, num_subgoals=request.num_subgoals
        )

        # If metrics requested, suggest metrics for each subgoal
        if request.include_metrics:
            for subgoal in subgoals:
                metrics = await self.ai_agent.suggest_metrics(
                    title=subgoal.title, description=subgoal.description, category=goal.category
                )
                subgoal.metrics = metrics  # type: ignore

        response = GoalDecomposeResponse(
            parent_goal_id=goal.id,
            suggested_subgoals=subgoals,  # type: ignore
            reasoning=f"AI-generated {len(subgoals)} subgoals based on the main goal analysis",
        )

        return response
