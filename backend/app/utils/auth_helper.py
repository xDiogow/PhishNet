from flask_jwt_extended import get_jwt_identity
from app.repository.user_repository import UserRepository


def get_current_user():
    user_id = get_jwt_identity()
    if not user_id:
        return None
    return UserRepository().get_by_id(user_id)


def has_permission(user, permission):
    if user.is_admin:
        return True
    from app.repository.user_permission_repository import UserPermissionRepository
    return UserPermissionRepository().has_permission(user.id, user.tenant_id, permission)
