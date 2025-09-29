"""Tests for authentication."""

import pytest
from fastapi.testclient import TestClient

from backend.core.schemas import UserCreate


def test_register_user(client: TestClient, sample_user_data: dict[str, str]) -> None:
    """Test user registration."""
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 201

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == sample_user_data["email"]
    assert data["user"]["username"] == sample_user_data["username"]


def test_register_duplicate_email(client: TestClient, sample_user_data: dict[str, str]) -> None:
    """Test registration with duplicate email."""
    # Register first user
    client.post("/api/v1/auth/register", json=sample_user_data)

    # Try to register again with same email
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


def test_login(client: TestClient, sample_user_data: dict[str, str]) -> None:
    """Test user login."""
    # Register user
    client.post("/api/v1/auth/register", json=sample_user_data)

    # Login
    login_data = {"email": sample_user_data["email"], "password": sample_user_data["password"]}

    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient, sample_user_data: dict[str, str]) -> None:
    """Test login with invalid credentials."""
    # Register user
    client.post("/api/v1/auth/register", json=sample_user_data)

    # Try to login with wrong password
    login_data = {"email": sample_user_data["email"], "password": "wrongpassword"}

    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401


@pytest.mark.integration
def test_auth_flow(client: TestClient, sample_user_data: dict[str, str]) -> None:
    """Test complete authentication flow."""
    # Register
    register_response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert register_response.status_code == 201
    token = register_response.json()["access_token"]

    # Get current user
    headers = {"Authorization": f"Bearer {token}"}
    user_response = client.get("/api/v1/users/me", headers=headers)
    assert user_response.status_code == 200
    assert user_response.json()["email"] == sample_user_data["email"]
