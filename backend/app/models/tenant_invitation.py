from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, BigInteger, String, Boolean, DateTime, ForeignKey, UniqueConstraint, Index

from app.models.base import Base


class TenantInvitation(Base):
    __tablename__ = "tenant_invitations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    invitation_code: Mapped[str] = mapped_column(String(64), nullable=False)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    used_by_user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("invitation_code", name="uq_tenant_invitation_code"),
        Index("ix_tenant_invitations_code", "invitation_code"),
        Index("ix_tenant_invitations_tenant_id", "tenant_id"),
        Index("ix_tenant_invitations_is_used", "is_used"),
    )

    def __repr__(self) -> str:
        return f"TenantInvitation(id={self.id!r}, invitation_code={self.invitation_code!r}, tenant_id={self.tenant_id!r}, is_used={self.is_used!r})"

    def is_expired(self) -> bool:
        """Check if the invitation has expired."""
        if self.expires_at is None:
            return False
        now = datetime.now(timezone.utc)
        expires = self.expires_at if self.expires_at.tzinfo else self.expires_at.replace(tzinfo=timezone.utc)
        return now > expires

    def is_valid(self) -> bool:
        """Check if the invitation is valid (not used and not expired)."""
        return not self.is_used and not self.is_expired()
