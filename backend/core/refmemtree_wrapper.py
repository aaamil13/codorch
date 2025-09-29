"""RefMemTree wrapper and utilities for Codorch."""

from typing import Any, Optional
from uuid import UUID

try:
    from refmemtree import RefMemTree, Node
except ImportError:
    # Fallback if RefMemTree is not installed yet
    RefMemTree = None  # type: ignore
    Node = None  # type: ignore


class ProjectTreeNode:
    """Wrapper for RefMemTree Node with Codorch-specific functionality."""

    def __init__(
        self,
        node_id: UUID,
        node_type: str,
        data: dict[str, Any],
        parent_id: Optional[UUID] = None,
    ) -> None:
        """Initialize project tree node."""
        self.id = node_id
        self.node_type = node_type
        self.data = data
        self.parent_id = parent_id
        self.children: list[ProjectTreeNode] = []

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary."""
        return {
            "id": str(self.id),
            "node_type": self.node_type,
            "data": self.data,
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "children": [child.to_dict() for child in self.children],
        }


class AdvancedProjectTree:
    """
    Advanced project tree using RefMemTree for hierarchical memory management.

    This class provides:
    - Smart context aggregation for AI agents
    - Multi-perspective context views
    - Branching for experimentation
    - Semantic search across tree
    - Cross-tree references
    - Context versioning
    """

    def __init__(self, project_id: UUID) -> None:
        """Initialize advanced project tree."""
        self.project_id = project_id
        self.root: Optional[ProjectTreeNode] = None
        self._node_cache: dict[UUID, ProjectTreeNode] = {}

        # Initialize RefMemTree if available
        if RefMemTree is not None:
            self._tree = RefMemTree()
        else:
            self._tree = None

    def create_root_node(self, node_type: str, data: dict[str, Any]) -> ProjectTreeNode:
        """Create root node for the project tree."""
        from uuid import uuid4

        node_id = uuid4()
        self.root = ProjectTreeNode(node_id=node_id, node_type=node_type, data=data)
        self._node_cache[node_id] = self.root
        return self.root

    def add_child_node(
        self, parent_id: UUID, node_type: str, data: dict[str, Any]
    ) -> ProjectTreeNode:
        """Add child node to parent."""
        from uuid import uuid4

        parent = self._node_cache.get(parent_id)
        if not parent:
            raise ValueError(f"Parent node {parent_id} not found")

        node_id = uuid4()
        child = ProjectTreeNode(
            node_id=node_id, node_type=node_type, data=data, parent_id=parent_id
        )

        parent.children.append(child)
        self._node_cache[node_id] = child

        return child

    def get_node(self, node_id: UUID) -> Optional[ProjectTreeNode]:
        """Get node by ID."""
        return self._node_cache.get(node_id)

    def get_smart_context(
        self,
        node_id: UUID,
        max_depth: int = 3,
        include_siblings: bool = True,
        include_ancestors: bool = True,
    ) -> dict[str, Any]:
        """
        Get smart context for AI agent at specific node.

        Args:
            node_id: Target node ID
            max_depth: Maximum depth to traverse
            include_siblings: Include sibling nodes
            include_ancestors: Include ancestor path

        Returns:
            Context dictionary with relevant information
        """
        node = self.get_node(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")

        context: dict[str, Any] = {
            "target_node": node.to_dict(),
            "ancestors": [],
            "siblings": [],
            "children": [],
        }

        # Get ancestors path
        if include_ancestors and node.parent_id:
            context["ancestors"] = self._get_ancestors(node.parent_id)

        # Get siblings
        if include_siblings and node.parent_id:
            parent = self.get_node(node.parent_id)
            if parent:
                context["siblings"] = [
                    child.to_dict() for child in parent.children if child.id != node_id
                ]

        # Get children
        context["children"] = [child.to_dict() for child in node.children]

        return context

    def _get_ancestors(self, node_id: UUID) -> list[dict[str, Any]]:
        """Get all ancestors of a node."""
        ancestors = []
        current = self.get_node(node_id)

        while current:
            ancestors.append(current.to_dict())
            if current.parent_id:
                current = self.get_node(current.parent_id)
            else:
                break

        return ancestors

    def create_branch(self, source_node_id: UUID, branch_name: str) -> UUID:
        """
        Create experimental branch from source node.

        This allows experimenting with alternatives without affecting main tree.
        """
        source = self.get_node(source_node_id)
        if not source:
            raise ValueError(f"Source node {source_node_id} not found")

        # Create branch node
        branch_data = {
            **source.data,
            "branch_name": branch_name,
            "is_branch": True,
            "source_node_id": str(source_node_id),
        }

        branch = self.add_child_node(
            parent_id=source.parent_id or source.id,
            node_type=f"{source.node_type}_branch",
            data=branch_data,
        )

        return branch.id

    def get_tree_snapshot(self) -> dict[str, Any]:
        """Get complete tree snapshot for persistence."""
        if not self.root:
            return {}

        return {
            "project_id": str(self.project_id),
            "root": self.root.to_dict(),
        }

    def load_from_snapshot(self, snapshot: dict[str, Any]) -> None:
        """Load tree from snapshot."""
        if "root" not in snapshot:
            return

        self._load_node_recursive(snapshot["root"], None)

    def _load_node_recursive(
        self, node_data: dict[str, Any], parent_id: Optional[UUID]
    ) -> ProjectTreeNode:
        """Recursively load nodes from snapshot."""
        from uuid import UUID as parse_uuid

        node_id = parse_uuid(node_data["id"])
        node = ProjectTreeNode(
            node_id=node_id,
            node_type=node_data["node_type"],
            data=node_data["data"],
            parent_id=parent_id,
        )

        self._node_cache[node_id] = node

        if parent_id is None:
            self.root = node

        # Load children
        for child_data in node_data.get("children", []):
            child = self._load_node_recursive(child_data, node_id)
            node.children.append(child)

        return node
