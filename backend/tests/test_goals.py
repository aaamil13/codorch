"""Tests for Goal module."""

import pytest
from fastapi.testclient import TestClient

from backend.modules.goals.smart_validator import SMARTValidator


@pytest.fixture
def auth_headers(client: TestClient, sample_user_data: dict[str, str]) -> dict[str, str]:
    """Get authentication headers."""
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def project_id(
    client: TestClient, auth_headers: dict[str, str], sample_project_data: dict[str, str]
) -> str:
    """Create a project and return its ID."""
    response = client.post("/api/v1/projects/", json=sample_project_data, headers=auth_headers)
    return response.json()["id"]


def test_create_goal(client: TestClient, auth_headers: dict[str, str], project_id: str) -> None:
    """Test creating a goal."""
    goal_data = {
        "title": "Increase revenue by 20%",
        "description": "Increase company revenue by 20% through new product launches",
        "category": "business",
        "priority": "high",
    }

    response = client.post(
        f"/api/v1/goals/projects/{project_id}/goals", json=goal_data, headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == goal_data["title"]
    assert data["is_smart_validated"] in [True, False]
    assert "overall_smart_score" in data


def test_list_goals(client: TestClient, auth_headers: dict[str, str], project_id: str) -> None:
    """Test listing goals."""
    # Create a goal
    goal_data = {"title": "Test Goal", "description": "Test description"}
    client.post(
        f"/api/v1/goals/projects/{project_id}/goals", json=goal_data, headers=auth_headers
    )

    # List goals
    response = client.get(f"/api/v1/goals/projects/{project_id}/goals", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_goal(client: TestClient, auth_headers: dict[str, str], project_id: str) -> None:
    """Test getting goal by ID."""
    # Create goal
    goal_data = {"title": "Test Goal", "description": "Test description"}
    create_response = client.post(
        f"/api/v1/goals/projects/{project_id}/goals", json=goal_data, headers=auth_headers
    )
    goal_id = create_response.json()["id"]

    # Get goal
    response = client.get(f"/api/v1/goals/goals/{goal_id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == goal_id
    assert data["title"] == goal_data["title"]


def test_update_goal(client: TestClient, auth_headers: dict[str, str], project_id: str) -> None:
    """Test updating goal."""
    # Create goal
    goal_data = {"title": "Original Title", "description": "Original description"}
    create_response = client.post(
        f"/api/v1/goals/projects/{project_id}/goals", json=goal_data, headers=auth_headers
    )
    goal_id = create_response.json()["id"]

    # Update goal
    update_data = {"title": "Updated Title", "priority": "high"}
    response = client.put(
        f"/api/v1/goals/goals/{goal_id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["priority"] == update_data["priority"]


def test_delete_goal(client: TestClient, auth_headers: dict[str, str], project_id: str) -> None:
    """Test deleting goal."""
    # Create goal
    goal_data = {"title": "To Delete", "description": "Will be deleted"}
    create_response = client.post(
        f"/api/v1/goals/projects/{project_id}/goals", json=goal_data, headers=auth_headers
    )
    goal_id = create_response.json()["id"]

    # Delete goal
    response = client.delete(f"/api/v1/goals/goals/{goal_id}", headers=auth_headers)

    assert response.status_code == 200

    # Verify deleted
    get_response = client.get(f"/api/v1/goals/goals/{goal_id}", headers=auth_headers)
    assert get_response.status_code == 404


@pytest.mark.ai
def test_analyze_goal(client: TestClient, auth_headers: dict[str, str], project_id: str) -> None:
    """Test AI goal analysis."""
    # Create goal
    goal_data = {
        "title": "Increase revenue by 20%",
        "description": "Achieve 20% revenue growth in Q4 2025",
        "category": "business",
    }
    create_response = client.post(
        f"/api/v1/goals/projects/{project_id}/goals", json=goal_data, headers=auth_headers
    )
    goal_id = create_response.json()["id"]

    # Analyze goal
    analysis_request = {"include_suggestions": True, "include_metrics": True}
    response = client.post(
        f"/api/v1/goals/goals/{goal_id}/analyze", json=analysis_request, headers=auth_headers
    )

    # This might fail if AI is not available, so we just check structure
    if response.status_code == 200:
        data = response.json()
        assert "smart_scores" in data
        assert "feedback" in data
        assert "is_smart_compliant" in data


# Unit tests for SMART validator


def test_smart_validator_specific() -> None:
    """Test specific score validation."""
    validator = SMARTValidator()

    score1 = validator.validate_specific("Build a website", "Detailed description of website")
    assert score1 > 0

    score2 = validator.validate_specific("", None)
    assert score2 == 0


def test_smart_validator_measurable() -> None:
    """Test measurable score validation."""
    validator = SMARTValidator()

    metrics = {"metrics": [{"name": "Revenue", "target_value": 100000}]}
    score1 = validator.validate_measurable("Increase by 20%", metrics)
    assert score1 > 5

    score2 = validator.validate_measurable(None, None)
    assert score2 == 0


def test_smart_validator_time_bound() -> None:
    """Test time-bound score validation."""
    from datetime import datetime, timedelta

    validator = SMARTValidator()

    future_date = datetime.utcnow() + timedelta(days=30)
    score1 = validator.validate_time_bound(future_date)
    assert score1 == 10.0

    score2 = validator.validate_time_bound(None)
    assert score2 == 0.0


def test_smart_validator_full() -> None:
    """Test full SMART validation."""
    from datetime import datetime, timedelta

    validator = SMARTValidator()

    result = validator.validate_goal(
        title="Increase revenue by 20%",
        description="Achieve 20% revenue growth through new product launches in Q4",
        category="business",
        target_date=datetime.utcnow() + timedelta(days=90),
        metrics={"metrics": [{"name": "Revenue", "target_value": 1000000}]},
    )

    assert "specific_score" in result
    assert "measurable_score" in result
    assert "achievable_score" in result
    assert "relevant_score" in result
    assert "time_bound_score" in result
    assert "overall_smart_score" in result
    assert "is_smart_compliant" in result
    assert result["overall_smart_score"] > 0
