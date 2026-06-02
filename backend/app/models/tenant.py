from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, ForeignKey, UniqueConstraint, Index

from app.models.base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    operator_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL", use_alter=True, name="fk_tenant_operator"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("name", name="uq_tenant_name"),
        Index("ix_tenants_name", "name"),
    )

    def __repr__(self) -> str:
        return f"Tenant(id={self.id!r}, name={self.name!r})"
