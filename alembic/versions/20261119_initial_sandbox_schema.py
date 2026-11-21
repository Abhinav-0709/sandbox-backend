"""Initial sandbox microservice schema

Revision ID: 20261119_initial
Revises: 
Create Date: 2026-11-19 19:22:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20261119_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. sandbox_environments
    op.create_table(
        'sandbox_environments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=False),
        sa.Column('role_title', sa.String(length=100), nullable=False),
        sa.Column('difficulty', sa.String(length=50), nullable=False, server_default='intermediate'),
        sa.Column('estimated_minutes', sa.SmallInteger(), nullable=False, server_default='40'),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('evaluation_rules', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('version', sa.String(length=20), nullable=False, server_default='1.0.0'),
        sa.Column('external_simulation_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_sandbox_environments_slug', 'sandbox_environments', ['slug'], unique=True)
    op.create_index('ix_sandbox_environments_category', 'sandbox_environments', ['category'])

    # 2. sandbox_sessions
    op.create_table(
        'sandbox_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('environment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sandbox_environments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_sub', sa.String(length=255), nullable=True),
        sa.Column('user_email', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='CREATED'),
        sa.Column('workspace_state', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('time_limit_seconds', sa.Integer(), nullable=False, server_default='2400'),
        sa.Column('time_remaining_seconds', sa.Integer(), nullable=False, server_default='2400'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('session_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_sandbox_sessions_status', 'sandbox_sessions', ['status'])
    op.create_index('ix_sandbox_sessions_env', 'sandbox_sessions', ['environment_id'])
    op.create_index('ix_sandbox_sessions_user', 'sandbox_sessions', ['user_sub'])

    # 3. sandbox_activity_events
    op.create_table(
        'sandbox_activity_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sandbox_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('event_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('client_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('server_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sequence_no', sa.Integer(), nullable=False, server_default='1'),
    )
    op.create_index('ix_sandbox_events_session', 'sandbox_activity_events', ['session_id'])
    op.create_index('ix_sandbox_events_seq', 'sandbox_activity_events', ['session_id', 'sequence_no'])

    # 4. sandbox_submissions
    op.create_table(
        'sandbox_submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sandbox_sessions.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('workspace_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('answers', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('integrity_flags', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 5. sandbox_evaluation_results
    op.create_table(
        'sandbox_evaluation_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('submission_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sandbox_submissions.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sandbox_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('overall_score', sa.Integer(), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('evaluation_method', sa.String(length=50), nullable=False, server_default='deterministic'),
        sa.Column('score_breakdown', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('task_evaluations', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('question_evaluations', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('integrity_audit', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('feedback_summary', sa.Text(), nullable=True),
        sa.Column('evaluator_version', sa.String(length=20), nullable=False, server_default='1.0.0'),
        sa.Column('evaluated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_sandbox_eval_session', 'sandbox_evaluation_results', ['session_id'])


def downgrade() -> None:
    op.drop_table('sandbox_evaluation_results')
    op.drop_table('sandbox_submissions')
    op.drop_table('sandbox_activity_events')
    op.drop_table('sandbox_sessions')
    op.drop_table('sandbox_environments')
