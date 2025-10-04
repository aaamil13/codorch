"""API endpoints for Code Generation Module (Module 6)."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user, get_db
from backend.db.models import User
from backend.modules.code_generation.schemas import (
    CodeGenerationSessionCreate,
    CodeGenerationSessionResponse,
    PreGenerationValidation,
    GeneratedFileResponse,
    ApprovalRequest,
    ApprovalResponse,
)
from backend.modules.code_generation.service import CodeGenerationService

router = APIRouter(prefix="/code-generation", tags=["code-generation"])


@router.post("/projects/{project_id}/validate", response_model=PreGenerationValidation)
async def validate_project(
    project_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Validate project readiness for code generation."""
    service = CodeGenerationService(session)
    validation = await service.validation_pipeline.validate_project_readiness(project_id)
    return validation


@router.post("/sessions", response_model=CodeGenerationSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    data: CodeGenerationSessionCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create code generation session."""
    service = CodeGenerationService(session)
    gen_session = await service.create_session(data)

    # Auto-validate
    await service.validate_project(gen_session.id)

    return gen_session


@router.get("/sessions/{session_id}", response_model=CodeGenerationSessionResponse)
async def get_session(
    session_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get generation session."""
    service = CodeGenerationService(session)
    gen_session = await service.get_session(session_id)
    if not gen_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return gen_session


@router.get("/projects/{project_id}/sessions", response_model=list[CodeGenerationSessionResponse])
async def list_sessions(
    project_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all sessions for project."""
    service = CodeGenerationService(session)
    sessions = await service.list_sessions(project_id)
    return sessions


@router.post("/sessions/{session_id}/scaffold", response_model=CodeGenerationSessionResponse)
async def generate_scaffold(
    session_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate code scaffold."""
    service = CodeGenerationService(session)
    gen_session = await service.generate_scaffold(session_id)
    if not gen_session:
        raise HTTPException(status_code=400, detail="Cannot generate scaffold - check session status")
    return gen_session


@router.post("/sessions/{session_id}/approve-scaffold", response_model=ApprovalResponse)
async def approve_scaffold(
    session_id: UUID,
    data: ApprovalRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve generated scaffold."""
    if not data.approved:
        return ApprovalResponse(
            session_id=session_id,
            stage="scaffold",
            approved=False,
            next_step="regenerate_scaffold",
        )

    service = CodeGenerationService(session)
    gen_session = await service.approve_scaffold(session_id, current_user.id)
    if not gen_session:
        raise HTTPException(status_code=404, detail="Session not found")

    return ApprovalResponse(
        session_id=session_id,
        stage="scaffold",
        approved=True,
        next_step="generate_implementation",
    )


@router.post("/sessions/{session_id}/implementation", response_model=CodeGenerationSessionResponse)
async def generate_implementation(
    session_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate full implementation."""
    service = CodeGenerationService(session)
    gen_session = await service.generate_implementation(session_id)
    if not gen_session:
        raise HTTPException(status_code=400, detail="Cannot generate code")
    return gen_session


@router.post("/sessions/{session_id}/approve-code", response_model=ApprovalResponse)
async def approve_code(
    session_id: UUID,
    data: ApprovalRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve generated code."""
    service = CodeGenerationService(session)
    gen_session = await service.get_session(session_id)
    if not gen_session:
        raise HTTPException(status_code=404, detail="Session not found")

    if data.approved:
        gen_session.human_approved_code = True
        gen_session.approved_by = current_user.id
        gen_session.status = "completed"
        await service.repo.update(gen_session)

    return ApprovalResponse(
        session_id=session_id,
        stage="code",
        approved=data.approved,
        next_step="download" if data.approved else "regenerate",
    )


@router.get("/sessions/{session_id}/files", response_model=list[GeneratedFileResponse])
async def list_files(
    session_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List generated files."""
    service = CodeGenerationService(session)
    files = await service.file_repo.get_by_session(session_id)
    return files


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete session."""
    service = CodeGenerationService(session)
    success = await service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
