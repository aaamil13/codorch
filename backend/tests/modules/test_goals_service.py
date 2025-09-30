"""Unit tests for Goals Service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from backend.db.models import Project, User
from backend.modules.goals.schemas import GoalCreate, GoalUpdate
from backend.modules.goals.service import GoalService


@pytest.fixture
def test_project(db_session, test_user: User):
    """Create a test project."""
    project = Project(
        name="Test Project",
        description="Test project",
        status="active",
        created_by=test_user.id,
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def goal_service(db_session):
    """Create GoalService instance."""
    return GoalService(db_session)


class TestGoalService:
    """Test GoalService methods."""

    def test_create_goal_with_smart_validation(self, goal_service, test_project):
        """Test creating a goal with SMART validation."""
        goal_data = GoalCreate(
            project_id=test_project.id,
            title="Increase revenue by 20%",
            description="Increase monthly revenue by 20% in Q4 2025",
            category="business",
        )

        goal = goal_service.create_goal(goal_data)

        assert goal.id is not None
        assert goal.title == goal_data.title
        # SMART scores should be calculated
        assert goal.specific_score is not None
        assert goal.measurable_score is not None
        assert goal.achievable_score is not None
        assert goal.relevant_score is not None
        assert goal.time_bound_score is not None
        assert goal.smart_score is not None

    def test_get_goal(self, goal_service, test_project):
        """Test getting a goal."""
        goal_data = GoalCreate(
            project_id=test_project.id,
            title="Test Goal",
        )
        created_goal = goal_service.create_goal(goal_data)

        retrieved_goal = goal_service.get_goal(created_goal.id)

        assert retrieved_goal is not None
        assert retrieved_goal.id == created_goal.id

    def test_list_goals(self, goal_service, test_project):
        """Test listing goals."""
        # Create goals
        for i in range(3):
            goal_service.create_goal(
                GoalCreate(
                    project_id=test_project.id,
                    title=f"Goal {i}",
                )
            )

        goals = goal_service.list_goals(test_project.id)

        assert len(goals) == 3

    def test_update_goal(self, goal_service, test_project):
        """Test updating a goal."""
        goal = goal_service.create_goal(
            GoalCreate(
                project_id=test_project.id,
                title="Original Title",
            )
        )

        updated_goal = goal_service.update_goal(
            goal.id,
            GoalUpdate(title="Updated Title"),
        )

        assert updated_goal is not None
        assert updated_goal.title == "Updated Title"
        # SMART scores should be recalculated
        assert updated_goal.smart_score is not None

    def test_delete_goal(self, goal_service, test_project):
        """Test deleting a goal."""
        goal = goal_service.create_goal(
            GoalCreate(
                project_id=test_project.id,
                title="Goal to Delete",
            )
        )

        result = goal_service.delete_goal(goal.id)

        assert result is True
        assert goal_service.get_goal(goal.id) is None

    @pytest.mark.asyncio
    async def test_analyze_goal(self, goal_service, test_project):
        """Test AI goal analysis."""
        goal = goal_service.create_goal(
            GoalCreate(
                project_id=test_project.id,
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

            analysis = await goal_service.analyze_goal(goal.id)

            assert "strengths" in analysis
            assert "weaknesses" in analysis
            assert "suggestions" in analysis
            assert "smart_feedback" in analysis

    @pytest.mark.asyncio
    async def test_decompose_goal(self, goal_service, test_project):
        """Test AI goal decomposition."""
        goal = goal_service.create_goal(
            GoalCreate(
                project_id=test_project.id,
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

            result = await goal_service.decompose_goal(goal.id)

            assert "subgoals" in result
            assert "reasoning" in result
            assert len(result["subgoals"]) == 2

    def test_smart_score_calculation(self, goal_service, test_project):
        """Test SMART score calculation logic."""
        # Goal with good SMART properties
        smart_goal = goal_service.create_goal(
            GoalCreate(
                project_id=test_project.id,
                title="Increase sales by 25%",
                description="Increase monthly sales by 25% by December 2025 through new marketing campaign",
                category="business",
            )
        )

        # Goal with poor SMART properties
        vague_goal = goal_service.create_goal(
            GoalCreate(
                project_id=test_project.id,
                title="Be better",
                description="Improve things",
                category="other",
            )
        )

        # SMART goal should have higher overall score
        assert smart_goal.smart_score > vague_goal.smart_score
        assert smart_goal.measurable_score > vague_goal.measurable_score
        assert smart_goal.specific_score > vague_goal.specific_score
