from flask import jsonify
from flask_jwt_extended import jwt_required
from app.utils.auth_helper import get_current_user
from app.repository.user_permission_repository import UserPermissionRepository
from . import bp


@bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    permissions = UserPermissionRepository().get_permissions(user.id, user.tenant_id)
    return jsonify({
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'tenant_id': user.tenant_id,
            'is_admin': user.is_admin,
            'permissions': permissions,
        }
    }), 200
