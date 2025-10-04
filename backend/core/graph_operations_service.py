from typing import Dict, Optional, List, Any, Callable, Type
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from refmemtree import GraphSystem, GraphNode


class GraphOperationsService:
    def __init__(self, graph_system: GraphSystem):
        self.graph_system = graph_system

    async def add_node_to_graph(
        self,
        node_id: UUID,
        node_type: str,
        data: dict,
    ) -> bool:
        """Add node to RefMemTree graph."""
        try:
            self.graph_system.add_node(node_id=str(node_id), node_type=node_type, data=data)
            return True
        except Exception as e:
            print(f"Failed to add node to RefMemTree: {e}")
            return False

    async def add_dependency_to_graph(
        self,
        from_node_id: UUID,
        to_node_id: UUID,
        dependency_type: str,
    ) -> bool:
        """Add dependency to RefMemTree graph."""
        try:
            from_node = self.graph_system.get_node(str(from_node_id))
            if from_node:
                from_node.add_dependency(
                    target_node_id=str(to_node_id),
                    dependency_type=dependency_type,
                )
                return True
        except Exception as e:
            print(f"Failed to add dependency to RefMemTree: {e}")

        return False

    async def update_node_in_graph(
        self,
        node_id: UUID,
        node_type: str,
        data: dict,
    ) -> bool:
        """Update node in RefMemTree graph."""
        try:
            node = self.graph_system.get_node(str(node_id))
            if node:
                node.node_type = node_type
                node.data = data
                # Trigger change analysis in RefMemTree if needed
                # node.on_change() 
                return True
            return False
        except Exception as e:
            print(f"Failed to update node in RefMemTree: {e}")
            return False

    async def remove_node_from_graph(
        self,
        node_id: UUID,
    ) -> bool:
        """Remove node from RefMemTree graph."""
        try:
            self.graph_system.remove_node(str(node_id))
            return True
        except Exception as e:
            print(f"Failed to remove node from RefMemTree: {e}")
            return False
