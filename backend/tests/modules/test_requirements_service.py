"""
Tests for Requirements Service.
"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.models import User, Project

from backend.modules.requirements.service import RequirementsService
from backend.modules.requirements.schemas import RequirementCreate


@pytest.mark.asyncio
class TestRequirementsService:
    """Test Requirements Service."""

    async def test_create_requirement(self, async_session: AsyncSession, sample_project: Project, sample_user: User) -> None:
        """Test creating requirement."""
        service = RequirementsService(async_session)

        data = RequirementCreate(
            project_id=sample_project.id,
            type="functional",
            category="security",
            title="User Authentication",
            description="System must support user authentication with JWT tokens",
            priority="must_have",
            acceptance_criteria=["JWT token generation", "Token validation"],
        )

        requirement = await service.create_requirement(data, sample_user.id)

        assert requirement is not None
        assert requirement.title == "User Authentication"
        assert requirement.type == "functional"
        assert requirement.status == "draft"

    async def test_list_requirements_with_filters(self, async_session: AsyncSession, sample_project: Project, sample_user: User) -> None:
        """Test listing requirements with filters."""
        service = RequirementsService(async_session)

        # Create multiple requirements
        for i in range(3):
            data = RequirementCreate(
                project_id=sample_project.id,
                type="functional" if i % 2 == 0 else "technical",
                category="core",
                title=f"Requirement {i}",
                description=f"Description {i}",
                priority="must_have",
            )
            await service.create_requirement(data, sample_user.id)

        # List all
        all_reqs = await service.list_requirements(sample_project.id)
        assert len(all_reqs) >= 3

        # Filter by type
        functional = await service.list_requirements(sample_project.id, type_filter="functional")
        assert all(r.type == "functional" for r in functional)

    async def test_basic_validation(self, async_session: AsyncSession, sample_project: Project, sample_user: User) -> None:
        """Test basic requirement validation."""
        service = RequirementsService(async_session)

        # Create requirement with short description
        data = RequirementCreate(
            project_id=sample_project.id,
            type="functional",
            category="general",
            title="Short",
            description="Too short",  # < 50 chars
            priority="should_have",
        )
        requirement = await service.create_requirement(data, sample_user.id)

        # Validate
        validation = service._basic_validation(requirement)

        assert validation.overall_score < 10.0  # Not perfect
        assert len(validation.issues) > 0  # Has issues


@pytest.fixture
async def sample_user(async_session: AsyncSession) -> User:
    """Create sample user."""
    from datetime import datetime

    user = User(
        email="test@test.com",
        username="testuser",
        hashed_password="hashed",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_session.add(user)
    await async_session.commit()
    return user


@pytest.fixture
async def sample_project(async_session: AsyncSession, sample_user: User) -> Project:
    """Create sample project."""
    from datetime import datetime

    project = Project(
        name="Test Project",
        description="Test",
        goal="Test goal",
        owner_id=sample_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_session.add(project)
    await async_session.commit()
    return project
