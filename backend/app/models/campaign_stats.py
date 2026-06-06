from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey

from app.models.base import Base


class CampaignStats(Base):
    """Local storage for campaign statistics"""
    __tablename__ = "campaign_stats"

    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), primary_key=True)
    total_targets: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sent_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    opened_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clicked_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    submitted_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reported_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationship back to campaign
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="stats")  # noqa: F821

    def __repr__(self) -> str:
        return f"CampaignStats(campaign_id={self.campaign_id!r}, total={self.total_targets!r}, opened={self.opened_count!r})"
