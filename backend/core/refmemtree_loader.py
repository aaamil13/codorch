"""
RefMemTree Loader - Loads existing database data into RefMemTree on project open.

This is the CRITICAL component that bridges PostgreSQL ↔ RefMemTree.
"""

from typing import Dict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.refmemtree_advanced import DependencyLink, NodeRule, RefMemTreeManager
from backend.db.models import ArchitectureModule, ArchitectureRule, ModuleDependency


class RefMemTreeLoader:
    """
    Loads project data from PostgreSQL into RefMemTree.

    Call this when:
    - Project is first opened
    - User refreshes architecture
    - After major changes
    """

    async def load_project(
        self,
        project_id: UUID,
        session: AsyncSession,
    ) -> RefMemTreeManager:
        """
        Load complete project into RefMemTree.

        Returns initialized RefMemTreeManager with all data loaded.
        """
        manager = RefMemTreeManager()

        # Step 1: Load all architecture modules
        await self._load_modules(project_id, session, manager)

        # Step 2: Load all module dependencies
        await self._load_dependencies(project_id, session, manager)

        # Step 3: Load all architecture rules
        await self._load_rules(project_id, session, manager)

        return manager

    async def _load_modules(
        self,
        project_id: UUID,
        session: AsyncSession,
        manager: RefMemTreeManager,
    ) -> None:
        """Load all architecture modules into RefMemTree."""
        result = await session.execute(select(ArchitectureModule).where(ArchitectureModule.project_id == project_id))
        modules = result.scalars().all()

        for module in modules:
            # Register module in RefMemTree
            module_data = {
                "name": module.name,
                "type": module.module_type,
                "level": module.level,
                "status": module.status,
                "description": module.description,
                "ai_generated": module.ai_generated,
            }

            manager.register_node(module.id, module_data)

    async def _load_dependencies(
        self,
        project_id: UUID,
        session: AsyncSession,
        manager: RefMemTreeManager,
    ) -> None:
        """Load all module dependencies into RefMemTree."""
        result = await session.execute(select(ModuleDependency).where(ModuleDependency.project_id == project_id))
        dependencies = result.scalars().all()

        # Strength mapping based on dependency type
        strength_map = {
            "extends": 1.0,  # Highest coupling - inheritance
            "import": 0.9,  # High coupling - direct import
            "implements": 0.8,  # High coupling - interface implementation
            "uses": 0.6,  # Medium coupling - service usage
            "depends_on": 0.4,  # Low coupling - general dependency
        }

        for dep in dependencies:
            strength = strength_map.get(dep.dependency_type, 0.5)

            link = DependencyLink(
                from_node_id=dep.from_module_id,
                to_node_id=dep.to_module_id,
                dependency_type=dep.dependency_type,
                strength=strength,
            )

            manager.add_dependency(link)

    async def _load_rules(
        self,
        project_id: UUID,
        session: AsyncSession,
        manager: RefMemTreeManager,
    ) -> None:
        """Load all architecture rules into RefMemTree."""
        result = await session.execute(select(ArchitectureRule).where(ArchitectureRule.project_id == project_id))
        rules = result.scalars().all()

        for rule in rules:
            node_rule = NodeRule(
                rule_id=rule.id,
                rule_type=rule.rule_type,
                condition=str(rule.rule_definition.get("condition", "")),
                action=str(rule.rule_definition.get("action", "")),
                priority=rule.rule_definition.get("priority", 0),
            )

            # Add to specific module or store for global rules
            if rule.module_id:
                manager.add_rule(rule.module_id, node_rule)
            # Global rules would be stored separately

    async def get_loading_stats(
        self,
        project_id: UUID,
        session: AsyncSession,
    ) -> Dict:
        """Get statistics about what will be loaded."""
        # Count modules
        modules_result = await session.execute(
            select(ArchitectureModule).where(ArchitectureModule.project_id == project_id)
        )
        modules_count = len(list(modules_result.scalars().all()))

        # Count dependencies
        deps_result = await session.execute(select(ModuleDependency).where(ModuleDependency.project_id == project_id))
        deps_count = len(list(deps_result.scalars().all()))

        # Count rules
        rules_result = await session.execute(select(ArchitectureRule).where(ArchitectureRule.project_id == project_id))
        rules_count = len(list(rules_result.scalars().all()))

        return {
            "modules": modules_count,
            "dependencies": deps_count,
            "rules": rules_count,
            "estimated_load_time": f"{(modules_count + deps_count + rules_count) * 0.01:.2f}s",
        }


# ============================================================================
# Global RefMemTree Manager Cache
# ============================================================================

# In-memory cache of RefMemTree managers per project
_refmem_cache: Dict[UUID, RefMemTreeManager] = {}


async def get_refmemtree_manager(
    project_id: UUID,
    session: AsyncSession,
    force_reload: bool = False,
) -> RefMemTreeManager:
    """
    Get or create RefMemTreeManager for a project.

    Caches managers in memory for performance.

    Args:
        project_id: Project UUID
        session: Database session
        force_reload: Force reload from DB

    Returns:
        RefMemTreeManager instance with all data loaded
    """
    # Check cache
    if not force_reload and project_id in _refmem_cache:
        return _refmem_cache[project_id]

    # Load from database
    loader = RefMemTreeLoader()
    manager = await loader.load_project(project_id, session)

    # Cache it
    _refmem_cache[project_id] = manager

    return manager


def clear_refmemtree_cache(project_id: Optional[UUID] = None) -> None:
    """
    Clear RefMemTree cache.

    Args:
        project_id: Specific project to clear, or None for all
    """
    global _refmem_cache

    if project_id:
        if project_id in _refmem_cache:
            del _refmem_cache[project_id]
    else:
        _refmem_cache.clear()
