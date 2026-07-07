import math
from flask import Blueprint, request, jsonify, current_app, Response
from flask_jwt_extended import jwt_required
from app.repository.audit_log_repository import AuditLogRepository
from app.utils.auth_helper import get_current_user

bp = Blueprint('audit_logs', __name__, url_prefix='/api/audit-logs')

def format_audit_details(log):
    """Convert JSON details into a human-readable string."""
    if not log.details:
        return "No additional details"

    details = log.details
    action = log.action

    if action == 'LOGIN':
        return f"User logged in from {details.get('email', 'unknown email')}"

    if action == 'CREATE_CAMPAIGN':
        return f"Created campaign '{details.get('name')}' using template #{details.get('template_id')}"

    if action == 'USER_REGISTER':
        return f"New user registered: {details.get('first_name')} {details.get('last_name')} ({details.get('email')}) using code {details.get('invitation_code')}"

    # Fallback: list all key/value pairs
    parts = []
    for key, value in details.items():
        parts.append(f"{key}: {value}")
    return ", ".join(parts)

def audit_log_to_dict(log):
    """Convert AuditLog model to dictionary."""
    return {
        'id': log.id,
        'user_id': log.user_id,
        'user_email': log.user.email if log.user else 'System',
        'user_name': f"{log.user.first_name} {log.user.last_name}" if log.user else 'System',
        'action': log.action,
        'resource_type': log.resource_type,
        'resource_id': log.resource_id,
        'details': format_audit_details(log),
        'created_at': log.created_at.isoformat()
    }

@bp.route('', methods=['GET'])
@jwt_required()
def get_audit_logs():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # Filtering parameters
        user_id_filter = request.args.get('user_id', type=int)
        action_filter = request.args.get('action')
        resource_type_filter = request.args.get('resource_type')

        repo = AuditLogRepository()
        logs, total_count = repo.get_by_tenant(
            tenant_id=user.tenant_id,
            page=page,
            per_page=per_page,
            user_id=user_id_filter,
            action=action_filter,
            resource_type=resource_type_filter
        )

        return jsonify({
            'logs': [audit_log_to_dict(log) for log in logs],
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': math.ceil(total_count / per_page) if total_count > 0 else 0
        }), 200

    except Exception:
        current_app.logger.exception('Error fetching audit logs')
        return jsonify({'error': 'Failed to fetch audit logs'}), 500

@bp.route('/export', methods=['GET'])
@jwt_required()
def export_audit_logs():
    try:
        user = get_current_user()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Filtering parameters
        user_id_filter = request.args.get('user_id', type=int)
        action_filter = request.args.get('action')
        resource_type_filter = request.args.get('resource_type')

        repo = AuditLogRepository()
        logs = repo.get_all_by_tenant(
            tenant_id=user.tenant_id,
            user_id=user_id_filter,
            action=action_filter,
            resource_type=resource_type_filter
        )

        def csv_field(value):
            text = str(value) if value is not None else ''
            return '"' + text.replace('"', '""') + '"'

        csv_lines = []
        csv_lines.append('"ID","Date","User Email","User Name","Action","Resource Type","Resource ID","Details"')

        for log in logs:
            user_email = log.user.email if log.user else 'System'
            user_name = (log.user.first_name + ' ' + log.user.last_name) if log.user else 'System'
            details = format_audit_details(log)
            line = ','.join([
                csv_field(log.id),
                csv_field(log.created_at.isoformat()),
                csv_field(user_email),
                csv_field(user_name),
                csv_field(log.action),
                csv_field(log.resource_type),
                csv_field(log.resource_id),
                csv_field(details)
            ])
            csv_lines.append(line)

        csv_content = '\n'.join(csv_lines)
        response = Response(csv_content, mimetype='text/csv')
        response.headers.set("Content-Disposition", "attachment", filename="audit_logs.csv")
        return response

    except Exception:
        current_app.logger.exception('Error exporting audit logs')
        return jsonify({'error': 'Failed to export audit logs'}), 500
