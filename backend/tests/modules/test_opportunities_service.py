"""Unit tests for Opportunities Service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Project, User
from backend.modules.opportunities.schemas import (
    OpportunityCreate,
    OpportunityGenerateRequest,
    OpportunityCompareRequest,
    OpportunityUpdate,
)
from backend.modules.opportunities.service import OpportunityService


@pytest.fixture
async def test_project(db_session: AsyncSession, test_user: User) -> Project:
    """Create test project."""
    project = Project(name="Test Project", description="Test", goal="Test Goal", owner_id=test_user.id)
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest.fixture
def opp_service(db_session: AsyncSession) -> OpportunityService:
    """Create OpportunityService instance."""
    return OpportunityService(db_session)


class TestOpportunityService:
    """Test OpportunityService methods."""

    @pytest.mark.asyncio
    async def test_create_opportunity_with_scoring(
        self, opp_service: OpportunityService, test_project: Project
    ) -> None:
        """Test creating opportunity with automatic scoring."""
        opp_data = OpportunityCreate(
            title="AI-powered analytics",
            description="Build analytics dashboard with AI insights",
            category="product",
        )

        opp = await opp_service.create_opportunity(test_project.id, opp_data)

        assert opp.id is not None
        assert opp.title == opp_data.title
        # Scores should be calculated
        assert opp.score is not None
        assert opp.feasibility_score is not None
        assert opp.impact_score is not None
        assert opp.innovation_score is not None
        assert opp.resource_score is not None

    @pytest.mark.asyncio
    async def test_get_opportunity(self, opp_service: OpportunityService, test_project: Project) -> None:
        """Test getting opportunity."""
        opp = await opp_service.create_opportunity(
            test_project.id,
            OpportunityCreate(
                title="Test Opportunity",
                description="Test",
                category="Test",
            ),
        )

        retrieved = await opp_service.get_opportunity(opp.id)

        assert retrieved is not None
        assert retrieved.id == opp.id

    @pytest.mark.asyncio
    async def test_list_opportunities(self, opp_service: OpportunityService, test_project: Project) -> None:
        """Test listing opportunities."""
        for i in range(3):
            await opp_service.create_opportunity(
                test_project.id,
                OpportunityCreate(
                    title=f"Opportunity {i}",
                    description="Test",
                    category="Test",
                ),
            )

        opps = await opp_service.list_opportunities(test_project.id)

        assert len(opps) == 3

    @pytest.mark.asyncio
    async def test_update_opportunity(self, opp_service: OpportunityService, test_project: Project) -> None:
        """Test updating opportunity."""
        opp = await opp_service.create_opportunity(
            test_project.id,
            OpportunityCreate(
                title="Original",
                description="Test",
                category="Test",
            ),
        )

        updated = await opp_service.update_opportunity(
            opp.id,
            OpportunityUpdate(title="Updated"),
        )

        assert updated is not None
        assert updated.title == "Updated"
        # Scores should be recalculated
        assert updated.score is not None

    @pytest.mark.asyncio
    async def test_delete_opportunity(self, opp_service: OpportunityService, test_project: Project) -> None:
        """Test deleting opportunity."""
        opp = await opp_service.create_opportunity(
            test_project.id,
            OpportunityCreate(
                title="To Delete",
                description="Test",
                category="Test",
            ),
        )

        await opp_service.delete_opportunity(opp.id)

        assert await opp_service.get_opportunity(opp.id) is None

    @pytest.mark.asyncio
    async def test_generate_opportunities(self, opp_service: OpportunityService, test_project: Project) -> None:
        """Test AI opportunity generation."""
        request = OpportunityGenerateRequest(
            context="SaaS platform for project management",
            num_opportunities=3,
            creativity_level="balanced",
            include_scoring=True,
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

            result = await opp_service.generate_opportunities(test_project.id, request)

            assert hasattr(result, "opportunities")
            assert len(result.opportunities) >= 2

    @pytest.mark.asyncio
    async def test_compare_opportunities(self, opp_service: OpportunityService, test_project: Project) -> None:
        """Test opportunity comparison."""
        # Create opportunities
        opp1 = await opp_service.create_opportunity(
            test_project.id,
            OpportunityCreate(
                title="Opportunity 1",
                description="Test",
                category="Test",
            ),
        )
        opp2 = await opp_service.create_opportunity(
            test_project.id,
            OpportunityCreate(
                title="Opportunity 2",
                description="Test",
                category="Test",
            ),
        )

        request = OpportunityCompareRequest(
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

            result = await opp_service.compare_opportunities(request.opportunity_ids)

            assert hasattr(result, "comparison")
            assert hasattr(result, "recommendation")

    @pytest.mark.asyncio
    async def test_get_top_opportunities(self, opp_service: OpportunityService, test_project: Project) -> None:
        """Test getting top-ranked opportunities."""
        # Create opportunities with different scores
        await opp_service.create_opportunity(
            test_project.id,
            OpportunityCreate(
                title="High",
                description="High impact opportunity with clear benefits",
                category="Test",
            ),
        )
        await opp_service.create_opportunity(
            test_project.id,
            OpportunityCreate(
                title="Low",
                description="Low priority",
                category="other",
            ),
        )

        top_opps = await opp_service.get_top_opportunities(test_project.id, limit=1)

        assert len(top_opps) >= 1

    @pytest.mark.asyncio
    async def test_scoring_calculation(self, opp_service: OpportunityService, test_project: Project) -> None:
        """Test scoring calculation logic."""
        # High-quality opportunity
        good_opp = await opp_service.create_opportunity(
            test_project.id,
            OpportunityCreate(
                title="Revolutionary AI Platform",
                description="Build cutting-edge AI platform with proven technology and clear market demand",
                category="product",
            ),
        )

        # Low-quality opportunity
        poor_opp = await opp_service.create_opportunity(
            test_project.id,
            OpportunityCreate(
                title="Something",
                description="Do something",
                category="other",
            ),
        )

        # Good opportunity should have higher score
        assert good_opp.score is not None
        assert poor_opp.score is not None
        assert good_opp.score > poor_opp.score
