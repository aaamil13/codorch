"""Opportunity service layer."""

from typing import Optional, Sequence, Dict, Any, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai_agents.opportunity_team import (
    CreativeIdeaGenerator,
    OpportunityAnalyzer,
    StructuredIdeaGenerator,
    SupervisorAgent,
)
from backend.db.models import Goal, Opportunity, Project
from backend.modules.opportunities.repository import OpportunityRepository
from backend.modules.opportunities.schemas import (
    AIGeneratedOpportunity,
    OpportunityCreate,
    OpportunityGenerateRequest,
    OpportunityGenerateResponse,
    OpportunityUpdate,
)
from backend.modules.opportunities.scoring import OpportunityScorer


class OpportunityService:
    """Service layer for Opportunity operations."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize service."""
        self.db = db
        self.repository = OpportunityRepository(db)
        self.scorer = OpportunityScorer()

    async def create_opportunity(self, project_id: UUID, opportunity_data: OpportunityCreate) -> Opportunity:
        """Create new opportunity."""
        # Verify project exists
        project_result = await self.db.execute(select(Project).filter(Project.id == project_id))
        project = project_result.scalars().first()
        if not project:
            raise ValueError("Project not found")

        # Verify goal if specified
        if opportunity_data.goal_id:
            goal_result = await self.db.execute(select(Goal).filter(Goal.id == opportunity_data.goal_id))
            goal = goal_result.scalars().first()
            if not goal or goal.project_id != project_id:
                raise ValueError("Goal not found or belongs to different project")

        # Create opportunity via repository
        created_opportunity = await self.repository.create(opportunity_data, project_id)

        # Calculate scores and update
        scores = self.scorer.calculate_overall_score(
            description=created_opportunity.description,
            category=created_opportunity.category,
            target_market=created_opportunity.target_market,
            value_proposition=created_opportunity.value_proposition,
            estimated_effort=created_opportunity.estimated_effort,
            required_resources=created_opportunity.required_resources,
        )

        created_opportunity.feasibility_score = scores["feasibility_score"]
        created_opportunity.impact_score = scores["impact_score"]
        created_opportunity.innovation_score = scores["innovation_score"]
        created_opportunity.resource_score = scores["resource_score"]
        created_opportunity.score = scores["overall_score"]
        created_opportunity.scoring_details = scores

        return await self.repository.update(created_opportunity)

    async def get_opportunity(self, opportunity_id: UUID) -> Optional[Opportunity]:
        """Get opportunity by ID."""
        return await self.repository.get_by_id(opportunity_id)

    async def list_opportunities(self, project_id: UUID, skip: int = 0, limit: int = 100) -> Sequence[Opportunity]:
        """List opportunities for project."""
        return await self.repository.get_by_project(project_id, skip, limit)

    async def update_opportunity(self, opportunity_id: UUID, opportunity_update: OpportunityUpdate) -> Opportunity:
        """Update opportunity."""
        opportunity = await self.repository.get_by_id(opportunity_id)
        if not opportunity:
            raise ValueError("Opportunity not found")

        # Update fields
        if opportunity_update.title is not None:
            opportunity.title = opportunity_update.title
        if opportunity_update.description is not None:
            opportunity.description = opportunity_update.description
        if opportunity_update.category is not None:
            opportunity.category = opportunity_update.category
        if opportunity_update.target_market is not None:
            opportunity.target_market = opportunity_update.target_market
        if opportunity_update.value_proposition is not None:
            opportunity.value_proposition = opportunity_update.value_proposition
        if opportunity_update.estimated_effort is not None:
            opportunity.estimated_effort = opportunity_update.estimated_effort
        if opportunity_update.estimated_timeline is not None:
            opportunity.estimated_timeline = opportunity_update.estimated_timeline
        if opportunity_update.status is not None:
            opportunity.status = opportunity_update.status
        if opportunity_update.required_resources is not None:
            opportunity.required_resources = opportunity_update.required_resources

        # Re-calculate scores if key fields changed
        if any(
            [
                opportunity_update.description,
                opportunity_update.target_market,
                opportunity_update.value_proposition,
                opportunity_update.estimated_effort,
            ]
        ):
            scores = self.scorer.calculate_overall_score(
                description=opportunity.description,
                category=opportunity.category,
                target_market=opportunity.target_market,
                value_proposition=opportunity.value_proposition,
                estimated_effort=opportunity.estimated_effort,
                required_resources=opportunity.required_resources,
            )

            opportunity.feasibility_score = scores["feasibility_score"]
            opportunity.impact_score = scores["impact_score"]
            opportunity.innovation_score = scores["innovation_score"]
            opportunity.resource_score = scores["resource_score"]
            opportunity.score = scores["overall_score"]
            opportunity.scoring_details = scores

        return await self.repository.update(opportunity)

    async def delete_opportunity(self, opportunity_id: UUID) -> None:
        """Delete opportunity."""
        opportunity = await self.repository.get_by_id(opportunity_id)
        if not opportunity:
            raise ValueError("Opportunity not found")

        await self.repository.delete(opportunity)

    async def generate_opportunities(
        self, project_id: UUID, request: OpportunityGenerateRequest
    ) -> OpportunityGenerateResponse:
        """
        Generate opportunities using AI Team.

        AI Team workflow:
        1. Creative Generator → generates N ideas (high creativity)
        2. Structured Generator → generates N ideas (practical focus)
        3. Analyzer → analyzes all ideas
        4. Supervisor → makes final selection
        """
        # Verify project
        project_result = await self.db.execute(select(Project).filter(Project.id == project_id))
        project = project_result.scalars().first()
        if not project:
            raise ValueError("Project not found")

        # Get goal context if specified
        goal_context = None
        if request.goal_id:
            goal_result = await self.db.execute(select(Goal).filter(Goal.id == request.goal_id))
            goal = goal_result.scalars().first()
            if not goal or goal.project_id != project_id:
                raise ValueError("Goal not found or belongs to different project")

        # Build context
        context = request.context or project.goal
        if goal_context:
            context = f"{context}\n\n{goal_context}"

        # Step 1: Creative Generator
        creative_gen = CreativeIdeaGenerator()
        creative_result = await creative_gen.generate_ideas(
            context=context,
            goal=goal_context,
            num_ideas=max(request.num_opportunities // 2, 2),
        )

        # Step 2: Structured Generator
        structured_gen = StructuredIdeaGenerator()
        structured_result = await structured_gen.generate_ideas(
            context=context,
            goal=goal_context,
            num_ideas=max(request.num_opportunities // 2, 2),
        )

        # Combine ideas
        all_ideas = creative_result.ideas + structured_result.ideas

        # Step 3: Analyzer
        analyzer = OpportunityAnalyzer()
        analyses = []
        for i, idea in enumerate(all_ideas):
            analysis = await analyzer.analyze_opportunity(idea, i)
            analyses.append(analysis)

        # Step 4: Supervisor
        supervisor = SupervisorAgent()
        decision = await supervisor.review_opportunities(all_ideas, analyses)

        # Filter approved ideas
        approved_ideas = [all_ideas[i] for i in decision.approved_ideas]

        # Build response
        from backend.modules.opportunities.schemas import AIGeneratedOpportunity

        response_ideas = [
            AIGeneratedOpportunity(
                title=idea.title,
                description=idea.description,
                category=idea.category,
                target_market=idea.target_market,
                value_proposition=idea.value_proposition,
                estimated_effort=idea.estimated_effort,
                estimated_timeline=idea.estimated_timeline,
                innovation_level=idea.innovation_level,
                reasoning=idea.reasoning,
            )
            for idea in approved_ideas
        ]

        response = OpportunityGenerateResponse(
            project_id=project_id,
            goal_id=request.goal_id,
            opportunities=response_ideas,
            generation_metadata={
                "creative_ideas": len(creative_result.ideas),
                "structured_ideas": len(structured_result.ideas),
                "total_generated": len(all_ideas),
                "approved": len(approved_ideas),
                "rejected": len(decision.rejected_ideas),
                "supervisor_reasoning": decision.reasoning,
            },
        )

        return response

    async def get_top_opportunities(self, project_id: UUID, limit: int = 10) -> Sequence[Opportunity]:
        """Get top-scored opportunities."""
        return await self.repository.get_top_scored(project_id, limit)

    async def compare_opportunities(self, opportunity_ids: List[UUID]) -> Dict[str, Any]:
        """Compare multiple opportunities."""
        opportunities = await self.repository.get_multiple_by_ids(opportunity_ids)

        if not opportunities:
            raise ValueError("No opportunities found")

        # Sort by score
        sorted_opps = sorted(opportunities, key=lambda o: o.score or 0, reverse=True)

        comparison = {
            "opportunities": [
                {
                    "id": str(opp.id),
                    "title": opp.title,
                    "score": opp.score,
                    "feasibility": opp.feasibility_score,
                    "impact": opp.impact_score,
                    "innovation": opp.innovation_score,
                    "rank": i + 1,
                }
                for i, opp in enumerate(sorted_opps)
            ],
            "winner": (
                {
                    "id": str(sorted_opps[0].id),
                    "title": sorted_opps[0].title,
                    "score": sorted_opps[0].score,
                }
                if sorted_opps
                else None
            ),
        }

        return comparison
