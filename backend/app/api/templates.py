"""Template API routes.

Template scoping:
  Global templates  (tenant_id IS NULL) — created by platform admins, visible to all
                                          tenants, editable only by platform admins.
  Tenant templates  (tenant_id = X)     — created by tenant users with manage_templates,
                                          visible/editable only within that tenant.

Routes:
  GET    /api/templates        list accessible templates (global + own)
  GET    /api/templates/<id>   template detail (manage_templates or admin)
  POST   /api/templates        create template (admin → global, manage_templates → tenant)
  PUT    /api/templates/<id>   update (admin for global, manage_templates for own)
  DELETE /api/templates/<id>   delete (same rules as PUT)
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.models.template import Template
from app.models.campaign import Campaign, CampaignStatus
from app.repository.template_repository import TemplateRepository
from app.utils.auth_helper import get_current_user, has_permission
from app.extensions import db

bp = Blueprint('templates', __name__, url_prefix='/api/templates')


def template_to_dict(template: Template) -> dict:
    return {
        'id': template.id,
        'name': template.name,
        'is_global': template.tenant_id is None,
        'tenant_id': template.tenant_id,
        'created_by_user_id': template.created_by_user_id,
        'created_at': template.created_at.isoformat() if template.created_at else None,
        'email_template': {
            'subject': template.subject,
            'html': template.email_html,
        },
        'landing_page': {
            'html': template.landing_page_html,
        },
    }


def _can_manage(user, template: Template) -> bool:
    """Return True if user may edit or delete this template."""
    if template.tenant_id is None:
        return user.is_admin
    return template.tenant_id == user.tenant_id and has_permission(user, 'manage_templates')


def _running_campaigns_using(template_id: int) -> list:
    return (
        db.session.query(Campaign)
        .filter(
            Campaign.template_id == template_id,
            Campaign.status == CampaignStatus.RUNNING,
        )
        .all()
    )


@bp.route('', methods=['GET'])
@jwt_required()
def get_all_templates():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        templates = TemplateRepository().get_all_for_tenant(user.tenant_id)
        return jsonify({'templates': [template_to_dict(t) for t in templates]}), 200
    except Exception:
        current_app.logger.exception('Error getting templates')
        return jsonify({'error': 'Failed to get templates'}), 500


@bp.route('/<int:template_id>', methods=['GET'])
@jwt_required()
def get_template(template_id):
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.is_admin and not has_permission(user, 'manage_templates'):
            return jsonify({'error': 'Permission denied', 'required': 'manage_templates'}), 403

        template = TemplateRepository().get_by_id_for_tenant(template_id, user.tenant_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        return jsonify(template_to_dict(template)), 200
    except Exception:
        current_app.logger.exception('Error getting template')
        return jsonify({'error': 'Failed to get template'}), 500


@bp.route('', methods=['POST'])
@jwt_required()
def create_template():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.is_admin and not has_permission(user, 'manage_templates'):
            return jsonify({'error': 'Permission denied', 'required': 'manage_templates'}), 403

        email_data = data.get('email_template_data', {})
        landing_data = data.get('landing_page_data', {})

        missing = [f for f in ['name', 'email_template_data', 'landing_page_data'] if not data.get(f)]
        if missing:
            return jsonify({'error': 'Missing required fields', 'missing': missing}), 400

        subject = (email_data.get('subject') or '').strip()
        if not subject:
            return jsonify({'error': 'Email template subject is required'}), 400
        if not email_data.get('html'):
            return jsonify({'error': 'Email template HTML is required'}), 400
        if not landing_data.get('html'):
            return jsonify({'error': 'Landing page HTML is required'}), 400

        # Platform admins create global templates; tenant users create tenant-private templates
        tenant_id = None if user.is_admin else user.tenant_id

        template = Template(
            tenant_id=tenant_id,
            name=data['name'],
            subject=subject,
            email_html=email_data['html'],
            landing_page_html=landing_data['html'],
            created_by_user_id=user.id,
        )
        TemplateRepository().create(template)

        return jsonify({
            'status': 'success',
            'message': 'Template created successfully',
            'template': template_to_dict(template),
        }), 201
    except Exception:
        current_app.logger.exception('Error creating template')
        return jsonify({'error': 'Failed to create template'}), 500


@bp.route('/<int:template_id>', methods=['PUT'])
@jwt_required()
def update_template(template_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        repo = TemplateRepository()
        template = repo.get_by_id_for_tenant(template_id, user.tenant_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        if not _can_manage(user, template):
            return jsonify({'error': 'Permission denied'}), 403

        running = _running_campaigns_using(template_id)
        if running:
            name_list = [c.name for c in running]
            names = ', '.join(name_list)
            return jsonify({
                'error': 'Template is in use by a running campaign',
                'message': (
                    f"Cannot edit this template while campaign(s) [{names}] are running. "
                    "Stop the campaign first, then update the template."
                ),
            }), 409

        email_data = data.get('email_template_data')
        landing_data = data.get('landing_page_data')

        if data.get('name'):
            template.name = data['name']
        if email_data:
            subject = (email_data.get('subject') or '').strip()
            if not subject:
                return jsonify({'error': 'Email template subject cannot be empty'}), 400
            template.subject = subject
            if email_data.get('html'):
                template.email_html = email_data['html']
        if landing_data:
            if landing_data.get('html'):
                template.landing_page_html = landing_data['html']

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Template updated successfully',
            'template': template_to_dict(template),
        }), 200
    except Exception:
        current_app.logger.exception('Error updating template')
        return jsonify({'error': 'Failed to update template'}), 500


@bp.route('/<int:template_id>', methods=['DELETE'])
@jwt_required()
def delete_template(template_id):
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        repo = TemplateRepository()
        template = repo.get_by_id_for_tenant(template_id, user.tenant_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        if not _can_manage(user, template):
            return jsonify({'error': 'Permission denied'}), 403

        running = _running_campaigns_using(template_id)
        if running:
            name_list = [c.name for c in running]
            names = ', '.join(name_list)
            return jsonify({
                'error': 'Template is in use by a running campaign',
                'message': (
                    f"Cannot delete this template while campaign(s) [{names}] are running. "
                    "Stop the campaign first."
                ),
            }), 409

        repo.delete(template_id)
        return jsonify({'status': 'success', 'message': 'Template deleted successfully'}), 200
    except Exception:
        current_app.logger.exception('Error deleting template')
        return jsonify({'error': 'Failed to delete template'}), 500
