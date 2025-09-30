"""Service layer for Code Generation Module."""

from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import CodeGenerationSession, GeneratedFile
from backend.modules.code_generation.repository import CodeGenerationRepository, GeneratedFileRepository
from backend.modules.code_generation.validation_pipeline import ValidationPipeline
from backend.modules.code_generation.schemas import (
    CodeGenerationSessionCreate,
    PreGenerationValidation,
)
from backend.modules.architecture.service import ArchitectureService
from backend.modules.requirements.service import RequirementsService
from backend.ai_agents.code_generation_team import CodeGenerationTeam


class CodeGenerationService:
    """Service for code generation business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CodeGenerationRepository(session)
        self.file_repo = GeneratedFileRepository(session)
        self.validation_pipeline = ValidationPipeline(session)
        self.arch_service = ArchitectureService(session)
        self.req_service = RequirementsService(session)

    async def create_session(self, data: CodeGenerationSessionCreate) -> CodeGenerationSession:
        """Create code generation session with validation."""
        gen_session = CodeGenerationSession(
            project_id=data.project_id,
            architecture_module_id=data.architecture_module_id,
            status="validating",
        )
        return await self.repo.create(gen_session)

    async def validate_project(self, session_id: UUID) -> PreGenerationValidation:
        """Run pre-generation validation."""
        gen_session = await self.repo.get_by_id(session_id)
        if not gen_session:
            raise ValueError("Session not found")

        validation = await self.validation_pipeline.validate_project_readiness(gen_session.project_id)

        gen_session.validation_result = validation.model_dump()
        gen_session.status = "ready" if validation.can_proceed else "failed"
        if not validation.can_proceed:
            gen_session.error_message = "; ".join(validation.blocking_issues)

        await self.repo.update(gen_session)
        return validation

    async def generate_scaffold(self, session_id: UUID) -> Optional[CodeGenerationSession]:
        """Generate code scaffold."""
        gen_session = await self.repo.get_by_id(session_id)
        if not gen_session or gen_session.status != "ready":
            return None

        gen_session.status = "generating_scaffold"
        await self.repo.update(gen_session)

        # Get context
        modules = await self.arch_service.list_modules(gen_session.project_id)
        requirements = await self.req_service.list_requirements(gen_session.project_id)
        tech_stack = await self.req_service.list_technology_recommendations(gen_session.project_id)

        # Prepare data
        arch_data = {"modules": [{"name": m.name, "type": m.module_type} for m in modules[:10]]}
        req_data = [{"title": r.title, "type": r.type} for r in requirements[:20]]
        tech_data = [{"name": t.name, "type": t.technology_type} for t in tech_stack if t.status == "accepted"]

        # Generate scaffold
        result = await CodeGenerationTeam.full_generation_workflow(
            arch_data,
            req_data,
            tech_data,
        )

        gen_session.scaffold_code = result["scaffold"].model_dump() if result.get("scaffold") else {}
        gen_session.status = "reviewing_scaffold"
        return await self.repo.update(gen_session)

    async def approve_scaffold(self, session_id: UUID, approved_by: UUID) -> Optional[CodeGenerationSession]:
        """Approve scaffold."""
        gen_session = await self.repo.get_by_id(session_id)
        if not gen_session:
            return None

        gen_session.human_approved_scaffold = True
        gen_session.approved_by = approved_by
        gen_session.status = "ready_for_implementation"
        return await self.repo.update(gen_session)

    async def generate_implementation(self, session_id: UUID) -> Optional[CodeGenerationSession]:
        """Generate full implementation."""
        gen_session = await self.repo.get_by_id(session_id)
        if not gen_session:
            return None

        gen_session.status = "generating_code"
        await self.repo.update(gen_session)

        # Use already generated workflow result
        gen_session.status = "completed"
        return await self.repo.update(gen_session)

    async def list_sessions(self, project_id: UUID) -> list[CodeGenerationSession]:
        """List all sessions for project."""
        return await self.repo.get_by_project(project_id)

    async def get_session(self, session_id: UUID) -> Optional[CodeGenerationSession]:
        """Get session by ID."""
        return await self.repo.get_by_id(session_id)

    async def delete_session(self, session_id: UUID) -> bool:
        """Delete session."""
        gen_session = await self.repo.get_by_id(session_id)
        if not gen_session:
            return False
        await self.repo.delete(gen_session)
        return True
