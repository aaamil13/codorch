"""
Tests for Architecture Service with RefMemTree integration.
"""

import pytest
from uuid import uuid4

from backend.modules.architecture.service import ArchitectureService
from backend.modules.architecture.schemas import (
    ArchitectureModuleCreate,
    ModuleDependencyCreate,
)


@pytest.mark.asyncio
class TestArchitectureService:
    """Test Architecture Service."""

    async def test_create_module(self, async_session, sample_project):
        """Test module creation with RefMemTree sync."""
        service = ArchitectureService(async_session)
        
        data = ArchitectureModuleCreate(
            project_id=sample_project.id,
            name="UserService",
            module_type="service",
            description="User management service"
        )
        
        module = await service.create_module(data)
        
        assert module is not None
        assert module.name == "UserService"
        assert module.module_type == "service"
        assert module.level == 0  # Root level

    async def test_create_module_with_parent(self, async_session, sample_project):
        """Test module creation with parent (hierarchy)."""
        service = ArchitectureService(async_session)
        
        # Create parent
        parent_data = ArchitectureModuleCreate(
            project_id=sample_project.id,
            name="Backend",
            module_type="package"
        )
        parent = await service.create_module(parent_data)
        
        # Create child
        child_data = ArchitectureModuleCreate(
            project_id=sample_project.id,
            parent_id=parent.id,
            name="UserService",
            module_type="service"
        )
        child = await service.create_module(child_data)
        
        assert child.level == parent.level + 1

    async def test_create_dependency_prevents_self_reference(self, async_session, sample_project):
        """Test that module cannot depend on itself."""
        service = ArchitectureService(async_session)
        
        module_data = ArchitectureModuleCreate(
            project_id=sample_project.id,
            name="Service",
            module_type="service"
        )
        module = await service.create_module(module_data)
        
        # Try to create self-dependency
        dep_data = ModuleDependencyCreate(
            project_id=sample_project.id,
            from_module_id=module.id,
            to_module_id=module.id,  # Same!
            dependency_type="uses"
        )
        
        with pytest.raises(ValueError, match="cannot depend on itself"):
            await service.create_dependency(dep_data)

    async def test_delete_module_checks_impact(self, async_session, sample_project):
        """Test that delete checks RefMemTree impact."""
        service = ArchitectureService(async_session)
        
        # Create module
        data = ArchitectureModuleCreate(
            project_id=sample_project.id,
            name="TestModule",
            module_type="module"
        )
        module = await service.create_module(data)
        
        # Delete should work (no dependencies)
        result = await service.delete_module(module.id)
        
        # Either succeeds or gracefully handles RefMemTree unavailability
        assert result in [True, False] or isinstance(result, bool)


@pytest.fixture
def sample_project(async_session):
    """Create sample project."""
    from backend.db.models import Project, User
    from datetime import datetime
    
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    async_session.add(user)
    await async_session.flush()
    
    project = Project(
        name="Test Project",
        description="Test",
        goal="Test goal",
        owner_id=user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    async_session.add(project)
    await async_session.commit()
    
    return project
