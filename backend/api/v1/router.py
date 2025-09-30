"""Main API v1 router."""

from fastapi import APIRouter

from backend.api.v1 import analytics, architecture, auth, code_generation, goals, opportunities, projects, research, requirements, tree_nodes, users, websocket

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(tree_nodes.router, tags=["tree-nodes"])
api_router.include_router(analytics.router, tags=["analytics"])
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
api_router.include_router(research.router, prefix="/research", tags=["research"])
api_router.include_router(architecture.router, prefix="/architecture", tags=["architecture"])
api_router.include_router(requirements.router, prefix="/requirements", tags=["requirements"])
api_router.include_router(code_generation.router, prefix="/code-generation", tags=["code-generation"])
api_router.include_router(websocket.router, tags=["websocket"])
