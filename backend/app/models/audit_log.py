from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, Index, JSON

from app.models.base import Base


class AuditLog(Base):
    """A record of every important action performed on the platform (login, create, delete, etc.)."""
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # SET NULL: if the user is deleted, the log entry is kept but user_id becomes NULL
    # (we keep the history even when the user no longer exists)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # CASCADE: deleting a tenant removes all its audit logs
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    # e.g. "LOGIN", "CREATE_CAMPAIGN", "DELETE_TEMPLATE"
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    # e.g. "campaign", "template" — the type of object the action was performed on
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # The ID of the specific object (as a string to support any ID format)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # JSON column: stores a flexible dict of extra context (e.g. {"campaign_name": "Q4 Test"})
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # foreign_keys=[user_id] is required because AuditLog has two FKs pointing to different tables,
    # so SQLAlchemy needs to know which one this relationship follows
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])  # noqa: F821

    __table_args__ = (
        Index("ix_audit_logs_tenant_id", "tenant_id"),
        Index("ix_audit_logs_user_id", "user_id"),
        # Index on created_at to speed up time-range queries (e.g. "logs from last 7 days")
        Index("ix_audit_logs_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"AuditLog(id={self.id}, action={self.action}, user_id={self.user_id}, tenant_id={self.tenant_id})"
