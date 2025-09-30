"""Main API v1 router."""

from fastapi import APIRouter

from backend.api.v1 import architecture, auth, goals, opportunities, projects, research, requirements, users

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(goals.router, prefix="/goals", tags=["goals"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
api_router.include_router(research.router, prefix="/research", tags=["research"])
api_router.include_router(architecture.router, prefix="/architecture", tags=["architecture"])
<<<<<<< Current (Your changes)
<<<<<<< Current (Your changes)
=======
api_router.include_router(requirements.router, prefix="/requirements", tags=["requirements"])
>>>>>>> Incoming (Background Agent changes)
=======
api_router.include_router(requirements.router, prefix="/requirements", tags=["requirements"])
>>>>>>> Incoming (Background Agent changes)
