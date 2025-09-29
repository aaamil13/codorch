"""Pydantic schemas for Architecture Module."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# Architecture Module Schemas
# ============================================================================


class ArchitectureModuleBase(BaseModel):
    """Base schema for architecture module."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    module_type: str = Field(default="package", max_length=50)
    level: int = Field(default=0, ge=0)
    position_x: Optional[float] = None
    position_y: Optional[float] = None


class ArchitectureModuleCreate(ArchitectureModuleBase):
    """Schema for creating architecture module."""

    project_id: UUID
    parent_id: Optional[UUID] = None
    tree_node_id: Optional[UUID] = None
    module_metadata: Optional[dict[str, Any]] = None


class ArchitectureModuleUpdate(BaseModel):
    """Schema for updating architecture module."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    module_type: Optional[str] = Field(None, max_length=50)
    level: Optional[int] = Field(None, ge=0)
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    module_metadata: Optional[dict[str, Any]] = None
    status: Optional[str] = Field(None, pattern="^(draft|approved|implemented)$")


class ArchitectureModuleResponse(ArchitectureModuleBase):
    """Schema for architecture module response."""

    id: UUID
    project_id: UUID
    parent_id: Optional[UUID] = None
    tree_node_id: Optional[UUID] = None
    ai_generated: bool
    generation_reasoning: Optional[dict[str, Any]] = None
    status: str
    approved_at: Optional[datetime] = None
    approved_by: Optional[UUID] = None
    module_metadata: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Module Dependency Schemas
# ============================================================================


class ModuleDependencyBase(BaseModel):
    """Base schema for module dependency."""

    dependency_type: str = Field(..., max_length=50)
    description: Optional[str] = None


class ModuleDependencyCreate(ModuleDependencyBase):
    """Schema for creating module dependency."""

    project_id: UUID
    from_module_id: UUID
    to_module_id: UUID
    dependency_metadata: Optional[dict[str, Any]] = None


class ModuleDependencyUpdate(BaseModel):
    """Schema for updating module dependency."""

    dependency_type: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    dependency_metadata: Optional[dict[str, Any]] = None


class ModuleDependencyResponse(ModuleDependencyBase):
    """Schema for module dependency response."""

    id: UUID
    project_id: UUID
    from_module_id: UUID
    to_module_id: UUID
    dependency_metadata: Optional[dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Architecture Rule Schemas
# ============================================================================


class ArchitectureRuleBase(BaseModel):
    """Base schema for architecture rule."""

    level: str = Field(..., pattern="^(global|module|component)$")
    rule_type: str = Field(..., pattern="^(naming|dependency|layer|tech|security)$")
    rule_definition: dict[str, Any] = Field(...)


class ArchitectureRuleCreate(ArchitectureRuleBase):
    """Schema for creating architecture rule."""

    project_id: UUID
    module_id: Optional[UUID] = None
    ai_generated: bool = False
    active: bool = True


class ArchitectureRuleUpdate(BaseModel):
    """Schema for updating architecture rule."""

    level: Optional[str] = Field(None, pattern="^(global|module|component)$")
    rule_type: Optional[str] = Field(None, pattern="^(naming|dependency|layer|tech|security)$")
    rule_definition: Optional[dict[str, Any]] = None
    active: Optional[bool] = None


class ArchitectureRuleResponse(ArchitectureRuleBase):
    """Schema for architecture rule response."""

    id: UUID
    project_id: UUID
    module_id: Optional[UUID] = None
    ai_generated: bool
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Architecture Generation Schemas
# ============================================================================


class ArchitectureGenerationRequest(BaseModel):
    """Schema for architecture generation request."""

    project_id: UUID
    goal_ids: list[UUID] = Field(default_factory=list, description="Goals to include in analysis")
    opportunity_ids: list[UUID] = Field(default_factory=list, description="Opportunities to include")
    architectural_style: Optional[str] = Field(
        None, description="Preferred architectural style (layered, microservices, etc.)"
    )
    preferences: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional preferences (max_depth, technologies, etc.)",
    )


class ArchitectureGenerationResponse(BaseModel):
    """Schema for architecture generation response."""

    modules: list[ArchitectureModuleResponse]
    dependencies: list[ModuleDependencyResponse]
    rules: list[ArchitectureRuleResponse]
    architectural_style: str
    reasoning: str
    overall_score: float = Field(ge=0.0, le=10.0)


# ============================================================================
# Architecture Validation Schemas
# ============================================================================


class ValidationIssue(BaseModel):
    """Schema for validation issue."""

    type: str = Field(..., description="Issue type (circular_dependency, invalid_type, etc.)")
    severity: str = Field(..., pattern="^(critical|warning|info)$")
    message: str
    affected_modules: list[UUID] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class ArchitectureValidationResponse(BaseModel):
    """Schema for architecture validation response."""

    is_valid: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
    warnings_count: int
    errors_count: int


# ============================================================================
# Complexity Analysis Schemas
# ============================================================================


class ComplexityMetrics(BaseModel):
    """Schema for complexity metrics."""

    module_count: int
    avg_dependencies: float
    max_depth: int
    cyclomatic_complexity: int
    coupling_score: float = Field(ge=0.0, le=10.0)
    cohesion_score: float = Field(ge=0.0, le=10.0)


class ComplexityHotspot(BaseModel):
    """Schema for complexity hotspot."""

    module_id: UUID
    module_name: str
    complexity_score: float = Field(ge=0.0, le=10.0)
    reason: str
    suggestions: list[str] = Field(default_factory=list)


class ComplexityAnalysisResponse(BaseModel):
    """Schema for complexity analysis response."""

    overall_complexity: float = Field(ge=0.0, le=10.0)
    metrics: ComplexityMetrics
    hotspots: list[ComplexityHotspot] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


# ============================================================================
# Impact Analysis Schemas
# ============================================================================


class ImpactAnalysisRequest(BaseModel):
    """Schema for impact analysis request."""

    module_id: UUID
    change_type: str = Field(..., pattern="^(modify|delete|add)$")


class AffectedModule(BaseModel):
    """Schema for affected module."""

    module_id: UUID
    module_name: str
    impact_level: str = Field(..., pattern="^(direct|indirect|cascading)$")
    affected_features: list[str] = Field(default_factory=list)


class ImpactAnalysisResponse(BaseModel):
    """Schema for impact analysis response."""

    module_id: UUID
    change_type: str
    affected_modules: list[AffectedModule] = Field(default_factory=list)
    breaking_changes: bool
    testing_scope: list[str] = Field(default_factory=list, description="Areas that need testing")
    recommendations: list[str] = Field(default_factory=list)


# ============================================================================
# Shared Modules Schemas
# ============================================================================


class SharedModuleInfo(BaseModel):
    """Schema for shared module information."""

    module_id: UUID
    module_name: str
    usage_count: int
    used_by: list[UUID] = Field(default_factory=list, description="Module IDs that use this")


class SharedModulesResponse(BaseModel):
    """Schema for shared modules response."""

    shared_modules: list[SharedModuleInfo] = Field(default_factory=list)
    total_count: int
