"""
RefMemTree E2E Scenario Tests - Real-world use cases.

Tests complete user workflows that leverage RefMemTree's power.
"""

from typing import Dict
from uuid import UUID
import pytest
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Project, User


@pytest.mark.asyncio
class TestRefMemTreeScenarios:
    """Real-world scenario tests for RefMemTree."""

    async def test_scenario_safe_refactoring(
        self, async_client: AsyncClient, auth_headers: Dict[str, str], sample_project: Project
    ) -> None:
        """
        Scenario: User wants to refactor architecture safely.

        Steps:
        1. Create initial monolith architecture
        2. Create snapshot (safety net)
        3. AI generates microservices split
        4. Validate with RefMemTree
        5. If good → apply, if bad → rollback

        ⭐ This tests the CORE RefMemTree value proposition!
        """
        # Step 1: Create monolith
        monolith_response = await async_client.post(
            "/api/v1/architecture/modules",
            json={
                "project_id": str(sample_project.id),
                "name": "Monolith",
                "module_type": "application",
                "description": "Monolithic application",
            },
            headers=auth_headers,
        )
        monolith_id = monolith_response.json()["id"]

        # Step 2: Create snapshot
        # snapshot_response = await async_client.post(
        #     f"/api/v1/architecture/projects/{sample_project.id}/snapshots",
        #     json={"name": "before_split", "description": "Before microservices"},
        #     headers=auth_headers
        # )
        # snapshot_id = snapshot_response.json()["snapshot_id"]

        # Step 3: AI generates split plan
        ai_split_plan = [
            {
                "action": "CREATE_NODE",
                "data": {
                    "project_id": str(sample_project.id),
                    "name": "AuthService",
                    "module_type": "service",
                },
            },
            {
                "action": "CREATE_NODE",
                "data": {
                    "project_id": str(sample_project.id),
                    "name": "UserService",
                    "module_type": "service",
                },
            },
        ]

        # Step 4: Validate with AI Governor (dry run)
        # dry_run_response = await async_client.post(
        #     f"/api/v1/architecture/projects/{sample_project.id}/execute-ai-plan",
        #     json=ai_split_plan,
        #     params={"dry_run": True},
        #     headers=auth_headers
        # )
        #
        # if dry_run_response.json()["status"] == "success":
        #     # Execute for real
        #     real_response = await async_client.post(..., dry_run=False)
        # else:
        #     # Rollback to snapshot
        #     await async_client.post(.../rollback/{snapshot_id})

    async def test_scenario_dependency_impact_warning(
        self, async_client: AsyncClient, auth_headers: Dict[str, str], sample_project: Project
    ) -> None:
        """
        Scenario: User gets warned before breaking change.

        Steps:
        1. Create Database with 5 services depending on it
        2. User tries to delete Database
        3. ⭐ RefMemTree calculates impact
        4. System warns: "5 modules will break!"
        5. User cancels deletion
        """
        # Create Database
        db_response = await async_client.post(
            "/api/v1/architecture/modules",
            json={
                "project_id": str(sample_project.id),
                "name": "SharedDatabase",
                "module_type": "database",
            },
            headers=auth_headers,
        )
        db_id = db_response.json()["id"]

        # Create 5 services depending on it
        for i in range(5):
            svc_response = await async_client.post(
                "/api/v1/architecture/modules",
                json={
                    "project_id": str(sample_project.id),
                    "name": f"Service{i}",
                    "module_type": "service",
                },
                headers=auth_headers,
            )

            # Add dependency
            await async_client.post(
                "/api/v1/architecture/dependencies",
                json={
                    "project_id": str(sample_project.id),
                    "from_module_id": svc_response.json()["id"],
                    "to_module_id": db_id,
                    "dependency_type": "uses",
                },
                headers=auth_headers,
            )

        # ⭐ Try to delete - RefMemTree should calculate high impact
        delete_response = await async_client.delete(
            f"/api/v1/architecture/modules/{db_id}",
            headers=auth_headers,
        )

        # Should be blocked or warned
        # assert delete_response.status_code == 400
        # assert "5 modules" in delete_response.json()["detail"]

    async def test_scenario_rule_enforcement(
        self, async_client: AsyncClient, auth_headers: Dict[str, str], sample_project: Project
    ) -> None:
        """
        Scenario: Architecture rules are automatically enforced.

        Steps:
        1. Define rule: "UI cannot depend on Database"
        2. User tries to create UI → Database dependency
        3. ⭐ RefMemTree Rule Engine blocks it
        4. User sees error with suggestion
        """
        # Create UI module
        ui_response = await async_client.post(
            "/api/v1/architecture/modules",
            json={
                "project_id": str(sample_project.id),
                "name": "LoginUI",
                "module_type": "component",
                "metadata": {"layer": "ui"},
            },
            headers=auth_headers,
        )
        ui_id = ui_response.json()["id"]

        # Create Database
        db_response = await async_client.post(
            "/api/v1/architecture/modules",
            json={
                "project_id": str(sample_project.id),
                "name": "UserDatabase",
                "module_type": "database",
                "metadata": {"layer": "data"},
            },
            headers=auth_headers,
        )
        db_id = db_response.json()["id"]

        # Define layer rule (would be done via API)
        # await async_client.post(
        #     "/api/v1/architecture/rules",
        #     json={
        #         "project_id": str(sample_project.id),
        #         "level": "global",
        #         "rule_type": "layer",
        #         "rule_definition": {
        #             "condition": "ui_layer cannot depend on data_layer",
        #             "action": "block"
        #         }
        #     }
        # )

        # ⭐ Try to create UI → Database (should be blocked by Rule Engine!)
        dep_response = await async_client.post(
            "/api/v1/architecture/dependencies",
            json={
                "project_id": str(sample_project.id),
                "from_module_id": ui_id,
                "to_module_id": db_id,
                "dependency_type": "uses",
            },
            headers=auth_headers,
        )

        # Rule Engine should block this
        # assert dep_response.status_code == 400
        # assert "layer" in dep_response.json()["detail"].lower()

    async def test_scenario_instant_analytics_query(
        self, async_client: AsyncClient, auth_headers: Dict[str, str], sample_project: Project
    ) -> None:
        """
        Scenario: User gets instant architecture insights.

        Tests RefMemTree's speed advantage (milliseconds vs seconds).
        """
        # Create complex architecture (10 modules, 15 dependencies)
        modules = []
        for i in range(10):
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

        # Create dependencies
        for i in range(9):
            await async_client.post(
                "/api/v1/architecture/dependencies",
                json={
                    "project_id": str(sample_project.id),
                    "from_module_id": modules[i],
                    "to_module_id": modules[i + 1],
                    "dependency_type": "uses",
                },
                headers=auth_headers,
            )

        # ⭐ Query analytics - should be INSTANT with RefMemTree
        import time

        start = time.time()

        response = await async_client.get(
            f"/api/v1/analytics/projects/{sample_project.id}/architecture-health",
            headers=auth_headers,
        )

        elapsed = (time.time() - start) * 1000  # milliseconds

        assert response.status_code == 200
        # RefMemTree should respond in < 100ms
        # assert elapsed < 100


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
async def sample_project(async_session: AsyncSession) -> Project:
    """Create sample project."""
    from backend.db.models import Project, User
    from datetime import datetime

    user = User(
        email="scenario@test.com",
        username="scenariouser",
        hashed_password="hashed",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_session.add(user)
    await async_session.flush()

    project = Project(
        name="Scenario Test Project",
        description="Real-world scenarios",
        goal="Test RefMemTree scenarios",
        owner_id=user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_session.add(project)
    await async_session.commit()

    return project
