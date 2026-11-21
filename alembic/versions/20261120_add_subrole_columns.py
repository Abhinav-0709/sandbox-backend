"""Add subrole_id and subrole_title to sandbox_environments

Revision ID: 20261120_subrole
Revises: 20261119_initial
Create Date: 2026-11-20 18:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '20261120_subrole'
down_revision = '20261119_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'sandbox_environments',
        sa.Column('subrole_id', sa.String(length=100), nullable=True)
    )
    op.add_column(
        'sandbox_environments',
        sa.Column('subrole_title', sa.String(length=100), nullable=True)
    )
    op.create_index(
        'ix_sandbox_environments_subrole_id',
        'sandbox_environments',
        ['subrole_id']
    )


def downgrade() -> None:
    op.drop_index('ix_sandbox_environments_subrole_id', table_name='sandbox_environments')
    op.drop_column('sandbox_environments', 'subrole_title')
    op.drop_column('sandbox_environments', 'subrole_id')
