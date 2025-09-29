"""Base Pydantic schemas for the application."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# User Schemas


class UserBase(BaseSchema):
    """Base user schema."""

    email: str = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(None, max_length=255, description="Full name")


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseSchema):
    """Schema for updating a user."""

    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase, TimestampMixin):
    """Schema for user response."""

    id: UUID
    is_active: bool = True
    is_superuser: bool = False


class UserInDB(UserResponse):
    """Schema for user in database."""

    hashed_password: str


# Project Schemas


class ProjectBase(BaseSchema):
    """Base project schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    goal: str = Field(..., min_length=1, description="Main project goal")


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""

    pass


class ProjectUpdate(BaseSchema):
    """Schema for updating a project."""

    name: Optional[str] = None
    description: Optional[str] = None
    goal: Optional[str] = None
    current_stage: Optional[str] = None
    status: Optional[str] = None


class ProjectResponse(ProjectBase, TimestampMixin):
    """Schema for project response."""

    id: UUID
    current_stage: Optional[str] = None
    status: str = "active"
    created_by: UUID


# Tree Node Schemas


class TreeNodeBase(BaseSchema):
    """Base tree node schema."""

    node_type: str = Field(..., description="Type of node")
    data: dict[str, Any] = Field(default_factory=dict, description="Node data")
    position: Optional[int] = None
    level: Optional[int] = None


class TreeNodeCreate(TreeNodeBase):
    """Schema for creating a tree node."""

    parent_id: Optional[UUID] = None


class TreeNodeUpdate(BaseSchema):
    """Schema for updating a tree node."""

    data: Optional[dict[str, Any]] = None
    position: Optional[int] = None


class TreeNodeResponse(TreeNodeBase, TimestampMixin):
    """Schema for tree node response."""

    id: UUID
    project_id: UUID
    parent_id: Optional[UUID] = None
    path: Optional[str] = None


# Authentication Schemas


class Token(BaseSchema):
    """Token schema."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseSchema):
    """Token data schema."""

    user_id: Optional[UUID] = None
    username: Optional[str] = None


class LoginRequest(BaseSchema):
    """Login request schema."""

    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")


class LoginResponse(BaseSchema):
    """Login response schema."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# API Response Schemas


class MessageResponse(BaseSchema):
    """Generic message response."""

    message: str
    detail: Optional[str] = None


class ErrorResponse(BaseSchema):
    """Error response schema."""

    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class PaginatedResponse(BaseSchema):
    """Paginated response schema."""

    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
