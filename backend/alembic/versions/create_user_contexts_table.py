"""Create user_contexts table

Revision ID: create_user_contexts
Revises: 
Create Date: 2025-01-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_user_contexts'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create user_contexts table for storing user session context."""
    op.create_table(
        'user_contexts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', sa.String(255), nullable=False, unique=True),
        sa.Column('primary_domain', sa.String(255), nullable=True),
        sa.Column('competitors', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('industry', sa.String(255), nullable=True),
        sa.Column('company_size', sa.String(50), nullable=True),
        sa.Column('monitoring_sites', postgresql.JSONB, nullable=True),
        sa.Column('preferences', postgresql.JSONB, nullable=True),
        sa.Column('last_analysis', sa.DateTime, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('now()'))
    )
    
    # Create index on session_id for faster lookups
    op.create_index('ix_user_contexts_session_id', 'user_contexts', ['session_id'])


def downgrade():
    """Drop user_contexts table."""
    op.drop_index('ix_user_contexts_session_id', 'user_contexts')
    op.drop_table('user_contexts')