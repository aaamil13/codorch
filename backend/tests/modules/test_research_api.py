"""Integration tests for Research API endpoints."""

import pytest
from unittest.mock import AsyncMock, patch

from backend.db.models import Project


@pytest.fixture
def test_project(db_session, test_user):
    """Create test project."""
    project = Project(
        name="Test Project",
        description="Test",
        status="active",
        created_by=test_user.id,
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


class TestResearchAPI:
    """Test Research API endpoints."""

    def test_create_session(self, client, auth_headers, test_project):
        """Test POST /api/v1/research/sessions."""
        response = client.post(
            "/api/v1/research/sessions",
            json={
                "project_id": str(test_project.id),
                "title": "Test Research",
                "description": "Test session",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Research"
        assert data["status"] == "active"
        assert "id" in data

    def test_list_sessions(self, client, auth_headers, test_project):
        """Test GET /api/v1/research/sessions."""
        # Create sessions
        for i in range(3):
            client.post(
                "/api/v1/research/sessions",
                json={
                    "project_id": str(test_project.id),
                    "title": f"Session {i}",
                },
                headers=auth_headers,
            )

        response = client.get(
            f"/api/v1/research/sessions?project_id={test_project.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_session(self, client, auth_headers, test_project):
        """Test GET /api/v1/research/sessions/{id}."""
        create_response = client.post(
            "/api/v1/research/sessions",
            json={
                "project_id": str(test_project.id),
                "title": "Test",
            },
            headers=auth_headers,
        )
        session_id = create_response.json()["id"]

        response = client.get(
            f"/api/v1/research/sessions/{session_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id

    def test_get_session_not_found(self, client, auth_headers):
        """Test getting non-existent session."""
        from uuid import uuid4

        response = client.get(
            f"/api/v1/research/sessions/{uuid4()}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_update_session(self, client, auth_headers, test_project):
        """Test PUT /api/v1/research/sessions/{id}."""
        create_response = client.post(
            "/api/v1/research/sessions",
            json={
                "project_id": str(test_project.id),
                "title": "Original",
            },
            headers=auth_headers,
        )
        session_id = create_response.json()["id"]

        response = client.put(
            f"/api/v1/research/sessions/{session_id}",
            json={"title": "Updated"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated"

    def test_delete_session(self, client, auth_headers, test_project):
        """Test DELETE /api/v1/research/sessions/{id}."""
        create_response = client.post(
            "/api/v1/research/sessions",
            json={
                "project_id": str(test_project.id),
                "title": "To Delete",
            },
            headers=auth_headers,
        )
        session_id = create_response.json()["id"]

        response = client.delete(
            f"/api/v1/research/sessions/{session_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

    def test_archive_session(self, client, auth_headers, test_project):
        """Test POST /api/v1/research/sessions/{id}/archive."""
        create_response = client.post(
            "/api/v1/research/sessions",
            json={
                "project_id": str(test_project.id),
                "title": "To Archive",
            },
            headers=auth_headers,
        )
        session_id = create_response.json()["id"]

        response = client.post(
            f"/api/v1/research/sessions/{session_id}/archive",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "archived"

    def test_get_messages(self, client, auth_headers, test_project):
        """Test GET /api/v1/research/sessions/{id}/messages."""
        create_response = client.post(
            "/api/v1/research/sessions",
            json={
                "project_id": str(test_project.id),
                "title": "Test",
            },
            headers=auth_headers,
        )
        session_id = create_response.json()["id"]

        response = client.get(
            f"/api/v1/research/sessions/{session_id}/messages",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_chat(self, client, auth_headers, test_project):
        """Test POST /api/v1/research/sessions/{id}/chat."""
        create_response = client.post(
            "/api/v1/research/sessions",
            json={
                "project_id": str(test_project.id),
                "title": "Chat Test",
            },
            headers=auth_headers,
        )
        session_id = create_response.json()["id"]

        with patch(
            "backend.ai_agents.research_team.ResearchTeam.conduct_research",
            new_callable=AsyncMock,
        ) as mock_research:
            mock_research.return_value = MagicMock(
                research_summary="Test summary",
                key_insights=["Insight 1", "Insight 2"],
                findings=[
                    {
                        "type": "technical",
                        "title": "Finding",
                        "description": "Test finding",
                        "confidence": 0.8,
                    }
                ],
                next_steps=["Step 1"],
                confidence=0.85,
            )

            response = client.post(
                f"/api/v1/research/sessions/{session_id}/chat",
                json={"message": "What are the best practices?"},
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert "content" in data
            assert "message_id" in data

    def test_get_findings(self, client, auth_headers, test_project):
        """Test GET /api/v1/research/sessions/{id}/findings."""
        create_response = client.post(
            "/api/v1/research/sessions",
            json={
                "project_id": str(test_project.id),
                "title": "Test",
            },
            headers=auth_headers,
        )
        session_id = create_response.json()["id"]

        response = client.get(
            f"/api/v1/research/sessions/{session_id}/findings",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_finding(self, client, auth_headers, test_project):
        """Test POST /api/v1/research/findings."""
        session_response = client.post(
            "/api/v1/research/sessions",
            json={
                "project_id": str(test_project.id),
                "title": "Test",
            },
            headers=auth_headers,
        )
        session_id = session_response.json()["id"]

        response = client.post(
            "/api/v1/research/findings",
            json={
                "session_id": session_id,
                "finding_type": "technical",
                "title": "Test Finding",
                "description": "Test description",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Finding"

    def test_get_finding(self, client, auth_headers, test_project):
        """Test GET /api/v1/research/findings/{id}."""
        session_response = client.post(
            "/api/v1/research/sessions",
            json={
                "project_id": str(test_project.id),
                "title": "Test",
            },
            headers=auth_headers,
        )
        session_id = session_response.json()["id"]

        create_response = client.post(
            "/api/v1/research/findings",
            json={
                "session_id": session_id,
                "finding_type": "technical",
                "title": "Test",
                "description": "Test",
            },
            headers=auth_headers,
        )
        finding_id = create_response.json()["id"]

        response = client.get(
            f"/api/v1/research/findings/{finding_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == finding_id

    def test_update_finding(self, client, auth_headers, test_project):
        """Test PUT /api/v1/research/findings/{id}."""
        session_response = client.post(
            "/api/v1/research/sessions",
            json={
                "project_id": str(test_project.id),
                "title": "Test",
            },
            headers=auth_headers,
        )
        session_id = session_response.json()["id"]

        create_response = client.post(
            "/api/v1/research/findings",
            json={
                "session_id": session_id,
                "finding_type": "technical",
                "title": "Original",
                "description": "Test",
            },
            headers=auth_headers,
        )
        finding_id = create_response.json()["id"]

        response = client.put(
            f"/api/v1/research/findings/{finding_id}",
            json={"title": "Updated"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated"

    def test_delete_finding(self, client, auth_headers, test_project):
        """Test DELETE /api/v1/research/findings/{id}."""
        session_response = client.post(
            "/api/v1/research/sessions",
            json={
                "project_id": str(test_project.id),
                "title": "Test",
            },
            headers=auth_headers,
        )
        session_id = session_response.json()["id"]

        create_response = client.post(
            "/api/v1/research/findings",
            json={
                "session_id": session_id,
                "finding_type": "technical",
                "title": "To Delete",
                "description": "Test",
            },
            headers=auth_headers,
        )
        finding_id = create_response.json()["id"]

        response = client.delete(
            f"/api/v1/research/findings/{finding_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

    def test_get_statistics(self, client, auth_headers, test_project):
        """Test GET /api/v1/research/sessions/{id}/statistics."""
        create_response = client.post(
            "/api/v1/research/sessions",
            json={
                "project_id": str(test_project.id),
                "title": "Test",
            },
            headers=auth_headers,
        )
        session_id = create_response.json()["id"]

        response = client.get(
            f"/api/v1/research/sessions/{session_id}/statistics",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "message_count" in data
        assert "finding_count" in data

    def test_unauthorized_access(self, client, test_project):
        """Test accessing without authentication."""
        response = client.get(f"/api/v1/research/sessions?project_id={test_project.id}")

        assert response.status_code == 401
