"""Add scheduled_posts, published_posts, audit_logs, workflow_runs tables

Revision ID: df540a59b961
Revises: f2af254f5540
Create Date: 2026-09-08 07:04:03.906077

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df540a59b961'
down_revision: Union[str, Sequence[str], None] = 'f2af254f5540'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create scheduled_posts table
    op.create_table(
        'scheduled_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_draft_id', sa.Integer(), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'processing', 'published', 'failed', 'cancelled', name='schedulestatus'), nullable=False),
        sa.Column('published_post_id', sa.Integer(), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, default=0),
        sa.Column('max_retries', sa.Integer(), nullable=False, default=3),
        sa.Column('next_retry_at', sa.DateTime(), nullable=True),
        sa.Column('idempotency_key', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['content_draft_id'], ['content_drafts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['published_post_id'], ['published_posts.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('content_draft_id'),
        sa.UniqueConstraint('idempotency_key')
    )
    op.create_index(op.f('ix_scheduled_posts_id'), 'scheduled_posts', ['id'], unique=False)
    
    # Create published_posts table
    op.create_table(
        'published_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_draft_id', sa.Integer(), nullable=False),
        sa.Column('x_post_id', sa.String(length=255), nullable=False),
        sa.Column('x_user_id', sa.String(length=255), nullable=True),
        sa.Column('published_content', sa.Text(), nullable=False),
        sa.Column('published_title', sa.String(length=500), nullable=False),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['content_draft_id'], ['content_drafts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('content_draft_id'),
        sa.UniqueConstraint('x_post_id')
    )
    op.create_index(op.f('ix_published_posts_id'), 'published_posts', ['id'], unique=False)
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action', sa.Enum('draft_created', 'draft_updated', 'state_transition', 'quality_check_run', 'content_approved', 'content_rejected', 'post_scheduled', 'post_cancelled', 'publish_attempt', 'publish_success', 'publish_failure', 'knowledge_created', 'knowledge_updated', 'knowledge_deleted', 'brand_profile_updated', 'scheduler_run', 'workflow_started', 'workflow_completed', 'workflow_failed', name='auditaCTION'), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('action_metadata', sa.JSON(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False, default=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_id'), 'audit_logs', ['id'], unique=False)
    
    # Create workflow_runs table
    op.create_table(
        'workflow_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('execution_id', sa.String(length=255), nullable=False),
        sa.Column('workflow_type', sa.Enum('research', 'idea_generation', 'content_drafting', 'quality_check', 'analytics_analysis', name='workflowtype'), nullable=False),
        sa.Column('workflow_name', sa.String(length=255), nullable=False),
        sa.Column('status', sa.Enum('pending', 'running', 'completed', 'failed', 'cancelled', name='workflowstatus'), nullable=False),
        sa.Column('model_used', sa.String(length=255), nullable=True),
        sa.Column('input_tokens', sa.Integer(), nullable=True),
        sa.Column('output_tokens', sa.Integer(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('input_references', sa.JSON(), nullable=True),
        sa.Column('output_reference', sa.String(length=255), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('execution_id')
    )
    op.create_index(op.f('ix_workflow_runs_id'), 'workflow_runs', ['id'], unique=False)
    
    # Add foreign key index for scheduled_posts
    op.create_index(op.f('ix_scheduled_posts_content_draft_id'), 'scheduled_posts', ['content_draft_id'], unique=False)
    op.create_index(op.f('ix_scheduled_posts_published_post_id'), 'scheduled_posts', ['published_post_id'], unique=False)
    
    # Add foreign key index for published_posts
    op.create_index(op.f('ix_published_posts_content_draft_id'), 'published_posts', ['content_draft_id'], unique=False)
    
    # Add foreign key index for audit_logs
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_audit_logs_user_id'), table_name='audit_logs')
    op.drop_index(op.f('ix_published_posts_content_draft_id'), table_name='published_posts')
    op.drop_index(op.f('ix_scheduled_posts_published_post_id'), table_name='scheduled_posts')
    op.drop_index(op.f('ix_scheduled_posts_content_draft_id'), table_name='scheduled_posts')
    op.drop_index(op.f('ix_workflow_runs_id'), table_name='workflow_runs')
    op.drop_table('workflow_runs')
    op.drop_index(op.f('ix_audit_logs_id'), table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index(op.f('ix_published_posts_id'), table_name='published_posts')
    op.drop_table('published_posts')
    op.drop_index(op.f('ix_scheduled_posts_id'), table_name='scheduled_posts')
    op.drop_table('scheduled_posts')
