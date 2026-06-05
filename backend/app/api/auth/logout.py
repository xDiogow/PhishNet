import time
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.repository.session_repository import session_repo
from app.utils.auth_helper import get_current_user
from app.services.audit_log_service import audit_service
from . import bp


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    token = get_jwt()
    jti = token["jti"]
    exp = token["exp"]
    ttl = max(int(exp - time.time()), 0) + 60  # 60s grace buffer

    session_repo.revoke_token(jti, ttl)

    user = get_current_user()
    if user:
        audit_service.log_action(
            user_id=user.id,
            tenant_id=user.tenant_id,
            action='LOGOUT',
            resource_type='User',
            resource_id=str(user.id),
            details={'email': user.email}
        )

    return jsonify({'message': 'Successfully logged out'}), 200
