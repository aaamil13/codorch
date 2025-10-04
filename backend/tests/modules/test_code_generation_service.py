"""
Tests for Code Generation Service.
"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.models import Project

from backend.modules.code_generation.service import CodeGenerationService
from backend.modules.code_generation.schemas import CodeGenerationSessionCreate


@pytest.mark.asyncio
class TestCodeGenerationService:
    """Test Code Generation Service."""

    async def test_create_session(self, async_session: AsyncSession, sample_project: Project) -> None:
        """Test creating code generation session."""
        service = CodeGenerationService(async_session)

        data = CodeGenerationSessionCreate(project_id=sample_project.id)

        session_obj = await service.create_session(data)

        assert session_obj is not None
        assert session_obj.project_id == sample_project.id
        assert session_obj.status == "validating"

    async def test_list_sessions(self, async_session: AsyncSession, sample_project: Project) -> None:
        """Test listing sessions."""
        service = CodeGenerationService(async_session)

        # Create session
        data = CodeGenerationSessionCreate(project_id=sample_project.id)
        await service.create_session(data)

        # List
        sessions = await service.list_sessions(sample_project.id)

        assert len(sessions) >= 1


@pytest.fixture
async def sample_project(async_session: AsyncSession) -> Project:
    """Create sample project."""
    from backend.db.models import Project, User
    from datetime import datetime

    user = User(
        email="codegen@test.com",
        username="codegenuser",
        hashed_password="hashed",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_session.add(user)
    await async_session.flush()

    project = Project(
        name="CodeGen Project",
        description="Test",
        goal="Generate code",
        owner_id=user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_session.add(project)
    await async_session.commit()

    return project
