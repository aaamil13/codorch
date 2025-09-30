"""Unit tests for Opportunities Service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from backend.db.models import Project, User
from backend.modules.opportunities.schemas import (
    OpportunityCreate,
    OpportunityGenerateRequest,
    OpportunityComparisonRequest,
)
from backend.modules.opportunities.service import OpportunityService


@pytest.fixture
def test_project(db_session, test_user: User):
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


@pytest.fixture
def opp_service(db_session):
    """Create OpportunityService instance."""
    return OpportunityService(db_session)


class TestOpportunityService:
    """Test OpportunityService methods."""

    def test_create_opportunity_with_scoring(self, opp_service, test_project):
        """Test creating opportunity with automatic scoring."""
        opp_data = OpportunityCreate(
            project_id=test_project.id,
            title="AI-powered analytics",
            description="Build analytics dashboard with AI insights",
            category="product",
        )

        opp = opp_service.create_opportunity(opp_data)

        assert opp.id is not None
        assert opp.title == opp_data.title
        # Scores should be calculated
        assert opp.score is not None
        assert opp.feasibility_score is not None
        assert opp.impact_score is not None
        assert opp.innovation_score is not None
        assert opp.resource_score is not None

    def test_get_opportunity(self, opp_service, test_project):
        """Test getting opportunity."""
        opp = opp_service.create_opportunity(
            OpportunityCreate(
                project_id=test_project.id,
                title="Test Opportunity",
            )
        )

        retrieved = opp_service.get_opportunity(opp.id)

        assert retrieved is not None
        assert retrieved.id == opp.id

    def test_list_opportunities(self, opp_service, test_project):
        """Test listing opportunities."""
        for i in range(3):
            opp_service.create_opportunity(
                OpportunityCreate(
                    project_id=test_project.id,
                    title=f"Opportunity {i}",
                )
            )

        opps = opp_service.list_opportunities(test_project.id)

        assert len(opps) == 3

    def test_update_opportunity(self, opp_service, test_project):
        """Test updating opportunity."""
        opp = opp_service.create_opportunity(
            OpportunityCreate(
                project_id=test_project.id,
                title="Original",
            )
        )

        from backend.modules.opportunities.schemas import OpportunityUpdate

        updated = opp_service.update_opportunity(
            opp.id,
            OpportunityUpdate(title="Updated"),
        )

        assert updated is not None
        assert updated.title == "Updated"
        # Scores should be recalculated
        assert updated.score is not None

    def test_delete_opportunity(self, opp_service, test_project):
        """Test deleting opportunity."""
        opp = opp_service.create_opportunity(
            OpportunityCreate(
                project_id=test_project.id,
                title="To Delete",
            )
        )

        result = opp_service.delete_opportunity(opp.id)

        assert result is True
        assert opp_service.get_opportunity(opp.id) is None

    @pytest.mark.asyncio
    async def test_generate_opportunities(self, opp_service, test_project):
        """Test AI opportunity generation."""
        request = OpportunityGenerateRequest(
            project_id=test_project.id,
            context="SaaS platform for project management",
            count=3,
        )

        with patch("backend.modules.opportunities.service.OpportunityTeam") as mock_team_class:
            mock_team = MagicMock()
            mock_team.generate_opportunities = AsyncMock(
                return_value={
                    "opportunities": [
                        {
                            "title": "Mobile app",
                            "description": "Native mobile application",
                            "category": "product",
                        },
                        {
                            "title": "AI features",
                            "description": "Smart automation",
                            "category": "feature",
                        },
                    ],
                    "reasoning": "Based on market analysis",
                }
            )
            mock_team_class.return_value = mock_team

            result = await opp_service.generate_opportunities(request)

            assert "opportunities" in result
            assert len(result["opportunities"]) >= 2

    @pytest.mark.asyncio
    async def test_compare_opportunities(self, opp_service, test_project):
        """Test opportunity comparison."""
        # Create opportunities
        opp1 = opp_service.create_opportunity(
            OpportunityCreate(
                project_id=test_project.id,
                title="Opportunity 1",
            )
        )
        opp2 = opp_service.create_opportunity(
            OpportunityCreate(
                project_id=test_project.id,
                title="Opportunity 2",
            )
        )

        request = OpportunityComparisonRequest(
            opportunity_ids=[opp1.id, opp2.id],
        )

        with patch("backend.modules.opportunities.service.OpportunityTeam") as mock_team_class:
            mock_team = MagicMock()
            mock_team.compare_opportunities = AsyncMock(
                return_value={
                    "comparison": {
                        "winner": str(opp1.id),
                        "strengths": {"opp1": ["Better"], "opp2": ["Good"]},
                    },
                    "recommendation": "Choose opportunity 1",
                }
            )
            mock_team_class.return_value = mock_team

            result = await opp_service.compare_opportunities(request)

            assert "comparison" in result
            assert "recommendation" in result

    def test_get_top_opportunities(self, opp_service, test_project):
        """Test getting top-ranked opportunities."""
        # Create opportunities with different scores
        opp_service.create_opportunity(
            OpportunityCreate(
                project_id=test_project.id,
                title="High",
                description="High impact opportunity with clear benefits",
            )
        )
        opp_service.create_opportunity(
            OpportunityCreate(
                project_id=test_project.id,
                title="Low",
                description="Low priority",
            )
        )

        top_opps = opp_service.get_top_opportunities(test_project.id, limit=1)

        assert len(top_opps) >= 1

    def test_scoring_calculation(self, opp_service, test_project):
        """Test scoring calculation logic."""
        # High-quality opportunity
        good_opp = opp_service.create_opportunity(
            OpportunityCreate(
                project_id=test_project.id,
                title="Revolutionary AI Platform",
                description="Build cutting-edge AI platform with proven technology and clear market demand",
                category="product",
                target_market="Enterprise B2B",
                value_proposition="Reduce costs by 50%",
            )
        )

        # Low-quality opportunity
        poor_opp = opp_service.create_opportunity(
            OpportunityCreate(
                project_id=test_project.id,
                title="Something",
                description="Do something",
                category="other",
            )
        )

        # Good opportunity should have higher score
        assert good_opp.score > poor_opp.score
