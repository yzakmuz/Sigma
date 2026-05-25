"""Initial schema creation

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-04-12

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_created_at'), 'users', ['created_at'])

    # Create lessons table
    op.create_table(
        'lessons',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('topic', sa.Enum('arithmetic', 'algebra', 'geometry'), nullable=False),
        sa.Column('level', sa.Enum('beginner', 'intermediate', 'advanced'), nullable=False),
        sa.Column('problems_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_lessons_topic'), 'lessons', ['topic'])
    op.create_index(op.f('ix_lessons_level'), 'lessons', ['level'])
    op.create_index(op.f('ix_lessons_created_at'), 'lessons', ['created_at'])

    # Create user_progress table
    op.create_table(
        'user_progress',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('lesson_id', sa.String(36), nullable=False),
        sa.Column('status', sa.Enum('not_started', 'in_progress', 'completed'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_user_progress_user_id'), 'user_progress', ['user_id'])
    op.create_index(op.f('ix_user_progress_lesson_id'), 'user_progress', ['lesson_id'])
    op.create_index(op.f('ix_user_progress_status'), 'user_progress', ['status'])


def downgrade() -> None:
    op.drop_index(op.f('ix_user_progress_status'), table_name='user_progress')
    op.drop_index(op.f('ix_user_progress_lesson_id'), table_name='user_progress')
    op.drop_index(op.f('ix_user_progress_user_id'), table_name='user_progress')
    op.drop_table('user_progress')

    op.drop_index(op.f('ix_lessons_created_at'), table_name='lessons')
    op.drop_index(op.f('ix_lessons_level'), table_name='lessons')
    op.drop_index(op.f('ix_lessons_topic'), table_name='lessons')
    op.drop_table('lessons')

    op.drop_index(op.f('ix_users_created_at'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
