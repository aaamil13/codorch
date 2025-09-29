"""SQLAlchemy models."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base


class User(Base):
    """User model."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="owner")


class Project(Base):
    """Project model."""

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    current_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tree_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Foreign keys
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    tree_nodes: Mapped[list["TreeNode"]] = relationship("TreeNode", back_populates="project")
    goals: Mapped[list["Goal"]] = relationship("Goal", back_populates="project")


class TreeNode(Base):
    """Tree node model for RefMemTree persistence."""

    __tablename__ = "tree_nodes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tree_nodes.id", ondelete="CASCADE"), nullable=True
    )
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="tree_nodes")
    parent: Mapped[Optional["TreeNode"]] = relationship(
        "TreeNode", remote_side=[id], back_populates="children"
    )
    children: Mapped[list["TreeNode"]] = relationship("TreeNode", back_populates="parent")


class Goal(Base):
    """Goal model for Module 1: Goal Definition Engine."""

    __tablename__ = "goals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    tree_node_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tree_nodes.id", ondelete="SET NULL"), nullable=True
    )
    parent_goal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=True
    )

    # Goal content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # SMART validation
    is_smart_validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    specific_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    measurable_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    achievable_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    relevant_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    time_bound_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    overall_smart_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Metrics and tracking
    metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    target_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completion_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # AI analysis
    ai_feedback: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ai_suggestions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    priority: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="goals")
    parent_goal: Mapped[Optional["Goal"]] = relationship(
        "Goal", remote_side=[id], back_populates="subgoals"
    )
    subgoals: Mapped[list["Goal"]] = relationship("Goal", back_populates="parent_goal")