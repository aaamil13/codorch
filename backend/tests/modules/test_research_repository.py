"""Unit tests for Research Repository."""

import pytest
from uuid import uuid4

from backend.db.models import Project, ResearchSession, User
from backend.modules.research.repository import (
    ResearchSessionRepository,
    ResearchMessageRepository,
    ResearchFindingRepository,
)
from backend.modules.research.schemas import (
    ResearchFindingCreate,
    ResearchMessageCreate,
    ResearchSessionCreate,
)


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
def session_repo(db_session):
    """Create ResearchSessionRepository."""
    return ResearchSessionRepository(db_session)


@pytest.fixture
def message_repo(db_session):
    """Create ResearchMessageRepository."""
    return ResearchMessageRepository(db_session)


@pytest.fixture
def finding_repo(db_session):
    """Create ResearchFindingRepository."""
    return ResearchFindingRepository(db_session)


class TestResearchSessionRepository:
    """Test ResearchSessionRepository."""

    def test_create_session(self, session_repo, test_project, test_user):
        """Test creating research session."""
        session = ResearchSession(
            project_id=test_project.id,
            title="Test Research",
            description="Test session",
            created_by=test_user.id,
        )

        created = session_repo.create(session)

        assert created.id is not None
        assert created.title == "Test Research"
        assert created.status == "active"

    def test_get_by_id(self, session_repo, test_project, test_user):
        """Test getting session by ID."""
        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        created = session_repo.create(session)

        retrieved = session_repo.get_by_id(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_by_project(self, session_repo, test_project, test_user):
        """Test getting sessions by project."""
        for i in range(3):
            session = ResearchSession(
                project_id=test_project.id,
                title=f"Session {i}",
                created_by=test_user.id,
            )
            session_repo.create(session)

        sessions = session_repo.get_by_project(test_project.id)

        assert len(sessions) == 3
        assert all(s.project_id == test_project.id for s in sessions)

    def test_get_by_project_with_status_filter(
        self, session_repo, test_project, test_user
    ):
        """Test filtering sessions by status."""
        active_session = ResearchSession(
            project_id=test_project.id,
            title="Active",
            status="active",
            created_by=test_user.id,
        )
        archived_session = ResearchSession(
            project_id=test_project.id,
            title="Archived",
            status="archived",
            created_by=test_user.id,
        )
        session_repo.create(active_session)
        session_repo.create(archived_session)

        active_sessions = session_repo.get_by_project(
            test_project.id, status="active"
        )

        assert len(active_sessions) == 1
        assert active_sessions[0].status == "active"

    def test_update_session(self, session_repo, test_project, test_user):
        """Test updating session."""
        session = ResearchSession(
            project_id=test_project.id,
            title="Original",
            created_by=test_user.id,
        )
        created = session_repo.create(session)

        created.title = "Updated"
        updated = session_repo.update(created)

        assert updated.title == "Updated"

    def test_delete_session(self, session_repo, test_project, test_user):
        """Test deleting session."""
        session = ResearchSession(
            project_id=test_project.id,
            title="To Delete",
            created_by=test_user.id,
        )
        created = session_repo.create(session)

        session_repo.delete(created)

        assert session_repo.get_by_id(created.id) is None


class TestResearchMessageRepository:
    """Test ResearchMessageRepository."""

    def test_create_message(self, message_repo, session_repo, test_project, test_user):
        """Test creating message."""
        from backend.db.models import ResearchMessage

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = session_repo.create(session)

        message = ResearchMessage(
            session_id=session.id,
            role="user",
            content="Test message",
        )

        created = message_repo.create(message)

        assert created.id is not None
        assert created.content == "Test message"

    def test_get_by_session(self, message_repo, session_repo, test_project, test_user):
        """Test getting messages by session."""
        from backend.db.models import ResearchMessage

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = session_repo.create(session)

        for i in range(3):
            message = ResearchMessage(
                session_id=session.id,
                role="user",
                content=f"Message {i}",
            )
            message_repo.create(message)

        messages = message_repo.get_by_session(session.id)

        assert len(messages) == 3

    def test_get_latest_messages(
        self, message_repo, session_repo, test_project, test_user
    ):
        """Test getting latest messages."""
        from backend.db.models import ResearchMessage

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = session_repo.create(session)

        for i in range(10):
            message = ResearchMessage(
                session_id=session.id,
                role="user",
                content=f"Message {i}",
            )
            message_repo.create(message)

        latest = message_repo.get_latest_messages(session.id, limit=3)

        assert len(latest) == 3

    def test_count_by_session(
        self, message_repo, session_repo, test_project, test_user
    ):
        """Test counting messages."""
        from backend.db.models import ResearchMessage

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = session_repo.create(session)

        for i in range(5):
            message = ResearchMessage(
                session_id=session.id,
                role="user",
                content=f"Message {i}",
            )
            message_repo.create(message)

        count = message_repo.count_by_session(session.id)

        assert count == 5


class TestResearchFindingRepository:
    """Test ResearchFindingRepository."""

    def test_create_finding(
        self, finding_repo, session_repo, test_project, test_user
    ):
        """Test creating finding."""
        from backend.db.models import ResearchFinding

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = session_repo.create(session)

        finding = ResearchFinding(
            session_id=session.id,
            finding_type="technical",
            title="Test Finding",
            description="Test description",
        )

        created = finding_repo.create(finding)

        assert created.id is not None
        assert created.title == "Test Finding"

    def test_get_by_session(self, finding_repo, session_repo, test_project, test_user):
        """Test getting findings by session."""
        from backend.db.models import ResearchFinding

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = session_repo.create(session)

        for i in range(3):
            finding = ResearchFinding(
                session_id=session.id,
                finding_type="technical",
                title=f"Finding {i}",
                description="Test",
            )
            finding_repo.create(finding)

        findings = finding_repo.get_by_session(session.id)

        assert len(findings) == 3

    def test_get_by_session_with_type_filter(
        self, finding_repo, session_repo, test_project, test_user
    ):
        """Test filtering findings by type."""
        from backend.db.models import ResearchFinding

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = session_repo.create(session)

        technical = ResearchFinding(
            session_id=session.id,
            finding_type="technical",
            title="Technical",
            description="Test",
        )
        market = ResearchFinding(
            session_id=session.id,
            finding_type="market",
            title="Market",
            description="Test",
        )
        finding_repo.create(technical)
        finding_repo.create(market)

        technical_findings = finding_repo.get_by_session(
            session.id, finding_type="technical"
        )

        assert len(technical_findings) == 1
        assert technical_findings[0].finding_type == "technical"

    def test_get_high_confidence_findings(
        self, finding_repo, session_repo, test_project, test_user
    ):
        """Test getting high-confidence findings."""
        from backend.db.models import ResearchFinding

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = session_repo.create(session)

        high_conf = ResearchFinding(
            session_id=session.id,
            finding_type="technical",
            title="High Confidence",
            description="Test",
            confidence_score=0.9,
        )
        low_conf = ResearchFinding(
            session_id=session.id,
            finding_type="technical",
            title="Low Confidence",
            description="Test",
            confidence_score=0.3,
        )
        finding_repo.create(high_conf)
        finding_repo.create(low_conf)

        high_findings = finding_repo.get_high_confidence_findings(
            session.id, min_confidence=0.7
        )

        assert len(high_findings) == 1
        assert high_findings[0].confidence_score >= 0.7

    def test_count_by_type(self, finding_repo, session_repo, test_project, test_user):
        """Test counting findings by type."""
        from backend.db.models import ResearchFinding

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = session_repo.create(session)

        for i in range(2):
            finding = ResearchFinding(
                session_id=session.id,
                finding_type="technical",
                title=f"Technical {i}",
                description="Test",
            )
            finding_repo.create(finding)

        finding = ResearchFinding(
            session_id=session.id,
            finding_type="market",
            title="Market",
            description="Test",
        )
        finding_repo.create(finding)

        counts = finding_repo.count_by_type(session.id)

        assert counts["technical"] == 2
        assert counts["market"] == 1
