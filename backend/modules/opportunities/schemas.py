"""Pydantic schemas for Opportunity module."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from backend.core.schemas import BaseSchema, TimestampMixin


class OpportunityScores(BaseSchema):
    """Opportunity scoring schema."""

    feasibility_score: float = Field(..., ge=0, le=10, description="Feasibility score (0-10)")
    impact_score: float = Field(..., ge=0, le=10, description="Impact score (0-10)")
    innovation_score: float = Field(..., ge=0, le=10, description="Innovation score (0-10)")
    resource_score: float = Field(..., ge=0, le=10, description="Resource availability (0-10)")
    overall_score: float = Field(..., ge=0, le=10, description="Overall score")


class OpportunityBase(BaseSchema):
    """Base opportunity schema."""

    title: str = Field(..., min_length=1, max_length=255, description="Opportunity title")
    description: Optional[str] = Field(default=None, description="Opportunity description")
    category: Optional[str] = Field(default=None, max_length=100, description="Category")
    target_market: Optional[str] = Field(default=None, description="Target market description")
    value_proposition: Optional[str] = Field(default=None, description="Unique value proposition")
    estimated_effort: Optional[str] = Field(default=None, description="Estimated effort")
    estimated_timeline: Optional[str] = Field(default=None, description="Estimated timeline")


class OpportunityCreate(OpportunityBase):
    """Schema for creating opportunity."""

    goal_id: Optional[UUID] = Field(default=None, description="Related goal ID")
    required_resources: Optional[dict] = Field(default_factory=dict)


class OpportunityUpdate(BaseSchema):
    """Schema for updating opportunity."""

    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    target_market: Optional[str] = None
    value_proposition: Optional[str] = None
    estimated_effort: Optional[str] = None
    estimated_timeline: Optional[str] = None
    status: Optional[str] = None
    required_resources: Optional[dict] = None


class OpportunityResponse(OpportunityBase, TimestampMixin):
    """Schema for opportunity response."""

    id: UUID
    project_id: UUID
    goal_id: Optional[UUID] = None
    tree_node_id: Optional[UUID] = None

    # AI generation
    ai_generated: bool = False
    ai_reasoning: Optional[dict] = None

    # Scoring
    score: Optional[float] = None
    feasibility_score: Optional[float] = None
    impact_score: Optional[float] = None
    innovation_score: Optional[float] = None
    resource_score: Optional[float] = None
    scoring_details: Optional[dict] = None

    # Business details
    required_resources: Optional[dict] = None

    # Status
    status: str = "proposed"
    approved_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None


class OpportunityGenerateRequest(BaseSchema):
    """Request schema for AI opportunity generation."""

    goal_id: Optional[UUID] = Field(None, description="Base on specific goal")
    context: Optional[str] = Field(None, description="Additional context")
    num_opportunities: int = Field(5, ge=1, le=10, description="Number to generate")
    creativity_level: str = Field("balanced", description="Creativity level: conservative, balanced, creative")
    include_scoring: bool = Field(True, description="Include automatic scoring")


class AIGeneratedOpportunity(BaseSchema):
    """AI-generated opportunity suggestion."""

    title: str
    description: str
    category: str
    target_market: str
    value_proposition: str
    estimated_effort: str
    estimated_timeline: str
    innovation_level: str
    reasoning: str


class OpportunityGenerateResponse(BaseSchema):
    """Response schema for opportunity generation."""

    project_id: UUID
    goal_id: Optional[UUID] = None
    opportunities: list[AIGeneratedOpportunity]
    generation_metadata: dict = Field(default_factory=dict)


class OpportunityCompareRequest(BaseSchema):
    """Request schema for opportunity comparison."""

    opportunity_ids: list[UUID] = Field(..., min_length=2, max_length=10)
    criteria: list[str] = Field(default_factory=lambda: ["feasibility", "impact", "innovation", "resources"])


class OpportunityComparison(BaseSchema):
    """Comparison result for an opportunity."""

    opportunity_id: UUID
    title: str
    scores: OpportunityScores
    rank: int
    strengths: list[str]
    weaknesses: list[str]


class OpportunityCompareResponse(BaseSchema):
    """Response schema for opportunity comparison."""

    opportunities: list[OpportunityComparison]
    winner_id: UUID
    reasoning: str
    comparison_matrix: dict = Field(default_factory=dict)
