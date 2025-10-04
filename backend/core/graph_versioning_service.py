from typing import Dict, Optional, List, Any, Callable, Type
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from backend.lib.refmemtree.graph_system import GraphSystem, GraphNode


class GraphVersioningService:
    def __init__(self, graph_system: GraphSystem):
        self.graph_system = graph_system

    async def create_snapshot(
        self,
        name: str,
        description: str,
    ) -> str:
        """
        Create architecture snapshot using RefMemTree.
        """
        version_id = str(uuid4())
        self.graph_system.create_version(version_id=version_id, description=description)
        return version_id

    async def rollback_to_snapshot(
        self,
        version_id: str,
    ) -> Dict:
        """
        Rollback architecture to previous snapshot.
        """
        success = self.graph_system.rollback_to_version(version_id)
        if success:
            return {
                "status": "success",
                "version_id": version_id,
            }
        else:
            return {"status": "failed", "error": f"Failed to rollback to version {version_id}"}

    async def list_snapshots(self) -> List[Dict]:
        """
        List all snapshots for project.
        """
        versions = self.graph_system.list_versions()
        return [
            {
                "version_id": v.get("version_id"),
                "name": v.get("version_id"),  # No name in this version
                "description": v.get("description"),
                "created_at": v.get("created_at"),
                "node_count": 0,  # Not available in this version
            }
            for v in versions
        ]
