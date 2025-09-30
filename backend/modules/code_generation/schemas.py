"""Pydantic schemas for Code Generation Module."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# Validation Schemas
# ============================================================================


class ValidationCheck(BaseModel):
    """Individual validation check result."""

    check_name: str
    passed: bool
    score: float = Field(ge=0.0, le=10.0)
    message: str
    issues: list[str] = Field(default_factory=list)


class PreGenerationValidation(BaseModel):
    """Pre-generation validation result."""

    architecture_completeness: float = Field(ge=0.0, le=100.0)
    requirements_clarity: float = Field(ge=0.0, le=100.0)
    dependencies_resolved: bool
    circular_dependencies: bool
    overall_readiness: float = Field(ge=0.0, le=100.0)
    checks: list[ValidationCheck] = Field(default_factory=list)
    can_proceed: bool
    blocking_issues: list[str] = Field(default_factory=list)


# ============================================================================
# Generation Session Schemas
# ============================================================================


class CodeGenerationSessionBase(BaseModel):
    """Base schema for code generation session."""

    project_id: UUID
    architecture_module_id: Optional[UUID] = None


class CodeGenerationSessionCreate(CodeGenerationSessionBase):
    """Schema for creating code generation session."""

    pass


class CodeGenerationSessionResponse(CodeGenerationSessionBase):
    """Schema for code generation session response."""

    id: UUID
    status: str
    validation_result: Optional[dict[str, Any]] = None
    scaffold_code: Optional[dict[str, Any]] = None
    generated_code: Optional[dict[str, Any]] = None
    test_code: Optional[dict[str, Any]] = None
    documentation: Optional[dict[str, Any]] = None
    human_approved_scaffold: bool
    human_approved_code: bool
    approved_by: Optional[UUID] = None
    approved_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Generated File Schemas
# ============================================================================


class GeneratedFileBase(BaseModel):
    """Base schema for generated file."""

    file_path: str = Field(min_length=1, max_length=500)
    file_type: str = Field(pattern="^(source|test|config|documentation)$")
    language: Optional[str] = None
    content: str = Field(min_length=1)


class GeneratedFileCreate(GeneratedFileBase):
    """Schema for creating generated file."""

    session_id: UUID


class GeneratedFileResponse(GeneratedFileBase):
    """Schema for generated file response."""

    id: UUID
    session_id: UUID
    ai_generated: bool
    review_status: str
    review_comments: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ============================================================================
# Code Generation Request/Response
# ============================================================================


class ScaffoldGenerationRequest(BaseModel):
    """Request for scaffold generation."""

    session_id: UUID


class CodeGenerationRequest(BaseModel):
    """Request for full code generation."""

    session_id: UUID
    include_tests: bool = True
    include_docs: bool = True


class CodeGenerationResponse(BaseModel):
    """Response for code generation."""

    session_id: UUID
    status: str
    files_generated: int
    scaffold: Optional[dict[str, Any]] = None
    code: Optional[dict[str, Any]] = None
    tests: Optional[dict[str, Any]] = None
    documentation: Optional[dict[str, Any]] = None


# ============================================================================
# Approval Schemas
# ============================================================================


class ApprovalRequest(BaseModel):
    """Request for human approval."""

    approved: bool
    comments: Optional[str] = None


class ApprovalResponse(BaseModel):
    """Response for approval."""

    session_id: UUID
    stage: str  # scaffold, code
    approved: bool
    next_step: str
