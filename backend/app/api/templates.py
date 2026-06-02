"""Template API routes"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.gophish import TemplatesService
from app.repository.user_repository import UserRepository
from app.utils.auth_helper import admin_required

bp = Blueprint('templates', __name__, url_prefix='/api/templates')


def template_summary_to_dict(template_map) -> dict:
    """Convert template to summary dictionary"""
    return {
        'id': template_map.id,
        'name': template_map.name,
        'created_by_user_id': template_map.created_by_user_id,
        'created_at': template_map.created_at.isoformat() if template_map.created_at else None,
    }


def template_detail_to_dict(template_details: dict) -> dict:
    """Convert template to detail dictionary"""
    template_map = template_details['template_map']
    email_template = template_details['email_template']
    landing_page = template_details['landing_page']
    
    result = template_summary_to_dict(template_map)
    result['email_template'] = {
        'id': email_template.id,
        'name': email_template.name,
        'subject': getattr(email_template, 'subject', ''),
        'html': email_template.html,
        'attachments': [{'name': att.name, 'type': att.type} for att in getattr(email_template, 'attachments', [])]
    }
    result['landing_page'] = {
        'id': landing_page.id,
        'name': landing_page.name,
        'html': landing_page.html,
        'redirect_url': getattr(landing_page, 'redirect_url', ''),
    }
    
    return result


@bp.route('', methods=['GET'])
@jwt_required()
def get_all_templates():
    try:
        service = TemplatesService()
        templates = service.get_all_templates()
        
        return jsonify({
            'templates': [template_summary_to_dict(template) for template in templates]
        }), 200
    except Exception as e:
        current_app.logger.exception('Error getting all templates')
        return jsonify({'error': 'Failed to get templates', 'message': str(e)}), 500


@bp.route('/<int:template_id>', methods=['GET'])
@admin_required
def get_template(template_id):
    try:
        service = TemplatesService()
        template_details = service.get_template_details(template_id)
        
        if not template_details:
            return jsonify({'error': 'Template not found'}), 404
        
        return jsonify(template_detail_to_dict(template_details)), 200
    except Exception as e:
        current_app.logger.exception('Error getting template')
        return jsonify({'error': 'Failed to get template', 'message': str(e)}), 500


@bp.route('', methods=['POST'])
@admin_required
def create_template():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user_id = get_jwt_identity()
        user_repo = UserRepository()
        user = user_repo.get_by_id(user_id)
        
        required_fields = ['name', 'email_template_data', 'landing_page_data']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields,
                'missing': missing_fields
            }), 400
        
        email_template_data = data.get('email_template_data', {})
        subject = email_template_data.get('subject', '').strip() if email_template_data.get('subject') else ''
        if not subject:
            return jsonify({
                'error': 'Email template subject is required and cannot be empty'
            }), 400
        if not email_template_data.get('html'):
            return jsonify({
                'error': 'Email template HTML is required'
            }), 400
        
        landing_page_data = data.get('landing_page_data', {})
        if not landing_page_data.get('html'):
            return jsonify({
                'error': 'Landing page HTML is required'
            }), 400
        
        service = TemplatesService()
        result = service.create_template(
            name=data.get('name'),
            email_template_data=email_template_data,
            landing_page_data=landing_page_data,
            created_by_user_id=user.id
        )
        
        if result.get('status') == 'success':
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except TypeError as e:
        current_app.logger.error(f'Type error creating template: {e}')
        return jsonify({'error': 'Invalid template data', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.exception('Error creating template')
        return jsonify({'error': 'Failed to create template', 'message': str(e)}), 500


@bp.route('/<int:template_id>', methods=['PUT'])
@admin_required
def update_template(template_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email_template_data = data.get('email_template_data')
        if email_template_data:
            # Subject is required when updating email_template_data
            subject = email_template_data.get('subject', '').strip() if email_template_data.get('subject') else ''
            if not subject:
                return jsonify({
                    'error': 'Email template subject is required and cannot be empty'
                }), 400
        
        service = TemplatesService()
        result = service.update_template(
            template_id=template_id,
            name=data.get('name'),
            email_template_data=email_template_data,
            landing_page_data=data.get('landing_page_data')
        )
        
        if result.get('status') == 'success':
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except ValueError as e:
        return jsonify({'error': 'Invalid template ID', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.exception('Error updating template')
        return jsonify({'error': 'Failed to update template', 'message': str(e)}), 500


@bp.route('/<int:template_id>', methods=['DELETE'])
@admin_required
def delete_template(template_id):
    try:
        service = TemplatesService()
        result = service.delete_template(template_id)
        
        if result.get('status') == 'success':
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except ValueError as e:
        return jsonify({'error': 'Invalid template ID', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.exception('Error deleting template')
        return jsonify({'error': 'Failed to delete template', 'message': str(e)}), 500
