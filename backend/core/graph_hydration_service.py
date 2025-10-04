from typing import Dict, Optional, List, Any, Callable, Type
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import ArchitectureModule, ArchitectureRule, ModuleDependency
from refmemtree import GraphSystem, GraphNode


class GraphHydrationService:
    def __init__(self, graph_system: GraphSystem):
        self.graph_system = graph_system

    async def hydrate_from_database(
        self,
        project_id: UUID,
        session: AsyncSession,
    ) -> None:
        """
        Hydrate GraphSystem from PostgreSQL data FOR SPECIFIC PROJECT.
        """
        # Step 1: Load ONLY modules for THIS project
        modules_result = await session.execute(
            select(ArchitectureModule)
            .where(ArchitectureModule.project_id == project_id)
            .order_by(ArchitectureModule.level)
        )
        modules = modules_result.scalars().all()

        for module in modules:
            self.graph_system.add_node(
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
        deps_result = await session.execute(select(ModuleDependency).where(ModuleDependency.project_id == project_id))
        dependencies = deps_result.scalars().all()

        for dep in dependencies:
            try:
                from_node = self.graph_system.get_node(str(dep.from_module_id))
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
        rules_result = await session.execute(select(ArchitectureRule).where(ArchitectureRule.project_id == project_id))
        rules = rules_result.scalars().all()

        for rule in rules:
            try:
                self.graph_system.add_rule(
                    name=f"{rule.rule_type}_{rule.id}",
                    rule_type=rule.rule_type,
                    validator=self._create_validator_from_rule(rule),
                    severity="error" if rule.level == "global" else "warning",
                    auto_fix=False,
                )
            except Exception as e:
                print(f"  ⚠️  Failed to add rule: {e}")

    def _create_validator_from_rule(self, rule: ArchitectureRule) -> Callable[[GraphNode], bool]:
        """
        Create validator function from ArchitectureRule.
        """
        rule_def = rule.rule_definition or {}
        rule_type = rule.rule_type

        if rule_type == "naming":
            condition = rule_def.get("condition", "")

            def naming_validator(node: GraphNode) -> bool:
                name: str = node.data.get("name", "")
                if "endswith" in condition:
                    suffix: str = condition.split("'")[1] if "'" in condition else ""
                    return name.endswith(suffix)
                return True

            return naming_validator

        elif rule_type == "dependency":
            max_deps: int = rule_def.get("max_dependencies", 999)

            def dependency_validator(node: GraphNode) -> bool:
                deps: list = node.get_dependencies(direction="outgoing")
                return len(deps) <= max_deps

            return dependency_validator

        elif rule_type == "layer":

            def layer_validator(node: GraphNode) -> bool:
                return True

            return layer_validator

        else:

            def default_validator(node: GraphNode) -> bool:
                return True

            return default_validator
