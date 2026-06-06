"""Authentication and authorization helper functions"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.repository.user_repository import UserRepository


def get_current_user():
    """Get the current authenticated user from JWT token"""
    user_id = get_jwt_identity()
    if not user_id:
        return None

    user_repo = UserRepository()
    return user_repo.get_by_id(user_id)


def admin_required(f):
    """Require admin access"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user_repo = UserRepository()
        user = user_repo.get_by_id(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403

        return f(*args, **kwargs)
    return decorated_function
