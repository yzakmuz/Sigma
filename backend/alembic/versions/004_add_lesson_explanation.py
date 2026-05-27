"""Add explanation to lessons

Revision ID: 004_add_lesson_explanation
Revises: 003_fix_unicode_in_problems
Create Date: 2026-05-27

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004_add_lesson_explanation'
down_revision = '003_fix_unicode_in_problems'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add explanation column to lessons table
    op.add_column('lessons', sa.Column('explanation', sa.Text(), nullable=True))

def downgrade() -> None:
    # Remove explanation column from lessons table
    op.drop_column('lessons', 'explanation')