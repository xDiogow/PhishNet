"""Add reported_at to campaign_results

Revision ID: e3f4a5b6c7d8
Revises: e2f3a4b5c6d7
Create Date: 2026-07-02

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e3f4a5b6c7d8'
down_revision = 'e2f3a4b5c6d7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('campaign_results', sa.Column('reported_at', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('campaign_results', 'reported_at')
