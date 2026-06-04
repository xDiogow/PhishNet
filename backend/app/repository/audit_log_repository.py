from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy import desc
from app.models.audit_log import AuditLog
from app.repository.base_repository import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self):
        super().__init__(AuditLog)

    def get_by_tenant(
        self,
        tenant_id: int,
        page: int = 1,
        per_page: int = 20,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None
    ) -> Tuple[List[AuditLog], int]:
        """
        Get audit logs for a tenant with pagination and filtering.
        Returns a tuple of (logs, total_count).
        """
        query = self._apply_filters(tenant_id, user_id, action, resource_type)

        total_count = query.count()

        logs = (
            query.order_by(desc(AuditLog.created_at))
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        return logs, total_count

    def get_all_by_tenant(
        self,
        tenant_id: int,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None
    ) -> List[AuditLog]:
        """
        Get all audit logs for a tenant with filtering, without pagination.
        """
        query = self._apply_filters(tenant_id, user_id, action, resource_type)
        return query.order_by(desc(AuditLog.created_at)).all()

    def delete_older_than(self, cutoff: datetime) -> int:
        """Delete all audit logs created before cutoff (system-wide retention purge).

        Returns the number of rows deleted.
        """
        count = (
            self.session.query(AuditLog)
            .filter(AuditLog.created_at < cutoff)
            .count()
        )
        self.session.query(AuditLog).filter(AuditLog.created_at < cutoff).delete(
            synchronize_session=False
        )
        self.session.commit()
        return count

    def _apply_filters(
        self,
        tenant_id: int,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None
    ):
        query = self.session.query(AuditLog).filter(AuditLog.tenant_id == tenant_id)

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)

        return query
