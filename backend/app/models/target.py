from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint, Index

from app.models.base import Base


class Target(Base):
    """A person who receives phishing emails. Targets belong to a tenant."""
    __tablename__ = "targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    email: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Optional: not all targets have a job title
    position: Mapped[str] = mapped_column(String(100), nullable=True)

    # CASCADE: deleting a tenant removes all its targets
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        # The same email can exist in two different tenants, but not twice in the same tenant
        UniqueConstraint("email", "tenant_id", name="uq_target_email_tenant"),
        Index("ix_targets_tenant_id", "tenant_id"),
        Index("ix_targets_email", "email"),
    )

    def __repr__(self) -> str:
        return f"Target(id={self.id}, email={self.email}, first_name={self.first_name}, last_name={self.last_name})"
