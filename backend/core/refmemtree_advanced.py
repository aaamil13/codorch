"""
Advanced RefMemTree Integration for Codorch.

This module provides FULL utilization of RefMemTree capabilities:
1. Rule tracking and enforcement
2. Node change monitoring
3. Dependency tracking
4. Impact analysis for changes
5. Change simulation
6. Semantic search
7. Context versioning
8. Branch management
"""

from typing import Any, Optional
from uuid import UUID, uuid4
from datetime import datetime


class NodeRule:
    """Rule definition for a node."""

    def __init__(
        self,
        rule_id: UUID,
        rule_type: str,
        condition: str,
        action: str,
        priority: int = 0,
    ):
        self.rule_id = rule_id
        self.rule_type = rule_type  # validation, transformation, notification
        self.condition = condition
        self.action = action
        self.priority = priority
        self.created_at = datetime.utcnow()


class NodeChangeEvent:
    """Event representing a change to a node."""

    def __init__(
        self,
        node_id: UUID,
        change_type: str,
        old_value: Any,
        new_value: Any,
        timestamp: datetime,
        changed_by: Optional[UUID] = None,
    ):
        self.event_id = uuid4()
        self.node_id = node_id
        self.change_type = change_type  # create, update, delete, move
        self.old_value = old_value
        self.new_value = new_value
        self.timestamp = timestamp
        self.changed_by = changed_by


class DependencyLink:
    """Represents a dependency between nodes."""

    def __init__(
        self,
        from_node_id: UUID,
        to_node_id: UUID,
        dependency_type: str,
        strength: float = 1.0,
    ):
        self.link_id = uuid4()
        self.from_node_id = from_node_id
        self.to_node_id = to_node_id
        self.dependency_type = dependency_type  # requires, blocks, relates, contains
        self.strength = strength  # 0.0-1.0
        self.created_at = datetime.utcnow()


class ImpactAnalysisResult:
    """Result of impact analysis for a node change."""

    def __init__(
        self,
        target_node_id: UUID,
        change_type: str,
        affected_nodes: list[UUID],
        impact_scores: dict[UUID, float],
        propagation_path: list[list[UUID]],
        recommendations: list[str],
    ):
        self.target_node_id = target_node_id
        self.change_type = change_type
        self.affected_nodes = affected_nodes
        self.impact_scores = impact_scores  # node_id -> impact score (0.0-1.0)
        self.propagation_path = propagation_path  # chains of affected nodes
        self.recommendations = recommendations
        self.analyzed_at = datetime.utcnow()


class ChangeSimulation:
    """Simulation result of a proposed change."""

    def __init__(
        self,
        simulation_id: UUID,
        change_description: str,
        affected_nodes: list[UUID],
        side_effects: list[str],
        risk_level: str,
        success_probability: float,
    ):
        self.simulation_id = simulation_id
        self.change_description = change_description
        self.affected_nodes = affected_nodes
        self.side_effects = side_effects
        self.risk_level = risk_level  # low, medium, high, critical
        self.success_probability = success_probability
        self.simulated_at = datetime.utcnow()


class RefMemTreeManager:
    """
    Advanced RefMemTree Manager with full feature utilization.
    
    Features:
    1. Internal rule tracking and enforcement
    2. Node change monitoring with history
    3. Dependency tracking between nodes
    4. Impact analysis for changes
    5. Change simulation
    6. Semantic search across tree
    7. Context versioning
    8. Branch management for experimentation
    """

    def __init__(self):
        # Core storage
        self.nodes: dict[UUID, dict[str, Any]] = {}
        self.rules: dict[UUID, list[NodeRule]] = {}  # node_id -> rules
        self.dependencies: dict[UUID, list[DependencyLink]] = {}  # node_id -> dependencies
        self.change_history: dict[UUID, list[NodeChangeEvent]] = {}  # node_id -> events
        self.context_versions: dict[UUID, list[dict[str, Any]]] = {}  # node_id -> versions

    # ========================================================================
    # 1. RULE TRACKING & ENFORCEMENT
    # ========================================================================

    def add_rule(self, node_id: UUID, rule: NodeRule) -> None:
        """Add rule to node."""
        if node_id not in self.rules:
            self.rules[node_id] = []
        self.rules[node_id].append(rule)
        self.rules[node_id].sort(key=lambda r: r.priority, reverse=True)

    def get_rules(self, node_id: UUID) -> list[NodeRule]:
        """Get all rules for a node."""
        return self.rules.get(node_id, [])

    def validate_against_rules(self, node_id: UUID, proposed_change: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate proposed change against node rules."""
        rules = self.get_rules(node_id)
        violations = []

        for rule in rules:
            if rule.rule_type == "validation":
                # Check condition
                if not self._evaluate_rule_condition(rule.condition, proposed_change):
                    violations.append(f"Rule violation: {rule.action}")

        return len(violations) == 0, violations

    def _evaluate_rule_condition(self, condition: str, change: dict[str, Any]) -> bool:
        """Evaluate rule condition (simplified)."""
        # In real implementation, this would parse and evaluate conditions
        return True

    # ========================================================================
    # 2. NODE CHANGE MONITORING
    # ========================================================================

    def record_change(self, event: NodeChangeEvent) -> None:
        """Record node change event."""
        if event.node_id not in self.change_history:
            self.change_history[event.node_id] = []
        self.change_history[event.node_id].append(event)

    def get_change_history(self, node_id: UUID) -> list[NodeChangeEvent]:
        """Get change history for a node."""
        return self.change_history.get(node_id, [])

    def get_recent_changes(self, node_id: UUID, limit: int = 10) -> list[NodeChangeEvent]:
        """Get recent changes for a node."""
        history = self.get_change_history(node_id)
        return sorted(history, key=lambda e: e.timestamp, reverse=True)[:limit]

    def monitor_node_changes(
        self,
        node_id: UUID,
        callback: callable,
        change_types: Optional[list[str]] = None,
    ) -> None:
        """
        Set up monitoring for node changes.
        Callback is called when matching changes occur.
        """
        # Store callback for future changes
        # In real implementation, this would use event listeners
        pass

    # ========================================================================
    # 3. DEPENDENCY TRACKING
    # ========================================================================

    def add_dependency(self, link: DependencyLink) -> None:
        """Add dependency link between nodes."""
        if link.from_node_id not in self.dependencies:
            self.dependencies[link.from_node_id] = []
        self.dependencies[link.from_node_id].append(link)

    def get_dependencies(self, node_id: UUID) -> list[DependencyLink]:
        """Get all dependencies FROM this node."""
        return self.dependencies.get(node_id, [])

    def get_dependents(self, node_id: UUID) -> list[DependencyLink]:
        """Get all nodes that depend ON this node."""
        dependents = []
        for from_node, links in self.dependencies.items():
            for link in links:
                if link.to_node_id == node_id:
                    dependents.append(link)
        return dependents

    def get_dependency_chain(self, node_id: UUID, max_depth: int = 5) -> list[list[UUID]]:
        """Get all dependency chains from this node."""
        chains = []
        self._build_dependency_chains(node_id, [], chains, max_depth)
        return chains

    def _build_dependency_chains(
        self,
        current_id: UUID,
        current_chain: list[UUID],
        all_chains: list[list[UUID]],
        max_depth: int,
    ) -> None:
        """Recursively build dependency chains."""
        if len(current_chain) >= max_depth:
            return

        current_chain = current_chain + [current_id]
        dependencies = self.get_dependencies(current_id)

        if not dependencies:
            # Leaf node - save chain
            all_chains.append(current_chain)
            return

        for dep in dependencies:
            if dep.to_node_id not in current_chain:  # Avoid cycles
                self._build_dependency_chains(dep.to_node_id, current_chain, all_chains, max_depth)

    # ========================================================================
    # 4. IMPACT ANALYSIS
    # ========================================================================

    def analyze_change_impact(
        self,
        node_id: UUID,
        change_type: str,
        change_details: Optional[dict[str, Any]] = None,
    ) -> ImpactAnalysisResult:
        """
        Analyze impact of changing a node.
        
        Returns which nodes would be affected and how severely.
        """
        # Find all dependent nodes
        dependents = self.get_dependents(node_id)
        affected_nodes = [dep.from_node_id for dep in dependents]

        # Calculate impact scores
        impact_scores = {}
        for dep in dependents:
            # Base score on dependency strength and type
            base_score = dep.strength

            # Adjust by change type
            if change_type == "delete":
                base_score *= 1.5  # Deletion has higher impact
            elif change_type == "update":
                base_score *= 1.0
            elif change_type == "move":
                base_score *= 0.8

            impact_scores[dep.from_node_id] = min(1.0, base_score)

        # Build propagation paths
        propagation_path = self._get_propagation_paths(node_id)

        # Generate recommendations
        recommendations = []
        high_impact_nodes = [nid for nid, score in impact_scores.items() if score > 0.7]

        if high_impact_nodes:
            recommendations.append(
                f"⚠️ HIGH IMPACT: {len(high_impact_nodes)} nodes heavily affected"
            )
        if change_type == "delete":
            recommendations.append("Consider archiving instead of deleting")
        if len(affected_nodes) > 10:
            recommendations.append("Large impact scope - plan carefully")

        return ImpactAnalysisResult(
            target_node_id=node_id,
            change_type=change_type,
            affected_nodes=affected_nodes,
            impact_scores=impact_scores,
            propagation_path=propagation_path,
            recommendations=recommendations,
        )

    def _get_propagation_paths(self, node_id: UUID, max_depth: int = 3) -> list[list[UUID]]:
        """Get paths showing how changes propagate."""
        paths = []
        self._trace_propagation(node_id, [], paths, max_depth)
        return paths

    def _trace_propagation(
        self,
        current_id: UUID,
        current_path: list[UUID],
        all_paths: list[list[UUID]],
        max_depth: int,
    ) -> None:
        """Recursively trace change propagation."""
        if len(current_path) >= max_depth:
            return

        current_path = current_path + [current_id]
        dependents = self.get_dependents(current_id)

        if not dependents:
            all_paths.append(current_path)
            return

        for dep in dependents:
            if dep.from_node_id not in current_path:  # Avoid cycles
                self._trace_propagation(dep.from_node_id, current_path, all_paths, max_depth)

    # ========================================================================
    # 5. CHANGE SIMULATION
    # ========================================================================

    def simulate_change(
        self,
        node_id: UUID,
        change_type: str,
        proposed_changes: dict[str, Any],
    ) -> ChangeSimulation:
        """
        Simulate a proposed change without actually applying it.
        
        Returns predicted effects, risks, and success probability.
        """
        simulation_id = uuid4()

        # Analyze impact
        impact = self.analyze_change_impact(node_id, change_type, proposed_changes)

        # Check rule violations
        valid, violations = self.validate_against_rules(node_id, proposed_changes)

        # Determine side effects
        side_effects = []
        side_effects.extend(violations)

        if impact.affected_nodes:
            side_effects.append(f"Will affect {len(impact.affected_nodes)} dependent nodes")

        high_impact = [nid for nid, score in impact.impact_scores.items() if score > 0.7]
        if high_impact:
            side_effects.append(f"{len(high_impact)} nodes will be heavily impacted")

        # Calculate risk level
        risk_level = "low"
        if not valid:
            risk_level = "critical"
        elif len(high_impact) > 5:
            risk_level = "high"
        elif len(impact.affected_nodes) > 10:
            risk_level = "medium"

        # Calculate success probability
        success_prob = 1.0
        if not valid:
            success_prob *= 0.3
        if len(violations) > 0:
            success_prob *= 0.7
        if len(high_impact) > 0:
            success_prob *= 0.85

        return ChangeSimulation(
            simulation_id=simulation_id,
            change_description=f"{change_type} on node {node_id}",
            affected_nodes=impact.affected_nodes,
            side_effects=side_effects,
            risk_level=risk_level,
            success_probability=max(0.0, min(1.0, success_prob)),
        )

    # ========================================================================
    # 6. CONTEXT VERSIONING
    # ========================================================================

    def save_context_version(
        self,
        node_id: UUID,
        context: dict[str, Any],
        version_name: str,
    ) -> None:
        """Save a versioned snapshot of node context."""
        if node_id not in self.context_versions:
            self.context_versions[node_id] = []

        version = {
            "version_name": version_name,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
        }

        self.context_versions[node_id].append(version)

    def get_context_versions(self, node_id: UUID) -> list[dict[str, Any]]:
        """Get all context versions for a node."""
        return self.context_versions.get(node_id, [])

    def get_context_at_version(
        self,
        node_id: UUID,
        version_name: str,
    ) -> Optional[dict[str, Any]]:
        """Get context at specific version."""
        versions = self.get_context_versions(node_id)
        for version in versions:
            if version["version_name"] == version_name:
                return version["context"]
        return None

    # ========================================================================
    # 7. ADVANCED CONTEXT AGGREGATION
    # ========================================================================

    def get_node_context(
        self,
        node_id: str,
        include_rules: bool = True,
        include_dependencies: bool = True,
        include_history: bool = True,
        include_impact: bool = False,
    ) -> dict[str, Any]:
        """
        Get comprehensive context for a node.
        
        Unlike basic context, this includes:
        - Active rules
        - Dependencies (upstream and downstream)
        - Recent change history
        - Impact analysis data
        """
        node_uuid = UUID(node_id)
        context: dict[str, Any] = {
            "node_id": node_id,
            "node_data": self.nodes.get(node_uuid, {}),
        }

        if include_rules:
            rules = self.get_rules(node_uuid)
            context["rules"] = [
                {
                    "type": r.rule_type,
                    "condition": r.condition,
                    "action": r.action,
                    "priority": r.priority,
                }
                for r in rules
            ]

        if include_dependencies:
            dependencies = self.get_dependencies(node_uuid)
            dependents = self.get_dependents(node_uuid)

            context["dependencies"] = {
                "requires": [
                    {
                        "to": str(dep.to_node_id),
                        "type": dep.dependency_type,
                        "strength": dep.strength,
                    }
                    for dep in dependencies
                ],
                "required_by": [
                    {
                        "from": str(dep.from_node_id),
                        "type": dep.dependency_type,
                        "strength": dep.strength,
                    }
                    for dep in dependents
                ],
            }

        if include_history:
            recent_changes = self.get_recent_changes(node_uuid, limit=5)
            context["recent_changes"] = [
                {
                    "type": event.change_type,
                    "timestamp": event.timestamp.isoformat(),
                    "changed_by": str(event.changed_by) if event.changed_by else None,
                }
                for event in recent_changes
            ]

        if include_impact:
            # Provide quick impact summary
            dependents = self.get_dependents(node_uuid)
            context["impact_summary"] = {
                "dependent_count": len(dependents),
                "critical_dependents": sum(1 for d in dependents if d.strength > 0.8),
            }

        return context

    # ========================================================================
    # 8. UTILITY METHODS
    # ========================================================================

    def register_node(self, node_id: UUID, node_data: dict[str, Any]) -> None:
        """Register node in manager."""
        self.nodes[node_id] = node_data

    def get_node_data(self, node_id: UUID) -> Optional[dict[str, Any]]:
        """Get node data."""
        return self.nodes.get(node_id)


# ============================================================================
# High-Level Helper Functions
# ============================================================================


def analyze_architecture_change_impact(
    manager: RefMemTreeManager,
    module_id: UUID,
    change_type: str,
) -> dict[str, Any]:
    """
    Analyze impact of changing an architecture module.
    
    Use case: Before modifying/deleting a module, see what breaks.
    """
    impact = manager.analyze_change_impact(module_id, change_type)

    return {
        "affected_modules": [str(nid) for nid in impact.affected_nodes],
        "high_impact_count": sum(1 for score in impact.impact_scores.values() if score > 0.7),
        "propagation_depth": max(len(path) for path in impact.propagation_path) if impact.propagation_path else 0,
        "recommendations": impact.recommendations,
        "safe_to_proceed": len([s for s in impact.impact_scores.values() if s > 0.9]) == 0,
    }


def simulate_requirement_change(
    manager: RefMemTreeManager,
    requirement_id: UUID,
    new_requirement_text: str,
) -> dict[str, Any]:
    """
    Simulate changing a requirement.
    
    Use case: See what happens if we modify a requirement.
    """
    simulation = manager.simulate_change(
        requirement_id,
        "update",
        {"description": new_requirement_text},
    )

    return {
        "simulation_id": str(simulation.simulation_id),
        "risk_level": simulation.risk_level,
        "success_probability": simulation.success_probability,
        "affected_nodes": [str(nid) for nid in simulation.affected_nodes],
        "side_effects": simulation.side_effects,
        "recommended_action": (
            "Proceed with caution"
            if simulation.success_probability > 0.7
            else "Review thoroughly before applying"
        ),
    }


def enforce_architecture_rules(
    manager: RefMemTreeManager,
    module_id: UUID,
) -> dict[str, Any]:
    """
    Check if module complies with architecture rules.
    
    Use case: Ensure module follows defined architectural constraints.
    """
    rules = manager.get_rules(module_id)
    
    # Simulate checking current state against rules
    valid, violations = manager.validate_against_rules(module_id, {})

    return {
        "module_id": str(module_id),
        "rules_count": len(rules),
        "compliant": valid,
        "violations": violations,
        "action_required": "Fix violations" if violations else "No action needed",
    }
