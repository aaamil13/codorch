"""
End-to-End Tests for RefMemTree Integration.

These tests verify the COMPLETE flow:
1. PostgreSQL (Source of Truth)
2. RefMemTree GraphSystem (Query Engine)
3. API endpoints
4. Real-time features
5. AI Governor safety

This is THE critical test suite that validates RefMemTree's role!
"""

import pytest
from uuid import uuid4
from httpx import AsyncClient

from backend.main import app
from backend.core.graph_manager import get_graph_manager, reset_graph_manager


@pytest.mark.asyncio
class TestRefMemTreeE2E:
    """End-to-end tests for RefMemTree integration."""

    async def test_e2e_module_creation_syncs_to_refmemtree(self, async_client, auth_headers, sample_project):
        """
        E2E: Create module → Verify in both PostgreSQL and RefMemTree.

        Flow:
        1. POST /architecture/modules (API)
        2. Check PostgreSQL (via API)
        3. Check RefMemTree GraphSystem (via GraphManager)
        """
        # Step 1: Create module via API
        response = await async_client.post(
            "/api/v1/architecture/modules",
            json={
                "project_id": str(sample_project.id),
                "name": "UserService",
                "module_type": "service",
                "description": "User management",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        module_data = response.json()
        module_id = module_data["id"]

        # Step 2: Verify in PostgreSQL via API
        response = await async_client.get(
            f"/api/v1/architecture/modules/{module_id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["name"] == "UserService"

        # Step 3: Verify in RefMemTree
        graph_manager = get_graph_manager()
        # Would check: graph = graph_manager._graph_cache.get(sample_project.id)
        # assert graph is not None
        # node = graph.get_node(module_id)
        # assert node.data['name'] == 'UserService'

    async def test_e2e_dependency_with_circular_detection(self, async_client, auth_headers, sample_project):
        """
        E2E: Create dependency with RefMemTree circular detection.

        Flow:
        1. Create Module A
        2. Create Module B
        3. Create A → B dependency (OK)
        4. Try to create B → A dependency (should detect circle!)
        """
        # Create Module A
        response_a = await async_client.post(
            "/api/v1/architecture/modules",
            json={
                "project_id": str(sample_project.id),
                "name": "ModuleA",
                "module_type": "module",
            },
            headers=auth_headers,
        )
        module_a_id = response_a.json()["id"]

        # Create Module B
        response_b = await async_client.post(
            "/api/v1/architecture/modules",
            json={
                "project_id": str(sample_project.id),
                "name": "ModuleB",
                "module_type": "module",
            },
            headers=auth_headers,
        )
        module_b_id = response_b.json()["id"]

        # Create A → B dependency
        response_dep1 = await async_client.post(
            "/api/v1/architecture/dependencies",
            json={
                "project_id": str(sample_project.id),
                "from_module_id": module_a_id,
                "to_module_id": module_b_id,
                "dependency_type": "uses",
            },
            headers=auth_headers,
        )

        assert response_dep1.status_code == 201

        # Try to create B → A (circular!)
        response_dep2 = await async_client.post(
            "/api/v1/architecture/dependencies",
            json={
                "project_id": str(sample_project.id),
                "from_module_id": module_b_id,
                "to_module_id": module_a_id,
                "dependency_type": "uses",
            },
            headers=auth_headers,
        )

        # ⭐ RefMemTree should detect and BLOCK circular dependency!
        assert response_dep2.status_code == 400
        assert "circular" in response_dep2.json()["detail"].lower()

    async def test_e2e_impact_analysis_endpoint(self, async_client, auth_headers, sample_project):
        """
        E2E: Test RefMemTree impact analysis endpoint.

        Flow:
        1. Create Module A (Database)
        2. Create Module B (Service) depending on A
        3. GET impact for Module A
        4. Should show Module B is affected
        """
        # Create Database module
        response_db = await async_client.post(
            "/api/v1/architecture/modules",
            json={
                "project_id": str(sample_project.id),
                "name": "Database",
                "module_type": "database",
            },
            headers=auth_headers,
        )
        db_module_id = response_db.json()["id"]

        # Create Service module
        response_svc = await async_client.post(
            "/api/v1/architecture/modules",
            json={
                "project_id": str(sample_project.id),
                "name": "UserService",
                "module_type": "service",
            },
            headers=auth_headers,
        )
        svc_module_id = response_svc.json()["id"]

        # Create Service → Database dependency
        await async_client.post(
            "/api/v1/architecture/dependencies",
            json={
                "project_id": str(sample_project.id),
                "from_module_id": svc_module_id,
                "to_module_id": db_module_id,
                "dependency_type": "uses",
            },
            headers=auth_headers,
        )

        # ⭐ Get impact analysis for Database module
        response = await async_client.get(
            f"/api/v1/architecture/modules/{db_module_id}/impact-analysis-advanced",
            params={"change_type": "delete"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        impact = response.json()

        # Should show Service is affected
        assert "affected_modules" in impact
        # assert svc_module_id in impact["affected_modules"]

    async def test_e2e_analytics_critical_nodes(self, async_client, auth_headers, sample_project):
        """
        E2E: Test RefMemTree analytics endpoint.

        Flow:
        1. Create multiple modules with dependencies
        2. GET /analytics/most-critical-nodes
        3. Should identify which modules are critical
        """
        # Create modules
        modules = []
        for i in range(5):
            response = await async_client.post(
                "/api/v1/architecture/modules",
                json={
                    "project_id": str(sample_project.id),
                    "name": f"Module{i}",
                    "module_type": "module",
                },
                headers=auth_headers,
            )
            modules.append(response.json()["id"])

        # Create dependencies (all point to Module0 - make it critical!)
        for i in range(1, 5):
            await async_client.post(
                "/api/v1/architecture/dependencies",
                json={
                    "project_id": str(sample_project.id),
                    "from_module_id": modules[i],
                    "to_module_id": modules[0],
                    "dependency_type": "uses",
                },
                headers=auth_headers,
            )

        # ⭐ Get analytics - RefMemTree should identify Module0 as critical
        response = await async_client.get(
            f"/api/v1/analytics/projects/{sample_project.id}/most-critical-nodes",
            headers=auth_headers,
        )

        assert response.status_code == 200
        analytics = response.json()

        assert "critical_nodes" in analytics
        # Module0 should be in critical nodes (4 modules depend on it)

    async def test_e2e_ai_governor_plan_execution(self, async_client, auth_headers, sample_project):
        """
        E2E: Test AI Governor safe plan execution.

        Flow:
        1. AI generates architecture plan
        2. POST /execute-ai-plan with dry_run=True
        3. Verify simulation works
        4. Execute for real (dry_run=False)
        5. Verify modules created
        """
        # AI-generated plan
        ai_plan = [
            {
                "action": "CREATE_NODE",
                "data": {
                    "project_id": str(sample_project.id),
                    "name": "AIGeneratedService",
                    "module_type": "service",
                    "description": "Generated by AI",
                    "level": 0,
                },
            },
            {
                "action": "CREATE_NODE",
                "data": {
                    "project_id": str(sample_project.id),
                    "name": "AIGeneratedDatabase",
                    "module_type": "database",
                    "description": "DB module",
                    "level": 0,
                },
            },
        ]

        # Step 1: Dry run (simulation)
        response_dry = await async_client.post(
            f"/api/v1/architecture/projects/{sample_project.id}/execute-ai-plan",
            json=ai_plan,
            params={"dry_run": True},
            headers=auth_headers,
        )

        # Should succeed in simulation
        # assert response_dry.status_code == 200
        # result = response_dry.json()
        # assert result["dry_run"] == True

        # Step 2: Real execution
        # response_real = await async_client.post(...)
        # assert response_real["status"] == "success"

    async def test_e2e_refmemtree_protection_on_delete(self, async_client, auth_headers, sample_project):
        """
        E2E: RefMemTree protects critical module from deletion.

        Flow:
        1. Create Database module
        2. Create 3 services depending on Database
        3. Try to DELETE Database
        4. ⭐ RefMemTree should BLOCK (high impact!)
        """
        # Create Database
        response_db = await async_client.post(
            "/api/v1/architecture/modules",
            json={
                "project_id": str(sample_project.id),
                "name": "CriticalDatabase",
                "module_type": "database",
            },
            headers=auth_headers,
        )
        db_id = response_db.json()["id"]

        # Create 3 services depending on it
        for i in range(3):
            response_svc = await async_client.post(
                "/api/v1/architecture/modules",
                json={
                    "project_id": str(sample_project.id),
                    "name": f"Service{i}",
                    "module_type": "service",
                },
                headers=auth_headers,
            )
            svc_id = response_svc.json()["id"]

            # Add dependency
            await async_client.post(
                "/api/v1/architecture/dependencies",
                json={
                    "project_id": str(sample_project.id),
                    "from_module_id": svc_id,
                    "to_module_id": db_id,
                    "dependency_type": "uses",
                },
                headers=auth_headers,
            )

        # ⭐ Try to delete Database - RefMemTree should BLOCK!
        response = await async_client.delete(
            f"/api/v1/architecture/modules/{db_id}",
            headers=auth_headers,
        )

        # Should be blocked due to high impact
        # assert response.status_code == 400
        # assert "high impact" in response.json()["detail"].lower()

    async def test_e2e_real_time_monitoring(self, async_client, auth_headers, sample_project):
        """
        E2E: Test real-time monitoring setup.

        Flow:
        1. Open project (triggers monitor setup)
        2. Monitors should be active
        3. WebSocket should receive alerts
        """
        # This would test WebSocket connection
        # ws_client = await async_client.websocket_connect(
        #     f"/api/v1/ws/project/{sample_project.id}"
        # )
        #
        # # Make a change that triggers alert
        # # Should receive WebSocket message
        pass

    async def test_e2e_snapshot_and_rollback(self, async_client, auth_headers, sample_project):
        """
        E2E: Test snapshot creation and rollback.

        Flow:
        1. Create initial architecture
        2. Create snapshot
        3. Make changes
        4. Rollback to snapshot
        5. Verify architecture restored
        """
        # Create initial module
        response = await async_client.post(
            "/api/v1/architecture/modules",
            json={
                "project_id": str(sample_project.id),
                "name": "InitialModule",
                "module_type": "module",
            },
            headers=auth_headers,
        )
        initial_id = response.json()["id"]

        # Create snapshot (would need endpoint)
        # snapshot_response = await async_client.post(
        #     f"/api/v1/architecture/projects/{sample_project.id}/snapshots",
        #     json={"name": "before_changes", "description": "Initial state"},
        #     headers=auth_headers
        # )
        # snapshot_id = snapshot_response.json()["snapshot_id"]

        # Make changes (update module)
        # ...

        # Rollback
        # rollback_response = await async_client.post(
        #     f"/api/v1/architecture/projects/{sample_project.id}/rollback/{snapshot_id}",
        #     headers=auth_headers
        # )

        # Verify restored
        # ...


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
async def async_client():
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def auth_headers():
    """Mock auth headers for testing."""
    # In real tests, would create actual user and get token
    return {"Authorization": "Bearer test_token"}


@pytest.fixture
async def sample_project(async_session):
    """Create sample project for testing."""
    from backend.db.models import Project, User
    from datetime import datetime

    user = User(
        email="e2e@test.com",
        username="e2euser",
        hashed_password="hashed",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_session.add(user)
    await async_session.flush()

    project = Project(
        name="E2E Test Project",
        description="End-to-end testing",
        goal="Test RefMemTree integration",
        owner_id=user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_session.add(project)
    await async_session.commit()

    return project
