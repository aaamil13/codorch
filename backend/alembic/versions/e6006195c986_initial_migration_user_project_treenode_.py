"""Initial migration: User, Project, TreeNode, Goal, Opportunity

Revision ID: e6006195c986
Revises: 
Create Date: 2025-09-30 01:09:38.887753

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e6006195c986'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('goal', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='planning'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_projects_created_by', 'projects', ['created_by'])

    # Create tree_nodes table
    op.create_table(
        'tree_nodes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('node_type', sa.String(length=50), nullable=False),
        sa.Column('content', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('embedding', sa.LargeBinary(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['tree_nodes.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_tree_nodes_project_id', 'tree_nodes', ['project_id'])
    op.create_index('ix_tree_nodes_parent_id', 'tree_nodes', ['parent_id'])

    # Create goals table
    op.create_table(
        'goals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tree_node_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('parent_goal_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('is_smart_validated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('specific_score', sa.Float(), nullable=True),
        sa.Column('measurable_score', sa.Float(), nullable=True),
        sa.Column('achievable_score', sa.Float(), nullable=True),
        sa.Column('relevant_score', sa.Float(), nullable=True),
        sa.Column('time_bound_score', sa.Float(), nullable=True),
        sa.Column('overall_smart_score', sa.Float(), nullable=True),
        sa.Column('metrics', sa.JSON(), nullable=True),
        sa.Column('target_date', sa.DateTime(), nullable=True),
        sa.Column('completion_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('ai_feedback', sa.JSON(), nullable=True),
        sa.Column('ai_suggestions', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='draft'),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tree_node_id'], ['tree_nodes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parent_goal_id'], ['goals.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_goals_project_id', 'goals', ['project_id'])

    # Create opportunities table
    op.create_table(
        'opportunities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tree_node_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('goal_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('ai_generated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('generation_prompt', sa.Text(), nullable=True),
        sa.Column('ai_reasoning', sa.JSON(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('feasibility_score', sa.Float(), nullable=True),
        sa.Column('impact_score', sa.Float(), nullable=True),
        sa.Column('innovation_score', sa.Float(), nullable=True),
        sa.Column('resource_score', sa.Float(), nullable=True),
        sa.Column('scoring_details', sa.JSON(), nullable=True),
        sa.Column('target_market', sa.Text(), nullable=True),
        sa.Column('value_proposition', sa.Text(), nullable=True),
        sa.Column('estimated_effort', sa.String(length=50), nullable=True),
        sa.Column('estimated_timeline', sa.String(length=100), nullable=True),
        sa.Column('required_resources', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='proposed'),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tree_node_id'], ['tree_nodes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
    )
    op.create_index('ix_opportunities_project_id', 'opportunities', ['project_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('opportunities')
    op.drop_table('goals')
    op.drop_table('tree_nodes')
    op.drop_table('projects')
    op.drop_table('users')