from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, Index

from app.models.base import Base


class CampaignResult(Base):
    """Per-target result for a campaign. Each row has a unique tracking token."""
    __tablename__ = "campaign_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)

    email: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Tracking token — unique UUID embedded in phishing email links
    tracking_token: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)

    # Status reflects highest-severity event: Sent → Opened → Clicked → Submitted Data
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Sent")

    # Event timestamps — None means the event has not occurred yet
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="results")

    __table_args__ = (
        Index("ix_campaign_results_campaign_id", "campaign_id"),
        Index("ix_campaign_results_token", "tracking_token"),
    )

    def __repr__(self) -> str:
        return f"CampaignResult(campaign_id={self.campaign_id!r}, email={self.email!r}, status={self.status!r})"
