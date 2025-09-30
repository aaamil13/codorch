"""Integration tests for Opportunities API endpoints."""

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


class TestOpportunitiesAPI:
    """Test Opportunities API endpoints."""

    def test_create_opportunity(self, client, auth_headers, test_project):
        """Test POST /api/v1/opportunities."""
        response = client.post(
            "/api/v1/opportunities",
            json={
                "project_id": str(test_project.id),
                "title": "AI Chatbot",
                "description": "Build intelligent chatbot",
                "category": "product",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "AI Chatbot"
        assert "score" in data
        assert "id" in data

    def test_create_opportunity_missing_fields(self, client, auth_headers):
        """Test creating opportunity without required fields."""
        response = client.post(
            "/api/v1/opportunities",
            json={
                # Missing project_id and title
                "description": "Test",
            },
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_list_opportunities(self, client, auth_headers, test_project):
        """Test GET /api/v1/opportunities."""
        # Create opportunities
        for i in range(3):
            client.post(
                "/api/v1/opportunities",
                json={
                    "project_id": str(test_project.id),
                    "title": f"Opportunity {i}",
                },
                headers=auth_headers,
            )

        response = client.get(
            f"/api/v1/opportunities?project_id={test_project.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_opportunities_with_filters(self, client, auth_headers, test_project):
        """Test filtering opportunities."""
        client.post(
            "/api/v1/opportunities",
            json={
                "project_id": str(test_project.id),
                "title": "Product Opp",
                "category": "product",
            },
            headers=auth_headers,
        )
        client.post(
            "/api/v1/opportunities",
            json={
                "project_id": str(test_project.id),
                "title": "Market Opp",
                "category": "market",
            },
            headers=auth_headers,
        )

        response = client.get(
            f"/api/v1/opportunities?project_id={test_project.id}&category=product",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "product"

    def test_get_opportunity(self, client, auth_headers, test_project):
        """Test GET /api/v1/opportunities/{id}."""
        create_response = client.post(
            "/api/v1/opportunities",
            json={
                "project_id": str(test_project.id),
                "title": "Test Opportunity",
            },
            headers=auth_headers,
        )
        opp_id = create_response.json()["id"]

        response = client.get(
            f"/api/v1/opportunities/{opp_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == opp_id

    def test_get_opportunity_not_found(self, client, auth_headers):
        """Test getting non-existent opportunity."""
        from uuid import uuid4

        response = client.get(
            f"/api/v1/opportunities/{uuid4()}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_update_opportunity(self, client, auth_headers, test_project):
        """Test PUT /api/v1/opportunities/{id}."""
        create_response = client.post(
            "/api/v1/opportunities",
            json={
                "project_id": str(test_project.id),
                "title": "Original",
            },
            headers=auth_headers,
        )
        opp_id = create_response.json()["id"]

        response = client.put(
            f"/api/v1/opportunities/{opp_id}",
            json={"title": "Updated"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated"

    def test_delete_opportunity(self, client, auth_headers, test_project):
        """Test DELETE /api/v1/opportunities/{id}."""
        create_response = client.post(
            "/api/v1/opportunities",
            json={
                "project_id": str(test_project.id),
                "title": "To Delete",
            },
            headers=auth_headers,
        )
        opp_id = create_response.json()["id"]

        response = client.delete(
            f"/api/v1/opportunities/{opp_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(
            f"/api/v1/opportunities/{opp_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_generate_opportunities(self, client, auth_headers, test_project):
        """Test POST /api/v1/opportunities/generate."""
        with patch(
            "backend.ai_agents.opportunity_team.SupervisorAgent.generate_opportunities",
            new_callable=AsyncMock,
        ) as mock_generate:
            mock_generate.return_value = {
                "opportunities": [
                    {
                        "title": "AI Feature",
                        "description": "Add AI capabilities",
                        "category": "feature",
                    }
                ],
                "reasoning": "Market demand",
            }

            response = client.post(
                "/api/v1/opportunities/generate",
                json={
                    "project_id": str(test_project.id),
                    "context": "SaaS platform",
                    "count": 3,
                },
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert "opportunities" in data

    @pytest.mark.asyncio
    async def test_compare_opportunities(self, client, auth_headers, test_project):
        """Test POST /api/v1/opportunities/compare."""
        # Create opportunities
        opp1_response = client.post(
            "/api/v1/opportunities",
            json={
                "project_id": str(test_project.id),
                "title": "Opportunity 1",
            },
            headers=auth_headers,
        )
        opp2_response = client.post(
            "/api/v1/opportunities",
            json={
                "project_id": str(test_project.id),
                "title": "Opportunity 2",
            },
            headers=auth_headers,
        )

        opp1_id = opp1_response.json()["id"]
        opp2_id = opp2_response.json()["id"]

        with patch(
            "backend.ai_agents.opportunity_team.SupervisorAgent.compare_opportunities",
            new_callable=AsyncMock,
        ) as mock_compare:
            mock_compare.return_value = {
                "comparison": {"winner": opp1_id},
                "recommendation": "Choose first",
            }

            response = client.post(
                "/api/v1/opportunities/compare",
                json={
                    "opportunity_ids": [opp1_id, opp2_id],
                },
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert "comparison" in data

    def test_get_top_opportunities(self, client, auth_headers, test_project):
        """Test GET /api/v1/opportunities/top."""
        # Create opportunities
        for i in range(5):
            client.post(
                "/api/v1/opportunities",
                json={
                    "project_id": str(test_project.id),
                    "title": f"Opportunity {i}",
                },
                headers=auth_headers,
            )

        response = client.get(
            f"/api/v1/opportunities/top?project_id={test_project.id}&limit=3",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    def test_unauthorized_access(self, client, test_project):
        """Test accessing without authentication."""
        response = client.get(f"/api/v1/opportunities?project_id={test_project.id}")

        assert response.status_code == 401
