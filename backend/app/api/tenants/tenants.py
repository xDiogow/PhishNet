from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.services.tenant_service import create_tenant, get_tenant_by_id, get_all_tenants
from app.utils.auth_helper import admin_required
from app.repository.tenant_repository import TenantRepository
from app.repository.user_repository import UserRepository

bp = Blueprint('tenants', __name__, url_prefix='/api/tenants')


def tenant_to_dict(tenant):
    """Convert tenant to dictionary"""
    return {
        'id': tenant.id,
        'name': tenant.name,
        'created_at': tenant.created_at.isoformat() if tenant.created_at else None
    }


@bp.route('', methods=['POST'])
@admin_required
def create_tenant_route():
    """Create a new tenant with an initial invitation."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        name = data.get('name')
        invitation_expires_days = data.get('invitation_expires_days')
        
        if not name:
            return jsonify({
                'error': 'Missing required field',
                'required': ['name']
            }), 400
        
        result = create_tenant(name, invitation_expires_days)
        
        if result['status'] == 'error':
            return jsonify({
                'error': result['message']
            }), 409
        
        tenant = result['tenant']
        invitation = result['invitation']
        
        return jsonify({
            'message': result['message'],
            'tenant': tenant_to_dict(tenant),
            'invitation': {
                'id': invitation.id,
                'invitation_code': invitation.invitation_code,
                'tenant_id': invitation.tenant_id,
                'is_used': invitation.is_used,
                'expires_at': invitation.expires_at.isoformat() if invitation.expires_at else None,
                'created_at': invitation.created_at.isoformat() if invitation.created_at else None
            }
        }), 201
        
    except Exception as e:
        current_app.logger.exception('Error creating tenant')
        return jsonify({'error': 'Failed to create tenant', 'message': str(e)}), 500


@bp.route('', methods=['GET'])
@admin_required
def get_all_tenants_route():
    """Get all tenants."""
    try:
        tenants = get_all_tenants()
        return jsonify({
            'tenants': [tenant_to_dict(tenant) for tenant in tenants]
        }), 200
    except Exception as e:
        current_app.logger.exception('Error getting all tenants')
        return jsonify({'error': 'Failed to get tenants', 'message': str(e)}), 500


@bp.route('/<int:tenant_id>', methods=['GET'])
@admin_required
def get_tenant_route(tenant_id):
    """Get a specific tenant by ID."""
    try:
        tenant = get_tenant_by_id(tenant_id)
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        return jsonify(tenant_to_dict(tenant)), 200
    except Exception as e:
        current_app.logger.exception('Error getting tenant')
        return jsonify({'error': 'Failed to get tenant', 'message': str(e)}), 500


@bp.route('/<int:tenant_id>', methods=['PUT'])
@admin_required
def update_tenant_route(tenant_id):
    """Update a tenant."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        tenant_repo = TenantRepository()
        tenant = tenant_repo.get_by_id(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        update_data = {}
        
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({'error': 'Tenant name cannot be empty'}), 400
            
            if name != tenant.name:
                existing_tenant = tenant_repo.get_by_name(name)
                if existing_tenant:
                    return jsonify({
                        'error': 'Tenant with this name already exists',
                        'message': 'Tenant names must be unique'
                    }), 400
            update_data['name'] = name
        
        if not update_data:
            return jsonify({'error': 'No fields to update'}), 400
        
        updated_tenant = tenant_repo.update_by_id(tenant_id, **update_data)
        
        return jsonify({
            'status': 'success',
            'message': 'Tenant updated successfully',
            'tenant': tenant_to_dict(updated_tenant)
        }), 200
            
    except ValueError as e:
        current_app.logger.error(f'Validation error updating tenant: {e}')
        return jsonify({'error': 'Invalid tenant data', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.exception('Error updating tenant')
        return jsonify({'error': 'Failed to update tenant', 'message': str(e)}), 500


@bp.route('/<int:tenant_id>', methods=['DELETE'])
@admin_required
def delete_tenant_route(tenant_id):
    """Delete a tenant."""
    try:
        tenant_repo = TenantRepository()
        tenant = tenant_repo.get_by_id(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
        
        # Check if tenant has users
        user_repo = UserRepository()
        users = user_repo.get_all_by_tenant_id(tenant_id, active_only=False)
        
        if users:
            user_emails = [user.email for user in users]
            return jsonify({
                'error': 'Cannot delete tenant with associated users',
                'message': f'There are {len(users)} user(s) in this tenant',
                'users': user_emails,
                'details': 'Please delete or reassign all users before deleting this tenant'
            }), 400
        
        tenant_repo.delete(tenant_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Tenant deleted successfully'
        }), 200
            
    except ValueError as e:
        return jsonify({'error': 'Invalid tenant ID', 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.exception('Error deleting tenant')
        return jsonify({'error': 'Failed to delete tenant', 'message': str(e)}), 500
