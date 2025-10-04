from typing import Dict, Optional, List, Any, Callable, Type
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.lib.refmemtree.graph_system import GraphSystem, GraphNode


class GraphAnalyticsService:
    def __init__(self, graph_system: GraphSystem):
        self.graph_system = graph_system

    async def detect_circular_dependencies(self) -> List[List[str]]:
        """
        Detect circular dependencies using RefMemTree.
        """
        try:
            cycles: List[List[str]] = self.graph_system.dependency_tracker.find_circular_dependencies()
            return cycles
        except Exception as e:
            print(f"Failed to detect cycles in RefMemTree: {e}")
            return []

    async def calculate_node_impact(
        self,
        node_id: UUID,
        change_type: str = "update",
    ) -> dict:
        """
        Calculate impact of changing a node using RefMemTree.
        """
        try:
            node = self.graph_system.get_node(str(node_id))
            if not node:
                return {"error": "Node not found"}

            impact = node.calculate_impact(
                change_type=change_type,
                propagation_depth=10,
                consider_transitive=True,
            )

            return {
                "impact_score": impact.impact_score,
                "affected_nodes": [n.id for n in impact.affected_nodes],
                "directly_affected": len(impact.directly_affected_nodes),
                "indirectly_affected": len(impact.indirectly_affected_nodes),
                "breaking_changes": impact.breaking_changes,
                "recommendations": impact.recommendations,
            }
        except Exception as e:
            print(f"Failed to calculate impact: {e}")
            return {"error": str(e)}

    async def simulate_change(
        self,
        node_id: UUID,
        proposed_change: dict,
    ) -> dict:
        """
        Simulate change using RefMemTree without applying it.
        """
        try:
            simulation = self.graph_system.simulate_change(
                node_id=str(node_id),
                change=proposed_change,
                dry_run=True,
                include_rollback=True,
                validate=True,
            )

            return {
                "simulation_id": simulation.id,
                "valid": simulation.is_valid,
                "affected_nodes": [n.id for n in simulation.affected_nodes],
                "constraint_violations": simulation.constraint_violations,
                "warnings": simulation.warnings,
                "rollback_available": simulation.can_rollback,
            }
        except Exception as e:
            print(f"Failed to simulate change: {e}")
            return {"error": str(e)}

    async def validate_rules(self) -> dict:
        """
        Validate all architecture rules using RefMemTree.
        """
        try:
            validation = self.graph_system.validate_rules(
                node_types=["module", "service", "component"],
                fail_fast=False,
                include_warnings=True,
            )

            return {
                "valid": validation.is_valid,
                "errors": [
                    {
                        "rule": err.rule_name,
                        "node_id": err.node_id,
                        "message": err.message,
                        "severity": err.severity,
                        "can_auto_fix": err.can_auto_fix,
                    }
                    for err in validation.errors
                ],
                "warnings": [
                    {
                        "rule": warn.rule_name,
                        "node_id": warn.node_id,
                        "message": warn.message,
                    }
                    for warn in validation.warnings
                ],
                "passed_rules": validation.passed_rules,
                "failed_rules": validation.failed_rules,
            }
        except Exception as e:
            print(f"Failed to validate rules: {e}")
            return {"error": str(e)}

    async def get_transitive_dependencies(
        self,
        node_id: UUID,
        max_depth: int = 10,
    ) -> Dict:
        """
        Get full dependency chains (transitive dependencies).
        """
        try:
            all_deps = self.graph_system.dependency_tracker.get_all_dependencies(str(node_id))

            return {
                "node_id": str(node_id),
                "dependency_chains": [],  # Not available in this version
                "total_unique_dependencies": len(all_deps),
                "max_depth": 0,  # Not available in this version
            }

        except Exception as e:
            return {"error": f"Failed to get transitive deps: {e}"}
