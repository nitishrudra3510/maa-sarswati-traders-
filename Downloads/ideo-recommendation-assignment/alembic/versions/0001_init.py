"""Initial database migration for Video Recommendation Engine

Revision ID: 0001_init
Revises: 
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database tables."""
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create videos table
    op.create_table('videos',
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('posted_at', sa.DateTime(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('video_id')
    )
    op.create_index(op.f('ix_videos_video_id'), 'videos', ['video_id'], unique=False)
    op.create_index(op.f('ix_videos_category'), 'videos', ['category'], unique=False)
    
    # Create user_engagements table
    op.create_table('user_engagements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('engagement_type', sa.Enum('VIEW', 'LIKE', 'INSPIRE', 'RATING', name='engagementtype'), nullable=False),
        sa.Column('rating_score', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.video_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_engagements_id'), 'user_engagements', ['id'], unique=False)
    op.create_index(op.f('ix_user_engagements_engagement_type'), 'user_engagements', ['engagement_type'], unique=False)
    op.create_index(op.f('ix_user_engagements_timestamp'), 'user_engagements', ['timestamp'], unique=False)


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index(op.f('ix_user_engagements_timestamp'), table_name='user_engagements')
    op.drop_index(op.f('ix_user_engagements_engagement_type'), table_name='user_engagements')
    op.drop_index(op.f('ix_user_engagements_id'), table_name='user_engagements')
    op.drop_table('user_engagements')
    op.drop_index(op.f('ix_videos_category'), table_name='videos')
    op.drop_index(op.f('ix_videos_video_id'), table_name='videos')
    op.drop_table('videos')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')