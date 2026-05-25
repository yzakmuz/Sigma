"""Add user_attempts table for tracking problem submissions

Revision ID: 002_add_user_attempts
Revises: 001_initial_schema
Create Date: 2026-04-13

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_user_attempts'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_attempts table
    op.create_table(
        'user_attempts',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('problem_id', sa.String(36), nullable=False),
        sa.Column('submitted_answer', sa.Text(), nullable=False),
        sa.Column('is_correct', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('attempt_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('time_spent_seconds', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index(op.f('ix_user_attempts_user_id'), 'user_attempts', ['user_id'])
    op.create_index(op.f('ix_user_attempts_problem_id'), 'user_attempts', ['problem_id'])
    op.create_index(op.f('ix_user_attempts_created_at'), 'user_attempts', ['created_at'])


def downgrade() -> None:
    op.drop_index(op.f('ix_user_attempts_created_at'), table_name='user_attempts')
    op.drop_index(op.f('ix_user_attempts_problem_id'), table_name='user_attempts')
    op.drop_index(op.f('ix_user_attempts_user_id'), table_name='user_attempts')
    op.drop_table('user_attempts')
