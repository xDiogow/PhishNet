from __future__ import annotations

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, Index

from app.models.base import Base


class CampaignResult(Base):
    """One row per target per campaign — tracks what each person did with the phishing email."""
    __tablename__ = "campaign_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # CASCADE: deleting a campaign removes all its result rows
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)

    # Target info is copied here at campaign creation so results are preserved
    # even if the target record is later deleted (GDPR erasure, etc.)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Unique UUID embedded in phishing email links to identify who clicked
    tracking_token: Mapped[str] = mapped_column(String(36), unique=True, nullable=False)

    # Status reflects the latest event: Pending (scheduled) → Sent → Opened → Clicked → Submitted Data; Reported when the target flags the phishing
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Sent")

    # Event timestamps — NULL means the event has not occurred yet
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reported_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="results")  # noqa: F821

    __table_args__ = (
        Index("ix_campaign_results_campaign_id", "campaign_id"),
        # Index on tracking_token for fast lookups when a target clicks the phishing link
        Index("ix_campaign_results_token", "tracking_token"),
    )

    def __repr__(self) -> str:
        return f"CampaignResult(campaign_id={self.campaign_id}, email={self.email}, status={self.status})"
