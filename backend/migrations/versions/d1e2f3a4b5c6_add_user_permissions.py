"""add user_permissions, drop tenant.operator_id

Revision ID: d1e2f3a4b5c6
Revises: c8d9e0f1a2b3
Create Date: 2026-07-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd1e2f3a4b5c6'
down_revision = 'c8d9e0f1a2b3'
branch_labels = None
depends_on = None

ALL_PERMISSIONS = ['manage_campaigns', 'manage_templates', 'manage_targets', 'manage_team']


def upgrade():
    op.create_table(
        'user_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('permission', sa.String(64), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'tenant_id', 'permission', name='uq_user_permission'),
    )
    op.create_index('ix_user_permissions_user_id', 'user_permissions', ['user_id'])
    op.create_index('ix_user_permissions_tenant_id', 'user_permissions', ['tenant_id'])

    # Backfill: existing operators (tenant.operator_id) get all permissions
    bind = op.get_bind()
    tenants = bind.execute(
        sa.text('SELECT id, operator_id FROM tenants WHERE operator_id IS NOT NULL')
    ).fetchall()
    for tenant in tenants:
        for perm in ALL_PERMISSIONS:
            bind.execute(
                sa.text(
                    'INSERT INTO user_permissions (user_id, tenant_id, permission) '
                    'VALUES (:uid, :tid, :perm) ON CONFLICT DO NOTHING'
                ),
                {'uid': tenant.operator_id, 'tid': tenant.id, 'perm': perm},
            )

    # Also backfill: is_admin users who may not have been recorded as operator_id
    admins = bind.execute(
        sa.text('SELECT id, tenant_id FROM users WHERE is_admin = TRUE')
    ).fetchall()
    for admin in admins:
        for perm in ALL_PERMISSIONS:
            bind.execute(
                sa.text(
                    'INSERT INTO user_permissions (user_id, tenant_id, permission) '
                    'VALUES (:uid, :tid, :perm) ON CONFLICT DO NOTHING'
                ),
                {'uid': admin.id, 'tid': admin.tenant_id, 'perm': perm},
            )

    op.drop_column('tenants', 'operator_id')


def downgrade():
    op.add_column('tenants', sa.Column('operator_id', sa.Integer(), nullable=True))
    op.drop_index('ix_user_permissions_tenant_id', 'user_permissions')
    op.drop_index('ix_user_permissions_user_id', 'user_permissions')
    op.drop_table('user_permissions')
