"""add requirements tables for module 5

Revision ID: b9f12a3d4e5f
Revises: a8507bc7ec0c
Create Date: 2025-09-30 04:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b9f12a3d4e5f"
down_revision: Union[str, None] = "a8507bc7ec0c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create requirements table
    op.create_table(
        "requirements",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("module_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=50), nullable=False, server_default="should_have"),
        sa.Column("acceptance_criteria", sa.JSON(), nullable=True),
        sa.Column("technical_specs", sa.JSON(), nullable=True),
        sa.Column(
            "dependencies",
            sa.JSON(),
            nullable=True,
            comment="List of requirement IDs this depends on",
        ),
        sa.Column("ai_generated", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("ai_validation_result", sa.JSON(), nullable=True),
        sa.Column("ai_suggestions", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="draft"),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["module_id"], ["architecture_modules.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_requirements_project_id"), "requirements", ["project_id"], unique=False)
    op.create_index(op.f("ix_requirements_module_id"), "requirements", ["module_id"], unique=False)
    op.create_index(op.f("ix_requirements_type"), "requirements", ["type"], unique=False)
    op.create_index(op.f("ix_requirements_status"), "requirements", ["status"], unique=False)

    # Create technology_recommendations table
    op.create_table(
        "technology_recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("module_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("technology_type", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=True),
        sa.Column("reasoning", sa.Text(), nullable=False),
        sa.Column("suitability_score", sa.Float(), nullable=False),
        sa.Column("popularity_score", sa.Float(), nullable=True),
        sa.Column("learning_curve_score", sa.Float(), nullable=True),
        sa.Column("ai_generated", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("alternatives", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="suggested"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["module_id"], ["architecture_modules.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_technology_recommendations_project_id"),
        "technology_recommendations",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_technology_recommendations_module_id"),
        "technology_recommendations",
        ["module_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_technology_recommendations_technology_type"),
        "technology_recommendations",
        ["technology_type"],
        unique=False,
    )

    # Create api_specifications table
    op.create_table(
        "api_specifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requirement_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("method", sa.String(length=10), nullable=False),
        sa.Column("path", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("request_schema", sa.JSON(), nullable=True),
        sa.Column("response_schema", sa.JSON(), nullable=True),
        sa.Column("error_codes", sa.JSON(), nullable=True),
        sa.Column("authentication_required", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("rate_limit", sa.String(length=100), nullable=True),
        sa.Column("examples", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["requirement_id"], ["requirements.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_api_specifications_requirement_id"),
        "api_specifications",
        ["requirement_id"],
        unique=False,
    )
    op.create_index(op.f("ix_api_specifications_method"), "api_specifications", ["method"], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f("ix_api_specifications_method"), table_name="api_specifications")
    op.drop_index(op.f("ix_api_specifications_requirement_id"), table_name="api_specifications")
    op.drop_table("api_specifications")

    op.drop_index(
        op.f("ix_technology_recommendations_technology_type"),
        table_name="technology_recommendations",
    )
    op.drop_index(
        op.f("ix_technology_recommendations_module_id"),
        table_name="technology_recommendations",
    )
    op.drop_index(
        op.f("ix_technology_recommendations_project_id"),
        table_name="technology_recommendations",
    )
    op.drop_table("technology_recommendations")

    op.drop_index(op.f("ix_requirements_status"), table_name="requirements")
    op.drop_index(op.f("ix_requirements_type"), table_name="requirements")
    op.drop_index(op.f("ix_requirements_module_id"), table_name="requirements")
    op.drop_index(op.f("ix_requirements_project_id"), table_name="requirements")
    op.drop_table("requirements")