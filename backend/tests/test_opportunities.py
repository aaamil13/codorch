"""Tests for Opportunity Engine - Module 2."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from backend.modules.opportunities.scoring import OpportunityScorer


# Unit Tests - Scoring


def test_score_feasibility_high():
    """Test high feasibility scoring."""
    score = OpportunityScorer.score_feasibility(
        description="Well-defined opportunity with existing infrastructure and proven approach",
        estimated_effort="small",
        required_resources={"team": 2, "tools": "existing"},
    )
    assert score >= 7.0


def test_score_feasibility_low():
    """Test low feasibility scoring."""
    score = OpportunityScorer.score_feasibility(
        description=None, estimated_effort=None, required_resources=None
    )
    assert score <= 6.0


def test_score_impact_high():
    """Test high impact scoring."""
    score = OpportunityScorer.score_impact(
        description="Significant revenue growth opportunity with proven market demand",
        target_market="Large enterprise segment with 10M+ potential customers",
        value_proposition="Unique value that increases customer revenue by 30%",
    )
    assert score >= 7.0


def test_score_innovation_high():
    """Test high innovation scoring."""
    score = OpportunityScorer.score_innovation(
        description="Revolutionary AI-powered approach using cutting-edge technology",
        category="technology",
        value_proposition="First-of-its-kind solution leveraging novel algorithms",
    )
    assert score >= 7.0


def test_overall_scoring():
    """Test overall scoring calculation."""
    scores = OpportunityScorer.calculate_overall_score(
        description="Innovative AI platform for enterprise automation",
        category="technology",
        target_market="Enterprise clients",
        value_proposition="30% cost reduction through automation",
        estimated_effort="medium",
        required_resources={"team": 5, "budget": "100k"},
    )

    assert "feasibility_score" in scores
    assert "impact_score" in scores
    assert "innovation_score" in scores
    assert "resource_score" in scores
    assert "overall_score" in scores

    assert 0 <= scores["overall_score"] <= 10


# Integration Tests - API Endpoints


@pytest.mark.asyncio
async def test_create_opportunity(client: TestClient, auth_headers: dict, project_id: str):
    """Test opportunity creation."""
    response = client.post(
        f"/api/v1/opportunities/projects/{project_id}/opportunities",
        json={
            "title": "AI-Powered Analytics Platform",
            "description": "Build comprehensive analytics platform with AI insights",
            "category": "technology",
            "target_market": "Small to medium businesses",
            "value_proposition": "Actionable insights in real-time",
            "estimated_effort": "medium",
            "estimated_timeline": "6 months",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "AI-Powered Analytics Platform"
    assert data["score"] is not None
    assert data["feasibility_score"] is not None
    assert data["impact_score"] is not None
    assert data["status"] == "proposed"


@pytest.mark.asyncio
async def test_list_opportunities(client: TestClient, auth_headers: dict, project_id: str):
    """Test listing opportunities."""
    # Create test opportunity first
    client.post(
        f"/api/v1/opportunities/projects/{project_id}/opportunities",
        json={
            "title": "Test Opportunity",
            "description": "Test description",
            "category": "business",
            "estimated_effort": "small",
        },
        headers=auth_headers,
    )

    # List opportunities
    response = client.get(
        f"/api/v1/opportunities/projects/{project_id}/opportunities", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_opportunity(client: TestClient, auth_headers: dict, project_id: str):
    """Test getting single opportunity."""
    # Create opportunity
    create_response = client.post(
        f"/api/v1/opportunities/projects/{project_id}/opportunities",
        json={
            "title": "Test Opportunity",
            "description": "Test description",
            "category": "business",
        },
        headers=auth_headers,
    )
    opportunity_id = create_response.json()["id"]

    # Get opportunity
    response = client.get(
        f"/api/v1/opportunities/opportunities/{opportunity_id}", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == opportunity_id
    assert data["title"] == "Test Opportunity"


@pytest.mark.asyncio
async def test_update_opportunity(client: TestClient, auth_headers: dict, project_id: str):
    """Test updating opportunity."""
    # Create opportunity
    create_response = client.post(
        f"/api/v1/opportunities/projects/{project_id}/opportunities",
        json={
            "title": "Original Title",
            "description": "Original description",
            "category": "business",
        },
        headers=auth_headers,
    )
    opportunity_id = create_response.json()["id"]

    # Update opportunity
    response = client.put(
        f"/api/v1/opportunities/opportunities/{opportunity_id}",
        json={
            "title": "Updated Title",
            "status": "active",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_delete_opportunity(client: TestClient, auth_headers: dict, project_id: str):
    """Test deleting opportunity."""
    # Create opportunity
    create_response = client.post(
        f"/api/v1/opportunities/projects/{project_id}/opportunities",
        json={
            "title": "To Be Deleted",
            "description": "Test",
            "category": "business",
        },
        headers=auth_headers,
    )
    opportunity_id = create_response.json()["id"]

    # Delete opportunity
    response = client.delete(
        f"/api/v1/opportunities/opportunities/{opportunity_id}", headers=auth_headers
    )

    assert response.status_code == 204

    # Verify deleted
    get_response = client.get(
        f"/api/v1/opportunities/opportunities/{opportunity_id}", headers=auth_headers
    )
    assert get_response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.ai
async def test_generate_opportunities(client: TestClient, auth_headers: dict, project_id: str):
    """Test AI opportunity generation."""
    response = client.post(
        f"/api/v1/opportunities/projects/{project_id}/opportunities/generate",
        json={
            "context": "E-commerce platform for sustainable products",
            "num_opportunities": 3,
            "creativity_level": "balanced",
            "include_scoring": True,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "opportunities" in data
    assert "generation_metadata" in data
    assert isinstance(data["opportunities"], list)
    assert len(data["opportunities"]) > 0

    # Check opportunity structure
    opp = data["opportunities"][0]
    assert "title" in opp
    assert "description" in opp
    assert "category" in opp
    assert "target_market" in opp
    assert "value_proposition" in opp


@pytest.mark.asyncio
async def test_get_top_opportunities(client: TestClient, auth_headers: dict, project_id: str):
    """Test getting top opportunities."""
    # Create multiple opportunities with different scores
    for i in range(3):
        client.post(
            f"/api/v1/opportunities/projects/{project_id}/opportunities",
            json={
                "title": f"Opportunity {i}",
                "description": f"Description {i}" * 10,  # Longer = higher score
                "category": "business",
                "value_proposition": "Strong value" if i > 0 else "Value",
                "estimated_effort": "small" if i > 1 else "large",
            },
            headers=auth_headers,
        )

    response = client.get(
        f"/api/v1/opportunities/projects/{project_id}/opportunities/top?limit=2",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2

    # Verify sorted by score (descending)
    if len(data) > 1:
        assert data[0]["score"] >= data[1]["score"]


@pytest.mark.asyncio
async def test_compare_opportunities(client: TestClient, auth_headers: dict, project_id: str):
    """Test opportunity comparison."""
    # Create two opportunities
    opp1 = client.post(
        f"/api/v1/opportunities/projects/{project_id}/opportunities",
        json={
            "title": "High Impact Opportunity",
            "description": "Very promising opportunity with high potential",
            "category": "business",
            "value_proposition": "Significant value creation",
            "estimated_effort": "small",
        },
        headers=auth_headers,
    ).json()

    opp2 = client.post(
        f"/api/v1/opportunities/projects/{project_id}/opportunities",
        json={
            "title": "Low Impact Opportunity",
            "description": "Basic opportunity",
            "category": "business",
        },
        headers=auth_headers,
    ).json()

    # Compare
    response = client.post(
        "/api/v1/opportunities/opportunities/compare",
        json={"opportunity_ids": [opp1["id"], opp2["id"]]},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "opportunities" in data
    assert "winner" in data
    assert len(data["opportunities"]) == 2

    # Check ranking
    assert data["opportunities"][0]["rank"] == 1
    assert data["opportunities"][1]["rank"] == 2


@pytest.mark.asyncio
async def test_opportunity_not_found(client: TestClient, auth_headers: dict):
    """Test 404 for non-existent opportunity."""
    fake_id = str(uuid4())
    response = client.get(
        f"/api/v1/opportunities/opportunities/{fake_id}", headers=auth_headers
    )
    assert response.status_code == 404
