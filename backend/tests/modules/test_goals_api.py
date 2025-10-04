"""Integration tests for Goals API endpoints."""

from typing import Dict
from uuid import UUID
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Project, User


@pytest.fixture
async def test_project(db_session: AsyncSession, test_user: User) -> Project:
    """Create test project."""
    project = Project(
        name="Test Project",
        description="Test",
        status="active",
        created_by=test_user.id,
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


class TestGoalsAPI:
    """Test Goals API endpoints."""

    def test_create_goal(self, client: TestClient, auth_headers: Dict[str, str], test_project: Project) -> None:
        """Test POST /api/v1/goals."""
        response = client.post(
            "/api/v1/goals",
            json={
                "project_id": str(test_project.id),
                "title": "Test Goal",
                "description": "Test description",
                "category": "business",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Goal"
        assert data["category"] == "business"
        assert "smart_score" in data
        assert "id" in data

    def test_create_goal_missing_fields(
        self, client: TestClient, auth_headers: Dict[str, str], test_project: Project
    ) -> None:
        """Test creating goal without required fields."""
        response = client.post(
            "/api/v1/goals",
            json={
                "project_id": str(test_project.id),
                # Missing title
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_list_goals(self, client: TestClient, auth_headers: Dict[str, str], test_project: Project) -> None:
        """Test GET /api/v1/goals."""
        # Create goals
        for i in range(3):
            client.post(
                "/api/v1/goals",
                json={
                    "project_id": str(test_project.id),
                    "title": f"Goal {i}",
                },
                headers=auth_headers,
            )

        response = client.get(
            f"/api/v1/goals?project_id={test_project.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_goals_with_filter(
        self, client: TestClient, auth_headers: Dict[str, str], test_project: Project
    ) -> None:
        """Test filtering goals by category."""
        client.post(
            "/api/v1/goals",
            json={
                "project_id": str(test_project.id),
                "title": "Business Goal",
                "category": "business",
            },
            headers=auth_headers,
        )
        client.post(
            "/api/v1/goals",
            json={
                "project_id": str(test_project.id),
                "title": "Technical Goal",
                "category": "technical",
            },
            headers=auth_headers,
        )

        response = client.get(
            f"/api/v1/goals?project_id={test_project.id}&category=business",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "business"

    def test_get_goal(self, client: TestClient, auth_headers: Dict[str, str], test_project: Project) -> None:
        """Test GET /api/v1/goals/{id}."""
        # Create goal
        create_response = client.post(
            "/api/v1/goals",
            json={
                "project_id": str(test_project.id),
                "title": "Test Goal",
            },
            headers=auth_headers,
        )
        goal_id = create_response.json()["id"]

        response = client.get(
            f"/api/v1/goals/{goal_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == goal_id
        assert data["title"] == "Test Goal"

    def test_get_goal_not_found(self, client: TestClient, auth_headers: Dict[str, str]) -> None:
        """Test getting non-existent goal."""
        from uuid import uuid4

        response = client.get(
            f"/api/v1/goals/{uuid4()}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_update_goal(self, client: TestClient, auth_headers: Dict[str, str], test_project: Project) -> None:
        """Test PUT /api/v1/goals/{id}."""
        # Create goal
        create_response = client.post(
            "/api/v1/goals",
            json={
                "project_id": str(test_project.id),
                "title": "Original Title",
            },
            headers=auth_headers,
        )
        goal_id = create_response.json()["id"]

        response = client.put(
            f"/api/v1/goals/{goal_id}",
            json={"title": "Updated Title"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    def test_delete_goal(self, client: TestClient, auth_headers: Dict[str, str], test_project: Project) -> None:
        """Test DELETE /api/v1/goals/{id}."""
        # Create goal
        create_response = client.post(
            "/api/v1/goals",
            json={
                "project_id": str(test_project.id),
                "title": "Goal to Delete",
            },
            headers=auth_headers,
        )
        goal_id = create_response.json()["id"]

        response = client.delete(
            f"/api/v1/goals/{goal_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(
            f"/api/v1/goals/{goal_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_analyze_goal(self, client: TestClient, auth_headers: Dict[str, str], test_project: Project) -> None:
        """Test POST /api/v1/goals/{id}/analyze."""
        # Create goal
        create_response = client.post(
            "/api/v1/goals",
            json={
                "project_id": str(test_project.id),
                "title": "Test Goal for Analysis",
            },
            headers=auth_headers,
        )
        goal_id = create_response.json()["id"]

        with patch(
            "backend.ai_agents.goal_analyst.GoalAnalystAgent.analyze_goal",
            new_callable=AsyncMock,
        ) as mock_analyze:
            mock_analyze.return_value = {
                "strengths": ["Clear"],
                "weaknesses": ["Vague"],
                "suggestions": ["Add metrics"],
            }

            response = client.post(
                f"/api/v1/goals/{goal_id}/analyze",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert "strengths" in data
            assert "weaknesses" in data

    @pytest.mark.asyncio
    async def test_decompose_goal(
        self, client: TestClient, auth_headers: Dict[str, str], test_project: Project
    ) -> None:
        """Test POST /api/v1/goals/{id}/decompose."""
        # Create goal
        create_response = client.post(
            "/api/v1/goals",
            json={
                "project_id": str(test_project.id),
                "title": "Complex Goal",
            },
            headers=auth_headers,
        )
        goal_id = create_response.json()["id"]

        with patch(
            "backend.ai_agents.goal_analyst.GoalAnalystAgent.suggest_subgoals",
            new_callable=AsyncMock,
        ) as mock_decompose:
            mock_decompose.return_value = {
                "subgoals": [
                    {"title": "Subgoal 1", "description": "First step"},
                    {"title": "Subgoal 2", "description": "Second step"},
                ],
                "reasoning": "Logical breakdown",
            }

            response = client.post(
                f"/api/v1/goals/{goal_id}/decompose",
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert "subgoals" in data
            assert len(data["subgoals"]) == 2

    def test_unauthorized_access(self, client: TestClient, test_project: Project) -> None:
        """Test accessing goals without authentication."""
        response = client.get(f"/api/v1/goals?project_id={test_project.id}")

        assert response.status_code == 401
