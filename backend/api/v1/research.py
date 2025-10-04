"""API endpoints for Research Module."""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai_agents.research_team import ResearchTeam
from backend.api.deps import get_current_user, get_db
from backend.db.models import User
from backend.modules.research.schemas import (
    ChatRequest,
    ChatResponse,
    ResearchFindingCreate,
    ResearchFindingResponse,
    ResearchFindingUpdate,
    ResearchMessageResponse,
    ResearchSessionCreate,
    ResearchSessionResponse,
    ResearchSessionUpdate,
)
from backend.modules.research.service import ResearchService

router = APIRouter()


# ============================================================================
# Research Session Endpoints
# ============================================================================


@router.post("/sessions", response_model=ResearchSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_research_session(
    data: ResearchSessionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResearchSessionResponse:
    """Create a new research session."""
    service = ResearchService(db)

    try:
        session = await service.create_session(data=data, current_user=current_user)

        # Add counts
        message_count = await service.message_repo.count_by_session(session.id)
        finding_count = await service.finding_repo.count_by_session(session.id)

        response = ResearchSessionResponse.model_validate(session)
        response.message_count = message_count
        response.finding_count = finding_count

        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/sessions", response_model=list[ResearchSessionResponse])
async def list_research_sessions(
    project_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
) -> list[ResearchSessionResponse]:
    """List research sessions for a project."""
    service = ResearchService(db)
    sessions = await service.list_sessions(
        project_id=project_id,
        skip=skip,
        limit=limit,
        status=status_filter,
    )

    responses = []
    for session in sessions:
        message_count = await service.message_repo.count_by_session(session.id)
        finding_count = await service.finding_repo.count_by_session(session.id)

        response = ResearchSessionResponse.model_validate(session)
        response.message_count = message_count
        response.finding_count = finding_count
        responses.append(response)

    return responses


@router.get("/sessions/{session_id}", response_model=ResearchSessionResponse)
async def get_research_session(
    session_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResearchSessionResponse:
    """Get research session by ID."""
    service = ResearchService(db)
    session = await service.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research session not found",
        )

    message_count = await service.message_repo.count_by_session(session.id)
    finding_count = await service.finding_repo.count_by_session(session.id)

    response = ResearchSessionResponse.model_validate(session)
    response.message_count = message_count
    response.finding_count = finding_count

    return response


@router.put("/sessions/{session_id}", response_model=ResearchSessionResponse)
async def update_research_session(
    session_id: UUID,
    data: ResearchSessionUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResearchSessionResponse:
    """Update research session."""
    service = ResearchService(db)
    session = await service.update_session(session_id=session_id, data=data)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research session not found",
        )

    message_count = await service.message_repo.count_by_session(session.id)
    finding_count = await service.finding_repo.count_by_session(session.id)

    response = ResearchSessionResponse.model_validate(session)
    response.message_count = message_count
    response.finding_count = finding_count

    return response


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_research_session(
    session_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete research session."""
    service = ResearchService(db)
    success = await service.delete_session(session_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research session not found",
        )


@router.post("/sessions/{session_id}/archive", response_model=ResearchSessionResponse)
async def archive_research_session(
    session_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResearchSessionResponse:
    """Archive research session."""
    service = ResearchService(db)
    session = await service.archive_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research session not found",
        )

    message_count = await service.message_repo.count_by_session(session.id)
    finding_count = await service.finding_repo.count_by_session(session.id)

    response = ResearchSessionResponse.model_validate(session)
    response.message_count = message_count
    response.finding_count = finding_count

    return response


# ============================================================================
# Research Message & Chat Endpoints
# ============================================================================


@router.get("/sessions/{session_id}/messages", response_model=list[ResearchMessageResponse])
async def get_session_messages(
    session_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
) -> list[ResearchMessageResponse]:
    """Get messages for a research session."""
    service = ResearchService(db)

    # Verify session exists
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research session not found",
        )

    messages = await service.get_messages(session_id=session_id, skip=skip, limit=limit)
    return [ResearchMessageResponse.model_validate(msg) for msg in messages]


@router.post("/sessions/{session_id}/chat", response_model=ChatResponse)
async def chat_with_research_team(
    session_id: UUID,
    request: ChatRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ChatResponse:
    """Send a message and get AI response from research team."""
    service = ResearchService(db)

    # Verify session exists
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research session not found",
        )

    # Save user message
    from backend.modules.research.schemas import ResearchMessageCreate

    user_message = await service.create_message(
        session_id=session_id,
        data=ResearchMessageCreate(role="user", content=request.message),
    )

    # Get previous messages for context
    previous_messages = await service.get_latest_messages(session_id=session_id, limit=10)
    message_history = [{"role": msg.role, "content": msg.content} for msg in reversed(previous_messages)]

    # Conduct research with AI team
    research_team = ResearchTeam()
    try:
        synthesis = await research_team.conduct_research(
            query=request.message,
            session_id=str(session_id),
            context_summary=session.context_summary,
            previous_messages=message_history,
        )

        # Create assistant response
        assistant_content = f"""**Research Summary:**
{synthesis.research_summary}

**Key Insights:**
{chr(10).join(f'• {insight}' for insight in synthesis.key_insights)}

**Next Steps:**
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(synthesis.next_steps))}

Confidence: {synthesis.confidence:.1%}
"""

        assistant_message = await service.create_message(
            session_id=session_id,
            data=ResearchMessageCreate(role="assistant", content=assistant_content),
            metadata={
                "agent": "ResearchTeam",
                "confidence": synthesis.confidence,
                "findings_count": len(synthesis.findings),
            },
        )

        # Auto-create findings from synthesis
        for finding_data in synthesis.findings:
            try:
                await service.create_finding(
                    data=ResearchFindingCreate(
                        session_id=session_id,
                        finding_type=finding_data.get("type", "other"),
                        title=finding_data.get("title", "Research Finding"),
                        description=finding_data.get("description", ""),
                        sources=finding_data.get("sources", []),
                        confidence_score=finding_data.get("confidence", 0.7),
                        relevance_score=finding_data.get("relevance", 0.8),
                    )
                )
            except Exception as e:
                print(f"Warning: Failed to create finding: {e}")

        return ChatResponse(
            message_id=assistant_message.id,
            content=assistant_content,
            agent="ResearchTeam",
            metadata=assistant_message.message_metadata,
        )

    except Exception as e:
        # Create error response
        error_content = f"I encountered an error while researching: {str(e)}"
        error_message = await service.create_message(
            session_id=session_id,
            data=ResearchMessageCreate(role="assistant", content=error_content),
            metadata={"error": str(e)},
        )

        return ChatResponse(
            message_id=error_message.id,
            content=error_content,
            agent="System",
            metadata={"error": True},
        )


# ============================================================================
# Research Finding Endpoints
# ============================================================================


@router.get("/sessions/{session_id}/findings", response_model=list[ResearchFindingResponse])
async def get_session_findings(
    session_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    finding_type: Optional[str] = None,
) -> list[ResearchFindingResponse]:
    """Get findings for a research session."""
    service = ResearchService(db)

    # Verify session exists
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research session not found",
        )

    findings = await service.list_findings(session_id=session_id, finding_type=finding_type)
    return [ResearchFindingResponse.model_validate(f) for f in findings]


@router.post("/findings", response_model=ResearchFindingResponse, status_code=status.HTTP_201_CREATED)
async def create_finding(
    data: ResearchFindingCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResearchFindingResponse:
    """Create a new research finding."""
    service = ResearchService(db)

    try:
        finding = await service.create_finding(data=data)
        return ResearchFindingResponse.model_validate(finding)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/findings/{finding_id}", response_model=ResearchFindingResponse)
async def get_finding(
    finding_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResearchFindingResponse:
    """Get research finding by ID."""
    service = ResearchService(db)
    finding = await service.get_finding(finding_id)

    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research finding not found",
        )

    return ResearchFindingResponse.model_validate(finding)


@router.put("/findings/{finding_id}", response_model=ResearchFindingResponse)
async def update_finding(
    finding_id: UUID,
    data: ResearchFindingUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ResearchFindingResponse:
    """Update research finding."""
    service = ResearchService(db)
    finding = await service.update_finding(finding_id=finding_id, data=data)

    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research finding not found",
        )

    return ResearchFindingResponse.model_validate(finding)


@router.delete("/findings/{finding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_finding(
    finding_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete research finding."""
    service = ResearchService(db)
    success = await service.delete_finding(finding_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research finding not found",
        )


# ============================================================================
# Statistics Endpoints
# ============================================================================


@router.get("/sessions/{session_id}/statistics")
async def get_session_statistics(
    session_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Get statistics for a research session."""
    service = ResearchService(db)

    # Verify session exists
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research session not found",
        )

    return await service.get_session_statistics(session_id)
