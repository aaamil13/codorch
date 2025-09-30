"""add code generation tables for module 6

Revision ID: c3d8e9f0a1b2
Revises: b9f12a3d4e5f
Create Date: 2025-09-30 05:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c3d8e9f0a1b2"
down_revision: Union[str, None] = "b9f12a3d4e5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create code_generation_sessions table
    op.create_table(
        "code_generation_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("architecture_module_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="validating"),
        sa.Column("validation_result", sa.JSON(), nullable=True),
        sa.Column("scaffold_code", sa.JSON(), nullable=True),
        sa.Column("generated_code", sa.JSON(), nullable=True),
        sa.Column("test_code", sa.JSON(), nullable=True),
        sa.Column("documentation", sa.JSON(), nullable=True),
        sa.Column("human_approved_scaffold", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("human_approved_code", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["architecture_module_id"], ["architecture_modules.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_code_generation_sessions_project_id"),
        "code_generation_sessions",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_code_generation_sessions_status"),
        "code_generation_sessions",
        ["status"],
        unique=False,
    )

    # Create generated_files table
    op.create_table(
        "generated_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_type", sa.String(length=50), nullable=False),
        sa.Column("language", sa.String(length=50), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("ai_generated", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("review_status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("review_comments", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["session_id"], ["code_generation_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_generated_files_session_id"),
        "generated_files",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_generated_files_file_type"),
        "generated_files",
        ["file_type"],
        unique=False,
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f("ix_generated_files_file_type"), table_name="generated_files")
    op.drop_index(op.f("ix_generated_files_session_id"), table_name="generated_files")
    op.drop_table("generated_files")

    op.drop_index(op.f("ix_code_generation_sessions_status"), table_name="code_generation_sessions")
    op.drop_index(op.f("ix_code_generation_sessions_project_id"), table_name="code_generation_sessions")
    op.drop_table("code_generation_sessions")
