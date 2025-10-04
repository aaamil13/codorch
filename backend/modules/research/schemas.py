"""Pydantic schemas for Research Module."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


# ============================================================================
# Research Session Schemas
# ============================================================================


class ResearchSessionBase(BaseSchema):
    """Base research session schema."""

    title: str = Field(..., min_length=1, max_length=255, description="Session title")
    description: Optional[str] = Field(default=None, description="Session description")
    goal_id: Optional[UUID] = Field(default=None, description="Related goal ID")
    opportunity_id: Optional[UUID] = Field(default=None, description="Related opportunity ID")
    tree_node_id: Optional[UUID] = Field(default=None, description="Related tree node ID")


class ResearchSessionCreate(ResearchSessionBase):
    """Schema for creating a research session."""

    project_id: UUID = Field(..., description="Project ID")


class ResearchSessionUpdate(BaseSchema):
    """Schema for updating a research session."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|completed|archived)$")


class ResearchSessionResponse(ResearchSessionBase):
    """Schema for research session response."""

    id: UUID
    project_id: UUID
    status: str
    context_summary: Optional[dict[str, Any]] = Field(default=None, description="Aggregated context from RefMemTree")
    message_count: int = Field(default=0, description="Number of messages")
    finding_count: int = Field(default=0, description="Number of findings")
    created_by: UUID
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Research Message Schemas
# ============================================================================


class ResearchMessageBase(BaseSchema):
    """Base research message schema."""

    content: str = Field(..., min_length=1, description="Message content")


class ResearchMessageCreate(ResearchMessageBase):
    """Schema for creating a research message."""

    role: str = Field(default="user", pattern="^(user|assistant|system)$")


class ResearchMessageResponse(ResearchMessageBase):
    """Schema for research message response."""

    id: UUID
    session_id: UUID
    role: str
    message_metadata: Optional[dict[str, Any]] = Field(
        default=None,
        description="Message metadata (agent, tokens, model, etc.)",
        alias="metadata",
    )
    created_at: datetime


# ============================================================================
# Research Finding Schemas
# ============================================================================


class ResearchFindingBase(BaseSchema):
    """Base research finding schema."""

    finding_type: str = Field(
        ...,
        pattern="^(technical|market|user|competitor|other)$",
        description="Type of finding",
    )
    title: str = Field(..., min_length=1, max_length=255, description="Finding title")
    description: str = Field(..., min_length=1, description="Finding description")
    sources: list[str] = Field(default_factory=list, description="Source references")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="AI confidence score")
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Relevance to research context")


class ResearchFindingCreate(ResearchFindingBase):
    """Schema for creating a research finding."""

    session_id: UUID = Field(..., description="Research session ID")


class ResearchFindingUpdate(BaseSchema):
    """Schema for updating a research finding."""

    finding_type: Optional[str] = Field(None, pattern="^(technical|market|user|competitor|other)$")
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    sources: Optional[list[str]] = None
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class ResearchFindingResponse(ResearchFindingBase):
    """Schema for research finding response."""

    id: UUID
    session_id: UUID
    created_at: datetime


# ============================================================================
# Research Context Schemas
# ============================================================================


class ResearchContext(BaseSchema):
    """Schema for research context from RefMemTree."""

    node_id: Optional[UUID] = None
    node_type: Optional[str] = None
    node_data: Optional[dict[str, Any]] = None
    parent_context: Optional[dict[str, Any]] = None
    sibling_context: Optional[list[dict[str, Any]]] = None
    project_context: Optional[dict[str, Any]] = None
    goal_context: Optional[dict[str, Any]] = None
    opportunity_context: Optional[dict[str, Any]] = None


# ============================================================================
# Chat Request/Response Schemas
# ============================================================================


class ChatRequest(BaseSchema):
    """Schema for chat message request."""

    message: str = Field(..., min_length=1, description="User message")
    stream: bool = Field(default=True, description="Enable streaming response")


class ChatResponse(BaseSchema):
    """Schema for chat response."""

    message_id: UUID
    content: str
    agent: Optional[str] = Field(None, description="Agent that generated response")
    metadata: Optional[dict[str, Any]] = None


# ============================================================================
# Semantic Search Schemas
# ============================================================================


class SemanticSearchRequest(BaseSchema):
    """Schema for semantic search request."""

    query: str = Field(..., min_length=1, description="Search query")
    project_id: Optional[UUID] = Field(None, description="Limit to project")
    session_id: Optional[UUID] = Field(None, description="Limit to session")
    finding_types: Optional[list[str]] = Field(None, description="Filter by finding types")
    limit: int = Field(default=10, ge=1, le=100, description="Number of results")


class SemanticSearchResult(BaseSchema):
    """Schema for semantic search result."""

    finding_id: UUID
    session_id: UUID
    title: str
    description: str
    finding_type: str
    relevance_score: float
    created_at: datetime


class SemanticSearchResponse(BaseSchema):
    """Schema for semantic search response."""

    query: str
    results: list[SemanticSearchResult]
    total: int


# ============================================================================
# Statistics Schemas
# ============================================================================


class ResearchStatistics(BaseSchema):
    """Schema for research statistics."""

    total_sessions: int
    active_sessions: int
    total_messages: int
    total_findings: int
    findings_by_type: dict[str, int]
    avg_confidence_score: float
    recent_activity: list[dict[str, Any]]
