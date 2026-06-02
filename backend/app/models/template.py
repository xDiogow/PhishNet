from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Index

from app.models.base import Base


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    email_html: Mapped[str] = mapped_column(Text, nullable=False)
    landing_page_html: Mapped[str] = mapped_column(Text, nullable=False)
    redirect_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_templates_name", "name"),
    )

    def __repr__(self) -> str:
        return f"Template(id={self.id!r}, name={self.name!r})"
