"""002 update leads schema

Revision ID: 002_update_leads
Revises: 001_initial
Create Date: 2026-01-08 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = '002_update_leads'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop old columns
    op.drop_column('leads', 'email')
    op.drop_column('leads', 'name')
    op.drop_column('leads', 'phone')
    op.drop_column('leads', 'source')
    op.drop_column('leads', 'session_id')
    
    # Rename metadata to request_details
    op.alter_column('leads', 'metadata', new_column_name='request_details')
    
    # Add new columns
    op.add_column('leads', sa.Column('type', sa.String(), nullable=False, server_default='training'))
    op.add_column('leads', sa.Column('diver_profile', JSONB, nullable=True))
    
    # Remove server_default after backfill
    op.alter_column('leads', 'type', server_default=None)


def downgrade() -> None:
    # Add back old columns
    op.add_column('leads', sa.Column('email', sa.String(), nullable=True))
    op.add_column('leads', sa.Column('name', sa.String(), nullable=True))
    op.add_column('leads', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('leads', sa.Column('source', sa.String(), nullable=True))
    op.add_column('leads', sa.Column('session_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
    
    # Rename request_details back to metadata
    op.alter_column('leads', 'request_details', new_column_name='metadata')
    
    # Drop new columns
    op.drop_column('leads', 'type')
    op.drop_column('leads', 'diver_profile')
