"""Repository pattern for Architecture Module."""

from typing import Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

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

    def __init__(self, db: Session):
        """Initialize repository."""
        self.db = db

    def create(self, data: ArchitectureModuleCreate) -> ArchitectureModule:
        """Create a new architecture module."""
        module = ArchitectureModule(**data.model_dump())
        self.db.add(module)
        self.db.commit()
        self.db.refresh(module)
        return module

    def get_by_id(self, module_id: UUID) -> Optional[ArchitectureModule]:
        """Get architecture module by ID."""
        return self.db.query(ArchitectureModule).filter(ArchitectureModule.id == module_id).first()

    def get_by_project(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 100,
        parent_id: Optional[UUID] = None,
        module_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[ArchitectureModule]:
        """Get architecture modules by project with filters."""
        query = self.db.query(ArchitectureModule).filter(ArchitectureModule.project_id == project_id)

        if parent_id is not None:
            query = query.filter(ArchitectureModule.parent_id == parent_id)

        if module_type:
            query = query.filter(ArchitectureModule.module_type == module_type)

        if status:
            query = query.filter(ArchitectureModule.status == status)

        return query.offset(skip).limit(limit).all()

    def get_root_modules(self, project_id: UUID) -> list[ArchitectureModule]:
        """Get root modules (modules without parent) for a project."""
        return (
            self.db.query(ArchitectureModule)
            .filter(
                ArchitectureModule.project_id == project_id,
                ArchitectureModule.parent_id.is_(None),
            )
            .all()
        )

    def get_children(self, parent_id: UUID) -> list[ArchitectureModule]:
        """Get child modules of a parent."""
        return (
            self.db.query(ArchitectureModule).filter(ArchitectureModule.parent_id == parent_id).all()
        )

    def update(self, module_id: UUID, data: ArchitectureModuleUpdate) -> Optional[ArchitectureModule]:
        """Update architecture module."""
        module = self.get_by_id(module_id)
        if not module:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(module, key, value)

        self.db.commit()
        self.db.refresh(module)
        return module

    def delete(self, module_id: UUID) -> bool:
        """Delete architecture module."""
        module = self.get_by_id(module_id)
        if not module:
            return False

        self.db.delete(module)
        self.db.commit()
        return True

    def approve(self, module_id: UUID, approved_by: UUID) -> Optional[ArchitectureModule]:
        """Approve architecture module."""
        from datetime import datetime

        module = self.get_by_id(module_id)
        if not module:
            return None

        module.status = "approved"
        module.approved_at = datetime.utcnow()
        module.approved_by = approved_by

        self.db.commit()
        self.db.refresh(module)
        return module

    def count_by_project(self, project_id: UUID) -> int:
        """Count modules in a project."""
        return self.db.query(ArchitectureModule).filter(ArchitectureModule.project_id == project_id).count()

    def get_by_level(self, project_id: UUID, level: int) -> list[ArchitectureModule]:
        """Get modules by level in hierarchy."""
        return (
            self.db.query(ArchitectureModule)
            .filter(
                ArchitectureModule.project_id == project_id,
                ArchitectureModule.level == level,
            )
            .all()
        )


class ModuleDependencyRepository:
    """Repository for ModuleDependency operations."""

    def __init__(self, db: Session):
        """Initialize repository."""
        self.db = db

    def create(self, data: ModuleDependencyCreate) -> ModuleDependency:
        """Create a new module dependency."""
        dependency = ModuleDependency(**data.model_dump())
        self.db.add(dependency)
        self.db.commit()
        self.db.refresh(dependency)
        return dependency

    def get_by_id(self, dependency_id: UUID) -> Optional[ModuleDependency]:
        """Get module dependency by ID."""
        return self.db.query(ModuleDependency).filter(ModuleDependency.id == dependency_id).first()

    def get_by_project(
        self,
        project_id: UUID,
        dependency_type: Optional[str] = None,
    ) -> list[ModuleDependency]:
        """Get module dependencies by project."""
        query = self.db.query(ModuleDependency).filter(ModuleDependency.project_id == project_id)

        if dependency_type:
            query = query.filter(ModuleDependency.dependency_type == dependency_type)

        return query.all()

    def get_dependencies_from(self, module_id: UUID) -> list[ModuleDependency]:
        """Get dependencies FROM a module (what this module depends on)."""
        return (
            self.db.query(ModuleDependency).filter(ModuleDependency.from_module_id == module_id).all()
        )

    def get_dependencies_to(self, module_id: UUID) -> list[ModuleDependency]:
        """Get dependencies TO a module (what depends on this module)."""
        return self.db.query(ModuleDependency).filter(ModuleDependency.to_module_id == module_id).all()

    def update(self, dependency_id: UUID, data: ModuleDependencyUpdate) -> Optional[ModuleDependency]:
        """Update module dependency."""
        dependency = self.get_by_id(dependency_id)
        if not dependency:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(dependency, key, value)

        self.db.commit()
        self.db.refresh(dependency)
        return dependency

    def delete(self, dependency_id: UUID) -> bool:
        """Delete module dependency."""
        dependency = self.get_by_id(dependency_id)
        if not dependency:
            return False

        self.db.delete(dependency)
        self.db.commit()
        return True

    def exists(self, from_module_id: UUID, to_module_id: UUID, dependency_type: str) -> bool:
        """Check if dependency exists."""
        return (
            self.db.query(ModuleDependency)
            .filter(
                ModuleDependency.from_module_id == from_module_id,
                ModuleDependency.to_module_id == to_module_id,
                ModuleDependency.dependency_type == dependency_type,
            )
            .first()
            is not None
        )


class ArchitectureRuleRepository:
    """Repository for ArchitectureRule operations."""

    def __init__(self, db: Session):
        """Initialize repository."""
        self.db = db

    def create(self, data: ArchitectureRuleCreate) -> ArchitectureRule:
        """Create a new architecture rule."""
        rule = ArchitectureRule(**data.model_dump())
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def get_by_id(self, rule_id: UUID) -> Optional[ArchitectureRule]:
        """Get architecture rule by ID."""
        return self.db.query(ArchitectureRule).filter(ArchitectureRule.id == rule_id).first()

    def get_by_project(
        self,
        project_id: UUID,
        level: Optional[str] = None,
        rule_type: Optional[str] = None,
        active_only: bool = True,
    ) -> list[ArchitectureRule]:
        """Get architecture rules by project."""
        query = self.db.query(ArchitectureRule).filter(ArchitectureRule.project_id == project_id)

        if level:
            query = query.filter(ArchitectureRule.level == level)

        if rule_type:
            query = query.filter(ArchitectureRule.rule_type == rule_type)

        if active_only:
            query = query.filter(ArchitectureRule.active == True)  # noqa: E712

        return query.all()

    def get_by_module(self, module_id: UUID, active_only: bool = True) -> list[ArchitectureRule]:
        """Get rules for a specific module."""
        query = self.db.query(ArchitectureRule).filter(ArchitectureRule.module_id == module_id)

        if active_only:
            query = query.filter(ArchitectureRule.active == True)  # noqa: E712

        return query.all()

    def get_global_rules(self, project_id: UUID, active_only: bool = True) -> list[ArchitectureRule]:
        """Get global rules for a project."""
        query = self.db.query(ArchitectureRule).filter(
            ArchitectureRule.project_id == project_id,
            ArchitectureRule.module_id.is_(None),
        )

        if active_only:
            query = query.filter(ArchitectureRule.active == True)  # noqa: E712

        return query.all()

    def update(self, rule_id: UUID, data: ArchitectureRuleUpdate) -> Optional[ArchitectureRule]:
        """Update architecture rule."""
        rule = self.get_by_id(rule_id)
        if not rule:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(rule, key, value)

        self.db.commit()
        self.db.refresh(rule)
        return rule

    def delete(self, rule_id: UUID) -> bool:
        """Delete architecture rule."""
        rule = self.get_by_id(rule_id)
        if not rule:
            return False

        self.db.delete(rule)
        self.db.commit()
        return True

    def deactivate(self, rule_id: UUID) -> Optional[ArchitectureRule]:
        """Deactivate rule without deleting."""
        rule = self.get_by_id(rule_id)
        if not rule:
            return None

        rule.active = False
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def count_by_type(self, project_id: UUID) -> dict[str, int]:
        """Count rules by type."""
        results = (
            self.db.query(ArchitectureRule.rule_type, func.count(ArchitectureRule.id))
            .filter(ArchitectureRule.project_id == project_id)
            .group_by(ArchitectureRule.rule_type)
            .all()
        )

        return {rule_type: count for rule_type, count in results}
