from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from app.services.tenant_invitation_service import (
    create_invitation,
    validate_invitation,
    get_invitation_by_code,
    get_invitations_by_tenant
)

bp = Blueprint('tenant_invitations', __name__, url_prefix='/api/tenant-invitations')


@bp.route('', methods=['POST'])
@jwt_required()
def create_invitation_route():
    """Create a new invitation for a tenant."""
    try:
        from flask_jwt_extended import get_jwt_identity
        from app.repository.user_repository import UserRepository
        from app.utils.tenant_helper import is_tenant_operator

        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        tenant_id = data.get('tenant_id')
        expires_days = data.get('expires_days')

        if not tenant_id:
            return jsonify({
                'error': 'Missing required field',
                'required': ['tenant_id']
            }), 400

        # Check if user is operator of the tenant
        user_id = get_jwt_identity()
        user_repo = UserRepository()
        user = user_repo.get_by_id(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Allow if user is admin or the tenant operator
        if not user.is_admin:
            if user.tenant_id != tenant_id:
                return jsonify({'error': 'Tenant mismatch'}), 403

            if not is_tenant_operator(user_id, tenant_id):
                return jsonify({
                    'error': 'Permission denied',
                    'message': 'Only tenant operators can create invitations'
                }), 403

        result = create_invitation(tenant_id, expires_days)

        if result['status'] == 'error':
            return jsonify({
                'message': result['message']
            }), 400

        invitation = result['invitation']

        return jsonify({
            'message': result['message'],
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
        current_app.logger.exception('Error creating invitation')
        return jsonify({'error': 'Failed to create invitation', 'message': str(e)}), 500


@bp.route('/validate', methods=['POST'])
def validate_invitation_route():
    """Validate an invitation code"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        invitation_code = data.get('invitation_code')

        if not invitation_code:
            return jsonify({
                'error': 'Missing required field',
                'required': ['invitation_code']
            }), 400

        result = validate_invitation(invitation_code)

        if result['status'] == 'error':
            return jsonify({
                'message': result['message']
            }), 400

        invitation = result['invitation']

        return jsonify({
            'message': result['message'],
            'valid': True,
            'invitation': {
                'id': invitation.id,
                'tenant_id': invitation.tenant_id,
                'is_used': invitation.is_used,
                'expires_at': invitation.expires_at.isoformat() if invitation.expires_at else None
            }
        }), 200

    except Exception as e:
        current_app.logger.exception('Error validating invitation')
        return jsonify({'error': 'Failed to validate invitation', 'message': str(e)}), 500


@bp.route('/<invitation_code>', methods=['GET'])
@jwt_required()
def get_invitation_route(invitation_code):
    """Get an invitation by code."""
    try:
        invitation = get_invitation_by_code(invitation_code)
        if not invitation:
            return jsonify({'error': 'Invitation not found'}), 404

        return jsonify({
            'id': invitation.id,
            'invitation_code': invitation.invitation_code,
            'tenant_id': invitation.tenant_id,
            'is_used': invitation.is_used,
            'used_at': invitation.used_at.isoformat() if invitation.used_at else None,
            'used_by_user_id': invitation.used_by_user_id,
            'expires_at': invitation.expires_at.isoformat() if invitation.expires_at else None,
            'created_at': invitation.created_at.isoformat() if invitation.created_at else None,
            'is_valid': invitation.is_valid()
        }), 200
    except Exception as e:
        current_app.logger.exception('Error getting invitation')
        return jsonify({'error': 'Failed to get invitation', 'message': str(e)}), 500


@bp.route('/tenant/<int:tenant_id>', methods=['GET'])
@jwt_required()
def get_invitations_by_tenant_route(tenant_id):
    """Get all invitations for a tenant (Operator Only)."""
    try:
        from flask_jwt_extended import get_jwt_identity
        from app.utils.tenant_helper import is_tenant_operator
        from app.repository.user_repository import UserRepository

        user_id = get_jwt_identity()
        user_repo = UserRepository()
        user = user_repo.get_by_id(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Allow if user is admin or the tenant operator
        if not user.is_admin and not is_tenant_operator(user_id, tenant_id):
            return jsonify({
                'error': 'Permission denied',
                'message': 'Only tenant operators can view invitations'
            }), 403

        is_used = request.args.get('is_used')
        is_used_filter = None
        if is_used is not None:
            is_used_filter = is_used.lower() == 'true'

        invitations = get_invitations_by_tenant(tenant_id, is_used_filter)

        return jsonify({
            'invitations': [{
                'id': invitation.id,
                'invitation_code': invitation.invitation_code,
                'tenant_id': invitation.tenant_id,
                'is_used': invitation.is_used,
                'used_at': invitation.used_at.isoformat() if invitation.used_at else None,
                'used_by_user_id': invitation.used_by_user_id,
                'expires_at': invitation.expires_at.isoformat() if invitation.expires_at else None,
                'created_at': invitation.created_at.isoformat() if invitation.created_at else None,
                'is_valid': invitation.is_valid()
            } for invitation in invitations]
        }), 200
    except Exception as e:
        current_app.logger.exception('Error getting invitations by tenant')
        return jsonify({'error': 'Failed to get invitations', 'message': str(e)}), 500
