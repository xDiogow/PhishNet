from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token, set_access_cookies
from app.extensions import bcrypt, limiter
from app.repository.user_repository import UserRepository
from app.repository.user_permission_repository import UserPermissionRepository
from . import bp


@bp.route('/login', methods=['POST'])
@limiter.limit('5 per minute')
def login():
    """Login a user."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email')
        password = data.get('password')
        tenant_id = data.get('tenant_id')

        if not email or not password:
            return jsonify({
                'error': 'Missing required fields',
                'required': ['email', 'password']
            }), 400

        user_repo = UserRepository()

        user = user_repo.get_by_email(email)
        if tenant_id and user and user.tenant_id != tenant_id:
            user = None

        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401

        if not user.is_active:
            return jsonify({'error': 'User account is inactive'}), 403

        if not bcrypt.check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid credentials'}), 401

        access_token = create_access_token(identity=str(user.id))

        perm_repo = UserPermissionRepository()
        permissions = perm_repo.get_permissions(user.id, user.tenant_id)

        from app.services.audit_log_service import audit_service
        audit_service.log_action(
            user_id=user.id,
            tenant_id=user.tenant_id,
            action='LOGIN',
            resource_type='User',
            resource_id=str(user.id),
            details={'email': user.email}
        )

        response = jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'tenant_id': user.tenant_id,
                'is_admin': user.is_admin,
                'permissions': permissions,
            },
        })
        set_access_cookies(response, access_token)
        return response, 200

    except Exception as e:
        current_app.logger.exception('Error during login')
        return jsonify({'error': 'Login failed'}), 500
