from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Index

from app.models.base import Base


class Template(Base):
    """An email + landing page pair used as the content for a phishing campaign."""
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # NULL tenant_id means this is a global template visible to all tenants (platform default)
    # CASCADE: deleting a tenant also deletes the templates it owns
    tenant_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    email_html: Mapped[str] = mapped_column(Text, nullable=False)
    landing_page_html: Mapped[str] = mapped_column(Text, nullable=False)
    # Optional: if NULL, the landing page does not redirect after form submission
    redirect_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # RESTRICT: prevents deleting a user who still owns templates (must reassign first)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_templates_name", "name"),
        Index("ix_templates_tenant_id", "tenant_id"),
    )

    def __repr__(self) -> str:
        return f"Template(id={self.id}, name={self.name})"
