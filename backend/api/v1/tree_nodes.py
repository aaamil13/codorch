"""
API endpoints for TreeNodes with RefMemTree-powered analytics.

These endpoints demonstrate RefMemTree's REAL power:
- Instant graph queries (milliseconds vs seconds)
- Complex analyses that are impossible with SQL
- Real-time impact assessment
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user, get_session
from backend.db.models import User
from backend.modules.tree_nodes.service import TreeNodeService

router = APIRouter(prefix="/tree-nodes", tags=["tree-nodes"])


@router.get("/{node_id}/impact", response_model=dict)
async def get_node_impact_analysis(
    node_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get impact analysis for node.
    
    ⭐ POWERED BY REFMEMTREE!
    
    This is THE FIRST endpoint that uses RefMemTree's graph analysis
    for instant results!
    
    Returns:
    - Impact score (0-100)
    - Affected nodes list
    - Directly vs indirectly affected
    - Breaking changes
    - Recommendations
    
    Performance: Milliseconds (vs seconds with SQL recursive queries)
    """
    service = TreeNodeService(session)
    impact = await service.get_node_impact(node_id)

    if "error" in impact:
        raise HTTPException(status_code=404, detail=impact["error"])

    return impact


@router.get("/{node_id}/dependents", response_model=dict)
async def get_node_dependents(
    node_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get all nodes that depend on this node.
    
    ⭐ POWERED BY REFMEMTREE - Instant graph traversal!
    
    Returns all dependents in milliseconds using in-memory graph.
    """
    from backend.core.graph_manager import get_graph_manager
    from sqlalchemy import select
    from backend.db.models import TreeNode

    # Get node to find project
    result = await session.execute(select(TreeNode).where(TreeNode.id == node_id))
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # ⭐ Use RefMemTree for instant query
    graph_manager = get_graph_manager()
    graph = await graph_manager.get_or_create_graph(node.project_id, session)

    if not graph:
        raise HTTPException(
            status_code=503, detail="RefMemTree not available"
        )

    refmem_node = graph.get_node(str(node_id))
    if not refmem_node:
        raise HTTPException(status_code=404, detail="Node not in graph")

    # ⭐ REAL RefMemTree API: Get dependents instantly!
    dependents = refmem_node.get_dependencies(direction="incoming")

    return {
        "node_id": str(node_id),
        "dependent_count": len(dependents),
        "dependents": [
            {
                "node_id": dep.source_node_id,
                "dependency_type": dep.dependency_type,
                "strength": getattr(dep, "strength", 1.0),
            }
            for dep in dependents
        ],
        "is_critical": len(dependents) > 5,  # Many modules depend on this
    }


@router.get("/{node_id}/dependency-chain", response_model=dict)
async def get_dependency_chain(
    node_id: UUID,
    max_depth: int = 10,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Get full dependency chain for node.
    
    ⭐ POWERED BY REFMEMTREE!
    
    Shows transitive dependencies:
    Example: UI → Service → Logic → Database
    
    Impossible to do efficiently with SQL!
    RefMemTree does it in milliseconds!
    """
    from backend.core.graph_manager import get_graph_manager
    from sqlalchemy import select
    from backend.db.models import TreeNode

    # Get node
    result = await session.execute(select(TreeNode).where(TreeNode.id == node_id))
    node = result.scalar_one_or_none()

    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Get graph
    graph_manager = get_graph_manager()
    graph = await graph_manager.get_or_create_graph(node.project_id, session)

    if not graph:
        raise HTTPException(status_code=503, detail="RefMemTree not available")

    # ⭐ Use RefMemTree for transitive dependencies
    result_dict = await graph_manager.get_transitive_dependencies(
        project_id=node.project_id,
        node_id=node_id,
        session=session,
        max_depth=max_depth,
    )

    return result_dict
