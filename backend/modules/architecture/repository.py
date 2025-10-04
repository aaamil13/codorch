"""Repository pattern for Architecture Module."""

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.db.models import ArchitectureModule, ArchitectureRule, ModuleDependency
from backend.modules.architecture.schemas import (
    ArchitectureModuleCreate,
    ArchitectureModuleUpdate,
    ArchitectureRuleCreate,
    ArchitectureRuleUpdate,
    ModuleDependencyCreate,
    ModuleDependencyUpdate,
)


class ArchitectureModuleRepository:
    """Repository for ArchitectureModule operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        self.db = db

    async def create(self, data: ArchitectureModuleCreate) -> ArchitectureModule:
        """Create a new architecture module."""
        module = ArchitectureModule(**data.model_dump())
        self.db.add(module)
        await self.db.commit()
        await self.db.refresh(module)
        return module

    async def get_by_id(self, module_id: UUID) -> Optional[ArchitectureModule]:
        """Get architecture module by ID."""
        result = await self.db.execute(select(ArchitectureModule).filter(ArchitectureModule.id == module_id))
        return result.scalars().first()

    async def get_by_project(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 100,
        parent_id: Optional[UUID] = None,
        module_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Sequence[ArchitectureModule]:
        """Get architecture modules by project with filters."""
        query = select(ArchitectureModule).filter(ArchitectureModule.project_id == project_id)

        if parent_id is not None:
            query = query.filter(ArchitectureModule.parent_id == parent_id)

        if module_type:
            query = query.filter(ArchitectureModule.module_type == module_type)

        if status:
            query = query.filter(ArchitectureModule.status == status)

        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def get_root_modules(self, project_id: UUID) -> Sequence[ArchitectureModule]:
        """Get root modules (modules without parent) for a project."""
        result = await self.db.execute(
            select(ArchitectureModule).filter(
                ArchitectureModule.project_id == project_id,
                ArchitectureModule.parent_id.is_(None),
            )
        )
        return result.scalars().all()

    async def get_children(self, parent_id: UUID) -> Sequence[ArchitectureModule]:
        """Get child modules of a parent."""
        result = await self.db.execute(select(ArchitectureModule).filter(ArchitectureModule.parent_id == parent_id))
        return result.scalars().all()

    async def update(self, module_id: UUID, data: ArchitectureModuleUpdate) -> Optional[ArchitectureModule]:
        """Update architecture module."""
        module = await self.get_by_id(module_id)
        if not module:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(module, key, value)

        await self.db.commit()
        await self.db.refresh(module)
        return module

    async def delete(self, module_id: UUID) -> bool:
        """Delete architecture module."""
        module = await self.get_by_id(module_id)
        if not module:
            return False

        await self.db.delete(module)
        await self.db.commit()
        return True

    async def approve(self, module_id: UUID, approved_by: UUID) -> Optional[ArchitectureModule]:
        """Approve architecture module."""
        from datetime import datetime

        module = await self.get_by_id(module_id)
        if not module:
            return None

        module.status = "approved"
        module.approved_at = datetime.utcnow()
        module.approved_by = approved_by

        await self.db.commit()
        await self.db.refresh(module)
        return module

    async def count_by_project(self, project_id: UUID) -> int:
        """Count modules in a project."""
        result = await self.db.execute(
            select(func.count()).select_from(ArchitectureModule).filter(ArchitectureModule.project_id == project_id)
        )
        return result.scalar_one()

    async def get_by_level(self, project_id: UUID, level: int) -> Sequence[ArchitectureModule]:
        """Get modules by level in hierarchy."""
        result = await self.db.execute(
            select(ArchitectureModule).filter(
                ArchitectureModule.project_id == project_id,
                ArchitectureModule.level == level,
            )
        )
        return result.scalars().all()


class ModuleDependencyRepository:
    """Repository for ModuleDependency operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        self.db = db

    async def create(self, data: ModuleDependencyCreate) -> ModuleDependency:
        """Create a new module dependency."""
        dependency = ModuleDependency(**data.model_dump())
        self.db.add(dependency)
        await self.db.commit()
        await self.db.refresh(dependency)
        return dependency

    async def get_by_id(self, dependency_id: UUID) -> Optional[ModuleDependency]:
        """Get module dependency by ID."""
        result = await self.db.execute(select(ModuleDependency).filter(ModuleDependency.id == dependency_id))
        return result.scalars().first()

    async def get_by_project(
        self,
        project_id: UUID,
        dependency_type: Optional[str] = None,
    ) -> Sequence[ModuleDependency]:
        """Get module dependencies by project."""
        query = select(ModuleDependency).filter(ModuleDependency.project_id == project_id)

        if dependency_type:
            query = query.filter(ModuleDependency.dependency_type == dependency_type)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_dependencies_from(self, module_id: UUID) -> Sequence[ModuleDependency]:
        """Get dependencies FROM a module (what this module depends on)."""
        result = await self.db.execute(select(ModuleDependency).filter(ModuleDependency.from_module_id == module_id))
        return result.scalars().all()

    async def get_dependencies_to(self, module_id: UUID) -> Sequence[ModuleDependency]:
        """Get dependencies TO a module (what depends on this module)."""
        result = await self.db.execute(select(ModuleDependency).filter(ModuleDependency.to_module_id == module_id))
        return result.scalars().all()

    async def update(self, dependency_id: UUID, data: ModuleDependencyUpdate) -> Optional[ModuleDependency]:
        """Update module dependency."""
        dependency = await self.get_by_id(dependency_id)
        if not dependency:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(dependency, key, value)

        await self.db.commit()
        await self.db.refresh(dependency)
        return dependency

    async def delete(self, dependency_id: UUID) -> bool:
        """Delete module dependency."""
        dependency = await self.get_by_id(dependency_id)
        if not dependency:
            return False

        await self.db.delete(dependency)
        await self.db.commit()
        return True

    async def exists(self, from_module_id: UUID, to_module_id: UUID, dependency_type: str) -> bool:
        """Check if dependency exists."""
        result = await self.db.execute(
            select(ModuleDependency).filter(
                ModuleDependency.from_module_id == from_module_id,
                ModuleDependency.to_module_id == to_module_id,
                ModuleDependency.dependency_type == dependency_type,
            )
        )
        return result.scalars().first() is not None


class ArchitectureRuleRepository:
    """Repository for ArchitectureRule operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository."""
        self.db = db

    async def create(self, data: ArchitectureRuleCreate) -> ArchitectureRule:
        """Create a new architecture rule."""
        rule = ArchitectureRule(**data.model_dump())
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def get_by_id(self, rule_id: UUID) -> Optional[ArchitectureRule]:
        """Get architecture rule by ID."""
        result = await self.db.execute(select(ArchitectureRule).filter(ArchitectureRule.id == rule_id))
        return result.scalars().first()

    async def get_by_project(
        self,
        project_id: UUID,
        level: Optional[str] = None,
        rule_type: Optional[str] = None,
        active_only: bool = True,
    ) -> Sequence[ArchitectureRule]:
        """Get architecture rules by project."""
        query = select(ArchitectureRule).filter(ArchitectureRule.project_id == project_id)

        if level:
            query = query.filter(ArchitectureRule.level == level)

        if rule_type:
            query = query.filter(ArchitectureRule.rule_type == rule_type)

        if active_only:
            query = query.filter(ArchitectureRule.active)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_module(self, module_id: UUID, active_only: bool = True) -> Sequence[ArchitectureRule]:
        """Get rules for a specific module."""
        query = select(ArchitectureRule).filter(ArchitectureRule.module_id == module_id)

        if active_only:
            query = query.filter(ArchitectureRule.active)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_global_rules(self, project_id: UUID, active_only: bool = True) -> Sequence[ArchitectureRule]:
        """Get global rules for a project."""
        query = select(ArchitectureRule).filter(
            ArchitectureRule.project_id == project_id,
            ArchitectureRule.module_id.is_(None),
        )

        if active_only:
            query = query.filter(ArchitectureRule.active)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update(self, rule_id: UUID, data: ArchitectureRuleUpdate) -> Optional[ArchitectureRule]:
        """Update architecture rule."""
        rule = await self.get_by_id(rule_id)
        if not rule:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(rule, key, value)

        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def delete(self, rule_id: UUID) -> bool:
        """Delete architecture rule."""
        rule = await self.get_by_id(rule_id)
        if not rule:
            return False

        await self.db.delete(rule)
        await self.db.commit()
        return True

    async def deactivate(self, rule_id: UUID) -> Optional[ArchitectureRule]:
        """Deactivate rule without deleting."""
        rule = await self.get_by_id(rule_id)
        if not rule:
            return None

        rule.active = False
        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def count_by_type(self, project_id: UUID) -> dict[str, int]:
        """Count rules by type."""
        results = await self.db.execute(
            select(ArchitectureRule.rule_type, func.count(ArchitectureRule.id))
            .filter(ArchitectureRule.project_id == project_id)
            .group_by(ArchitectureRule.rule_type)
        )

        return {rule_type: count for rule_type, count in results.all()}
