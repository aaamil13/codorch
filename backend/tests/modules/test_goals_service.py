"""Unit tests for Goals Service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Project, User
from backend.modules.goals.schemas import GoalCreate, GoalUpdate
from backend.modules.goals.service import GoalService


@pytest.fixture
async def test_project(db_session: AsyncSession, test_user: User) -> Project:
    """Create a test project."""
    project = Project(
        name="Test Project",
        description="Test project",
        goal="Test Goal",
        owner_id=test_user.id
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest.fixture
def goal_service(db_session: AsyncSession) -> GoalService:
    """Create GoalService instance."""
    return GoalService(db_session)


class TestGoalService:
    """Test GoalService methods."""

    @pytest.mark.asyncio
    async def test_create_goal_with_smart_validation(self, goal_service: GoalService, test_project: Project) -> None:
        """Test creating a goal with SMART validation."""
        goal_data = GoalCreate(
            title="Increase revenue by 20%",
            description="Increase monthly revenue by 20% in Q4 2025",
            category="business",
        )

        goal = await goal_service.create_goal(test_project.id, goal_data)

        assert goal.id is not None
        assert goal.title == goal_data.title
        # SMART scores should be calculated
        assert goal.specific_score is not None
        assert goal.measurable_score is not None
        assert goal.achievable_score is not None
        assert goal.relevant_score is not None
        assert goal.time_bound_score is not None
        assert goal.overall_smart_score is not None

    @pytest.mark.asyncio
    async def test_get_goal(self, goal_service: GoalService, test_project: Project) -> None:
        """Test getting a goal."""
        goal_data = GoalCreate(
            title="Test Goal",
        )
        created_goal = await goal_service.create_goal(test_project.id, goal_data)

        retrieved_goal = await goal_service.get_goal(created_goal.id)

        assert retrieved_goal is not None
        assert retrieved_goal.id == created_goal.id

    @pytest.mark.asyncio
    async def test_list_goals(self, goal_service: GoalService, test_project: Project) -> None:
        """Test listing goals."""
        # Create goals
        for i in range(3):
            await goal_service.create_goal(
                test_project.id,
                GoalCreate(
                    title=f"Goal {i}",
                )
            )

        goals = await goal_service.list_goals(test_project.id)

        assert len(goals) == 3

    @pytest.mark.asyncio
    async def test_update_goal(self, goal_service: GoalService, test_project: Project) -> None:
        """Test updating a goal."""
        goal = await goal_service.create_goal(
            test_project.id,
            GoalCreate(
                title="Original Title",
            )
        )

        updated_goal = await goal_service.update_goal(
            goal.id,
            GoalUpdate(title="Updated Title"),
        )

        assert updated_goal is not None
        assert updated_goal.title == "Updated Title"
        # SMART scores should be recalculated
        assert updated_goal.overall_smart_score is not None

    @pytest.mark.asyncio
    async def test_delete_goal(self, goal_service: GoalService, test_project: Project) -> None:
        """Test deleting a goal."""
        goal = await goal_service.create_goal(
            test_project.id,
            GoalCreate(
                title="Goal to Delete",
            )
        )

        await goal_service.delete_goal(goal.id)

        assert await goal_service.get_goal(goal.id) is None

    @pytest.mark.asyncio
    async def test_analyze_goal(self, goal_service: GoalService, test_project: Project) -> None:
        """Test AI goal analysis."""
        goal = await goal_service.create_goal(
            test_project.id,
            GoalCreate(
                title="Increase user engagement",
                description="Improve user engagement metrics",
            )
        )

        with patch("backend.modules.goals.service.GoalAnalystAgent") as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.analyze_goal = AsyncMock(
                return_value={
                    "strengths": ["Clear objective"],
                    "weaknesses": ["Needs specific metrics"],
                    "suggestions": ["Add target percentage"],
                    "smart_feedback": {
                        "specific": "Moderate",
                        "measurable": "Needs improvement",
                    },
                }
            )
            mock_agent_class.return_value = mock_agent
            from backend.modules.goals.schemas import GoalAnalysisRequest
            request = GoalAnalysisRequest(include_suggestions=True, include_metrics=True, include_subgoals=False)
            analysis = await goal_service.analyze_goal(goal.id, request)

            assert hasattr(analysis.feedback, "strengths")
            assert hasattr(analysis.feedback, "weaknesses")
            assert hasattr(analysis.feedback, "suggestions")

    @pytest.mark.asyncio
    async def test_decompose_goal(self, goal_service: GoalService, test_project: Project) -> None:
        """Test AI goal decomposition."""
        goal = await goal_service.create_goal(
            test_project.id,
            GoalCreate(
                title="Launch new product",
                description="Launch new SaaS product by Q4",
            )
        )

        with patch("backend.modules.goals.service.GoalAnalystAgent") as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.suggest_subgoals = AsyncMock(
                return_value={
                    "subgoals": [
                        {
                            "title": "Design product features",
                            "description": "Define core features",
                            "priority": "high",
                        },
                        {
                            "title": "Develop MVP",
                            "description": "Build minimum viable product",
                            "priority": "high",
                        },
                    ],
                    "reasoning": "Breaking down into phases",
                }
            )
            mock_agent_class.return_value = mock_agent
            from backend.modules.goals.schemas import GoalDecomposeRequest
            request = GoalDecomposeRequest(num_subgoals=3, include_metrics=True)
            result = await goal_service.decompose_goal(goal.id, request)

            assert hasattr(result, "suggested_subgoals")
            assert hasattr(result, "reasoning")
            assert len(result.suggested_subgoals) == 2

    @pytest.mark.asyncio
    async def test_smart_score_calculation(self, goal_service: GoalService, test_project: Project) -> None:
        """Test SMART score calculation logic."""
        # Goal with good SMART properties
        smart_goal = await goal_service.create_goal(
            test_project.id,
            GoalCreate(
                title="Increase sales by 25%",
                description="Increase monthly sales by 25% by December 2025 through new marketing campaign",
                category="business",
            )
        )

        # Goal with poor SMART properties
        vague_goal = await goal_service.create_goal(
            test_project.id,
            GoalCreate(
                title="Be better",
                description="Improve things",
                category="other",
            )
        )

        # SMART goal should have higher overall score
        assert smart_goal.overall_smart_score is not None
        assert vague_goal.overall_smart_score is not None
        assert smart_goal.overall_smart_score > vague_goal.overall_smart_score
        assert smart_goal.measurable_score is not None
        assert vague_goal.measurable_score is not None
        assert smart_goal.measurable_score > vague_goal.measurable_score
        assert smart_goal.specific_score is not None
        assert vague_goal.specific_score is not None
        assert smart_goal.specific_score > vague_goal.specific_score
