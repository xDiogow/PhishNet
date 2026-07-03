from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, BigInteger, String, Boolean, DateTime, ForeignKey, UniqueConstraint, Index

from app.models.base import Base


class TenantInvitation(Base):
    """A one-time code that lets a new user join a specific tenant.

    Two invitation modes:
    - Quick code: email is NULL, the code is shared manually (e.g. copy-paste)
    - Email invite: email is set, the code is sent directly to that address
    """
    __tablename__ = "tenant_invitations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    invitation_code: Mapped[str] = mapped_column(String(64), nullable=False)

    # CASCADE: deleting a tenant removes all its invitations
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Optional: NULL means the code has not been used yet
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # BigInteger to future-proof against very large user IDs; no FK so history is kept if the user is deleted
    used_by_user_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # Optional: NULL means the code never expires
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # Optional: NULL means this is a quick-code invite (not tied to a specific email)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("invitation_code", name="uq_tenant_invitation_code"),
        Index("ix_tenant_invitations_code", "invitation_code"),
        Index("ix_tenant_invitations_tenant_id", "tenant_id"),
        Index("ix_tenant_invitations_is_used", "is_used"),
    )

    def __repr__(self) -> str:
        return f"TenantInvitation(id={self.id}, invitation_code={self.invitation_code}, tenant_id={self.tenant_id}, is_used={self.is_used})"

    def is_expired(self) -> bool:
        """Return True if the invitation has passed its expiry date."""
        if self.expires_at is None:
            return False
        expires_at = self.expires_at
        # Make the datetime timezone-aware if it was stored without timezone info
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > expires_at

    def is_valid(self) -> bool:
        """Return True if the invitation can still be used (not used and not expired)."""
        return not self.is_used and not self.is_expired()
