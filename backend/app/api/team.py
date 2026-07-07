"""Team API routes.

Routes:
  GET    /api/team                            list all users in the caller's tenant
  PUT    /api/team/<user_id>/permissions      set permissions for a team member (manage_team required)
  GET    /api/team/targets                    list phishing targets for the caller's tenant
  POST   /api/team/targets                    add a new phishing target
  DELETE /api/team/targets/<id>               remove a phishing target (history preserved)
  DELETE /api/team/targets/<id>/gdpr          GDPR Art. 17 erasure: anonymize history then delete
"""
from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required
from app.repository.user_repository import UserRepository
from app.repository.user_permission_repository import UserPermissionRepository
from app.repository.target_repository import TargetRepository
from app.models.target import Target
from app.models.user_permission import ALL_PERMISSIONS
from app.services.audit_log_service import audit_service
from app.utils.auth_helper import get_current_user, has_permission

bp = Blueprint('team', __name__, url_prefix='/api/team')


def user_to_dict(user, permissions=None):
    return {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'tenant_id': user.tenant_id,
        'is_active': user.is_active,
        'is_admin': user.is_admin,
        'permissions': permissions or [],
        'created_at': user.created_at.isoformat() if user.created_at else None,
    }


def target_to_dict(target):
    return {
        'id': target.id,
        'email': target.email,
        'first_name': target.first_name,
        'last_name': target.last_name,
        'position': target.position,
        'tenant_id': target.tenant_id,
        'created_at': target.created_at.isoformat() if target.created_at else None,
    }


@bp.route('', methods=['GET'])
@jwt_required()
def get_team_members():
    """Get all team members in the same tenant as the current user."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_repo = UserRepository()
        perm_repo = UserPermissionRepository()
        team_members = user_repo.get_all_by_tenant_id(user.tenant_id, active_only=False)

        return jsonify({
            'team_members': [
                user_to_dict(m, perm_repo.get_permissions(m.id, m.tenant_id))
                for m in team_members
            ]
        }), 200

    except Exception:
        current_app.logger.exception('Error getting team members')
        return jsonify({'error': 'Failed to get team members'}), 500


@bp.route('/<int:member_id>/permissions', methods=['PUT'])
@jwt_required()
def set_member_permissions(member_id):
    """Replace all permissions for a team member. Requires manage_team permission."""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not has_permission(user, 'manage_team'):
            return jsonify({'error': 'Permission denied', 'required': 'manage_team'}), 403

        data = request.get_json()
        if data is None:
            return jsonify({'error': 'No data provided'}), 400

        new_permissions = data.get('permissions', [])
        if not isinstance(new_permissions, list):
            return jsonify({'error': 'permissions must be a list'}), 400

        invalid = [p for p in new_permissions if p not in ALL_PERMISSIONS]
        if invalid:
            return jsonify({'error': f'Unknown permissions: {invalid}', 'valid': ALL_PERMISSIONS}), 400

        user_repo = UserRepository()
        member = user_repo.get_by_id(member_id)
        if not member or member.tenant_id != user.tenant_id:
            return jsonify({'error': 'User not found'}), 404

        perm_repo = UserPermissionRepository()
        perm_repo.set_permissions(member_id, user.tenant_id, new_permissions)

        audit_service.log_action(
            user_id=user.id,
            tenant_id=user.tenant_id,
            action='SET_PERMISSIONS',
            resource_type='User',
            resource_id=str(member_id),
            details={'permissions': new_permissions},
        )

        return jsonify({
            'message': 'Permissions updated',
            'user_id': member_id,
            'permissions': new_permissions,
        }), 200

    except Exception:
        current_app.logger.exception('Error setting permissions')
        return jsonify({'error': 'Failed to set permissions'}), 500


@bp.route('/targets', methods=['GET'])
@jwt_required()
def get_targets():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        target_repo = TargetRepository()
        targets = target_repo.get_all_by_tenant_id(user.tenant_id)
        return jsonify({'targets': [target_to_dict(t) for t in targets]}), 200
    except Exception:
        current_app.logger.exception('Error getting targets')
        return jsonify({'error': 'Failed to get targets'}), 500


@bp.route('/targets', methods=['POST'])
@jwt_required()
def add_target():
    try:
        data = request.get_json()
        user = get_current_user()

        if not has_permission(user, 'manage_targets'):
            return jsonify({'error': 'Permission denied', 'required': 'manage_targets'}), 403

        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        position = data.get('position', '')

        if not email or not first_name or not last_name:
            return jsonify({'error': 'Missing required fields'}), 400

        target_repo = TargetRepository()
        existing = target_repo.get_by_email(email, user.tenant_id)
        if existing:
            return jsonify({'error': 'Target already exists'}), 409

        target = Target(
            email=email,
            first_name=first_name,
            last_name=last_name,
            position=position,
            tenant_id=user.tenant_id,
        )
        target = target_repo.create(target)

        audit_service.log_action(
            tenant_id=user.tenant_id,
            user_id=user.id,
            action='CREATE_TARGET',
            resource_type='Target',
            resource_id=str(target.id),
            details={'email': target.email, 'first_name': target.first_name, 'last_name': target.last_name},
        )

        return jsonify(target_to_dict(target)), 201

    except Exception:
        current_app.logger.exception('Error adding target')
        return jsonify({'error': 'Failed to add target'}), 500


@bp.route('/targets/<int:target_id>', methods=['DELETE'])
@jwt_required()
def delete_target(target_id):
    try:
        user = get_current_user()

        if not has_permission(user, 'manage_targets'):
            return jsonify({'error': 'Permission denied', 'required': 'manage_targets'}), 403

        target_repo = TargetRepository()
        target = target_repo.get_by_id(target_id)
        if not target or target.tenant_id != user.tenant_id:
            return jsonify({'error': 'Target not found'}), 404

        email = target.email
        target_repo.delete(target_id)

        audit_service.log_action(
            tenant_id=user.tenant_id,
            user_id=user.id,
            action='DELETE_TARGET',
            resource_type='Target',
            resource_id=str(target_id),
            details={'email': email},
        )

        return jsonify({'message': 'Target deleted successfully'}), 200

    except Exception:
        current_app.logger.exception('Error deleting target')
        return jsonify({'error': 'Failed to delete target'}), 500


@bp.route('/targets/<int:target_id>/gdpr', methods=['DELETE'])
@jwt_required()
def gdpr_erase_target(target_id):
    try:
        from app.repository.campaign_result_repository import CampaignResultRepository

        user = get_current_user()

        if not has_permission(user, 'manage_targets'):
            return jsonify({'error': 'Permission denied', 'required': 'manage_targets'}), 403

        target_repo = TargetRepository()
        target = target_repo.get_by_id(target_id)
        if not target or target.tenant_id != user.tenant_id:
            return jsonify({'error': 'Target not found'}), 404

        email = target.email
        result_repo = CampaignResultRepository()
        anonymized = result_repo.anonymize_by_email(email, user.tenant_id)
        target_repo.delete(target_id)

        audit_service.log_action(
            tenant_id=user.tenant_id,
            user_id=user.id,
            action='GDPR_ERASURE',
            resource_type='Target',
            resource_id=str(target_id),
            details={
                'anonymized_results': anonymized,
                'note': 'PII anonymized in campaign history per GDPR Art. 17',
            },
        )

        return jsonify({
            'message': 'Target erased and campaign history anonymized',
            'anonymized_results': anonymized,
        }), 200

    except Exception:
        current_app.logger.exception('Error during GDPR erasure')
        return jsonify({'error': 'GDPR erasure failed'}), 500
