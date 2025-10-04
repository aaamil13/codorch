"""Unit tests for Research Repository."""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

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
async def test_project(db_session: AsyncSession, test_user: User) -> Project:
    """Create test project."""
    project = Project(
        name="Test Project",
        description="Test",
        status="active",
        created_by=test_user.id,
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project


@pytest.fixture
def session_repo(db_session: AsyncSession) -> ResearchSessionRepository:
    """Create ResearchSessionRepository."""
    return ResearchSessionRepository(db_session)


@pytest.fixture
def message_repo(db_session: AsyncSession) -> ResearchMessageRepository:
    """Create ResearchMessageRepository."""
    return ResearchMessageRepository(db_session)


@pytest.fixture
def finding_repo(db_session: AsyncSession) -> ResearchFindingRepository:
    """Create ResearchFindingRepository."""
    return ResearchFindingRepository(db_session)


class TestResearchSessionRepository:
    """Test ResearchSessionRepository."""

    @pytest.mark.asyncio
    async def test_create_session(self, session_repo: ResearchSessionRepository, test_project: Project, test_user: User) -> None:
        """Test creating research session."""
        session = ResearchSession(
            project_id=test_project.id,
            title="Test Research",
            description="Test session",
            created_by=test_user.id,
        )

        created = await session_repo.create(session)

        assert created.id is not None
        assert created.title == "Test Research"
        assert created.status == "active"

    @pytest.mark.asyncio
    async def test_get_by_id(self, session_repo: ResearchSessionRepository, test_project: Project, test_user: User) -> None:
        """Test getting session by ID."""
        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        created = await session_repo.create(session)

        retrieved = await session_repo.get_by_id(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    @pytest.mark.asyncio
    async def test_get_by_project(self, session_repo: ResearchSessionRepository, test_project: Project, test_user: User) -> None:
        """Test getting sessions by project."""
        for i in range(3):
            session = ResearchSession(
                project_id=test_project.id,
                title=f"Session {i}",
                created_by=test_user.id,
            )
            await session_repo.create(session)

        sessions = await session_repo.get_by_project(test_project.id)

        assert len(sessions) == 3
        assert all(s.project_id == test_project.id for s in sessions)

    @pytest.mark.asyncio
    async def test_get_by_project_with_status_filter(self, session_repo: ResearchSessionRepository, test_project: Project, test_user: User) -> None:
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
        await session_repo.create(active_session)
        await session_repo.create(archived_session)

        active_sessions = await session_repo.get_by_project(test_project.id, status="active")

        assert len(active_sessions) == 1
        assert active_sessions[0].status == "active"

    @pytest.mark.asyncio
    async def test_update_session(self, session_repo: ResearchSessionRepository, test_project: Project, test_user: User) -> None:
        """Test updating session."""
        session = ResearchSession(
            project_id=test_project.id,
            title="Original",
            created_by=test_user.id,
        )
        created = await session_repo.create(session)

        created.title = "Updated"
        updated = await session_repo.update(created)

        assert updated.title == "Updated"

    @pytest.mark.asyncio
    async def test_delete_session(self, session_repo: ResearchSessionRepository, test_project: Project, test_user: User) -> None:
        """Test deleting session."""
        session = ResearchSession(
            project_id=test_project.id,
            title="To Delete",
            created_by=test_user.id,
        )
        created = await session_repo.create(session)

        await session_repo.delete(created)

        assert await session_repo.get_by_id(created.id) is None


class TestResearchMessageRepository:
    """Test ResearchMessageRepository."""

    @pytest.mark.asyncio
    async def test_create_message(self, message_repo: ResearchMessageRepository, session_repo: ResearchSessionRepository, test_project: Project, test_user: User) -> None:
        """Test creating message."""
        from backend.db.models import ResearchMessage

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = await session_repo.create(session)

        message = ResearchMessage(
            session_id=session.id,
            role="user",
            content="Test message",
        )

        created = await message_repo.create(message)

        assert created.id is not None
        assert created.content == "Test message"

    @pytest.mark.asyncio
    async def test_get_by_session(self, message_repo: ResearchMessageRepository, session_repo: ResearchSessionRepository, test_project: Project, test_user: User) -> None:
        """Test getting messages by session."""
        from backend.db.models import ResearchMessage

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = await session_repo.create(session)

        for i in range(3):
            message = ResearchMessage(
                session_id=session.id,
                role="user",
                content=f"Message {i}",
            )
            await message_repo.create(message)

        messages = await message_repo.get_by_session(session.id)

        assert len(messages) == 3

    @pytest.mark.asyncio
    async def test_get_latest_messages(self, message_repo: ResearchMessageRepository, session_repo: ResearchSessionRepository, test_project: Project, test_user: User) -> None:
        """Test getting latest messages."""
        from backend.db.models import ResearchMessage

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = await session_repo.create(session)

        for i in range(10):
            message = ResearchMessage(
                session_id=session.id,
                role="user",
                content=f"Message {i}",
            )
            await message_repo.create(message)

        latest = await message_repo.get_latest_messages(session.id, limit=3)

        assert len(latest) == 3

    @pytest.mark.asyncio
    async def test_count_by_session(self, message_repo: ResearchMessageRepository, session_repo: ResearchSessionRepository, test_project: Project, test_user: User) -> None:
        """Test counting messages."""
        from backend.db.models import ResearchMessage

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = await session_repo.create(session)

        for i in range(5):
            message = ResearchMessage(
                session_id=session.id,
                role="user",
                content=f"Message {i}",
            )
            await message_repo.create(message)

        count = await message_repo.count_by_session(session.id)

        assert count == 5


class TestResearchFindingRepository:
    """Test ResearchFindingRepository."""

    @pytest.mark.asyncio
    async def test_create_finding(self, finding_repo: ResearchFindingRepository, session_repo: ResearchSessionRepository, test_project: Project, test_user: User) -> None:
        """Test creating finding."""
        from backend.db.models import ResearchFinding

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = await session_repo.create(session)

        finding = ResearchFinding(
            session_id=session.id,
            finding_type="technical",
            title="Test Finding",
            description="Test description",
        )

        created = await finding_repo.create(finding)

        assert created.id is not None
        assert created.title == "Test Finding"

    @pytest.mark.asyncio
    async def test_get_by_session(self, finding_repo: ResearchFindingRepository, session_repo: ResearchSessionRepository, test_project: Project, test_user: User) -> None:
        """Test getting findings by session."""
        from backend.db.models import ResearchFinding

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = await session_repo.create(session)

        for i in range(3):
            finding = ResearchFinding(
                session_id=session.id,
                finding_type="technical",
                title=f"Finding {i}",
                description="Test",
            )
            await finding_repo.create(finding)

        findings = await finding_repo.get_by_session(session.id)

        assert len(findings) == 3

    @pytest.mark.asyncio
    async def test_get_by_session_with_type_filter(self, finding_repo: ResearchFindingRepository, session_repo: ResearchSessionRepository, test_project: Project, test_user: User) -> None:
        """Test filtering findings by type."""
        from backend.db.models import ResearchFinding

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = await session_repo.create(session)

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
        await finding_repo.create(technical)
        await finding_repo.create(market)

        technical_findings = await finding_repo.get_by_session(session.id, finding_type="technical")

        assert len(technical_findings) == 1
        assert technical_findings[0].finding_type == "technical"

    @pytest.mark.asyncio
    async def test_get_high_confidence_findings(self, finding_repo: ResearchFindingRepository, session_repo: ResearchSessionRepository, test_project: Project, test_user: User) -> None:
        """Test getting high-confidence findings."""
        from backend.db.models import ResearchFinding

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = await session_repo.create(session)

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
        await finding_repo.create(high_conf)
        await finding_repo.create(low_conf)

        high_findings = await finding_repo.get_high_confidence_findings(session.id, min_confidence=0.7)

        assert len(high_findings) == 1
        assert high_findings[0].confidence_score is not None
        assert high_findings[0].confidence_score >= 0.7

    @pytest.mark.asyncio
    async def test_count_by_type(self, finding_repo: ResearchFindingRepository, session_repo: ResearchSessionRepository, test_project: Project, test_user: User) -> None:
        """Test counting findings by type."""
        from backend.db.models import ResearchFinding

        session = ResearchSession(
            project_id=test_project.id,
            title="Test",
            created_by=test_user.id,
        )
        session = await session_repo.create(session)

        for i in range(2):
            finding = ResearchFinding(
                session_id=session.id,
                finding_type="technical",
                title=f"Technical {i}",
                description="Test",
            )
            await finding_repo.create(finding)

        finding = ResearchFinding(
            session_id=session.id,
            finding_type="market",
            title="Market",
            description="Test",
        )
        await finding_repo.create(finding)

        counts = await finding_repo.count_by_type(session.id)

        assert counts["technical"] == 2
        assert counts["market"] == 1
