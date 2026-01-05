"""001 initial (no-op)

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # No-op initial migration: schema exists from Drizzle
    pass

def downgrade() -> None:
    pass
