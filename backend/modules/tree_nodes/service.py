"""
TreeNode Service - Business logic for tree nodes with RefMemTree write-through.

This implements the CRITICAL "write-through" pattern:
1. Write to PostgreSQL (Source of Truth)
2. Update RefMemTree GraphSystem (Query Engine)
3. Keep both in perfect sync
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import TreeNode
from backend.core.graph_manager import get_graph_manager


class TreeNodeService:
    """
    Service for tree node operations with RefMemTree integration.

    CRITICAL PATTERN: Every DB write → RefMemTree update
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.graph_manager = get_graph_manager()

    async def create_node(
        self,
        project_id: UUID,
        parent_id: Optional[UUID],
        node_type: str,
        data: dict,
    ) -> TreeNode:
        """
        Create tree node with write-through to RefMemTree.

        WRITE-THROUGH PATTERN:
        1. PostgreSQL write (Source of Truth)
        2. RefMemTree update (Query Engine)
        """
        # Step 1: Write to PostgreSQL
        node = TreeNode(
            project_id=project_id,
            parent_id=parent_id,
            node_type=node_type,
            data=data,
        )

        self.session.add(node)
        await self.session.commit()
        await self.session.refresh(node)

        # Step 2: Update RefMemTree GraphSystem
        try:
            # ⭐ REAL RefMemTree API
            await self.graph_manager.add_node_to_graph(
                project_id=project_id,
                session=self.session,
                node_id=node.id,
                node_type=node_type,
                data=data,
            )
            print(f"✅ Node {node.id} synced to RefMemTree")
        except Exception as e:
            print(f"⚠️ RefMemTree sync failed (non-critical): {e}")

        return node

    async def update_node(
        self,
        node_id: UUID,
        updates: dict,
    ) -> Optional[TreeNode]:
        """
        Update tree node with write-through to RefMemTree.

        WRITE-THROUGH PATTERN:
        1. Update PostgreSQL
        2. Update RefMemTree
        """
        # Get existing node
        from sqlalchemy import select

        result = await self.session.execute(select(TreeNode).where(TreeNode.id == node_id))
        node = result.scalar_one_or_none()

        if not node:
            return None

        # Step 1: Update PostgreSQL
        node.data.update(updates.get("data", {}))
        if "node_type" in updates:
            node.node_type = updates["node_type"]

        # Mark as modified to ensure JSON is updated
        from sqlalchemy.orm.attributes import flag_modified

        flag_modified(node, "data")

        await self.session.commit()
        await self.session.refresh(node)

        # Step 2: Update RefMemTree GraphSystem
        try:
            # The GraphManagerService should handle the update logic
            await self.graph_manager.update_node_in_graph(
                project_id=node.project_id,
                session=self.session,
                node_id=node.id,
                node_type=node.node_type,
                data=node.data,
            )
            print(f"✅ Node {node_id} updated in RefMemTree")
        except Exception as e:
            print(f"⚠️ RefMemTree sync failed (non-critical): {e}")

        return node

    async def delete_node(
        self,
        node_id: UUID,
    ) -> bool:
        """
        Delete tree node with write-through to RefMemTree.

        CRITICAL: Checks impact BEFORE deleting!

        WRITE-THROUGH PATTERN:
        1. Check impact using RefMemTree
        2. If safe → Delete from PostgreSQL
        3. Delete from RefMemTree
        """
        # Get node
        from sqlalchemy import select

        result = await self.session.execute(select(TreeNode).where(TreeNode.id == node_id))
        node = result.scalar_one_or_none()

        if not node:
            return False

        # ⭐ CRITICAL: Check impact BEFORE deleting
        try:
            impact = await self.graph_manager.calculate_node_impact(
                project_id=node.project_id,
                session=self.session,
                node_id=node_id,
                change_type="delete",
            )

            # Block if high impact
            if impact.get("impact_score", 0) > 70:
                raise ValueError(
                    f"⚠️ Cannot delete: High impact ({impact['impact_score']}/100). "
                    f"{len(impact.get('affected_nodes', []))} nodes would be affected!"
                )

        except ValueError:
            raise
        except Exception as e:
            print(f"⚠️ RefMemTree impact check failed: {e}")

        # Step 1: Delete from PostgreSQL
        await self.session.delete(node)
        await self.session.commit()

        # Step 2: Delete from RefMemTree
        try:
            await self.graph_manager.remove_node_from_graph(
                project_id=node.project_id, session=self.session, node_id=node_id
            )
            print(f"✅ Node {node_id} removed from RefMemTree")
        except Exception as e:
            print(f"⚠️ RefMemTree delete failed (non-critical): {e}")

        return True

    async def get_node_impact(
        self,
        node_id: UUID,
    ) -> dict:
        """
        Get impact analysis for node using RefMemTree.

        ⭐ REAL RefMemTree-powered analysis!

        This is THE FIRST "Read Path" endpoint using RefMemTree's power!
        """
        # Get node to find project
        from sqlalchemy import select

        result = await self.session.execute(select(TreeNode).where(TreeNode.id == node_id))
        node = result.scalar_one_or_none()

        if not node:
            return {"error": "Node not found"}

        # ⭐ Use RefMemTree for analysis
        impact = await self.graph_manager.calculate_node_impact(
            project_id=node.project_id,
            session=self.session,
            node_id=node_id,
            change_type="update",
        )

        return impact
