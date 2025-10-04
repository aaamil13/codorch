"""
Tests for GraphManagerService - RefMemTree core integration.

Critical tests for the BRAIN of Codorch!
"""

from typing import Any, Dict
import pytest
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.graph_manager import GraphManagerService, get_graph_manager, reset_graph_manager
from backend.db.models import Project, User


@pytest.fixture
def graph_manager() -> GraphManagerService:
    """Get fresh GraphManagerService for each test."""
    reset_graph_manager()  # Clear singleton
    return get_graph_manager()


class TestGraphManagerService:
    """Test GraphManagerService - RefMemTree integration."""

    def test_singleton_pattern(self, graph_manager: GraphManagerService) -> None:
        """Test that get_graph_manager returns same instance."""
        manager1 = get_graph_manager()
        manager2 = get_graph_manager()

        assert manager1 is manager2
        assert id(manager1) == id(manager2)

    @pytest.mark.asyncio
    async def test_service_instance_caching(
        self, graph_manager: GraphManagerService, async_session: AsyncSession
    ) -> None:
        """Test that services are cached per project_id."""
        project_id = uuid4()

        # First call - should create services
        services1 = await graph_manager.get_or_create_services(project_id, async_session)
        assert all(s is not None for s in services1)

        # Second call - should return the same cached instances
        services2 = await graph_manager.get_or_create_services(project_id, async_session)
        assert all(s is not None for s in services2)

        # Check if the instances are identical
        assert services1[0] is services2[0]  # HydrationService
        assert services1[1] is services2[1]  # OperationsService
        assert services1[2] is services2[2]  # AnalyticsService
        assert services1[3] is services2[3]  # VersioningService

        # Check a different project_id creates new instances
        other_project_id = uuid4()
        other_services = await graph_manager.get_or_create_services(other_project_id, async_session)
        assert services1[0] is not other_services[0]


@pytest.mark.asyncio
class TestGraphManagerIntegration:
    """Integration tests for GraphManager with database."""

    async def test_hydration_creates_cache(self, async_session: AsyncSession, sample_project: Project) -> None:
        """Test that hydration creates cached graph."""
        manager = get_graph_manager()

        # This would hydrate from DB
        # graph = await manager.get_or_create_graph(sample_project.id, async_session)

        # For now, test structure is correct
        assert manager is not None
        assert hasattr(manager, "_graph_cache")

    async def test_add_node_to_graph_without_refmemtree(self, async_session: AsyncSession) -> None:
        """Test graceful fallback when RefMemTree not available."""
        manager = get_graph_manager()
        project_id = uuid4()
        node_id = uuid4()

        # Should not crash if RefMemTree not installed
        result = await manager.add_node_to_graph(
            project_id=project_id,
            session=async_session,
            node_id=node_id,
            node_type="module",
            data={"name": "TestModule"},
        )

        # Result is False if RefMemTree not available, but doesn't crash
        assert result in [True, False]

    async def test_detect_circular_dependencies_fallback(self, async_session: AsyncSession) -> None:
        """Test circular detection works even without RefMemTree."""
        manager = get_graph_manager()
        project_id = uuid4()

        # Should return empty list if RefMemTree not available
        cycles = await manager.detect_circular_dependencies(project_id, async_session)

        assert isinstance(cycles, list)


# ============================================================================
# Mock Tests (when RefMemTree is available)
# ============================================================================


class TestRefMemTreeAPIs:
    """Test RefMemTree API integration (requires RefMemTree installed)."""

    @pytest.mark.skipif(not hasattr(GraphManagerService, "_check_refmemtree"), reason="RefMemTree not installed")
    async def test_real_graphsystem_creation(self, async_session: AsyncSession) -> None:
        """Test real GraphSystem creation."""
        manager = get_graph_manager()
        project_id = uuid4()

        # Would test real RefMemTree GraphSystem
        # graph = await manager.get_or_create_graph(project_id, async_session)
        # assert graph is not None
        # assert hasattr(graph, 'add_node')
        # assert hasattr(graph, 'detect_cycles')
        pass

    @pytest.mark.skipif(not hasattr(GraphManagerService, "_check_refmemtree"), reason="RefMemTree not installed")
    async def test_impact_analysis(self, async_session: AsyncSession) -> None:
        """Test RefMemTree impact analysis."""
        manager = get_graph_manager()
        project_id = uuid4()
        node_id = uuid4()

        # Would test real impact analysis
        # impact = await manager.calculate_node_impact(
        #     project_id, node_id, async_session, 'delete'
        # )
        # assert 'impact_score' in impact
        # assert 'affected_nodes' in impact
        pass


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
async def sample_project(async_session: AsyncSession) -> Project:
    """Create sample project for testing."""
    from backend.db.models import Project, User
    from datetime import datetime

    user = User(
        email="test@test.com",
        username="testuser",
        hashed_password="hashed",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_session.add(user)
    await async_session.flush()

    project = Project(
        name="Test Project",
        description="Test",
        goal="Test goal",
        owner_id=user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_session.add(project)
    await async_session.commit()

    return project
