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
    opportunities: Mapped[list["Opportunity"]] = relationship("Opportunity", back_populates="project")


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
    parent: Mapped[Optional["TreeNode"]] = relationship("TreeNode", remote_side=[id], back_populates="children")
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
    parent_goal: Mapped[Optional["Goal"]] = relationship("Goal", remote_side=[id], back_populates="subgoals")
    subgoals: Mapped[list["Goal"]] = relationship("Goal", back_populates="parent_goal")


class Opportunity(Base):
    """Opportunity model for Module 2: Opportunity Engine."""

    __tablename__ = "opportunities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    tree_node_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tree_nodes.id", ondelete="SET NULL"), nullable=True
    )
    goal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("goals.id", ondelete="SET NULL"), nullable=True
    )

    # Opportunity content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # AI generation
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    generation_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_reasoning: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Scoring
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    feasibility_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    impact_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    innovation_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    resource_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    scoring_details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Business details
    target_market: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    value_proposition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    estimated_effort: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    estimated_timeline: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    required_resources: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Validation and approval
    status: Mapped[str] = mapped_column(String(50), default="proposed", nullable=False)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="opportunities")
    goal: Mapped[Optional["Goal"]] = relationship("Goal")
    approver: Mapped[Optional["User"]] = relationship("User")


class ResearchSession(Base):
    """Research session model for Module 3: Research Engine."""

    __tablename__ = "research_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    goal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("goals.id", ondelete="SET NULL"), nullable=True
    )
    opportunity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("opportunities.id", ondelete="SET NULL"), nullable=True
    )
    tree_node_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tree_nodes.id", ondelete="SET NULL"), nullable=True
    )

    # Session content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)

    # Context from RefMemTree
    context_summary: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="Aggregated context from RefMemTree"
    )

    # Timestamps
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    goal: Mapped[Optional["Goal"]] = relationship("Goal")
    opportunity: Mapped[Optional["Opportunity"]] = relationship("Opportunity")
    creator: Mapped["User"] = relationship("User")
    messages: Mapped[list["ResearchMessage"]] = relationship(
        "ResearchMessage", back_populates="session", cascade="all, delete-orphan"
    )
    findings: Mapped[list["ResearchFinding"]] = relationship(
        "ResearchFinding", back_populates="session", cascade="all, delete-orphan"
    )


class ResearchMessage(Base):
    """Research message model - chat messages in research sessions."""

    __tablename__ = "research_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False
    )

    # Message content
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Message metadata (agent info, model, tokens, timing, etc.)
    message_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session: Mapped["ResearchSession"] = relationship("ResearchSession", back_populates="messages")


class ResearchFinding(Base):
    """Research finding model - insights extracted from research."""

    __tablename__ = "research_findings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False
    )

    # Finding content
    finding_type: Mapped[str] = mapped_column(String(50), nullable=False)  # technical, market, user, competitor, other
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Sources and citations
    sources: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # Scoring
    confidence_score: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="AI confidence in finding (0-1)"
    )
    relevance_score: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True, comment="Relevance to research context (0-1)"
    )

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session: Mapped["ResearchSession"] = relationship("ResearchSession", back_populates="findings")


# ============================================================================
# Module 4: Architecture Designer Models
# ============================================================================


class ArchitectureModule(Base):
    """Architecture module model for Module 4: Architecture Designer."""

    __tablename__ = "architecture_modules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("architecture_modules.id", ondelete="CASCADE"), nullable=True
    )
    tree_node_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tree_nodes.id", ondelete="SET NULL"), nullable=True
    )

    # Module information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    module_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="package"
    )  # package, class, interface, service, component, etc.
    level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Depth in tree

    # Visual positioning (for canvas)
    position_x: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    position_y: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # AI generation
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    generation_reasoning: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Status and approval
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)  # draft, approved, implemented
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Metadata (technologies, patterns, notes, etc.)
    module_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    parent: Mapped[Optional["ArchitectureModule"]] = relationship(
        "ArchitectureModule", remote_side=[id], back_populates="children"
    )
    children: Mapped[list["ArchitectureModule"]] = relationship(
        "ArchitectureModule", back_populates="parent", cascade="all, delete-orphan"
    )
    approver: Mapped[Optional["User"]] = relationship("User")
    dependencies_from: Mapped[list["ModuleDependency"]] = relationship(
        "ModuleDependency",
        foreign_keys="ModuleDependency.from_module_id",
        back_populates="from_module",
        cascade="all, delete-orphan",
    )
    dependencies_to: Mapped[list["ModuleDependency"]] = relationship(
        "ModuleDependency",
        foreign_keys="ModuleDependency.to_module_id",
        back_populates="to_module",
        cascade="all, delete-orphan",
    )
    rules: Mapped[list["ArchitectureRule"]] = relationship(
        "ArchitectureRule", back_populates="module", cascade="all, delete-orphan"
    )


class ModuleDependency(Base):
    """Module dependency model - connections between architecture modules."""

    __tablename__ = "module_dependencies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    from_module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("architecture_modules.id", ondelete="CASCADE"), nullable=False
    )
    to_module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("architecture_modules.id", ondelete="CASCADE"), nullable=False
    )

    # Dependency information
    dependency_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # import, extends, uses, implements, depends_on
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadata (specific dependency configuration)
    dependency_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    from_module: Mapped["ArchitectureModule"] = relationship(
        "ArchitectureModule", foreign_keys=[from_module_id], back_populates="dependencies_from"
    )
    to_module: Mapped["ArchitectureModule"] = relationship(
        "ArchitectureModule", foreign_keys=[to_module_id], back_populates="dependencies_to"
    )


class ArchitectureRule(Base):
    """Architecture rule model - rules for architecture validation."""

    __tablename__ = "architecture_rules"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    module_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("architecture_modules.id", ondelete="CASCADE"), nullable=True
    )  # null = global rule

    # Rule information
    level: Mapped[str] = mapped_column(String(50), nullable=False)  # global, module, component
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)  # naming, dependency, layer, tech, security
    rule_definition: Mapped[dict] = mapped_column(JSON, nullable=False)  # Rule specification

    # AI and status
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    module: Mapped[Optional["ArchitectureModule"]] = relationship("ArchitectureModule", back_populates="rules")


# ============================================================================
# Module 5: Requirements Definition Models
# ============================================================================


class Requirement(Base):
    """Requirement model for Module 5: Requirements Definition."""

    __tablename__ = "requirements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    module_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("architecture_modules.id", ondelete="SET NULL"), nullable=True
    )

    # Content
    type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # functional, non_functional, technical, api, data, testing
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(
        String(50), default="should_have", nullable=False
    )  # must_have, should_have, nice_to_have

    # Details
    acceptance_criteria: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)
    technical_specs: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    dependencies: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, default=list, comment="List of requirement IDs this depends on"
    )

    # AI
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_validation_result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ai_suggestions: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)

    # Status
    status: Mapped[str] = mapped_column(
        String(50), default="draft", nullable=False
    )  # draft, validated, approved, implemented
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    module: Mapped[Optional["ArchitectureModule"]] = relationship("ArchitectureModule")
    approver: Mapped[Optional["User"]] = relationship("User", foreign_keys=[approved_by])
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    api_specifications: Mapped[list["APISpecification"]] = relationship(
        "APISpecification", back_populates="requirement", cascade="all, delete-orphan"
    )


class TechnologyRecommendation(Base):
    """Technology recommendation model for Module 5."""

    __tablename__ = "technology_recommendations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    module_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("architecture_modules.id", ondelete="SET NULL"), nullable=True
    )

    # Recommendation
    technology_type: Mapped[str] = mapped_column(String(50), nullable=False)  # framework, library, database, tool, etc.
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)

    # Scoring
    suitability_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-10
    popularity_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-10
    learning_curve_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # 0-10

    # AI
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    alternatives: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)

    # Status
    status: Mapped[str] = mapped_column(
        String(50), default="suggested", nullable=False
    )  # suggested, accepted, rejected

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    module: Mapped[Optional["ArchitectureModule"]] = relationship("ArchitectureModule")


class APISpecification(Base):
    """API specification model for Module 5."""

    __tablename__ = "api_specifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requirement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False
    )

    # Endpoint
    method: Mapped[str] = mapped_column(String(10), nullable=False)  # GET, POST, PUT, DELETE, PATCH
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Request/Response
    request_schema: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    response_schema: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_codes: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)

    # Details
    authentication_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rate_limit: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    examples: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    requirement: Mapped["Requirement"] = relationship("Requirement", back_populates="api_specifications")


class CodeGenerationSession(Base):
    """Code generation session model for Module 6."""

    __tablename__ = "code_generation_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    architecture_module_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("architecture_modules.id", ondelete="SET NULL"), nullable=True
    )

    # Status workflow
    status: Mapped[str] = mapped_column(
        String(50), default="validating", nullable=False
    )  # validating, ready, generating_scaffold, reviewing_scaffold, generating_code, reviewing_code, generating_tests, completed, failed

    # Generation data
    validation_result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    scaffold_code: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    generated_code: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    test_code: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    documentation: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Approval
    human_approved_scaffold: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    human_approved_code: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project")
    module: Mapped[Optional["ArchitectureModule"]] = relationship("ArchitectureModule")
    approver: Mapped[Optional["User"]] = relationship("User")
    generated_files: Mapped[list["GeneratedFile"]] = relationship(
        "GeneratedFile", back_populates="session", cascade="all, delete-orphan"
    )


class GeneratedFile(Base):
    """Generated file model for Module 6."""

    __tablename__ = "generated_files"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("code_generation_sessions.id", ondelete="CASCADE"), nullable=False
    )

    # File info
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
<<<<<<< Current (Your changes)
<<<<<<< Current (Your changes)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # source, test, config, documentation
=======
    file_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # source, test, config, documentation
>>>>>>> Incoming (Background Agent changes)
=======
    file_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # source, test, config, documentation
>>>>>>> Incoming (Background Agent changes)
    language: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # AI & Review
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    review_status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )  # pending, approved, rejected
    review_comments: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    session: Mapped["CodeGenerationSession"] = relationship("CodeGenerationSession", back_populates="generated_files")
