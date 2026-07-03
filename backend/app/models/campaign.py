from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, DateTime, Index, Enum as SQLEnum

from app.models.base import Base


class CampaignStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    STOPPED = "stopped"
    ARCHIVED = "archived"


class Campaign(Base):
    """A phishing simulation sent to a set of targets using a specific template."""
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    # CASCADE: deleting a tenant removes all its campaigns
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    # RESTRICT: prevents deleting a template that is still used by a campaign
    # Optional: a campaign may exist without a template (e.g. if the template was later deleted)
    template_id: Mapped[Optional[int]] = mapped_column(ForeignKey("templates.id", ondelete="RESTRICT"), nullable=True)

    status: Mapped[CampaignStatus] = mapped_column(SQLEnum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False)

    # RESTRICT: prevents deleting a user who created a campaign
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Optional timestamps: NULL means the event has not happened yet
    launched_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    stopped_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    scheduled_start_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    scheduled_end_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # One-to-one: each campaign has exactly one stats row (uselist=False means a single object, not a list)
    # cascade="all, delete-orphan": deleting the campaign also deletes its stats row
    stats: Mapped[Optional["CampaignStats"]] = relationship(
        "CampaignStats",
        back_populates="campaign",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # One-to-many: each campaign has many result rows, one per target
    # cascade="all, delete-orphan": deleting the campaign also deletes all its result rows
    results: Mapped[List["CampaignResult"]] = relationship(
        "CampaignResult",
        back_populates="campaign",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_campaigns_tenant_id", "tenant_id"),
    )

    def __repr__(self) -> str:
        return f"Campaign(id={self.id}, name={self.name}, status={self.status})"
