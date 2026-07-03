from __future__ import annotations

from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


ALL_PERMISSIONS = ['manage_campaigns', 'manage_templates', 'manage_targets', 'manage_team']


class UserPermission(Base):
    """Grants one specific permission to one user within one tenant.

    Each row represents a single permission grant.
    A user with 3 permissions has 3 rows in this table.
    Admins bypass this table entirely — they have all permissions by default.
    """
    __tablename__ = 'user_permissions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # CASCADE: deleting a user removes all their permission rows
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    # CASCADE: deleting a tenant removes all its permission rows
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False)

    # One of: 'manage_campaigns', 'manage_templates', 'manage_targets', 'manage_team'
    permission: Mapped[str] = mapped_column(String(64), nullable=False)

    __table_args__ = (
        # A user cannot have the same permission granted twice in the same tenant
        UniqueConstraint('user_id', 'tenant_id', 'permission', name='uq_user_permission'),
        Index('ix_user_permissions_user_id', 'user_id'),
        Index('ix_user_permissions_tenant_id', 'tenant_id'),
    )

    def __repr__(self) -> str:
        return f"UserPermission(user_id={self.user_id}, tenant_id={self.tenant_id}, permission={self.permission})"
