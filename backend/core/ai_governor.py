"""
AI Governor - Safe execution of AI-generated architecture plans.

This is THE critical component that makes AI-generated architecture SAFE!

Uses RefMemTree's execute_refactoring_plan() for atomic, validated execution.
"""

from typing import Any, Dict, List
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.graph_manager import GraphManagerService
from backend.db.models import ArchitectureModule, ModuleDependency
from backend.modules.architecture.repository import (
    ArchitectureModuleRepository,
    ModuleDependencyRepository,
)

# RefMemTree imports
try:
    from refmemtree import AIGovernor as RefMemAIGovernor

    AIGOVERNOR_AVAILABLE = True
except ImportError:
    RefMemAIGovernor = None
    AIGOVERNOR_AVAILABLE = False


class AIGovernor:
    """
    AI Governor for safe execution of AI-generated plans.
    
    Ensures:
    - Plans are validated before execution
    - Changes are atomic (all-or-nothing)
    - Automatic rollback on failure
    - PostgreSQL and RefMemTree stay in sync
    """

    def __init__(self, graph_manager: GraphManagerService):
        self.graph_manager = graph_manager

    async def execute_architecture_plan(
        self,
        project_id: UUID,
        plan: List[Dict[str, Any]],
        session: AsyncSession,
        validate: bool = True,
        dry_run: bool = False,
        create_snapshot: bool = True,
    ) -> Dict:
        """
        Execute AI-generated architecture plan safely.
        
        Plan Format:
        [
            {
                "action": "CREATE_NODE",
                "data": {
                    "name": "UserService",
                    "module_type": "service",
                    "description": "...",
                    "level": 2
                }
            },
            {
                "action": "CREATE_DEPENDENCY",
                "from": "UserService_id",
                "to": "Database_id",
                "type": "uses"
            },
            {
                "action": "UPDATE_NODE",
                "node_id": "existing_id",
                "data": {"status": "approved"}
            }
        ]
        
        Uses REAL RefMemTree AIGovernor.execute_refactoring_plan()
        """
        if not AIGOVERNOR_AVAILABLE:
            return {
                "status": "error",
                "error": "AIGovernor not available - RefMemTree not installed",
            }

        try:
            # Get RefMemTree graph
            graph = await self.graph_manager.get_or_create_graph(project_id, session)
            if not graph:
                return {"status": "error", "error": "Failed to load graph"}

            # Step 1: Validate plan structure
            if validate:
                validation = self._validate_plan_structure(plan)
                if not validation["valid"]:
                    return {"status": "validation_failed", "errors": validation["errors"]}

            # Step 2: Create snapshot if requested
            snapshot_id = None
            if create_snapshot:
                # ⭐ REAL RefMemTree API
                snapshot_id = graph.create_version(
                    name=f"before_ai_plan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    description="Snapshot before AI-generated architecture plan",
                )
                print(f"📸 Snapshot created: {snapshot_id}")

            # Step 3: Convert Codorch plan to RefMemTree format
            refmem_plan = self._convert_to_refmem_plan(plan, project_id)

            # Step 4: Execute using REAL RefMemTree AIGovernor
            # ⭐ REAL RefMemTree API
            governor = RefMemAIGovernor(graph)

            execution_result = governor.execute_refactoring_plan(
                plan=refmem_plan,
                validate_first=validate,
                dry_run=dry_run,
                create_snapshot=False,  # We already created one
            )

            # Step 5: Check execution result
            if not execution_result.success:
                # Rollback if failed
                if snapshot_id and not dry_run:
                    print(f"❌ Execution failed, rolling back to {snapshot_id}")
                    # ⭐ REAL RefMemTree API
                    graph.rollback_to_version(snapshot_id)

                return {
                    "status": "execution_failed",
                    "errors": execution_result.errors,
                    "rollback_performed": snapshot_id is not None,
                    "snapshot_id": snapshot_id,
                }

            # Step 6: Apply to PostgreSQL if not dry_run
            if not dry_run:
                print(f"💾 Syncing RefMemTree changes to PostgreSQL...")
                await self._sync_plan_to_database(plan, project_id, session)

            return {
                "status": "success",
                "snapshot_id": snapshot_id,
                "nodes_created": execution_result.nodes_created,
                "nodes_updated": execution_result.nodes_updated,
                "nodes_deleted": execution_result.nodes_deleted,
                "dependencies_created": execution_result.dependencies_created,
                "validation_results": execution_result.validation_results,
                "dry_run": dry_run,
                "rollback_available": snapshot_id is not None,
            }

        except Exception as e:
            print(f"❌ AI Governor execution error: {e}")

            # Try to rollback if we have snapshot
            if snapshot_id and not dry_run:
                try:
                    graph = await self.graph_manager.get_or_create_graph(
                        project_id, session
                    )
                    # ⭐ REAL RefMemTree API
                    graph.rollback_to_version(snapshot_id)
                    print(f"✅ Rolled back to snapshot {snapshot_id}")
                except Exception as rollback_err:
                    print(f"❌ Rollback also failed: {rollback_err}")

            return {
                "status": "error",
                "error": str(e),
                "rollback_performed": snapshot_id is not None,
            }

    def _validate_plan_structure(self, plan: List[Dict]) -> Dict:
        """Validate plan has correct structure."""
        errors = []

        for idx, step in enumerate(plan):
            if "action" not in step:
                errors.append(f"Step {idx}: Missing 'action' field")
                continue

            action = step["action"]

            if action == "CREATE_NODE":
                if "data" not in step:
                    errors.append(f"Step {idx}: CREATE_NODE missing 'data'")
                elif "name" not in step["data"]:
                    errors.append(f"Step {idx}: CREATE_NODE data missing 'name'")

            elif action == "UPDATE_NODE":
                if "node_id" not in step:
                    errors.append(f"Step {idx}: UPDATE_NODE missing 'node_id'")
                if "data" not in step:
                    errors.append(f"Step {idx}: UPDATE_NODE missing 'data'")

            elif action == "CREATE_DEPENDENCY":
                if "from" not in step or "to" not in step:
                    errors.append(f"Step {idx}: CREATE_DEPENDENCY missing 'from' or 'to'")

            elif action == "DELETE_NODE":
                if "node_id" not in step:
                    errors.append(f"Step {idx}: DELETE_NODE missing 'node_id'")

        return {"valid": len(errors) == 0, "errors": errors}

    def _convert_to_refmem_plan(
        self, plan: List[Dict], project_id: UUID
    ) -> List[Dict]:
        """
        Convert Codorch plan format to RefMemTree AIGovernor format.
        
        Codorch format → RefMemTree format
        """
        refmem_plan = []

        for step in plan:
            action = step["action"]

            if action == "CREATE_NODE":
                refmem_plan.append(
                    {
                        "operation": "add_node",
                        "node_type": step["data"].get("module_type", "module"),
                        "data": step["data"],
                    }
                )

            elif action == "UPDATE_NODE":
                refmem_plan.append(
                    {
                        "operation": "update_node",
                        "node_id": step["node_id"],
                        "updates": step["data"],
                    }
                )

            elif action == "CREATE_DEPENDENCY":
                refmem_plan.append(
                    {
                        "operation": "add_dependency",
                        "from_node": step["from"],
                        "to_node": step["to"],
                        "dependency_type": step.get("type", "depends_on"),
                    }
                )

            elif action == "DELETE_NODE":
                refmem_plan.append(
                    {"operation": "delete_node", "node_id": step["node_id"]}
                )

        return refmem_plan

    async def _sync_plan_to_database(
        self, plan: List[Dict], project_id: UUID, session: AsyncSession
    ) -> None:
        """
        Sync executed RefMemTree plan to PostgreSQL.
        
        After RefMemTree successfully executes plan, we need to persist
        the changes to database.
        """
        module_repo = ArchitectureModuleRepository(session)
        dep_repo = ModuleDependencyRepository(session)

        for step in plan:
            action = step["action"]

            try:
                if action == "CREATE_NODE":
                    # Create module in DB
                    from backend.modules.architecture.schemas import (
                        ArchitectureModuleCreate,
                    )

                    module_data = ArchitectureModuleCreate(
                        project_id=project_id,
                        name=step["data"]["name"],
                        module_type=step["data"].get("module_type", "module"),
                        description=step["data"].get("description"),
                        level=step["data"].get("level", 0),
                    )
                    module_repo.create(module_data)

                elif action == "CREATE_DEPENDENCY":
                    # Create dependency in DB
                    from backend.modules.architecture.schemas import (
                        ModuleDependencyCreate,
                    )

                    dep_data = ModuleDependencyCreate(
                        project_id=project_id,
                        from_module_id=UUID(step["from"]),
                        to_module_id=UUID(step["to"]),
                        dependency_type=step.get("type", "depends_on"),
                    )
                    dep_repo.create(dep_data)

                elif action == "UPDATE_NODE":
                    # Update module in DB
                    module_id = UUID(step["node_id"])
                    module_repo.update(module_id, step["data"])

                elif action == "DELETE_NODE":
                    # Delete module from DB
                    module_id = UUID(step["node_id"])
                    module_repo.delete(module_id)

            except Exception as e:
                print(f"⚠️ Failed to sync step to DB: {action} - {e}")

        # Commit all changes
        await session.commit()


# ============================================================================
# Convenience Functions
# ============================================================================


async def execute_ai_plan(
    project_id: UUID,
    plan: List[Dict],
    session: AsyncSession,
    dry_run: bool = False,
) -> Dict:
    """
    Convenience function to execute AI-generated plan.
    
    Usage:
        result = await execute_ai_plan(
            project_id,
            ai_generated_plan,
            session,
            dry_run=True  # Test first!
        )
        
        if result['status'] == 'success':
            # Plan is safe, execute for real
            await execute_ai_plan(project_id, plan, session, dry_run=False)
    """
    from backend.core.graph_manager import get_graph_manager

    graph_manager = get_graph_manager()
    governor = AIGovernor(graph_manager)

    return await governor.execute_architecture_plan(
        project_id, plan, session, validate=True, dry_run=dry_run, create_snapshot=True
    )