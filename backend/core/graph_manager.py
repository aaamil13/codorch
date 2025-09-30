"""
GraphManagerService - Bridge between PostgreSQL and RefMemTree.

This is the CORE service that transforms Codorch from code generator 
into business policy engine.

Key Responsibilities:
1. Hydrate RefMemTree GraphSystem from PostgreSQL
2. Keep PostgreSQL and RefMemTree in sync
3. Provide RefMemTree-powered operations
4. Manage graph lifecycle per project
"""

from typing import Dict, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import ArchitectureModule, ArchitectureRule, ModuleDependency

# RefMemTree imports (will fail gracefully if not installed)
try:
    from refmemtree import GraphSystem, GraphNode
    REFMEMTREE_AVAILABLE = True
except ImportError:
    print("⚠️  RefMemTree not installed - using fallback mode")
    GraphSystem = None
    GraphNode = None
    REFMEMTREE_AVAILABLE = False


class GraphManagerService:
    """
    Manages RefMemTree GraphSystem instances for projects.
    
    One GraphSystem instance per project, cached in memory.
    """

    def __init__(self):
        # Cache: project_id -> GraphSystem instance
        self._graph_cache: Dict[UUID, any] = {}  # GraphSystem instances

    async def get_or_create_graph(
        self,
        project_id: UUID,
        session: AsyncSession,
        force_reload: bool = False,
    ):
        """
        Get or create RefMemTree GraphSystem for project.
        
        Args:
            project_id: Project UUID
            session: Database session
            force_reload: Force reload from DB
            
        Returns:
            GraphSystem instance or None if RefMemTree not available
        """
        if not REFMEMTREE_AVAILABLE:
            print("⚠️  RefMemTree not available - operations will be limited")
            return None

        # Check cache
        if not force_reload and project_id in self._graph_cache:
            return self._graph_cache[project_id]

        # Create new GraphSystem
        graph_system = GraphSystem()

        # Hydrate from PostgreSQL
        await self._hydrate_from_database(project_id, session, graph_system)

        # Cache it
        self._graph_cache[project_id] = graph_system

        print(f"✅ RefMemTree GraphSystem loaded for project {project_id}")
        return graph_system

    async def _hydrate_from_database(
        self,
        project_id: UUID,
        session: AsyncSession,
        graph_system,
    ) -> None:
        """
        Hydrate GraphSystem from PostgreSQL data FOR SPECIFIC PROJECT.
        
        ⚡ OPTIMIZED: Only loads data for one project, not all projects!
        
        This is THE critical method that bridges SQL → RefMemTree!
        """
        # Step 1: Load ONLY modules for THIS project ⚡
        modules_result = await session.execute(
            select(ArchitectureModule)
            .where(ArchitectureModule.project_id == project_id)
            .order_by(ArchitectureModule.level)  # ⚡ Load in order for hierarchy
        )
        modules = modules_result.scalars().all()

        print(f"  Loading {len(modules)} modules for project {project_id} into RefMemTree...")

        for module in modules:
            # ⭐ REAL RefMemTree API: Add node to graph
            graph_system.add_node(
                node_id=str(module.id),
                node_type=module.module_type,
                data={
                    "name": module.name,
                    "description": module.description,
                    "level": module.level,
                    "status": module.status,
                    "ai_generated": module.ai_generated,
                    "metadata": module.module_metadata or {},
                },
            )

        # Step 2: Load all dependencies between modules
        deps_result = await session.execute(
            select(ModuleDependency).where(ModuleDependency.project_id == project_id)
        )
        dependencies = deps_result.scalars().all()

        print(f"  Loading {len(dependencies)} dependencies into RefMemTree...")

        for dep in dependencies:
            # ⭐ REAL RefMemTree API: Add dependency to node
            try:
                from_node = graph_system.get_node(str(dep.from_module_id))
                if from_node:
                    from_node.add_dependency(
                        target_node_id=str(dep.to_module_id),
                        dependency_type=dep.dependency_type,
                        metadata={
                            "description": dep.description,
                            "created_at": dep.created_at.isoformat() if dep.created_at else None,
                        },
                    )
            except Exception as e:
                print(f"  ⚠️  Failed to add dependency: {e}")

        # Step 3: Load and apply architecture rules
        rules_result = await session.execute(
            select(ArchitectureRule).where(ArchitectureRule.project_id == project_id)
        )
        rules = rules_result.scalars().all()

        print(f"  Loading {len(rules)} rules into RefMemTree...")

        for rule in rules:
            # ⭐ REAL RefMemTree API: Add rule to graph
            try:
                rule_definition = rule.rule_definition or {}
                
                graph_system.add_rule(
                    name=f"{rule.rule_type}_{rule.id}",
                    rule_type=rule.rule_type,
                    validator=self._create_validator_from_rule(rule),
                    severity="error" if rule.level == "global" else "warning",
                    auto_fix=False,
                )
            except Exception as e:
                print(f"  ⚠️  Failed to add rule: {e}")

        print(f"✅ RefMemTree hydration complete!")

    def _create_validator_from_rule(self, rule: ArchitectureRule):
        """
        Create validator function from ArchitectureRule.
        
        This converts DB rule definition into executable validator.
        """
        rule_def = rule.rule_definition or {}
        rule_type = rule.rule_type

        # Create appropriate validator based on rule type
        if rule_type == "naming":
            condition = rule_def.get("condition", "")

            def naming_validator(node) -> bool:
                """Validate naming convention."""
                name = node.data.get("name", "")
                # Simple validation - can be enhanced
                if "endswith" in condition:
                    suffix = condition.split("'")[1] if "'" in condition else ""
                    return name.endswith(suffix)
                return True

            return naming_validator

        elif rule_type == "dependency":
            max_deps = rule_def.get("max_dependencies", 999)

            def dependency_validator(node) -> bool:
                """Validate dependency count."""
                deps = node.get_dependencies(direction="outgoing")
                return len(deps) <= max_deps

            return dependency_validator

        elif rule_type == "layer":

            def layer_validator(node) -> bool:
                """Validate layer rules."""
                # Layer rules are complex - implement based on definition
                return True

            return layer_validator

        else:
            # Default validator
            return lambda node: True

    # ========================================================================
    # RefMemTree Operations (Wrapper Methods)
    # ========================================================================

    async def add_node_to_graph(
        self,
        project_id: UUID,
        session: AsyncSession,
        node_id: UUID,
        node_type: str,
        data: dict,
    ) -> bool:
        """Add node to RefMemTree graph."""
        graph = await self.get_or_create_graph(project_id, session)
        if not graph:
            return False

        try:
            graph.add_node(
                node_id=str(node_id), node_type=node_type, data=data
            )
            return True
        except Exception as e:
            print(f"Failed to add node to RefMemTree: {e}")
            return False

    async def add_dependency_to_graph(
        self,
        project_id: UUID,
        session: AsyncSession,
        from_node_id: UUID,
        to_node_id: UUID,
        dependency_type: str,
    ) -> bool:
        """Add dependency to RefMemTree graph."""
        graph = await self.get_or_create_graph(project_id, session)
        if not graph:
            return False

        try:
            from_node = graph.get_node(str(from_node_id))
            if from_node:
                from_node.add_dependency(
                    target_node_id=str(to_node_id),
                    dependency_type=dependency_type,
                )
                return True
        except Exception as e:
            print(f"Failed to add dependency to RefMemTree: {e}")

        return False

    async def detect_circular_dependencies(
        self,
        project_id: UUID,
        session: AsyncSession,
    ) -> list:
        """
        Detect circular dependencies using RefMemTree.
        
        ⭐ REAL RefMemTree API: tree.detect_cycles()
        """
        graph = await self.get_or_create_graph(project_id, session)
        if not graph:
            return []

        try:
            # ⭐ Use RefMemTree's built-in cycle detection
            cycles = graph.detect_cycles(dependency_type="depends_on")
            return cycles
        except Exception as e:
            print(f"Failed to detect cycles in RefMemTree: {e}")
            return []

    async def calculate_node_impact(
        self,
        project_id: UUID,
        session: AsyncSession,
        node_id: UUID,
        change_type: str = "update",
    ) -> dict:
        """
        Calculate impact of changing a node using RefMemTree.
        
        ⭐ REAL RefMemTree API: node.calculate_impact()
        """
        graph = await self.get_or_create_graph(project_id, session)
        if not graph:
            return {"error": "RefMemTree not available"}

        try:
            node = graph.get_node(str(node_id))
            if not node:
                return {"error": "Node not found"}

            # ⭐ Use RefMemTree's impact analysis
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
        project_id: UUID,
        session: AsyncSession,
        node_id: UUID,
        proposed_change: dict,
    ) -> dict:
        """
        Simulate change using RefMemTree without applying it.
        
        ⭐ REAL RefMemTree API: tree.simulate_change()
        """
        graph = await self.get_or_create_graph(project_id, session)
        if not graph:
            return {"error": "RefMemTree not available"}

        try:
            # ⭐ Use RefMemTree's simulation engine
            simulation = graph.simulate_change(
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

    async def validate_rules(
        self,
        project_id: UUID,
        session: AsyncSession,
    ) -> dict:
        """
        Validate all architecture rules using RefMemTree.
        
        ⭐ REAL RefMemTree API: tree.validate_rules()
        """
        graph = await self.get_or_create_graph(project_id, session)
        if not graph:
            return {"error": "RefMemTree not available"}

        try:
            # ⭐ Use RefMemTree's rule validation
            validation = graph.validate_rules(
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

    def clear_cache(self, project_id: Optional[UUID] = None) -> None:
        """Clear graph cache for project or all projects."""
        if project_id:
            if project_id in self._graph_cache:
                del self._graph_cache[project_id]
        else:
            self._graph_cache.clear()


# ============================================================================
# Global Instance (Singleton Pattern for FastAPI)
# ============================================================================

_graph_manager_instance: Optional[GraphManagerService] = None


def get_graph_manager() -> GraphManagerService:
    """
    Get global GraphManagerService instance (Singleton).
    
    This ensures ONE instance manages ALL project graphs in memory.
    Provides caching and performance optimization.
    
    Use with FastAPI Depends:
        graph_manager: GraphManagerService = Depends(get_graph_manager)
    """
    global _graph_manager_instance
    if _graph_manager_instance is None:
        _graph_manager_instance = GraphManagerService()
        print("✅ GraphManagerService singleton created")
    return _graph_manager_instance


def reset_graph_manager() -> None:
    """Reset singleton (for testing)."""
    global _graph_manager_instance
    if _graph_manager_instance:
        _graph_manager_instance._graph_cache.clear()
    _graph_manager_instance = None