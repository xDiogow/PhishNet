"""add email to tenant_invitations

Revision ID: c8d9e0f1a2b3
Revises: b9c1d2e3f4a5
Create Date: 2026-06-30 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'c8d9e0f1a2b3'
down_revision = 'b9c1d2e3f4a5'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('tenant_invitations', sa.Column('email', sa.String(255), nullable=True))


def downgrade():
    op.drop_column('tenant_invitations', 'email')
