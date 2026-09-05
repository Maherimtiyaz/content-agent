"""Initial migration: users, brand_profiles, content_pillars, knowledge_items

Revision ID: f2af254f5540
Revises: 
Create Date: 2026-09-05 12:22:08.564429

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2af254f5540'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create brand_profiles table
    op.create_table(
        'brand_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('professional_description', sa.Text(), nullable=True),
        sa.Column('experience', sa.Text(), nullable=True),
        sa.Column('technical_interests', sa.JSON(), nullable=True),
        sa.Column('skills', sa.JSON(), nullable=True),
        sa.Column('target_audience', sa.Text(), nullable=True),
        sa.Column('writing_style', sa.Text(), nullable=True),
        sa.Column('tone', sa.String(length=100), nullable=True),
        sa.Column('opinions', sa.Text(), nullable=True),
        sa.Column('topics_to_avoid', sa.Text(), nullable=True),
        sa.Column('example_posts', sa.JSON(), nullable=True),
        sa.Column('personal_goals', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_brand_profiles_id'), 'brand_profiles', ['id'], unique=False)

    # Create content_pillars table
    op.create_table(
        'content_pillars',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('brand_profile_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['brand_profile_id'], ['brand_profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_content_pillars_id'), 'content_pillars', ['id'], unique=False)

    # Create knowledge_items table
    op.create_table(
        'knowledge_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('knowledge_type', sa.Enum('project', 'lesson', 'experience', 'technical_note', 'opinion', 'experiment', 'idea', name='knowledgetype'), nullable=False),
        sa.Column('tags', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_knowledge_items_id'), 'knowledge_items', ['id'], unique=False)
    op.create_index(op.f('ix_knowledge_items_user_id'), 'knowledge_items', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_knowledge_items_user_id'), table_name='knowledge_items')
    op.drop_index(op.f('ix_knowledge_items_id'), table_name='knowledge_items')
    op.drop_table('knowledge_items')
    op.drop_index(op.f('ix_content_pillars_id'), table_name='content_pillars')
    op.drop_table('content_pillars')
    op.drop_index(op.f('ix_brand_profiles_id'), table_name='brand_profiles')
    op.drop_table('brand_profiles')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
