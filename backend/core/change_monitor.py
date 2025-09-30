"""
Change Monitor - Real-time change tracking using RefMemTree's node.on_change()

This implements RefMemTree's change monitoring capabilities for Codorch.
"""

from typing import Callable, Dict, List
from uuid import UUID
from datetime import datetime

from backend.core.graph_manager import GraphManagerService
from backend.core.event_emitter import get_event_emitter


class ChangeMonitor:
    """
    Monitors changes in architecture nodes using RefMemTree.
    
    Uses REAL RefMemTree API: node.on_change(callback)
    """

    def __init__(self, graph_manager: GraphManagerService):
        self.graph_manager = graph_manager
        self.event_emitter = get_event_emitter()
        self.callbacks: Dict[UUID, List[Callable]] = {}

    async def register_node_watcher(
        self,
        project_id: UUID,
        node_id: UUID,
        callback: Callable,
        session,
    ) -> bool:
        """
        Register watcher for node changes using RefMemTree.
        
        ⭐ Uses REAL RefMemTree API: node.on_change()
        
        Args:
            project_id: Project UUID
            node_id: Node to watch
            callback: Function to call on change
            session: DB session
            
        Returns:
            True if registered successfully
        """
        try:
            # Get RefMemTree graph
            graph = await self.graph_manager.get_or_create_graph(project_id, session)
            if not graph:
                return False

            # Get the node
            node = graph.get_node(str(node_id))
            if not node:
                print(f"Node {node_id} not found in RefMemTree")
                return False

            # ⭐ REAL RefMemTree API: node.on_change()
            node.on_change(
                lambda old_data, new_data: self._handle_change(
                    node_id, old_data, new_data, callback
                )
            )

            # Store callback reference
            if node_id not in self.callbacks:
                self.callbacks[node_id] = []
            self.callbacks[node_id].append(callback)

            print(f"✅ Change monitor registered for node {node_id}")
            return True

        except Exception as e:
            print(f"Failed to register change monitor: {e}")
            return False

    def _handle_change(
        self,
        node_id: UUID,
        old_data: dict,
        new_data: dict,
        callback: Callable,
    ) -> None:
        """
        Handle node change event from RefMemTree.
        
        Called automatically by RefMemTree when node changes.
        """
        # Build change info
        change_info = {
            "node_id": str(node_id),
            "old_data": old_data,
            "new_data": new_data,
            "changed_fields": self._get_changed_fields(old_data, new_data),
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Execute callback
        try:
            callback(change_info)
        except Exception as e:
            print(f"Error in change callback: {e}")

        # Emit global event
        self.event_emitter.emit("node_changed", change_info)

    def _get_changed_fields(self, old: dict, new: dict) -> List[str]:
        """Identify which fields changed."""
        changed = []
        all_keys = set(old.keys()) | set(new.keys())

        for key in all_keys:
            if old.get(key) != new.get(key):
                changed.append(key)

        return changed

    async def find_and_notify_dependents(
        self,
        project_id: UUID,
        node_id: UUID,
        change_info: dict,
        session,
    ) -> None:
        """
        Find dependent nodes and notify them of change.
        
        This is the CASCADE UPDATE feature.
        """
        try:
            graph = await self.graph_manager.get_or_create_graph(project_id, session)
            node = graph.get_node(str(node_id))

            if not node:
                return

            # ⭐ REAL RefMemTree API: get_dependencies()
            dependents = node.get_dependencies(direction="incoming")

            # Notify each dependent
            for dep in dependents:
                dependent_change = {
                    "dependent_node_id": dep.source_node_id,
                    "source_change": change_info,
                    "dependency_type": dep.dependency_type,
                    "requires_update": True,
                    "timestamp": datetime.utcnow().isoformat(),
                }

                # Emit event for dependent
                self.event_emitter.emit("dependent_needs_update", dependent_change)

        except Exception as e:
            print(f"Error notifying dependents: {e}")

    def unregister_all(self, node_id: UUID = None) -> None:
        """Unregister watchers."""
        if node_id:
            if node_id in self.callbacks:
                del self.callbacks[node_id]
        else:
            self.callbacks.clear()


# ============================================================================
# Convenience Functions
# ============================================================================


async def watch_module_changes(
    project_id: UUID,
    module_id: UUID,
    session,
    on_change: Callable,
) -> bool:
    """
    Convenience function to watch module changes.
    
    Usage:
        await watch_module_changes(
            project_id,
            module_id,
            session,
            on_change=lambda change: print(f"Module changed: {change}")
        )
    """
    from backend.core.graph_manager import get_graph_manager

    graph_manager = get_graph_manager()
    monitor = ChangeMonitor(graph_manager)

    return await monitor.register_node_watcher(
        project_id, module_id, on_change, session
    )
