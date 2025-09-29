"""Tests for project endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def auth_headers(client: TestClient, sample_user_data: dict[str, str]) -> dict[str, str]:
    """Get authentication headers for tests."""
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_project(
    client: TestClient, auth_headers: dict[str, str], sample_project_data: dict[str, str]
) -> None:
    """Test project creation."""
    response = client.post("/api/v1/projects/", json=sample_project_data, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_project_data["name"]
    assert data["goal"] == sample_project_data["goal"]
    assert "id" in data


def test_list_projects(
    client: TestClient, auth_headers: dict[str, str], sample_project_data: dict[str, str]
) -> None:
    """Test listing projects."""
    # Create a project
    client.post("/api/v1/projects/", json=sample_project_data, headers=auth_headers)

    # List projects
    response = client.get("/api/v1/projects/", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_project(
    client: TestClient, auth_headers: dict[str, str], sample_project_data: dict[str, str]
) -> None:
    """Test getting project by ID."""
    # Create project
    create_response = client.post(
        "/api/v1/projects/", json=sample_project_data, headers=auth_headers
    )
    project_id = create_response.json()["id"]

    # Get project
    response = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == sample_project_data["name"]


def test_update_project(
    client: TestClient, auth_headers: dict[str, str], sample_project_data: dict[str, str]
) -> None:
    """Test updating project."""
    # Create project
    create_response = client.post(
        "/api/v1/projects/", json=sample_project_data, headers=auth_headers
    )
    project_id = create_response.json()["id"]

    # Update project
    update_data = {"name": "Updated Project Name"}
    response = client.put(
        f"/api/v1/projects/{project_id}", json=update_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]


def test_delete_project(
    client: TestClient, auth_headers: dict[str, str], sample_project_data: dict[str, str]
) -> None:
    """Test deleting project."""
    # Create project
    create_response = client.post(
        "/api/v1/projects/", json=sample_project_data, headers=auth_headers
    )
    project_id = create_response.json()["id"]

    # Delete project
    response = client.delete(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert response.status_code == 200

    # Verify project is deleted
    get_response = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_unauthorized_access(client: TestClient, sample_project_data: dict[str, str]) -> None:
    """Test that unauthorized users cannot access projects."""
    response = client.get("/api/v1/projects/")
    assert response.status_code == 403  # Forbidden - no auth header
