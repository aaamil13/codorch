"""Service layer for Research Module."""

from typing import Optional, Sequence, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.refmemtree_wrapper import AdvancedProjectTree
from backend.db.models import ResearchFinding, ResearchMessage, ResearchSession, User
from backend.modules.research.repository import (
    ResearchFindingRepository,
    ResearchMessageRepository,
    ResearchSessionRepository,
)
from backend.modules.research.schemas import (
    ResearchFindingCreate,
    ResearchFindingUpdate,
    ResearchMessageCreate,
    ResearchSessionCreate,
    ResearchSessionUpdate,
)


class ResearchService:
    """Service for research operations."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session."""
        self.db = db
        self.session_repo = ResearchSessionRepository(db)
        self.message_repo = ResearchMessageRepository(db)
        self.finding_repo = ResearchFindingRepository(db)
        self.refmem_manager: Optional[AdvancedProjectTree] = None # Initialize as Optional, set later

    # ========================================================================
    # Research Session Operations
    # ========================================================================

    async def create_session(
        self,
        data: ResearchSessionCreate,
        current_user: User,
    ) -> ResearchSession:
        """Create a new research session with context aggregation."""
        # Aggregate context from RefMemTree if node_id provided
        context_summary = None
        if data.tree_node_id:
            try:
                # Initialize refmem_manager with the current project_id
                self.refmem_manager = AdvancedProjectTree(data.project_id)
                context_summary = self.refmem_manager.get_smart_context(
                    node_id=data.tree_node_id,
                )
            except Exception as e:
                # Context aggregation is not critical, continue without it
                print(f"Warning: Context aggregation failed: {e}")

        # Create session
        session = ResearchSession(
            project_id=data.project_id,
            goal_id=data.goal_id,
            opportunity_id=data.opportunity_id,
            tree_node_id=data.tree_node_id,
            title=data.title,
            description=data.description,
            context_summary=context_summary,
            status="active",
            created_by=current_user.id,
        )

        return await self.session_repo.create(session)

    async def get_session(self, session_id: UUID) -> Optional[ResearchSession]:
        """Get research session by ID."""
        return await self.session_repo.get_by_id(session_id)

    async def list_sessions(
        self,
        project_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> Sequence[ResearchSession]:
        """List research sessions for a project."""
        return await self.session_repo.get_by_project(
            project_id=project_id,
            skip=skip,
            limit=limit,
            status=status,
        )

    async def update_session(
        self,
        session_id: UUID,
        data: ResearchSessionUpdate,
    ) -> Optional[ResearchSession]:
        """Update research session."""
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            return None

        # Update fields
        if data.title is not None:
            session.title = data.title
        if data.description is not None:
            session.description = data.description
        if data.status is not None:
            session.status = data.status

        return await self.session_repo.update(session)

    async def delete_session(self, session_id: UUID) -> bool:
        """Delete research session."""
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            return False

        await self.session_repo.delete(session)
        return True

    async def archive_session(self, session_id: UUID) -> Optional[ResearchSession]:
        """Archive research session."""
        session = await self.session_repo.get_by_id(session_id)
        if not session:
            return None

        session.status = "archived"
        return await self.session_repo.update(session)

    # ========================================================================
    # Research Message Operations
    # ========================================================================

    async def create_message(
        self,
        session_id: UUID,
        data: ResearchMessageCreate,
        metadata: Optional[dict] = None,
    ) -> ResearchMessage:
        """Create a new research message."""
        message = ResearchMessage(
            session_id=session_id,
            role=data.role,
            content=data.content,
            message_metadata=metadata or {},
        )

        return await self.message_repo.create(message)

    async def get_messages(
        self,
        session_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ResearchMessage]:
        """Get messages for a research session."""
        return await self.message_repo.get_by_session(
            session_id=session_id,
            skip=skip,
            limit=limit,
        )

    async def get_latest_messages(
        self,
        session_id: UUID,
        limit: int = 10,
    ) -> Sequence[ResearchMessage]:
        """Get latest N messages from session."""
        return await self.message_repo.get_latest_messages(
            session_id=session_id,
            limit=limit,
        )

    # ========================================================================
    # Research Finding Operations
    # ========================================================================

    async def create_finding(
        self,
        data: ResearchFindingCreate,
    ) -> ResearchFinding:
        """Create a new research finding."""
        finding = ResearchFinding(
            session_id=data.session_id,
            finding_type=data.finding_type,
            title=data.title,
            description=data.description,
            sources=data.sources,
            confidence_score=data.confidence_score,
            relevance_score=data.relevance_score,
        )

        return await self.finding_repo.create(finding)

    async def get_finding(self, finding_id: UUID) -> Optional[ResearchFinding]:
        """Get research finding by ID."""
        return await self.finding_repo.get_by_id(finding_id)

    async def list_findings(
        self,
        session_id: UUID,
        finding_type: Optional[str] = None,
    ) -> Sequence[ResearchFinding]:
        """List findings for a research session."""
        return await self.finding_repo.get_by_session(
            session_id=session_id,
            finding_type=finding_type,
        )

    async def update_finding(
        self,
        finding_id: UUID,
        data: ResearchFindingUpdate,
    ) -> Optional[ResearchFinding]:
        """Update research finding."""
        finding = await self.finding_repo.get_by_id(finding_id)
        if not finding:
            return None

        # Update fields
        if data.finding_type is not None:
            finding.finding_type = data.finding_type
        if data.title is not None:
            finding.title = data.title
        if data.description is not None:
            finding.description = data.description
        if data.sources is not None:
            finding.sources = data.sources
        if data.confidence_score is not None:
            finding.confidence_score = data.confidence_score
        if data.relevance_score is not None:
            finding.relevance_score = data.relevance_score

        return await self.finding_repo.update(finding)

    async def delete_finding(self, finding_id: UUID) -> bool:
        """Delete research finding."""
        finding = await self.finding_repo.get_by_id(finding_id)
        if not finding:
            return False

        await self.finding_repo.delete(finding)
        return True

    async def get_high_confidence_findings(
        self,
        session_id: UUID,
        min_confidence: float = 0.7,
        limit: int = 10,
    ) -> Sequence[ResearchFinding]:
        """Get high-confidence findings for a session."""
        return await self.finding_repo.get_high_confidence_findings(
            session_id=session_id,
            min_confidence=min_confidence,
            limit=limit,
        )

    # ========================================================================
    # Statistics
    # ========================================================================

    async def get_session_statistics(self, session_id: UUID) -> dict:
        """Get statistics for a research session."""
        message_count = await self.message_repo.count_by_session(session_id)
        finding_count = await self.finding_repo.count_by_session(session_id)
        findings_by_type = await self.finding_repo.count_by_type(session_id)

        return {
            "session_id": str(session_id),
            "message_count": message_count,
            "finding_count": finding_count,
            "findings_by_type": findings_by_type,
        }

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    async def _aggregate_context(
        self,
        project_id: UUID, # Added project_id
        node_id: Optional[UUID] = None,
        goal_id: Optional[UUID] = None,
        opportunity_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Aggregate context from RefMemTree and related entities."""
        context: Dict[str, Any] = {}

        # Get tree node context if available
        if node_id:
            try:
                # Initialize refmem_manager with the correct project_id
                refmem_manager = AdvancedProjectTree(project_id)
                node_context = refmem_manager.get_smart_context(node_id)
                context["tree_node"] = node_context
            except Exception as e:
                print(f"Warning: Failed to get tree node context: {e}")

        # Get goal context if available
        if goal_id:
            from backend.modules.goals.repository import GoalRepository

            goal_repo = GoalRepository(self.db)
            goal = await goal_repo.get_by_id(goal_id)
            if goal:
                context["goal"] = {
                    "title": goal.title,
                    "description": goal.description,
                    "category": goal.category,
                    "smart_scores": {
                        "specific": goal.specific_score,
                        "measurable": goal.measurable_score,
                        "achievable": goal.achievable_score,
                        "relevant": goal.relevant_score,
                        "time_bound": goal.time_bound_score,
                    },
                }

        # Get opportunity context if available
        if opportunity_id:
            from backend.modules.opportunities.repository import OpportunityRepository

            opp_repo = OpportunityRepository(self.db)
            opportunity = await opp_repo.get_by_id(opportunity_id)
            if opportunity:
                context["opportunity"] = {
                    "title": opportunity.title,
                    "description": opportunity.description,
                    "category": opportunity.category,
                    "scores": {
                        "feasibility": opportunity.feasibility_score,
                        "impact": opportunity.impact_score,
                        "innovation": opportunity.innovation_score,
                        "resources": opportunity.resource_score,
                    },
                }

        return context
