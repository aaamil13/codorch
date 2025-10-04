"""
RefMemTree Advanced Integration for Architecture Module.

This module demonstrates FULL use of RefMemTree capabilities:
- Rule enforcement for architecture
- Change impact analysis before modifications
- Dependency tracking between modules
- Change simulation
"""

from uuid import UUID
from typing import Any, Optional

from backend.core.refmemtree_advanced import (
    RefMemTreeManager,
    NodeRule,
    DependencyLink,
    analyze_architecture_change_impact,
    simulate_requirement_change,
    enforce_architecture_rules,
)


class ArchitectureRefMemTreeIntegration:
    """Integration layer for Architecture Module with RefMemTree."""

    def __init__(self):
        self.manager = RefMemTreeManager()

    # ========================================================================
    # MODULE REGISTRATION WITH RULES
    # ========================================================================

    def register_architecture_module(
        self,
        module_id: UUID,
        module_data: dict[str, Any],
        architectural_rules: list[dict[str, Any]],
    ) -> None:
        """
        Register architecture module with its rules.

        Example:
            module_data = {"name": "UserService", "type": "service", ...}
            architectural_rules = [
                {
                    "type": "naming",
                    "condition": "name must end with 'Service'",
                    "action": "enforce_naming_convention"
                },
                {
                    "type": "dependency",
                    "condition": "cannot depend on UI layer",
                    "action": "block_invalid_dependency"
                }
            ]
        """
        # Register node
        self.manager.register_node(module_id, module_data)

        # Add rules
        for rule_data in architectural_rules:
            rule = NodeRule(
                rule_id=UUID(int=0),  # Would be generated
                rule_type=rule_data.get("type", "validation"),
                condition=rule_data.get("condition", ""),
                action=rule_data.get("action", ""),
                priority=rule_data.get("priority", 0),
            )
            self.manager.add_rule(module_id, rule)

    # ========================================================================
    # DEPENDENCY TRACKING
    # ========================================================================

    def track_module_dependency(
        self,
        from_module_id: UUID,
        to_module_id: UUID,
        dependency_type: str,
        strength: float = 1.0,
    ) -> None:
        """
        Track dependency between modules.

        Use case: When creating ModuleDependency in DB, also track in RefMemTree
        for impact analysis.

        Example:
            track_module_dependency(
                from_module_id=user_service_id,
                to_module_id=database_layer_id,
                dependency_type="uses",
                strength=0.9  # High coupling
            )
        """
        link = DependencyLink(
            from_node_id=from_module_id,
            to_node_id=to_module_id,
            dependency_type=dependency_type,
            strength=strength,
        )
        self.manager.add_dependency(link)

    def get_module_dependencies_analysis(self, module_id: UUID) -> dict[str, Any]:
        """
        Get comprehensive dependency analysis.

        Returns:
            - Direct dependencies
            - Indirect dependencies (chains)
            - Modules that depend on this module
            - Coupling strength analysis
        """
        dependencies = self.manager.get_dependencies(module_id)
        dependents = self.manager.get_dependents(module_id)
        chains = self.manager.get_dependency_chain(module_id)

        return {
            "module_id": str(module_id),
            "direct_dependencies": len(dependencies),
            "modules_depend_on_this": len(dependents),
            "dependency_chains": len(chains),
            "max_chain_depth": max(len(chain) for chain in chains) if chains else 0,
            "coupling_score": sum(d.strength for d in dependencies) / max(1, len(dependencies)),
            "is_critical": len(dependents) > 5,  # Many modules depend on this
        }

    # ========================================================================
    # IMPACT ANALYSIS BEFORE CHANGES
    # ========================================================================

    def analyze_module_modification_impact(
        self,
        module_id: UUID,
        modification_type: str = "update",
    ) -> dict[str, Any]:
        """
        Analyze impact BEFORE modifying a module.

        Use case: User wants to change a module - show what will be affected.

        Returns detailed impact analysis with recommendations.
        """
        return analyze_architecture_change_impact(
            self.manager,
            module_id,
            modification_type,
        )

    def analyze_module_deletion_impact(self, module_id: UUID) -> dict[str, Any]:
        """
        Specific analysis for module deletion.

        Use case: Before deleting module, show critical impact.
        """
        impact = self.analyze_module_modification_impact(module_id, "delete")

        # Add deletion-specific warnings
        if impact["high_impact_count"] > 0:
            impact["deletion_warning"] = (
                f"⚠️ CRITICAL: Deleting this module will break {impact['high_impact_count']} other modules!"
            )
            impact["recommended_action"] = "Archive instead of delete, or fix dependencies first"
        else:
            impact["deletion_warning"] = "Safe to delete - no critical dependencies"
            impact["recommended_action"] = "Proceed with deletion"

        return impact

    # ========================================================================
    # CHANGE SIMULATION
    # ========================================================================

    def simulate_architecture_change(
        self,
        module_id: UUID,
        proposed_changes: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Simulate proposed architecture changes.

        Use case: "What if I change this module's type from 'service' to 'component'?"

        Returns simulation with risk assessment.
        """
        simulation = self.manager.simulate_change(
            module_id,
            "update",
            proposed_changes,
        )

        return {
            "simulation_id": str(simulation.simulation_id),
            "risk_level": simulation.risk_level,
            "success_probability": f"{simulation.success_probability * 100:.1f}%",
            "affected_modules": len(simulation.affected_nodes),
            "side_effects": simulation.side_effects,
            "recommendation": (
                "✅ Low risk - safe to proceed"
                if simulation.risk_level == "low"
                else f"⚠️ {simulation.risk_level.upper()} risk - review carefully"
            ),
        }

    # ========================================================================
    # RULE ENFORCEMENT
    # ========================================================================

    def validate_module_against_rules(
        self,
        module_id: UUID,
        proposed_changes: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Validate module against defined architectural rules.

        Use case: Before saving module changes, check if they violate rules.

        Example rules:
        - "Service modules must end with 'Service'"
        - "UI components cannot depend on database layer"
        - "Maximum 5 dependencies per module"
        """
        return enforce_architecture_rules(self.manager, module_id)


# ============================================================================
# Usage Examples
# ============================================================================


def example_usage():
    """
    Example of how to use RefMemTree advanced features in Architecture Module.
    """
    integration = ArchitectureRefMemTreeIntegration()

    # Example 1: Register module with rules
    module_id = UUID(int=123)
    integration.register_architecture_module(
        module_id=module_id,
        module_data={"name": "UserService", "type": "service"},
        architectural_rules=[
            {
                "type": "naming",
                "condition": "name.endswith('Service')",
                "action": "Enforce naming convention",
                "priority": 10,
            },
            {
                "type": "dependency",
                "condition": "max_dependencies <= 5",
                "action": "Limit module coupling",
                "priority": 5,
            },
        ],
    )

    # Example 2: Track dependency
    database_id = UUID(int=456)
    integration.track_module_dependency(
        from_module_id=module_id,
        to_module_id=database_id,
        dependency_type="uses",
        strength=0.9,  # High coupling
    )

    # Example 3: Analyze impact before deletion
    impact = integration.analyze_module_deletion_impact(module_id)
    print(f"Deletion impact: {impact}")

    # Example 4: Simulate change
    simulation = integration.simulate_architecture_change(
        module_id,
        {"type": "component"},  # Change from service to component
    )
    print(f"Simulation result: {simulation}")

    # Example 5: Validate against rules
    validation = integration.validate_module_against_rules(module_id)
    print(f"Rule validation: {validation}")
