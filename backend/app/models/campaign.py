from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, DateTime, Index, Enum as SQLEnum

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.campaign_stats import CampaignStats
    from app.models.campaign_result import CampaignResult


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    STOPPED = "stopped"
    ARCHIVED = "archived"


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    template_id: Mapped[Optional[int]] = mapped_column(ForeignKey("templates.id", ondelete="RESTRICT"), nullable=True)
    status: Mapped[CampaignStatus] = mapped_column(SQLEnum(CampaignStatus), default=CampaignStatus.DRAFT, nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    launched_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    stopped_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    scheduled_start_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    scheduled_end_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    stats: Mapped[Optional["CampaignStats"]] = relationship("CampaignStats", back_populates="campaign", uselist=False, cascade="all, delete-orphan")
    results: Mapped[List["CampaignResult"]] = relationship("CampaignResult", back_populates="campaign", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_campaigns_tenant_id", "tenant_id"),
    )

    def __repr__(self) -> str:
        return f"Campaign(id={self.id!r}, name={self.name!r}, status={self.status!r})"
