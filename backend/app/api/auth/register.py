from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token, set_access_cookies
from sqlalchemy.exc import IntegrityError
from app.extensions import bcrypt, limiter
from app.repository.user_repository import UserRepository
from app.repository.user_permission_repository import UserPermissionRepository
from app.models.user import User
from app.models.user_permission import ALL_PERMISSIONS
from app.services.tenant_invitation_service import validate_invitation, use_invitation
from . import bp


@bp.route('/register', methods=['POST'])
@limiter.limit('5 per minute')
def register():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        password = data.get('password')
        invitation_code = data.get('invitation_code')

        if not email or not first_name or not last_name or not password or not invitation_code:
            return jsonify({
                'error': 'Missing required fields',
                'required': ['email', 'first_name', 'last_name', 'password', 'invitation_code']
            }), 400

        if '@' not in email:
            return jsonify({'error': 'Invalid email format'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400

        first_name = first_name.strip()
        last_name = last_name.strip()
        if not first_name or not last_name:
            return jsonify({'error': 'First name and last name cannot be empty'}), 400

        user_repo = UserRepository()

        validation_result = validate_invitation(invitation_code)
        if validation_result['status'] == 'error':
            return jsonify({'error': validation_result['message']}), 400

        invitation = validation_result['invitation']
        tenant_id = invitation.tenant_id

        existing_user = user_repo.get_by_email(email)
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        is_first_user = user_repo.count() == 0

        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=password_hash,
            tenant_id=tenant_id,
            is_active=True,
            is_admin=is_first_user,
        )

        try:
            user = user_repo.create(user)
        except IntegrityError as e:
            current_app.logger.error(f'Integrity error during user creation: {e}')
            return jsonify({'error': 'User creation failed due to constraint violation'}), 409

        use_result = use_invitation(invitation_code, user.id)
        if use_result['status'] == 'error':
            current_app.logger.warning(f'Failed to mark invitation as used: {use_result["message"]}')

        # First user on a tenant gets all permissions
        perm_repo = UserPermissionRepository()
        existing_members = user_repo.get_all_by_tenant_id(tenant_id)
        if len(existing_members) <= 1:
            perm_repo.grant_all(user.id, tenant_id, ALL_PERMISSIONS)

        permissions = perm_repo.get_permissions(user.id, tenant_id)

        access_token = create_access_token(identity=str(user.id))

        from app.services.audit_log_service import audit_service
        audit_service.log_action(
            user_id=user.id,
            tenant_id=tenant_id,
            action='USER_REGISTER',
            resource_type='User',
            resource_id=str(user.id),
            details={
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'invitation_code': invitation_code
            }
        )

        response = jsonify({
            'message': 'User registered successfully',
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
        return response, 201

    except Exception as e:
        current_app.logger.exception('Error during registration')
        return jsonify({'error': 'Registration failed'}), 500
