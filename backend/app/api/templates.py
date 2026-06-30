"""Template API routes.

Templates are stored entirely in the database. Each template bundles an
email (subject + HTML) and a landing page (HTML + optional redirect URL).
Admin-only endpoints require the @admin_required decorator.

Routes:
  GET    /api/templates        list all templates (any authenticated user)
  GET    /api/templates/<id>   get template detail (admin only)
  POST   /api/templates        create a template (admin only)
  PUT    /api/templates/<id>   update a template (admin only)
  DELETE /api/templates/<id>   delete a template (admin only)

HTML placeholders available to template authors:
  {{TRACKING_PIXEL}} — replaced with a 1×1 tracking pixel img tag when sending
  {{CLICK_URL}}      — replaced with the click-tracking redirect URL
  {{FORM_ACTION}}    — injected into the landing page form action attribute
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.template import Template
from app.models.campaign import Campaign, CampaignStatus
from app.repository.template_repository import TemplateRepository
from app.utils.auth_helper import admin_required
from app.extensions import db

bp = Blueprint('templates', __name__, url_prefix='/api/templates')


def template_to_dict(template: Template) -> dict:
    """Serialise a Template model to the API response shape."""
    return {
        'id': template.id,
        'name': template.name,
        'created_by_user_id': template.created_by_user_id,
        'created_at': template.created_at.isoformat() if template.created_at else None,
        'email_template': {
            'subject': template.subject,
            'html': template.email_html,
        },
        'landing_page': {
            'html': template.landing_page_html,
            'redirect_url': template.redirect_url or '',
        },
    }


@bp.route('', methods=['GET'])
@jwt_required()
def get_all_templates():
    """Return all templates. Available to any authenticated user."""
    try:
        repo = TemplateRepository()
        templates = repo.get_all()
        return jsonify({'templates': [template_to_dict(t) for t in templates]}), 200
    except Exception as e:
        current_app.logger.exception('Error getting templates')
        return jsonify({'error': 'Failed to get templates', 'message': str(e)}), 500


@bp.route('/<int:template_id>', methods=['GET'])
@admin_required
def get_template(template_id):
    """Return full detail for one template, including HTML bodies."""
    try:
        repo = TemplateRepository()
        template = repo.get_by_id(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        return jsonify(template_to_dict(template)), 200
    except Exception as e:
        current_app.logger.exception('Error getting template')
        return jsonify({'error': 'Failed to get template', 'message': str(e)}), 500


@bp.route('', methods=['POST'])
@admin_required
def create_template():
    """Create a new template.

    Expected body::

        {
            "name": "string",
            "email_template_data": {"subject": "...", "html": "..."},
            "landing_page_data":   {"html": "...", "redirect_url": "..."}
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user_id = get_jwt_identity()

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

        repo = TemplateRepository()
        template = Template(
            name=data['name'],
            subject=subject,
            email_html=email_data['html'],
            landing_page_html=landing_data['html'],
            redirect_url=landing_data.get('redirect_url') or None,
            created_by_user_id=int(user_id),
        )
        repo.create(template)

        return jsonify({
            'status': 'success',
            'message': 'Template created successfully',
            'template': template_to_dict(template),
        }), 201
    except Exception as e:
        current_app.logger.exception('Error creating template')
        return jsonify({'error': 'Failed to create template', 'message': str(e)}), 500


def _running_campaigns_using(template_id: int) -> list:
    """Return running campaigns that reference this template."""
    return (
        db.session.query(Campaign)
        .filter(
            Campaign.template_id == template_id,
            Campaign.status == CampaignStatus.RUNNING,
        )
        .all()
    )


@bp.route('/<int:template_id>', methods=['PUT'])
@admin_required
def update_template(template_id):
    """Partially update a template. All fields are optional — only provided fields are changed.

    Returns 409 if the template is currently used by a RUNNING campaign — editing it
    would change the landing page rendered for already-sent tracking links.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        repo = TemplateRepository()
        template = repo.get_by_id(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        running = _running_campaigns_using(template_id)
        if running:
            names = ', '.join(c.name for c in running)
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
            if 'redirect_url' in landing_data:
                template.redirect_url = landing_data['redirect_url'] or None

        from app.extensions import db
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Template updated successfully',
            'template': template_to_dict(template),
        }), 200
    except Exception as e:
        current_app.logger.exception('Error updating template')
        return jsonify({'error': 'Failed to update template', 'message': str(e)}), 500


@bp.route('/<int:template_id>', methods=['DELETE'])
@admin_required
def delete_template(template_id):
    """Permanently delete a template.

    Returns 409 if the template is used by a RUNNING campaign.
    """
    try:
        repo = TemplateRepository()
        template = repo.get_by_id(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404

        running = _running_campaigns_using(template_id)
        if running:
            names = ', '.join(c.name for c in running)
            return jsonify({
                'error': 'Template is in use by a running campaign',
                'message': (
                    f"Cannot delete this template while campaign(s) [{names}] are running. "
                    "Stop the campaign first."
                ),
            }), 409

        repo.delete(template_id)
        return jsonify({'status': 'success', 'message': 'Template deleted successfully'}), 200
    except Exception as e:
        current_app.logger.exception('Error deleting template')
        return jsonify({'error': 'Failed to delete template', 'message': str(e)}), 500
