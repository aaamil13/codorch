"""Pydantic schemas for Goal module."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from backend.core.schemas import BaseSchema, TimestampMixin


class MetricDefinition(BaseSchema):
    """Metric definition schema."""

    name: str = Field(..., description="Metric name")
    description: Optional[str] = Field(None, description="Metric description")
    target_value: Optional[float] = Field(None, description="Target value")
    current_value: Optional[float] = Field(None, description="Current value")
    unit: Optional[str] = Field(None, description="Unit of measurement")


class SMARTScores(BaseSchema):
    """SMART validation scores."""

    specific_score: float = Field(..., ge=0, le=10, description="Specific score (0-10)")
    measurable_score: float = Field(..., ge=0, le=10, description="Measurable score (0-10)")
    achievable_score: float = Field(..., ge=0, le=10, description="Achievable score (0-10)")
    relevant_score: float = Field(..., ge=0, le=10, description="Relevant score (0-10)")
    time_bound_score: float = Field(..., ge=0, le=10, description="Time-bound score (0-10)")
    overall_smart_score: float = Field(..., ge=0, le=10, description="Overall SMART score")


class AIFeedback(BaseSchema):
    """AI feedback schema."""

    feedback: list[str] = Field(default_factory=list, description="Feedback points")
    suggestions: list[str] = Field(default_factory=list, description="Improvement suggestions")
    strengths: list[str] = Field(default_factory=list, description="Goal strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Goal weaknesses")


class GoalBase(BaseSchema):
    """Base goal schema."""

    title: str = Field(..., min_length=1, max_length=255, description="Goal title")
    description: Optional[str] = Field(None, description="Goal description")
    category: Optional[str] = Field(None, max_length=100, description="Goal category")
    target_date: Optional[datetime] = Field(None, description="Target completion date")
    priority: Optional[str] = Field(None, description="Priority level (low, medium, high, critical)")

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        """Validate priority value."""
        if v is not None:
            allowed = ["low", "medium", "high", "critical"]
            if v.lower() not in allowed:
                raise ValueError(f"Priority must be one of: {allowed}")
            return v.lower()
        return v


class GoalCreate(GoalBase):
    """Schema for creating a goal."""

    parent_goal_id: Optional[UUID] = Field(None, description="Parent goal ID")
    metrics: Optional[list[MetricDefinition]] = Field(default_factory=list, description="Goal metrics")


class GoalUpdate(BaseSchema):
    """Schema for updating a goal."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    target_date: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    completion_percentage: Optional[float] = Field(None, ge=0, le=100)
    metrics: Optional[list[MetricDefinition]] = None


class GoalResponse(GoalBase, TimestampMixin):
    """Schema for goal response."""

    id: UUID
    project_id: UUID
    parent_goal_id: Optional[UUID] = None
    tree_node_id: Optional[UUID] = None

    # SMART validation
    is_smart_validated: bool = False
    specific_score: Optional[float] = None
    measurable_score: Optional[float] = None
    achievable_score: Optional[float] = None
    relevant_score: Optional[float] = None
    time_bound_score: Optional[float] = None
    overall_smart_score: Optional[float] = None

    # Metrics
    metrics: Optional[dict] = None
    completion_percentage: float = 0.0

    # AI analysis
    ai_feedback: Optional[dict] = None
    ai_suggestions: Optional[list] = None

    # Status
    status: str = "draft"


class GoalWithSubgoals(GoalResponse):
    """Goal response with subgoals."""

    subgoals: list[GoalResponse] = Field(default_factory=list)


class GoalAnalysisRequest(BaseSchema):
    """Request schema for goal analysis."""

    include_suggestions: bool = Field(True, description="Include improvement suggestions")
    include_metrics: bool = Field(True, description="Include metric suggestions")
    include_subgoals: bool = Field(False, description="Include subgoal suggestions")


class GoalAnalysisResponse(BaseSchema):
    """Response schema for goal analysis."""

    goal_id: UUID
    smart_scores: SMARTScores
    feedback: AIFeedback
    suggested_metrics: list[MetricDefinition] = Field(default_factory=list)
    suggested_subgoals: list[str] = Field(default_factory=list)
    is_smart_compliant: bool = Field(..., description="Whether goal passes SMART validation")


class GoalDecomposeRequest(BaseSchema):
    """Request schema for goal decomposition."""

    num_subgoals: int = Field(3, ge=1, le=10, description="Number of subgoals to generate")
    include_metrics: bool = Field(True, description="Include metrics for subgoals")


class SubgoalSuggestion(BaseSchema):
    """Suggested subgoal schema."""

    title: str
    description: str
    priority: str
    estimated_duration: Optional[str] = None
    metrics: list[MetricDefinition] = Field(default_factory=list)


class GoalDecomposeResponse(BaseSchema):
    """Response schema for goal decomposition."""

    parent_goal_id: UUID
    suggested_subgoals: list[SubgoalSuggestion]
    reasoning: str = Field(..., description="AI reasoning for decomposition")
