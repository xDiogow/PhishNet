from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, UniqueConstraint, Index

from app.models.base import Base


class Tenant(Base):
    """An organisation that uses the platform. All users and campaigns belong to a tenant."""
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        # No two tenants can share the same name
        UniqueConstraint("name", name="uq_tenant_name"),
        # Index speeds up lookups by name (search, login checks, etc.)
        Index("ix_tenants_name", "name"),
    )

    def __repr__(self) -> str:
        return f"Tenant(id={self.id}, name={self.name})"
