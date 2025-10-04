from typing import Dict, Optional, List, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.graph_hydration_service import GraphHydrationService
from backend.core.graph_operations_service import GraphOperationsService
from backend.core.graph_analytics_service import GraphAnalyticsService
from backend.core.graph_versioning_service import GraphVersioningService
from refmemtree import GraphSystem

class GraphManagerService:
    def __init__(self) -> None:
        self._graph_cache: Dict[UUID, GraphSystem] = {}
        self._hydration_services: Dict[UUID, GraphHydrationService] = {}
        self._operations_services: Dict[UUID, GraphOperationsService] = {}
        self._analytics_services: Dict[UUID, GraphAnalyticsService] = {}
        self._versioning_services: Dict[UUID, GraphVersioningService] = {}

    async def get_or_create_services(self, project_id: UUID, session: AsyncSession):
        if project_id not in self._graph_cache:
            graph_system = GraphSystem()
            self._graph_cache[project_id] = graph_system
            self._hydration_services[project_id] = GraphHydrationService(graph_system)
            self._operations_services[project_id] = GraphOperationsService(graph_system)
            self._analytics_services[project_id] = GraphAnalyticsService(graph_system)
            self._versioning_services[project_id] = GraphVersioningService(graph_system)
            await self._hydration_services[project_id].hydrate_from_database(project_id, session)

        return (
            self._hydration_services[project_id],
            self._operations_services[project_id],
            self._analytics_services[project_id],
            self._versioning_services[project_id],
        )

    async def add_node_to_graph(self, project_id: UUID, session: AsyncSession, node_id: UUID, node_type: str, data: dict) -> bool:
        _, ops, _, _ = await self.get_or_create_services(project_id, session)
        return await ops.add_node_to_graph(node_id, node_type, data)

    async def add_dependency_to_graph(self, project_id: UUID, session: AsyncSession, from_node_id: UUID, to_node_id: UUID, dependency_type: str) -> bool:
        _, ops, _, _ = await self.get_or_create_services(project_id, session)
        return await ops.add_dependency_to_graph(from_node_id, to_node_id, dependency_type)

    async def detect_circular_dependencies(self, project_id: UUID, session: AsyncSession) -> List[List[str]]:
        _, _, analytics, _ = await self.get_or_create_services(project_id, session)
        return await analytics.detect_circular_dependencies()

    async def calculate_node_impact(self, project_id: UUID, session: AsyncSession, node_id: UUID, change_type: str = "update") -> dict:
        _, _, analytics, _ = await self.get_or_create_services(project_id, session)
        return await analytics.calculate_node_impact(node_id, change_type)

    async def simulate_change(self, project_id: UUID, session: AsyncSession, node_id: UUID, proposed_change: dict) -> dict:
        _, _, analytics, _ = await self.get_or_create_services(project_id, session)
        return await analytics.simulate_change(node_id, proposed_change)

    async def validate_rules(self, project_id: UUID, session: AsyncSession) -> dict:
        _, _, analytics, _ = await self.get_or_create_services(project_id, session)
        return await analytics.validate_rules()

    async def create_snapshot(self, project_id: UUID, session: AsyncSession, name: str, description: str) -> str:
        _, _, _, versioning = await self.get_or_create_services(project_id, session)
        return await versioning.create_snapshot(name, description)

    async def rollback_to_snapshot(self, project_id: UUID, session: AsyncSession, version_id: str) -> Dict:
        _, _, _, versioning = await self.get_or_create_services(project_id, session)
        return await versioning.rollback_to_snapshot(version_id)

    async def list_snapshots(self, project_id: UUID, session: AsyncSession) -> List[Dict]:
        _, _, _, versioning = await self.get_or_create_services(project_id, session)
        return await versioning.list_snapshots()

    async def get_transitive_dependencies(self, project_id: UUID, session: AsyncSession, node_id: UUID, max_depth: int = 10) -> Dict:
        _, _, analytics, _ = await self.get_or_create_services(project_id, session)
        return await analytics.get_transitive_dependencies(node_id, max_depth)


_graph_manager_instance: Optional["GraphManagerService"] = None


def get_graph_manager() -> GraphManagerService:
    global _graph_manager_instance
    if _graph_manager_instance is None:
        _graph_manager_instance = GraphManagerService()
    return _graph_manager_instance


def reset_graph_manager() -> None:
    global _graph_manager_instance
    _graph_manager_instance = None
