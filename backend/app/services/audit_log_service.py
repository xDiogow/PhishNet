from flask import request
from app.models.audit_log import AuditLog
from app.repository.audit_log_repository import AuditLogRepository


class AuditLogService:
    def __init__(self):
        self.repository = AuditLogRepository()

    def log_action(self, tenant_id, action, user_id=None, resource_type=None, resource_id=None, details=None):
        # Get real client IP — X-Forwarded-For is set by Nginx when behind a reverse proxy
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            ip_address = forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.remote_addr

        log = AuditLog(
            user_id=user_id,
            tenant_id=tenant_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
        )
        return self.repository.create(log)


audit_service = AuditLogService()
