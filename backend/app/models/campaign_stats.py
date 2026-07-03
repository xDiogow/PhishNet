from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey

from app.models.base import Base


class CampaignStats(Base):
    """Aggregated counters for a campaign (sent, opened, clicked, etc.).

    There is exactly one stats row per campaign.
    Using campaign_id as the primary key (instead of a separate auto-increment id)
    enforces this one-to-one relationship at the database level.
    """
    __tablename__ = "campaign_stats"

    # This column is both the primary key AND the foreign key to campaigns.
    # It means: "each stats row is uniquely identified by its campaign."
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), primary_key=True)

    total_targets: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sent_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    opened_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clicked_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    submitted_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reported_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # back_populates="stats" links this to Campaign.stats so both sides stay in sync
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="stats")  # noqa: F821

    def __repr__(self) -> str:
        return f"CampaignStats(campaign_id={self.campaign_id}, total={self.total_targets}, opened={self.opened_count})"
