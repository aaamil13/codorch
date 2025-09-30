"""Unit tests for Research Service."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.db.models import Project, User
from backend.modules.research.schemas import (
    ResearchFindingCreate,
    ResearchMessageCreate,
    ResearchSessionCreate,
)
from backend.modules.research.service import ResearchService


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
def research_service(db_session):
    """Create ResearchService."""
    return ResearchService(db_session)


class TestResearchService:
    """Test ResearchService methods."""

    def test_create_session(self, research_service, test_project, test_user):
        """Test creating research session."""
        data = ResearchSessionCreate(
            project_id=test_project.id,
            title="Test Research",
            description="Test session",
        )

        session = research_service.create_session(data, test_user)

        assert session.id is not None
        assert session.title == "Test Research"
        assert session.status == "active"
        assert session.created_by == test_user.id

    def test_get_session(self, research_service, test_project, test_user):
        """Test getting session."""
        data = ResearchSessionCreate(
            project_id=test_project.id,
            title="Test",
        )
        created = research_service.create_session(data, test_user)

        retrieved = research_service.get_session(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_list_sessions(self, research_service, test_project, test_user):
        """Test listing sessions."""
        for i in range(3):
            data = ResearchSessionCreate(
                project_id=test_project.id,
                title=f"Session {i}",
            )
            research_service.create_session(data, test_user)

        sessions = research_service.list_sessions(test_project.id)

        assert len(sessions) == 3

    def test_list_sessions_with_status_filter(self, research_service, test_project, test_user):
        """Test filtering sessions by status."""
        # Create active session
        data1 = ResearchSessionCreate(
            project_id=test_project.id,
            title="Active",
        )
        research_service.create_session(data1, test_user)

        # Create and archive another
        data2 = ResearchSessionCreate(
            project_id=test_project.id,
            title="Archived",
        )
        session2 = research_service.create_session(data2, test_user)
        research_service.archive_session(session2.id)

        active_sessions = research_service.list_sessions(test_project.id, status="active")

        assert len(active_sessions) == 1
        assert active_sessions[0].status == "active"

    def test_archive_session(self, research_service, test_project, test_user):
        """Test archiving session."""
        data = ResearchSessionCreate(
            project_id=test_project.id,
            title="To Archive",
        )
        session = research_service.create_session(data, test_user)

        archived = research_service.archive_session(session.id)

        assert archived is not None
        assert archived.status == "archived"

    def test_create_message(self, research_service, test_project, test_user):
        """Test creating message."""
        session_data = ResearchSessionCreate(
            project_id=test_project.id,
            title="Test",
        )
        session = research_service.create_session(session_data, test_user)

        message_data = ResearchMessageCreate(
            role="user",
            content="Test message",
        )

        message = research_service.create_message(session.id, message_data, metadata={"test": "data"})

        assert message.id is not None
        assert message.content == "Test message"
        assert message.message_metadata == {"test": "data"}

    def test_get_messages(self, research_service, test_project, test_user):
        """Test getting messages."""
        session_data = ResearchSessionCreate(
            project_id=test_project.id,
            title="Test",
        )
        session = research_service.create_session(session_data, test_user)

        for i in range(3):
            message_data = ResearchMessageCreate(
                role="user",
                content=f"Message {i}",
            )
            research_service.create_message(session.id, message_data)

        messages = research_service.get_messages(session.id)

        assert len(messages) == 3

    def test_create_finding(self, research_service, test_project, test_user):
        """Test creating finding."""
        session_data = ResearchSessionCreate(
            project_id=test_project.id,
            title="Test",
        )
        session = research_service.create_session(session_data, test_user)

        finding_data = ResearchFindingCreate(
            session_id=session.id,
            finding_type="technical",
            title="Test Finding",
            description="Test description",
            confidence_score=0.8,
        )

        finding = research_service.create_finding(finding_data)

        assert finding.id is not None
        assert finding.title == "Test Finding"
        assert finding.confidence_score == 0.8

    def test_list_findings(self, research_service, test_project, test_user):
        """Test listing findings."""
        session_data = ResearchSessionCreate(
            project_id=test_project.id,
            title="Test",
        )
        session = research_service.create_session(session_data, test_user)

        for i in range(3):
            finding_data = ResearchFindingCreate(
                session_id=session.id,
                finding_type="technical",
                title=f"Finding {i}",
                description="Test",
            )
            research_service.create_finding(finding_data)

        findings = research_service.list_findings(session.id)

        assert len(findings) == 3

    def test_get_high_confidence_findings(self, research_service, test_project, test_user):
        """Test getting high-confidence findings."""
        session_data = ResearchSessionCreate(
            project_id=test_project.id,
            title="Test",
        )
        session = research_service.create_session(session_data, test_user)

        # High confidence finding
        research_service.create_finding(
            ResearchFindingCreate(
                session_id=session.id,
                finding_type="technical",
                title="High",
                description="Test",
                confidence_score=0.9,
            )
        )

        # Low confidence finding
        research_service.create_finding(
            ResearchFindingCreate(
                session_id=session.id,
                finding_type="technical",
                title="Low",
                description="Test",
                confidence_score=0.3,
            )
        )

        high_findings = research_service.get_high_confidence_findings(session.id, min_confidence=0.7)

        assert len(high_findings) == 1
        assert high_findings[0].confidence_score >= 0.7

    def test_get_session_statistics(self, research_service, test_project, test_user):
        """Test getting session statistics."""
        session_data = ResearchSessionCreate(
            project_id=test_project.id,
            title="Test",
        )
        session = research_service.create_session(session_data, test_user)

        # Add messages
        for i in range(5):
            research_service.create_message(
                session.id,
                ResearchMessageCreate(role="user", content=f"Message {i}"),
            )

        # Add findings
        for i in range(3):
            research_service.create_finding(
                ResearchFindingCreate(
                    session_id=session.id,
                    finding_type="technical",
                    title=f"Finding {i}",
                    description="Test",
                )
            )

        stats = research_service.get_session_statistics(session.id)

        assert stats["message_count"] == 5
        assert stats["finding_count"] == 3
        assert "findings_by_type" in stats
