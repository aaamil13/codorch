"""Unit tests for Goals Repository."""

import pytest
from uuid import uuid4

from backend.db.models import Goal, Project, User
from backend.modules.goals.repository import GoalRepository
from backend.modules.goals.schemas import GoalCreate, GoalUpdate


@pytest.fixture
def test_project(db_session, test_user: User):
    """Create a test project."""
    project = Project(
        name="Test Project for Goals",
        description="Test project",
        status="active",
        created_by=test_user.id,
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def goal_repo(db_session):
    """Create GoalRepository instance."""
    return GoalRepository(db_session)


class TestGoalRepository:
    """Test GoalRepository methods."""

    def test_create_goal(self, goal_repo, test_project):
        """Test creating a goal."""
        goal_data = GoalCreate(
            project_id=test_project.id,
            title="Test Goal",
            description="Test description",
            category="business",
        )

        goal = goal_repo.create(goal_data)

        assert goal.id is not None
        assert goal.title == "Test Goal"
        assert goal.description == "Test description"
        assert goal.category == "business"
        assert goal.project_id == test_project.id
        assert goal.status == "active"

    def test_get_goal_by_id(self, goal_repo, test_project):
        """Test getting a goal by ID."""
        goal_data = GoalCreate(
            project_id=test_project.id,
            title="Test Goal",
            description="Test description",
        )
        created_goal = goal_repo.create(goal_data)

        retrieved_goal = goal_repo.get_by_id(created_goal.id)

        assert retrieved_goal is not None
        assert retrieved_goal.id == created_goal.id
        assert retrieved_goal.title == created_goal.title

    def test_get_goal_by_id_not_found(self, goal_repo):
        """Test getting a non-existent goal."""
        goal = goal_repo.get_by_id(uuid4())
        assert goal is None

    def test_get_goals_by_project(self, goal_repo, test_project):
        """Test getting goals by project."""
        # Create multiple goals
        for i in range(3):
            goal_data = GoalCreate(
                project_id=test_project.id,
                title=f"Goal {i}",
                description=f"Description {i}",
            )
            goal_repo.create(goal_data)

        goals = goal_repo.get_by_project(test_project.id)

        assert len(goals) == 3
        assert all(g.project_id == test_project.id for g in goals)

    def test_get_goals_by_project_with_category(self, goal_repo, test_project):
        """Test filtering goals by category."""
        # Create goals with different categories
        goal_repo.create(
            GoalCreate(
                project_id=test_project.id,
                title="Business Goal",
                category="business",
            )
        )
        goal_repo.create(
            GoalCreate(
                project_id=test_project.id,
                title="Technical Goal",
                category="technical",
            )
        )

        business_goals = goal_repo.get_by_project(test_project.id, category="business")

        assert len(business_goals) == 1
        assert business_goals[0].category == "business"

    def test_update_goal(self, goal_repo, test_project):
        """Test updating a goal."""
        goal_data = GoalCreate(
            project_id=test_project.id,
            title="Original Title",
            description="Original description",
        )
        goal = goal_repo.create(goal_data)

        update_data = GoalUpdate(
            title="Updated Title",
            description="Updated description",
        )
        updated_goal = goal_repo.update(goal.id, update_data)

        assert updated_goal is not None
        assert updated_goal.title == "Updated Title"
        assert updated_goal.description == "Updated description"

    def test_delete_goal(self, goal_repo, test_project):
        """Test deleting a goal."""
        goal_data = GoalCreate(
            project_id=test_project.id,
            title="Goal to Delete",
        )
        goal = goal_repo.create(goal_data)

        result = goal_repo.delete(goal.id)

        assert result is True
        assert goal_repo.get_by_id(goal.id) is None

    def test_delete_nonexistent_goal(self, goal_repo):
        """Test deleting a non-existent goal."""
        result = goal_repo.delete(uuid4())
        assert result is False

    def test_get_goals_with_pagination(self, goal_repo, test_project):
        """Test pagination."""
        # Create 10 goals
        for i in range(10):
            goal_repo.create(
                GoalCreate(
                    project_id=test_project.id,
                    title=f"Goal {i}",
                )
            )

        # Get first 5
        page1 = goal_repo.get_by_project(test_project.id, skip=0, limit=5)
        assert len(page1) == 5

        # Get next 5
        page2 = goal_repo.get_by_project(test_project.id, skip=5, limit=5)
        assert len(page2) == 5

        # No overlap
        page1_ids = {g.id for g in page1}
        page2_ids = {g.id for g in page2}
        assert len(page1_ids & page2_ids) == 0
