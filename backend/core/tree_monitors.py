"""
Tree Monitoring Service - Automatic monitoring using RefMemTree's add_monitor()

Implements automatic alerts for:
- Circular dependencies
- High complexity
- Broken dependencies
- Rule violations
"""

from typing import Dict, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from refmemtree import GraphSystem

from backend.core.graph_manager import GraphManagerService
from backend.core.event_emitter import get_event_emitter


class TreeMonitoringService:
    """
    Tree-wide monitoring using RefMemTree's add_monitor() API.

    Automatically checks conditions and triggers alerts.
    """

    def __init__(self, graph_manager: GraphManagerService):
        self.graph_manager = graph_manager
        self.event_emitter = get_event_emitter()
        self.active_monitors: Dict[UUID, List] = {}

    async def setup_project_monitors(
        self,
        project_id: UUID,
        session: AsyncSession,
    ) -> Dict:
        """
        Setup automatic monitoring for project.

        Uses REAL RefMemTree API: tree.add_monitor()

        Call this when project is opened/loaded.
        """
        try:
            _, _, analytics, _ = await self.graph_manager.get_or_create_services(project_id, session)
            graph = analytics.graph_system
            if not graph:
                return {"error": "RefMemTree not available"}

            monitors_added = []

            # ⭐ Monitor 1: Circular Dependencies
            try:
                graph.add_monitor(
                    name="circular_deps_check",
                    condition=lambda tree: len(tree.detect_cycles()) > 0,
                    action=lambda: self._alert_circular_deps(project_id),
                    check_interval=60,  # Check every 60 seconds
                )
                monitors_added.append("circular_deps_check")
            except Exception as e:
                print(f"Failed to add circular deps monitor: {e}")

            # ⭐ Monitor 2: High Complexity
            try:
                graph.add_monitor(
                    name="complexity_alert",
                    condition=lambda tree: self._check_high_complexity(tree),
                    action=lambda: self._alert_high_complexity(project_id),
                    check_interval=300,  # Check every 5 minutes
                )
                monitors_added.append("complexity_alert")
            except Exception as e:
                print(f"Failed to add complexity monitor: {e}")

            # ⭐ Monitor 3: Broken Dependencies
            try:
                graph.add_monitor(
                    name="broken_deps_check",
                    condition=lambda tree: self._check_broken_deps(tree),
                    action=lambda: self._alert_broken_deps(project_id),
                    check_interval=120,  # Check every 2 minutes
                )
                monitors_added.append("broken_deps_check")
            except Exception as e:
                print(f"Failed to add broken deps monitor: {e}")

            # ⭐ Monitor 4: Rule Violations
            try:
                graph.add_monitor(
                    name="rule_violations_check",
                    condition=lambda tree: not tree.validate_rules().is_valid,
                    action=lambda: self._alert_rule_violations(project_id),
                    check_interval=180,  # Check every 3 minutes
                )
                monitors_added.append("rule_violations_check")
            except Exception as e:
                print(f"Failed to add rule violations monitor: {e}")

            # Store active monitors
            self.active_monitors[project_id] = monitors_added

            return {
                "status": "success",
                "monitors_active": len(monitors_added),
                "monitor_names": monitors_added,
            }

        except Exception as e:
            return {"error": f"Failed to setup monitors: {e}"}

    def _check_high_complexity(self, tree: "GraphSystem") -> bool:
        """Check if tree complexity is too high."""
        try:
            complexity = tree.calculate_complexity()
            return complexity > 80
        except:
            return False

    def _check_broken_deps(self, tree: "GraphSystem") -> bool:
        """Check for broken dependencies."""
        try:
            broken = tree.find_broken_dependencies()
            return len(broken) > 0
        except:
            return False

    # ========================================================================
    # Alert Methods (triggered by monitors)
    # ========================================================================

    def _alert_circular_deps(self, project_id: UUID) -> None:
        """Alert for circular dependencies."""
        alert = {
            "project_id": str(project_id),
            "type": "circular_dependencies",
            "severity": "critical",
            "title": "⚠️ Circular Dependencies Detected",
            "message": "Architecture has circular dependencies - requires immediate attention",
            "timestamp": datetime.utcnow().isoformat(),
            "actions": [
                "Review architecture dependencies",
                "Remove circular references",
                "Validate architecture",
            ],
        }

        # Emit alert event
        self.event_emitter.emit("alert", alert)

    def _alert_high_complexity(self, project_id: UUID) -> None:
        """Alert for high complexity."""
        alert = {
            "project_id": str(project_id),
            "type": "high_complexity",
            "severity": "warning",
            "title": "📊 High Complexity Detected",
            "message": "Architecture complexity score > 80 - consider simplification",
            "timestamp": datetime.utcnow().isoformat(),
            "actions": [
                "Review complexity dashboard",
                "Identify hotspots",
                "Consider module split",
            ],
        }

        self.event_emitter.emit("alert", alert)

    def _alert_broken_deps(self, project_id: UUID) -> None:
        """Alert for broken dependencies."""
        alert = {
            "project_id": str(project_id),
            "type": "broken_dependencies",
            "severity": "error",
            "title": "🔗 Broken Dependencies Found",
            "message": "Some modules have dependencies to non-existent modules",
            "timestamp": datetime.utcnow().isoformat(),
            "actions": [
                "Review dependencies",
                "Remove broken links",
                "Update module references",
            ],
        }

        self.event_emitter.emit("alert", alert)

    def _alert_rule_violations(self, project_id: UUID) -> None:
        """Alert for rule violations."""
        alert = {
            "project_id": str(project_id),
            "type": "rule_violations",
            "severity": "warning",
            "title": "📏 Architecture Rule Violations",
            "message": "Some modules violate defined architecture rules",
            "timestamp": datetime.utcnow().isoformat(),
            "actions": [
                "Review rules",
                "Fix violations",
                "Update architecture",
            ],
        }

        self.event_emitter.emit("alert", alert)

    async def stop_project_monitors(self, project_id: UUID, session: AsyncSession) -> None:
        """Stop all monitors for project."""
        try:
            _, _, analytics, _ = await self.graph_manager.get_or_create_services(project_id, session)
            graph = analytics.graph_system
            if graph:
                # ⭐ Remove all monitors
                graph.remove_all_monitors()

            if project_id in self.active_monitors:
                del self.active_monitors[project_id]

        except Exception as e:
            print(f"Error stopping monitors: {e}")


# ============================================================================
# Convenience Functions
# ============================================================================


async def setup_monitoring_for_project(
    project_id: UUID,
    session: AsyncSession,
) -> Dict:
    """
    Setup automatic monitoring for project.

    Call this when project is opened.
    """
    from backend.core.graph_manager import get_graph_manager

    graph_manager = get_graph_manager()
    monitor_service = TreeMonitoringService(graph_manager)

    return await monitor_service.setup_project_monitors(project_id, session)
