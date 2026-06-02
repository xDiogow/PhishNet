"""Replace GoPhish with native phishing engine

Revision ID: a1b2c3d4e5f6
Revises: 3b255be786f2
Create Date: 2026-06-02

- Drop instances table
- Restructure templates: remove GoPhish ID columns, add subject/email_html/landing_page_html/redirect_url
- Restructure campaigns: remove gophish_instance_id/gophish_campaign_id FK/columns
- Restructure campaign_results: add tracking_token + event timestamps, remove modified_date
- Restructure tenants: remove gophish_group_id and instance_id columns
"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = '3b255be786f2'
branch_labels = None
depends_on = None


def upgrade():
    # ------------------------------------------------------------------ #
    # tenants — drop GoPhish columns first (FK to instances)              #
    # ------------------------------------------------------------------ #
    with op.batch_alter_table('tenants') as batch_op:
        batch_op.drop_column('gophish_group_id')
        batch_op.drop_column('instance_id')

    # ------------------------------------------------------------------ #
    # campaigns — drop GoPhish columns (FK to instances)                  #
    # ------------------------------------------------------------------ #
    with op.batch_alter_table('campaigns') as batch_op:
        # Drop unique constraint that included gophish columns
        try:
            batch_op.drop_constraint('uq_campaign_gophish_map', type_='unique')
        except Exception:
            pass
        try:
            batch_op.drop_index('ix_campaigns_instance_id')
        except Exception:
            pass
        batch_op.drop_column('gophish_instance_id')
        batch_op.drop_column('gophish_campaign_id')

    # ------------------------------------------------------------------ #
    # templates — drop GoPhish columns, add content columns               #
    # ------------------------------------------------------------------ #
    with op.batch_alter_table('templates') as batch_op:
        try:
            batch_op.drop_constraint('uq_template_map', type_='unique')
        except Exception:
            pass
        try:
            batch_op.drop_index('ix_template_maps_instance_id')
        except Exception:
            pass
        try:
            batch_op.drop_index('ix_template_maps_name')
        except Exception:
            pass
        batch_op.drop_column('gophish_instance_id')
        batch_op.drop_column('gophish_email_template_id')
        batch_op.drop_column('gophish_landing_page_id')
        batch_op.add_column(sa.Column('subject', sa.String(500), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('email_html', sa.Text, nullable=False, server_default=''))
        batch_op.add_column(sa.Column('landing_page_html', sa.Text, nullable=False, server_default=''))
        batch_op.add_column(sa.Column('redirect_url', sa.String(500), nullable=True))
        batch_op.create_index('ix_templates_name', ['name'])

    # ------------------------------------------------------------------ #
    # campaign_results — add tracking columns, remove modified_date       #
    # ------------------------------------------------------------------ #
    with op.batch_alter_table('campaign_results') as batch_op:
        batch_op.add_column(sa.Column('tracking_token', sa.String(36), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('sent_at', sa.DateTime, nullable=True))
        batch_op.add_column(sa.Column('opened_at', sa.DateTime, nullable=True))
        batch_op.add_column(sa.Column('clicked_at', sa.DateTime, nullable=True))
        batch_op.add_column(sa.Column('submitted_at', sa.DateTime, nullable=True))
        batch_op.drop_column('modified_date')
        batch_op.create_unique_constraint('uq_campaign_result_token', ['tracking_token'])
        batch_op.create_index('ix_campaign_results_campaign_id', ['campaign_id'])
        batch_op.create_index('ix_campaign_results_token', ['tracking_token'])

    # ------------------------------------------------------------------ #
    # instances — drop table last (all FKs removed above)                 #
    # ------------------------------------------------------------------ #
    op.drop_table('instances')


def downgrade():
    # Recreate instances table
    op.create_table(
        'instances',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(120), nullable=False),
        sa.Column('base_url', sa.String(500), nullable=False),
        sa.Column('api_key', sa.Text, nullable=False),
        sa.Column('redirect_url', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )

    with op.batch_alter_table('tenants') as batch_op:
        batch_op.add_column(sa.Column('gophish_group_id', sa.Integer, nullable=True))
        batch_op.add_column(sa.Column('instance_id', sa.Integer, sa.ForeignKey('instances.id'), nullable=True))

    with op.batch_alter_table('campaigns') as batch_op:
        batch_op.add_column(sa.Column('gophish_instance_id', sa.Integer, sa.ForeignKey('instances.id'), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('gophish_campaign_id', sa.Integer, nullable=False, server_default='0'))

    with op.batch_alter_table('templates') as batch_op:
        batch_op.add_column(sa.Column('gophish_instance_id', sa.Integer, sa.ForeignKey('instances.id'), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('gophish_email_template_id', sa.Integer, nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('gophish_landing_page_id', sa.Integer, nullable=False, server_default='0'))
        batch_op.drop_column('subject')
        batch_op.drop_column('email_html')
        batch_op.drop_column('landing_page_html')
        batch_op.drop_column('redirect_url')

    with op.batch_alter_table('campaign_results') as batch_op:
        batch_op.drop_column('tracking_token')
        batch_op.drop_column('sent_at')
        batch_op.drop_column('opened_at')
        batch_op.drop_column('clicked_at')
        batch_op.drop_column('submitted_at')
        batch_op.add_column(sa.Column('modified_date', sa.DateTime, nullable=True))
