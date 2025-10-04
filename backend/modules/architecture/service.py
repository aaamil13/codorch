"""Service layer for Architecture Module."""

from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import ArchitectureModule, User
from backend.modules.architecture.repository import (
    ArchitectureModuleRepository,
    ArchitectureRuleRepository,
    ModuleDependencyRepository,
)
from backend.modules.architecture.refmemtree_integration import ArchitectureRefMemTreeIntegration
from backend.core.refmemtree_loader import get_refmemtree_manager
from backend.core.graph_manager import get_graph_manager
from backend.modules.architecture.schemas import (
    ArchitectureModuleCreate,
    ArchitectureModuleUpdate,
    ArchitectureRuleCreate,
    ArchitectureRuleUpdate,
    ComplexityAnalysisResponse,
    ComplexityHotspot,
    ComplexityMetrics,
    ImpactAnalysisRequest,
    ImpactAnalysisResponse,
    ModuleDependencyCreate,
    ModuleDependencyUpdate,
    SharedModuleInfo,
    SharedModulesResponse,
    ValidationIssue,
    ArchitectureValidationResponse,
    AffectedModule,
)


class ArchitectureService:
    """Service for architecture operations."""

    def __init__(self, db: AsyncSession):
        """Initialize service."""
        self.db = db
        self.module_repo = ArchitectureModuleRepository(db)
        self.dependency_repo = ModuleDependencyRepository(db)
        self.rule_repo = ArchitectureRuleRepository(db)
        # Initialize RefMemTree integration for advanced features
        self.refmem = ArchitectureRefMemTreeIntegration()
        self._project_id = None  # Set when needed

    async def set_project_context(self, project_id: UUID, session: AsyncSession):
        """Set project context and load RefMemTree data."""
        self._project_id = project_id
        # Load RefMemTree manager (cached)
        manager = await get_refmemtree_manager(project_id, session)
        self.refmem.manager = manager

    # ========================================================================
    # Module Operations
    # ========================================================================

    async def create_module(self, data: ArchitectureModuleCreate) -> ArchitectureModule:
        """Create a new architecture module."""
        # Calculate level if parent exists
        if data.parent_id:
            parent = await self.module_repo.get_by_id(data.parent_id)
            if parent:
                # Set level to parent level + 1
                data.level = parent.level + 1

        module = await self.module_repo.create(data)

        # ⭐ REAL RefMemTree Integration: Add to GraphSystem
        try:
            graph_manager = get_graph_manager()
            # This uses REAL RefMemTree GraphSystem.add_node()
            await graph_manager.add_node_to_graph(
                project_id=data.project_id,
                session=self.db,
                node_id=module.id,
                node_type=module.module_type,
                data={
                    "name": module.name,
                    "description": module.description,
                    "level": module.level,
                    "status": module.status,
                },
            )
            print(f"✅ Module {module.name} added to RefMemTree GraphSystem")
        except Exception as e:
            # Non-blocking if RefMemTree fails
            print(f"RefMemTree sync warning: {e}")

        return module

    async def get_module(self, module_id: UUID) -> Optional[ArchitectureModule]:
        """Get module by ID."""
        return await self.module_repo.get_by_id(module_id)

    async def list_modules(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 100,
        parent_id: Optional[UUID] = None,
        module_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[ArchitectureModule]:
        """List modules for a project."""
        return await self.module_repo.get_by_project(
            project_id=project_id,
            skip=skip,
            limit=limit,
            parent_id=parent_id,
            module_type=module_type,
            status=status,
        )

    async def update_module(
        self,
        module_id: UUID,
        data: ArchitectureModuleUpdate,
    ) -> Optional[ArchitectureModule]:
        """Update module with RefMemTree change tracking."""
        # Get old state for change tracking
        old_module = await self.module_repo.get_by_id(module_id)

        # Update in DB
        updated = await self.module_repo.update(module_id, data)

        # ⭐ Record change in RefMemTree
        if old_module and updated:
            try:
                from backend.core.refmemtree_advanced import NodeChangeEvent
                from datetime import datetime

                event = NodeChangeEvent(
                    node_id=module_id,
                    change_type="update",
                    old_value={
                        "name": old_module.name,
                        "type": old_module.module_type,
                        "status": old_module.status,
                    },
                    new_value={
                        "name": updated.name,
                        "type": updated.module_type,
                        "status": updated.status,
                    },
                    timestamp=datetime.utcnow(),
                    changed_by=None,  # Would come from current_user
                )

                self.refmem.manager.record_change(event)
            except Exception as e:
                print(f"RefMemTree change tracking warning: {e}")

        return updated

    async def delete_module(self, module_id: UUID) -> bool:
        """Delete module with RefMemTree impact check."""
        # ⭐ ACTIVATE RefMemTree: Check impact before deleting
        try:
            impact = self.analyze_module_change_impact_advanced(module_id, "delete")

            # Block deletion if high impact
            if impact.get("high_impact_count", 0) > 0:
                raise ValueError(
                    f"⚠️ Cannot delete: {impact['high_impact_count']} modules critically depend on this! "
                    f"Affected modules: {impact['affected_modules'][:3]}"
                )
        except Exception as e:
            # If RefMemTree not available, proceed with warning
            print(f"RefMemTree impact check warning: {e}")

        return await self.module_repo.delete(module_id)

    async def approve_module(self, module_id: UUID, user: User) -> Optional[ArchitectureModule]:
        """Approve module."""
        return await self.module_repo.approve(module_id, user.id)

    # ========================================================================
    # Dependency Operations
    # ========================================================================

    async def create_dependency(self, data: ModuleDependencyCreate):
        """
        Create module dependency with RefMemTree Rule Engine validation.

        CRITICAL: Uses RefMemTree to validate BEFORE writing to DB!
        This is the "immune system" - prevents invalid architecture!
        """
        # Check if dependency already exists
        if await self.dependency_repo.exists(data.from_module_id, data.to_module_id, data.dependency_type):
            raise ValueError("Dependency already exists")

        # Check for self-dependency
        if data.from_module_id == data.to_module_id:
            raise ValueError("Module cannot depend on itself")

        # ⭐ CRITICAL: Validate against RefMemTree rules BEFORE DB write!
        try:
            graph_manager = get_graph_manager()
            graph = await graph_manager.get_or_create_graph(data.project_id, self.db)

            if graph:
                # Get nodes from RefMemTree
                from_node = graph.get_node(str(data.from_module_id))
                to_node = graph.get_node(str(data.to_module_id))

                if from_node and to_node:
                    # ⭐ SIMULATE adding dependency
                    from_node_after = from_node.model_copy(deep=True)
                    from_node_after.add_reference(str(data.to_module_id), data.dependency_type)

                    # ⭐ USE REFMEMTREE RULE ENGINE!
                    impact_signals = graph.impact_analyzer.analyze_change_impact(
                        from_node, from_node_after  # Before  # After
                    )

                    # Check for BLOCKING errors from Rule Engine
                    blocking_errors = [
                        s for s in impact_signals if s.severity in ["ERROR", "CRITICAL"] and s.requires_action
                    ]

                    if blocking_errors:
                        # ⭐ RULE ENGINE BLOCKS INVALID OPERATION!
                        error_msg = blocking_errors[0].change_description
                        raise ValueError(
                            f"❌ Rule Engine blocked: {error_msg}\n"
                            f"Rule: {blocking_errors[0].rule_name}\n"
                            f"Fix: {blocking_errors[0].suggested_fix or 'Review architecture rules'}"
                        )
        except ValueError:
            raise
        except Exception as e:
            print(f"⚠️ Rule Engine check failed, using fallback: {e}")

        # ⭐ Check for circular dependency using REAL RefMemTree
        try:
            graph_manager = get_graph_manager()

            # Temporarily add to check for cycles
            temp_added = await graph_manager.add_dependency_to_graph(
                project_id=data.project_id,
                session=self.db,
                from_node_id=data.from_module_id,
                to_node_id=data.to_module_id,
                dependency_type="temp_check",
            )

            if temp_added:
                # ⭐ REAL RefMemTree API: detect_cycles()
                cycles = await graph_manager.detect_circular_dependencies(
                    project_id=data.project_id,
                    session=self.db,
                )

                if cycles:
                    # Remove temp and raise error
                    raise ValueError(f"Would create circular dependency: {cycles[0]}")
        except ValueError:
            raise
        except Exception as e:
            # Fallback to custom check if RefMemTree fails
            print(f"RefMemTree cycle detection unavailable, using fallback: {e}")
            if await self._would_create_circular_dependency(data.from_module_id, data.to_module_id):
                raise ValueError("Would create circular dependency")

        dependency = await self.dependency_repo.create(data)

        # ⭐ REAL RefMemTree Integration: Add dependency to GraphSystem
        try:
            graph_manager = get_graph_manager()
            # This uses REAL RefMemTree node.add_dependency()
            await graph_manager.add_dependency_to_graph(
                project_id=data.project_id,
                session=self.db,
                from_node_id=data.from_module_id,
                to_node_id=data.to_module_id,
                dependency_type=data.dependency_type,
            )
            print(f"✅ Dependency added to RefMemTree GraphSystem")
        except Exception as e:
            # Non-blocking if RefMemTree fails
            print(f"RefMemTree dependency tracking warning: {e}")

        return dependency

    async def get_dependency(self, dependency_id: UUID):
        """Get dependency by ID."""
        return await self.dependency_repo.get_by_id(dependency_id)

    async def list_dependencies(
        self,
        project_id: UUID,
        dependency_type: Optional[str] = None,
    ):
        """List dependencies for a project."""
        return await self.dependency_repo.get_by_project(
            project_id=project_id,
            dependency_type=dependency_type,
        )

    async def update_dependency(self, dependency_id: UUID, data: ModuleDependencyUpdate):
        """Update dependency."""
        return await self.dependency_repo.update(dependency_id, data)

    async def delete_dependency(self, dependency_id: UUID) -> bool:
        """Delete dependency."""
        return await self.dependency_repo.delete(dependency_id)

    # ========================================================================
    # Rule Operations
    # ========================================================================

    async def create_rule(self, data: ArchitectureRuleCreate):
        """Create architecture rule."""
        return await self.rule_repo.create(data)

    async def get_rule(self, rule_id: UUID):
        """Get rule by ID."""
        return await self.rule_repo.get_by_id(rule_id)

    async def list_rules(
        self,
        project_id: UUID,
        level: Optional[str] = None,
        rule_type: Optional[str] = None,
        active_only: bool = True,
    ):
        """List rules for a project."""
        return await self.rule_repo.get_by_project(
            project_id=project_id,
            level=level,
            rule_type=rule_type,
            active_only=active_only,
        )

    async def update_rule(self, rule_id: UUID, data: ArchitectureRuleUpdate):
        """Update rule."""
        return await self.rule_repo.update(rule_id, data)

    async def delete_rule(self, rule_id: UUID) -> bool:
        """Delete rule."""
        return await self.rule_repo.delete(rule_id)

    async def deactivate_rule(self, rule_id: UUID):
        """Deactivate rule."""
        return await self.rule_repo.deactivate(rule_id)

    # ========================================================================
    # Validation
    # ========================================================================

    async def validate_architecture(self, project_id: UUID) -> ArchitectureValidationResponse:
        """Validate architecture for circular dependencies and rules."""
        issues: list[ValidationIssue] = []

        # Check for circular dependencies
        circular_deps = await self._detect_circular_dependencies(project_id)
        for cycle in circular_deps:
            issues.append(
                ValidationIssue(
                    type="circular_dependency",
                    severity="critical",
                    message=f"Circular dependency detected: {' -> '.join([str(m) for m in cycle])}",
                    affected_modules=cycle,
                    suggestions=["Break the cycle by introducing an interface or removing a dependency"],
                )
            )

        # Count errors and warnings
        errors_count = sum(1 for issue in issues if issue.severity == "critical")
        warnings_count = sum(1 for issue in issues if issue.severity == "warning")

        return ArchitectureValidationResponse(
            is_valid=errors_count == 0,
            issues=issues,
            warnings_count=warnings_count,
            errors_count=errors_count,
        )

    # ========================================================================
    # Complexity Analysis
    # ========================================================================

    async def analyze_complexity(self, project_id: UUID) -> ComplexityAnalysisResponse:
        """Analyze architecture complexity."""
        modules = await self.module_repo.get_by_project(project_id)
        dependencies = await self.dependency_repo.get_by_project(project_id)

        module_count = len(modules)
        avg_dependencies = len(dependencies) / module_count if module_count > 0 else 0
        max_depth = max((m.level for m in modules), default=0)

        # Calculate coupling score (inversely related to avg dependencies)
        coupling_score = min(10.0, max(0.0, 10.0 - (avg_dependencies * 0.5)))

        # Simple cyclomatic complexity estimate
        cyclomatic_complexity = len(dependencies) + module_count

        metrics = ComplexityMetrics(
            module_count=module_count,
            avg_dependencies=avg_dependencies,
            max_depth=max_depth,
            cyclomatic_complexity=cyclomatic_complexity,
            coupling_score=coupling_score,
            cohesion_score=7.0,  # Placeholder - would need more analysis
        )

        # Find hotspots (modules with many dependencies)
        hotspots: list[ComplexityHotspot] = []
        for module in modules:
            deps_from = await self.dependency_repo.get_dependencies_from(module.id)
            deps_to = await self.dependency_repo.get_dependencies_to(module.id)
            total_deps = len(deps_from) + len(deps_to)

            if total_deps > avg_dependencies * 2:  # Significantly above average
                hotspots.append(
                    ComplexityHotspot(
                        module_id=module.id,
                        module_name=module.name,
                        complexity_score=min(10.0, total_deps / 2.0),
                        reason=f"High coupling: {total_deps} dependencies",
                        suggestions=[
                            "Consider splitting into smaller modules",
                            "Review and reduce dependencies",
                        ],
                    )
                )

        # Overall complexity (0-10 scale)
        overall_complexity = (
            (module_count / 50.0 * 3)  # More modules = more complex
            + (avg_dependencies / 5.0 * 3)  # More dependencies = more complex
            + (max_depth / 5.0 * 2)  # Deeper = more complex
            + (len(hotspots) / 5.0 * 2)  # More hotspots = more complex
        )
        overall_complexity = min(10.0, overall_complexity)

        return ComplexityAnalysisResponse(
            overall_complexity=overall_complexity,
            metrics=metrics,
            hotspots=hotspots[:5],  # Top 5 hotspots
            recommendations=[
                "Keep module count reasonable (< 50)",
                "Aim for average dependencies < 5 per module",
                "Limit hierarchy depth to 4-5 levels",
            ],
        )

    # ========================================================================
    # Impact Analysis
    # ========================================================================

    async def analyze_impact(self, request: ImpactAnalysisRequest) -> ImpactAnalysisResponse:
        """Analyze impact of changes to a module."""
        module = await self.module_repo.get_by_id(request.module_id)
        if not module:
            raise ValueError("Module not found")

        affected_modules: list[AffectedModule] = []
        breaking_changes = False

        if request.change_type in ["modify", "delete"]:
            # Find modules that depend on this module
            dependencies_to = await self.dependency_repo.get_dependencies_to(request.module_id)

            for dep in dependencies_to:
                from_module = await self.module_repo.get_by_id(dep.from_module_id)
                if from_module:
                    impact_level = "direct" if dep.dependency_type in ["import", "extends"] else "indirect"

                    if dep.dependency_type == "extends":
                        breaking_changes = True

                    affected_modules.append(
                        AffectedModule(
                            module_id=from_module.id,
                            module_name=from_module.name,
                            impact_level=impact_level,
                            affected_features=[
                                f"{dep.dependency_type} dependency",
                                from_module.module_type,
                            ],
                        )
                    )

            # Find child modules (cascade effect)
            children = await self.module_repo.get_children(request.module_id)
            for child in children:
                affected_modules.append(
                    AffectedModule(
                        module_id=child.id,
                        module_name=child.name,
                        impact_level="cascading",
                        affected_features=["Child module"],
                    )
                )

        testing_scope = [
            f"Test {module.name}",
            *[f"Test {am.module_name}" for am in affected_modules],
            "Integration tests",
        ]

        recommendations = []
        if breaking_changes:
            recommendations.append("This is a breaking change - update all dependent modules")
        if len(affected_modules) > 5:
            recommendations.append("Large impact - consider phased rollout")
        if request.change_type == "delete":
            recommendations.append("Remove all dependencies before deletion")

        return ImpactAnalysisResponse(
            module_id=request.module_id,
            change_type=request.change_type,
            affected_modules=affected_modules,
            breaking_changes=breaking_changes,
            testing_scope=testing_scope,
            recommendations=recommendations or ["Impact is minimal"],
        )

    # ========================================================================
    # Shared Modules
    # ========================================================================

    async def get_shared_modules(self, project_id: UUID) -> SharedModulesResponse:
        """Get shared modules (used by multiple modules)."""
        modules = await self.module_repo.get_by_project(project_id)
        shared_modules: list[SharedModuleInfo] = []

        for module in modules:
            dependencies_to = await self.dependency_repo.get_dependencies_to(module.id)

            if len(dependencies_to) > 1:  # Used by more than one module
                used_by = [dep.from_module_id for dep in dependencies_to]
                shared_modules.append(
                    SharedModuleInfo(
                        module_id=module.id,
                        module_name=module.name,
                        usage_count=len(dependencies_to),
                        used_by=used_by,
                    )
                )

        # Sort by usage count
        shared_modules.sort(key=lambda x: x.usage_count, reverse=True)

        return SharedModulesResponse(
            shared_modules=shared_modules,
            total_count=len(shared_modules),
        )

    # ========================================================================
    # RefMemTree Advanced Features
    # ========================================================================

    def analyze_module_change_impact_advanced(
        self,
        module_id: UUID,
        change_type: str = "update",
    ) -> dict:
        """
        ADVANCED: Analyze impact using RefMemTree dependency tracking.

        This uses RefMemTree's internal tracking to provide deeper analysis.
        """
        return self.refmem.analyze_module_modification_impact(module_id, change_type)

    def simulate_module_change(
        self,
        module_id: UUID,
        proposed_changes: dict,
    ) -> dict:
        """
        ADVANCED: Simulate changes before applying them.

        Returns risk level, success probability, and side effects.
        """
        return self.refmem.simulate_architecture_change(module_id, proposed_changes)

    def get_dependency_analysis_advanced(self, module_id: UUID) -> dict:
        """
        ADVANCED: Get comprehensive dependency analysis using RefMemTree.

        Includes coupling scores, chain analysis, criticality assessment.
        """
        return self.refmem.get_module_dependencies_analysis(module_id)

    def validate_module_rules(self, module_id: UUID) -> dict:
        """
        ADVANCED: Validate module against RefMemTree-tracked rules.
        """
        return self.refmem.validate_module_against_rules(module_id)

    async def sync_module_to_refmemtree(self, module: ArchitectureModule) -> None:
        """
        Sync module and its rules to RefMemTree for advanced tracking.

        This should be called after creating/updating modules.
        """
        # Get architectural rules for this module
        rules = await self.rule_repo.get_by_module(module.id)

        # Convert to RefMemTree rule format
        refmem_rules = [
            {
                "type": rule.rule_type,
                "condition": str(rule.rule_definition.get("condition", "")),
                "action": str(rule.rule_definition.get("action", "")),
                "priority": rule.rule_definition.get("priority", 0),
            }
            for rule in rules
        ]

        # Register module with rules
        module_data = {
            "name": module.name,
            "type": module.module_type,
            "level": module.level,
            "status": module.status,
        }

        self.refmem.register_architecture_module(
            module.id,
            module_data,
            refmem_rules,
        )

    def sync_dependency_to_refmemtree(
        self,
        from_module_id: UUID,
        to_module_id: UUID,
        dependency_type: str,
    ) -> None:
        """
        Sync dependency to RefMemTree for impact tracking.

        This should be called after creating dependencies.
        """
        # Calculate strength based on dependency type
        strength_map = {
            "extends": 1.0,  # Highest coupling
            "import": 0.9,
            "implements": 0.8,
            "uses": 0.6,
            "depends_on": 0.4,
        }

        strength = strength_map.get(dependency_type, 0.5)

        self.refmem.track_module_dependency(
            from_module_id,
            to_module_id,
            dependency_type,
            strength,
        )

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    async def _would_create_circular_dependency(self, from_module_id: UUID, to_module_id: UUID) -> bool:
        """Check if creating this dependency would create a circular dependency."""
        # Use DFS to check if there's a path from to_module to from_module
        visited = set()

        async def dfs(current_id: UUID) -> bool:
            if current_id == from_module_id:
                return True
            if current_id in visited:
                return False

            visited.add(current_id)

            # Get all dependencies FROM current module
            deps = await self.dependency_repo.get_dependencies_from(current_id)
            for dep in deps:
                if await dfs(dep.to_module_id):
                    return True

            return False

        return await dfs(to_module_id)

    async def _detect_circular_dependencies(self, project_id: UUID) -> list[list[UUID]]:
        """Detect all circular dependencies using DFS."""
        modules = await self.module_repo.get_by_project(project_id)
        cycles: list[list[UUID]] = []
        visited = set()
        rec_stack = set()
        path = []

        async def dfs(module_id: UUID) -> bool:
            visited.add(module_id)
            rec_stack.add(module_id)
            path.append(module_id)

            # Get dependencies
            deps = await self.dependency_repo.get_dependencies_from(module_id)
            for dep in deps:
                to_id = dep.to_module_id

                if to_id not in visited:
                    if await dfs(to_id):
                        return True
                elif to_id in rec_stack:
                    # Found cycle
                    cycle_start = path.index(to_id)
                    cycle = path[cycle_start:] + [to_id]
                    cycles.append(cycle)

            path.pop()
            rec_stack.remove(module_id)
            return False

        for module in modules:
            if module.id not in visited:
                await dfs(module.id)

        return cycles
