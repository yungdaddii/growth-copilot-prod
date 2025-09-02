"""Add User model and authentication fields

Revision ID: 174593336801
Revises: d995feb98eea
Create Date: 2025-09-01 20:25:42.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '174593336801'
down_revision: Union[str, None] = 'd995feb98eea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create subscription tier and status enums
    op.execute("CREATE TYPE subscriptiontier AS ENUM ('free', 'starter', 'pro', 'enterprise')")
    op.execute("CREATE TYPE subscriptionstatus AS ENUM ('active', 'cancelled', 'past_due', 'trialing', 'inactive')")
    
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('firebase_uid', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=True),
        sa.Column('photo_url', sa.String(), nullable=True),
        sa.Column('phone_number', sa.String(), nullable=True),
        sa.Column('company_name', sa.String(), nullable=True),
        sa.Column('company_website', sa.String(), nullable=True),
        sa.Column('company_size', sa.String(), nullable=True),
        sa.Column('industry', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('subscription_tier', postgresql.ENUM('free', 'starter', 'pro', 'enterprise', name='subscriptiontier'), nullable=False),
        sa.Column('subscription_status', postgresql.ENUM('active', 'cancelled', 'past_due', 'trialing', 'inactive', name='subscriptionstatus'), nullable=False),
        sa.Column('trial_ends_at', sa.DateTime(), nullable=True),
        sa.Column('stripe_customer_id', sa.String(), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(), nullable=True),
        sa.Column('monthly_analyses_limit', sa.Integer(), nullable=True),
        sa.Column('monthly_analyses_used', sa.Integer(), nullable=True),
        sa.Column('can_use_ai_chat', sa.Boolean(), nullable=True),
        sa.Column('can_export_data', sa.Boolean(), nullable=True),
        sa.Column('can_use_api', sa.Boolean(), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=True),
        sa.Column('email_notifications', sa.Boolean(), nullable=True),
        sa.Column('weekly_report', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.Column('last_active_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_firebase_uid'), 'users', ['firebase_uid'], unique=True)
    op.create_index(op.f('ix_users_stripe_customer_id'), 'users', ['stripe_customer_id'], unique=True)
    
    # Create user_contexts table
    op.create_table('user_contexts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('primary_domain', sa.String(), nullable=True),
        sa.Column('competitors', sa.JSON(), nullable=True),
        sa.Column('industry', sa.String(), nullable=True),
        sa.Column('company_size', sa.String(), nullable=True),
        sa.Column('monitoring_sites', sa.JSON(), nullable=True),
        sa.Column('preferences', sa.JSON(), nullable=True),
        sa.Column('last_analysis', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_contexts_session_id'), 'user_contexts', ['session_id'], unique=True)
    op.create_index(op.f('ix_user_contexts_user_id'), 'user_contexts', ['user_id'], unique=False)
    
    # Create site_snapshots table
    op.create_table('site_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('domain', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('snapshot_date', sa.DateTime(), nullable=True),
        sa.Column('page_title', sa.String(), nullable=True),
        sa.Column('meta_description', sa.Text(), nullable=True),
        sa.Column('headlines', sa.JSON(), nullable=True),
        sa.Column('cta_buttons', sa.JSON(), nullable=True),
        sa.Column('form_fields', sa.JSON(), nullable=True),
        sa.Column('images_count', sa.Integer(), nullable=True),
        sa.Column('testimonials_count', sa.Integer(), nullable=True),
        sa.Column('load_time', sa.Float(), nullable=True),
        sa.Column('page_size', sa.Float(), nullable=True),
        sa.Column('requests_count', sa.Integer(), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('internal_links', sa.Integer(), nullable=True),
        sa.Column('external_links', sa.Integer(), nullable=True),
        sa.Column('technologies', sa.JSON(), nullable=True),
        sa.Column('content_hash', sa.String(), nullable=True),
        sa.Column('full_content', sa.Text(), nullable=True),
        sa.Column('changes_detected', sa.JSON(), nullable=True),
        sa.Column('change_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_site_snapshots_domain'), 'site_snapshots', ['domain'], unique=False)
    op.create_index(op.f('ix_site_snapshots_snapshot_date'), 'site_snapshots', ['snapshot_date'], unique=False)
    
    # Create competitor_intelligence table
    op.create_table('competitor_intelligence',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('domain', sa.String(), nullable=True),
        sa.Column('industry', sa.String(), nullable=True),
        sa.Column('estimated_traffic', sa.Integer(), nullable=True),
        sa.Column('traffic_growth', sa.Float(), nullable=True),
        sa.Column('domain_authority', sa.Integer(), nullable=True),
        sa.Column('conversion_score', sa.Float(), nullable=True),
        sa.Column('conversion_elements', sa.JSON(), nullable=True),
        sa.Column('recent_updates', sa.JSON(), nullable=True),
        sa.Column('new_features', sa.JSON(), nullable=True),
        sa.Column('ab_tests', sa.JSON(), nullable=True),
        sa.Column('best_practices', sa.JSON(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_competitor_intelligence_domain'), 'competitor_intelligence', ['domain'], unique=False)
    op.create_index(op.f('ix_competitor_intelligence_industry'), 'competitor_intelligence', ['industry'], unique=False)
    
    # Create growth_benchmarks table
    op.create_table('growth_benchmarks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('industry', sa.String(), nullable=True),
        sa.Column('metric_name', sa.String(), nullable=True),
        sa.Column('p10_value', sa.Float(), nullable=True),
        sa.Column('p25_value', sa.Float(), nullable=True),
        sa.Column('median_value', sa.Float(), nullable=True),
        sa.Column('p75_value', sa.Float(), nullable=True),
        sa.Column('p90_value', sa.Float(), nullable=True),
        sa.Column('sample_size', sa.Integer(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('impact_on_conversion', sa.Float(), nullable=True),
        sa.Column('implementation_difficulty', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_growth_benchmarks_industry'), 'growth_benchmarks', ['industry'], unique=False)
    
    # Create growth_experiments table
    op.create_table('growth_experiments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('domain', sa.String(), nullable=True),
        sa.Column('experiment_type', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('hypothesis', sa.Text(), nullable=True),
        sa.Column('predicted_impact', sa.Float(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('impact_metric', sa.String(), nullable=True),
        sa.Column('implementation_code', sa.Text(), nullable=True),
        sa.Column('implementation_difficulty', sa.String(), nullable=True),
        sa.Column('estimated_hours', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('actual_impact', sa.Float(), nullable=True),
        sa.Column('similar_experiments', sa.JSON(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_growth_experiments_session_id'), 'growth_experiments', ['session_id'], unique=False)
    
    # Add user_id and session_id columns to existing tables
    op.add_column('conversations', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('conversations', sa.Column('session_id', sa.String(), nullable=True))
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)
    op.create_index(op.f('ix_conversations_session_id'), 'conversations', ['session_id'], unique=False)
    op.create_foreign_key('fk_conversations_user_id', 'conversations', 'users', ['user_id'], ['id'])
    
    op.add_column('analyses', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index(op.f('ix_analyses_user_id'), 'analyses', ['user_id'], unique=False)
    op.create_foreign_key('fk_analyses_user_id', 'analyses', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    # Drop foreign keys first
    op.drop_constraint('fk_analyses_user_id', 'analyses', type_='foreignkey')
    op.drop_constraint('fk_conversations_user_id', 'conversations', type_='foreignkey')
    
    # Remove added columns from existing tables
    op.drop_index(op.f('ix_analyses_user_id'), table_name='analyses')
    op.drop_column('analyses', 'user_id')
    
    op.drop_index(op.f('ix_conversations_session_id'), table_name='conversations')
    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    op.drop_column('conversations', 'session_id')
    op.drop_column('conversations', 'user_id')
    
    # Drop new tables
    op.drop_index(op.f('ix_growth_experiments_session_id'), table_name='growth_experiments')
    op.drop_table('growth_experiments')
    
    op.drop_index(op.f('ix_growth_benchmarks_industry'), table_name='growth_benchmarks')
    op.drop_table('growth_benchmarks')
    
    op.drop_index(op.f('ix_competitor_intelligence_industry'), table_name='competitor_intelligence')
    op.drop_index(op.f('ix_competitor_intelligence_domain'), table_name='competitor_intelligence')
    op.drop_table('competitor_intelligence')
    
    op.drop_index(op.f('ix_site_snapshots_snapshot_date'), table_name='site_snapshots')
    op.drop_index(op.f('ix_site_snapshots_domain'), table_name='site_snapshots')
    op.drop_table('site_snapshots')
    
    op.drop_index(op.f('ix_user_contexts_user_id'), table_name='user_contexts')
    op.drop_index(op.f('ix_user_contexts_session_id'), table_name='user_contexts')
    op.drop_table('user_contexts')
    
    op.drop_index(op.f('ix_users_stripe_customer_id'), table_name='users')
    op.drop_index(op.f('ix_users_firebase_uid'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE subscriptionstatus')
    op.execute('DROP TYPE subscriptiontier')