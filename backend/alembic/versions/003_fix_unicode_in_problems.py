"""Fix unicode in problems_json

Revision ID: 003_fix_unicode_in_problems
Revises: 002_add_user_attempts
Create Date: 2026-05-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic.
revision = '003_fix_unicode_in_problems'
down_revision = '002_add_user_attempts'
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    
    result = bind.execute(sa.text("SELECT id, problems_json FROM lessons"))
    for row in result:
        lesson_id = row[0]
        problems_json = row[1]
        
        if problems_json and chr(0x05b2) in problems_json:
            new_json = problems_json.replace(chr(0x05b2), '')
            bind.execute(
                sa.text("UPDATE lessons SET problems_json = :new_json WHERE id = :id"),
                {"new_json": new_json, "id": lesson_id}
            )
            
    session.commit()

def downgrade() -> None:
    pass
