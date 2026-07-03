from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint, Index

from app.models.base import Base


class User(Base):
    """A person who logs into the platform to manage campaigns and targets."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    email: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # CASCADE: deleting the tenant automatically deletes all its users
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Admins have access to all tenants; regular users only see their own tenant
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        # One email address can only belong to one account across the whole platform
        UniqueConstraint("email", name="uq_user_email"),
        Index("ix_users_email", "email"),
        Index("ix_users_tenant_id", "tenant_id"),
    )

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email}, first_name={self.first_name}, last_name={self.last_name})"
