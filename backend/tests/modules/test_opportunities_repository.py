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
            project_id=test_project.id,
            title="AI Chatbot",
            description="Build AI-powered chatbot",
            category="product",
        )

        opp = opp_repo.create(opp_data)

        assert opp.id is not None
        assert opp.title == "AI Chatbot"
        assert opp.category == "product"
        assert opp.status == "proposed"

    def test_get_by_id(self, opp_repo, test_project):
        """Test getting opportunity by ID."""
        opp = opp_repo.create(
            OpportunityCreate(
                project_id=test_project.id,
                title="Test Opportunity",
            )
        )

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
                OpportunityCreate(
                    project_id=test_project.id,
                    title=f"Opportunity {i}",
                )
            )

        opps = opp_repo.get_by_project(test_project.id)

        assert len(opps) == 3
        assert all(o.project_id == test_project.id for o in opps)

    def test_get_by_project_with_filters(self, opp_repo, test_project):
        """Test filtering opportunities."""
        opp_repo.create(
            OpportunityCreate(
                project_id=test_project.id,
                title="Product Opp",
                category="product",
                ai_generated=True,
            )
        )
        opp_repo.create(
            OpportunityCreate(
                project_id=test_project.id,
                title="Market Opp",
                category="market",
                ai_generated=False,
            )
        )

        # Filter by category
        product_opps = opp_repo.get_by_project(
            test_project.id, category="product"
        )
        assert len(product_opps) == 1
        assert product_opps[0].category == "product"

        # Filter by AI generated
        ai_opps = opp_repo.get_by_project(
            test_project.id, ai_generated=True
        )
        assert len(ai_opps) == 1
        assert ai_opps[0].ai_generated is True

    def test_update_opportunity(self, opp_repo, test_project):
        """Test updating opportunity."""
        opp = opp_repo.create(
            OpportunityCreate(
                project_id=test_project.id,
                title="Original",
            )
        )

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
        opp = opp_repo.create(
            OpportunityCreate(
                project_id=test_project.id,
                title="To Delete",
            )
        )

        result = opp_repo.delete(opp.id)

        assert result is True
        assert opp_repo.get_by_id(opp.id) is None

    def test_get_top_ranked(self, opp_repo, test_project):
        """Test getting top-ranked opportunities."""
        # Create opportunities with scores
        opp_repo.create(
            OpportunityCreate(
                project_id=test_project.id,
                title="High Score",
                score=0.9,
            )
        )
        opp_repo.create(
            OpportunityCreate(
                project_id=test_project.id,
                title="Low Score",
                score=0.3,
            )
        )
        opp_repo.create(
            OpportunityCreate(
                project_id=test_project.id,
                title="Medium Score",
                score=0.6,
            )
        )

        top_opps = opp_repo.get_top_ranked(test_project.id, limit=2)

        assert len(top_opps) == 2
        assert top_opps[0].title == "High Score"
        assert top_opps[1].title == "Medium Score"
        # Verify sorted descending
        assert top_opps[0].score >= top_opps[1].score

    def test_count_by_category(self, opp_repo, test_project):
        """Test counting opportunities by category."""
        opp_repo.create(
            OpportunityCreate(
                project_id=test_project.id,
                title="Product 1",
                category="product",
            )
        )
        opp_repo.create(
            OpportunityCreate(
                project_id=test_project.id,
                title="Product 2",
                category="product",
            )
        )
        opp_repo.create(
            OpportunityCreate(
                project_id=test_project.id,
                title="Market 1",
                category="market",
            )
        )

        counts = opp_repo.count_by_category(test_project.id)

        assert counts["product"] == 2
        assert counts["market"] == 1

    def test_pagination(self, opp_repo, test_project):
        """Test pagination."""
        for i in range(10):
            opp_repo.create(
                OpportunityCreate(
                    project_id=test_project.id,
                    title=f"Opp {i}",
                )
            )

        page1 = opp_repo.get_by_project(test_project.id, skip=0, limit=5)
        page2 = opp_repo.get_by_project(test_project.id, skip=5, limit=5)

        assert len(page1) == 5
        assert len(page2) == 5

        # No overlap
        page1_ids = {o.id for o in page1}
        page2_ids = {o.id for o in page2}
        assert len(page1_ids & page2_ids) == 0
