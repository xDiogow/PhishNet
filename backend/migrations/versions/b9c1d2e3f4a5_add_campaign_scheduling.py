"""add campaign scheduling fields

Revision ID: b9c1d2e3f4a5
Revises: a1b2c3d4e5f6
Create Date: 2026-06-30 22:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b9c1d2e3f4a5'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        with op.get_context().autocommit_block():
            op.execute(sa.text("ALTER TYPE campaignstatus ADD VALUE IF NOT EXISTS 'SCHEDULED'"))

    with op.batch_alter_table('campaigns') as batch_op:
        batch_op.add_column(sa.Column('scheduled_start_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('scheduled_end_at', sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table('campaigns') as batch_op:
        batch_op.drop_column('scheduled_end_at')
        batch_op.drop_column('scheduled_start_at')
    # PostgreSQL enum values cannot be removed without recreating the type
