"""Tests for main application."""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient) -> None:
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Codorch API"
    assert "version" in data
    assert data["tagline"] == "Orchestrating Ideas into Reality"


def test_health_endpoint(client: TestClient) -> None:
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_api_v1_health_endpoint(client: TestClient) -> None:
    """Test API v1 health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["api_version"] == "v1"
    assert "version" in data


@pytest.mark.integration
def test_cors_headers(client: TestClient) -> None:
    """Test CORS headers are present."""
    response = client.options("/", headers={"Origin": "http://localhost:9000"})
    assert response.status_code == 200
