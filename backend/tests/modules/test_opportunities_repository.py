"""Unit tests for Opportunities Repository."""

import pytest
from uuid import uuid4

from backend.db.models import Opportunity, Project, User
from backend.modules.opportunities.repository import OpportunityRepository
from backend.modules.opportunities.schemas import OpportunityCreate, OpportunityUpdate


@pytest.fixture
def test_project(db_session, test_user: User):
    """Create a test project."""
    project = Project(
        name="Test Project for Opportunities",
        description="Test project",
        status="active",
        created_by=test_user.id,
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@pytest.fixture
def opp_repo(db_session):
    """Create OpportunityRepository instance."""
    return OpportunityRepository(db_session)


class TestOpportunityRepository:
    """Test OpportunityRepository methods."""

    def test_create_opportunity(self, opp_repo, test_project):
        """Test creating an opportunity."""
        opp_data = OpportunityCreate(
            title="AI Chatbot",
            description="Build AI-powered chatbot",
            category="product",
        )

        opp = opp_repo.create(opp_data, test_project.id)

        assert opp.id is not None
        assert opp.title == "AI Chatbot"
        assert opp.category == "product"
        assert opp.status == "proposed"

    def test_get_by_id(self, opp_repo, test_project):
        """Test getting opportunity by ID."""
        opp_data = OpportunityCreate(title="Test Opportunity")
        opp = opp_repo.create(opp_data, test_project.id)

        retrieved = opp_repo.get_by_id(opp.id)

        assert retrieved is not None
        assert retrieved.id == opp.id

    def test_get_by_id_not_found(self, opp_repo):
        """Test getting non-existent opportunity."""
        opp = opp_repo.get_by_id(uuid4())
        assert opp is None

    def test_get_by_project(self, opp_repo, test_project):
        """Test getting opportunities by project."""
        for i in range(3):
            opp_repo.create(
                OpportunityCreate(title=f"Opportunity {i}"),
                test_project.id
            )

        opps = opp_repo.get_by_project(test_project.id)

        assert len(opps) == 3
        assert all(o.project_id == test_project.id for o in opps)

    def test_get_by_project_with_filters(self, opp_repo, test_project):
        """Test filtering opportunities."""
        opp1_data = OpportunityCreate(title="Product Opp", category="product")
        opp1 = opp_repo.create(opp1_data, test_project.id)
        opp1.ai_generated = True # Manually set for testing filter

        opp2_data = OpportunityCreate(title="Market Opp", category="market")
        opp2 = opp_repo.create(opp2_data, test_project.id)
        opp2.ai_generated = False

        # Filter by category
        product_opps = opp_repo.get_by_project(test_project.id, category="product")
        assert len(product_opps) == 1
        assert product_opps[0].category == "product"

        # Filter by AI generated
        ai_opps = opp_repo.get_by_project(test_project.id, ai_generated=True)
        assert len(ai_opps) == 1
        assert ai_opps[0].ai_generated is True

    def test_update_opportunity(self, opp_repo, test_project):
        """Test updating opportunity."""
        opp_data = OpportunityCreate(title="Original")
        opp = opp_repo.create(opp_data, test_project.id)

        updated = opp_repo.update(
            opp.id,
            OpportunityUpdate(
                title="Updated",
                description="New description",
            ),
        )

        assert updated is not None
        assert updated.title == "Updated"
        assert updated.description == "New description"

    def test_delete_opportunity(self, opp_repo, test_project):
        """Test deleting opportunity."""
        opp_data = OpportunityCreate(title="To Delete")
        opp = opp_repo.create(opp_data, test_project.id)

        result = opp_repo.delete(opp.id)

        assert result is True
        assert opp_repo.get_by_id(opp.id) is None

    def test_get_top_ranked(self, opp_repo, test_project):
        """Test getting top-ranked opportunities."""
        # Create opportunities with scores
        opp1 = opp_repo.create(OpportunityCreate(title="High Score"), test_project.id)
        opp1.score = 0.9
        opp2 = opp_repo.create(OpportunityCreate(title="Low Score"), test_project.id)
        opp2.score = 0.3
        opp3 = opp_repo.create(OpportunityCreate(title="Medium Score"), test_project.id)
        opp3.score = 0.6

        top_opps = opp_repo.get_top_ranked(test_project.id, limit=2)

        assert len(top_opps) == 2
        assert top_opps[0].title == "High Score"
        assert top_opps[1].title == "Medium Score"
        # Verify sorted descending
        assert top_opps[0].score >= top_opps[1].score

    def test_count_by_category(self, opp_repo, test_project):
        """Test counting opportunities by category."""
        opp_repo.create(
            OpportunityCreate(title="Product 1", category="product"),
            test_project.id
        )
        opp_repo.create(
            OpportunityCreate(title="Product 2", category="product"),
            test_project.id
        )
        opp_repo.create(
            OpportunityCreate(title="Market 1", category="market"),
            test_project.id
        )

        counts = opp_repo.count_by_category(test_project.id)

        assert counts["product"] == 2
        assert counts["market"] == 1

    def test_pagination(self, opp_repo, test_project):
        """Test pagination."""
        for i in range(10):
            opp_repo.create(
                OpportunityCreate(title=f"Opp {i}"),
                test_project.id
            )

        page1 = opp_repo.get_by_project(test_project.id, skip=0, limit=5)
        page2 = opp_repo.get_by_project(test_project.id, skip=5, limit=5)

        assert len(page1) == 5
        assert len(page2) == 5

        # No overlap
        page1_ids = {o.id for o in page1}
        page2_ids = {o.id for o in page2}
        assert len(page1_ids & page2_ids) == 0
