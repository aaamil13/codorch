"""Pydantic schemas for Requirements Module."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# Requirement Schemas
# ============================================================================


class RequirementBase(BaseModel):
    """Base schema for requirement."""

    type: str = Field(..., pattern="^(functional|non_functional|technical|api|data|testing)$")
    category: Optional[str] = Field(None, max_length=100)
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    priority: str = Field(default="should_have", pattern="^(must_have|should_have|nice_to_have)$")


class RequirementCreate(RequirementBase):
    """Schema for creating requirement."""

    project_id: UUID
    module_id: Optional[UUID] = None
    acceptance_criteria: list[str] = Field(default_factory=list)
    technical_specs: dict[str, Any] = Field(default_factory=dict)
    dependencies: list[UUID] = Field(default_factory=list)


class RequirementUpdate(BaseModel):
    """Schema for updating requirement."""

    type: Optional[str] = Field(None, pattern="^(functional|non_functional|technical|api|data|testing)$")
    category: Optional[str] = Field(None, max_length=100)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    priority: Optional[str] = Field(None, pattern="^(must_have|should_have|nice_to_have)$")
    acceptance_criteria: Optional[list[str]] = None
    technical_specs: Optional[dict[str, Any]] = None
    dependencies: Optional[list[UUID]] = None
    status: Optional[str] = Field(None, pattern="^(draft|validated|approved|implemented)$")


class RequirementResponse(RequirementBase):
    """Schema for requirement response."""

    id: UUID
    project_id: UUID
    module_id: Optional[UUID] = None
    acceptance_criteria: list[str] = Field(default_factory=list)
    technical_specs: dict[str, Any] = Field(default_factory=dict)
    dependencies: list[UUID] = Field(default_factory=list)
    ai_generated: bool
    ai_validation_result: Optional[dict[str, Any]] = None
    ai_suggestions: list[str] = Field(default_factory=list)
    status: str
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    created_by: UUID

    model_config = {"from_attributes": True}


# ============================================================================
# Technology Recommendation Schemas
# ============================================================================


class TechnologyRecommendationBase(BaseModel):
    """Base schema for technology recommendation."""

    technology_type: str = Field(..., max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    version: Optional[str] = Field(None, max_length=50)
    reasoning: str = Field(..., min_length=1)
    suitability_score: float = Field(..., ge=0.0, le=10.0)


class TechnologyRecommendationCreate(TechnologyRecommendationBase):
    """Schema for creating technology recommendation."""

    project_id: UUID
    module_id: Optional[UUID] = None
    popularity_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    learning_curve_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    alternatives: list[dict[str, Any]] = Field(default_factory=list)


class TechnologyRecommendationUpdate(BaseModel):
    """Schema for updating technology recommendation."""

    technology_type: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    version: Optional[str] = Field(None, max_length=50)
    reasoning: Optional[str] = Field(None, min_length=1)
    suitability_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    popularity_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    learning_curve_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    alternatives: Optional[list[dict[str, Any]]] = None
    status: Optional[str] = Field(None, pattern="^(suggested|accepted|rejected)$")


class TechnologyRecommendationResponse(TechnologyRecommendationBase):
    """Schema for technology recommendation response."""

    id: UUID
    project_id: UUID
    module_id: Optional[UUID] = None
    popularity_score: Optional[float] = None
    learning_curve_score: Optional[float] = None
    ai_generated: bool
    alternatives: list[dict[str, Any]] = Field(default_factory=list)
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# API Specification Schemas
# ============================================================================


class APISpecificationBase(BaseModel):
    """Base schema for API specification."""

    method: str = Field(..., pattern="^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$")
    path: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)


class APISpecificationCreate(APISpecificationBase):
    """Schema for creating API specification."""

    requirement_id: UUID
    request_schema: Optional[dict[str, Any]] = None
    response_schema: Optional[dict[str, Any]] = None
    error_codes: list[dict[str, Any]] = Field(default_factory=list)
    authentication_required: bool = True
    rate_limit: Optional[str] = Field(None, max_length=100)
    examples: list[dict[str, Any]] = Field(default_factory=list)


class APISpecificationUpdate(BaseModel):
    """Schema for updating API specification."""

    method: Optional[str] = Field(None, pattern="^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$")
    path: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=1)
    request_schema: Optional[dict[str, Any]] = None
    response_schema: Optional[dict[str, Any]] = None
    error_codes: Optional[list[dict[str, Any]]] = None
    authentication_required: Optional[bool] = None
    rate_limit: Optional[str] = Field(None, max_length=100)
    examples: Optional[list[dict[str, Any]]] = None


class APISpecificationResponse(APISpecificationBase):
    """Schema for API specification response."""

    id: UUID
    requirement_id: UUID
    request_schema: Optional[dict[str, Any]] = None
    response_schema: Optional[dict[str, Any]] = None
    error_codes: list[dict[str, Any]] = Field(default_factory=list)
    authentication_required: bool
    rate_limit: Optional[str] = None
    examples: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Validation Schemas
# ============================================================================


class RequirementValidationRequest(BaseModel):
    """Schema for requirement validation request."""

    requirement_id: UUID


class ValidationIssue(BaseModel):
    """Schema for validation issue."""

    type: str = Field(..., description="Issue type (clarity, completeness, consistency, feasibility)")
    severity: str = Field(..., pattern="^(critical|warning|info)$")
    message: str
    suggestion: Optional[str] = None


class RequirementValidationResult(BaseModel):
    """Schema for requirement validation result."""

    requirement_id: UUID
    overall_score: float = Field(ge=0.0, le=10.0, description="Overall quality score")
    completeness_score: float = Field(ge=0.0, le=10.0)
    clarity_score: float = Field(ge=0.0, le=10.0)
    consistency_score: float = Field(ge=0.0, le=10.0)
    feasibility_score: float = Field(ge=0.0, le=10.0)
    issues: list[ValidationIssue] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    is_valid: bool = Field(description="True if overall_score >= 7.0")


# ============================================================================
# Technology Recommendation Request/Response
# ============================================================================


class TechnologyRecommendationRequest(BaseModel):
    """Schema for technology recommendation request."""

    project_id: UUID
    module_id: Optional[UUID] = None
    requirements: list[UUID] = Field(default_factory=list, description="Requirement IDs to analyze")
    preferences: dict[str, Any] = Field(
        default_factory=dict,
        description="User preferences (languages, frameworks, etc.)",
    )


class TechnologyRecommendationSummary(BaseModel):
    """Schema for technology recommendation summary."""

    recommendations: list[TechnologyRecommendationResponse]
    total_count: int
    by_type: dict[str, int] = Field(default_factory=dict, description="Count by technology type")


# ============================================================================
# Requirements Report Schemas
# ============================================================================


class RequirementsSummary(BaseModel):
    """Schema for requirements summary."""

    total_count: int
    by_type: dict[str, int] = Field(default_factory=dict)
    by_status: dict[str, int] = Field(default_factory=dict)
    by_priority: dict[str, int] = Field(default_factory=dict)
    validation_coverage: float = Field(ge=0.0, le=100.0, description="% of validated requirements")


class RequirementsReport(BaseModel):
    """Schema for requirements report."""

    project_id: UUID
    summary: RequirementsSummary
    requirements: list[RequirementResponse]
    technology_recommendations: list[TechnologyRecommendationResponse]
    api_specifications_count: int
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Batch Validation Schema
# ============================================================================


class BatchValidationRequest(BaseModel):
    """Schema for batch validation request."""

    project_id: UUID
    requirement_ids: list[UUID] = Field(default_factory=list, description="Empty = validate all")


class BatchValidationResponse(BaseModel):
    """Schema for batch validation response."""

    project_id: UUID
    total_validated: int
    results: list[RequirementValidationResult]
    overall_quality_score: float = Field(ge=0.0, le=10.0)
    issues_count: int
    critical_issues_count: int
