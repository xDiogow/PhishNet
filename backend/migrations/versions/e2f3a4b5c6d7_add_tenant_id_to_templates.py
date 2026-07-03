"""add tenant_id to templates

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-07-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'e2f3a4b5c6d7'
down_revision = 'd1e2f3a4b5c6'
branch_labels = None
depends_on = None


def upgrade():
    # Add tenant_id as nullable first so existing rows don't fail
    with op.batch_alter_table('templates') as batch_op:
        batch_op.add_column(sa.Column('tenant_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_templates_tenant_id',
            'tenants',
            ['tenant_id'],
            ['id'],
            ondelete='CASCADE',
        )
        batch_op.create_index('ix_templates_tenant_id', ['tenant_id'])


def downgrade():
    with op.batch_alter_table('templates') as batch_op:
        batch_op.drop_index('ix_templates_tenant_id')
        batch_op.drop_constraint('fk_templates_tenant_id', type_='foreignkey')
        batch_op.drop_column('tenant_id')
