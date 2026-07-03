from datetime import datetime
from sqlalchemy import desc
from app.models.audit_log import AuditLog
from app.repository.base_repository import BaseRepository


class AuditLogRepository(BaseRepository):
    def __init__(self):
        super().__init__(AuditLog)

    def get_by_tenant(self, tenant_id, page=1, per_page=20, user_id=None, action=None, resource_type=None):
        """Get paginated audit logs for a tenant. Returns (logs, total_count)."""
        query = self._apply_filters(tenant_id, user_id, action, resource_type)
        total_count = query.count()
        logs = (
            query.order_by(desc(AuditLog.created_at))
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return logs, total_count

    def get_all_by_tenant(self, tenant_id, user_id=None, action=None, resource_type=None):
        """Get all audit logs for a tenant without pagination."""
        query = self._apply_filters(tenant_id, user_id, action, resource_type)
        return query.order_by(desc(AuditLog.created_at)).all()

    def delete_older_than(self, cutoff: datetime) -> int:
        """Delete logs older than cutoff. Returns number of rows deleted."""
        rows = (
            self.session.query(AuditLog)
            .filter(AuditLog.created_at < cutoff)
            .all()
        )
        count = len(rows)
        for row in rows:
            self.session.delete(row)
        self.session.commit()
        return count

    def _apply_filters(self, tenant_id, user_id=None, action=None, resource_type=None):
        query = self.session.query(AuditLog).filter(AuditLog.tenant_id == tenant_id)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        return query
