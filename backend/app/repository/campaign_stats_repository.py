from app.models.campaign_stats import CampaignStats
from app.repository.base_repository import BaseRepository


class CampaignStatsRepository(BaseRepository):
    def __init__(self):
        super().__init__(CampaignStats)

    def get_by_campaign_id(self, campaign_id: int):
        return self.session.query(CampaignStats).filter(
            CampaignStats.campaign_id == campaign_id
        ).first()

    def update_or_create(self, campaign_id: int, total_targets: int, sent_count: int,
                          opened_count: int, clicked_count: int, submitted_count: int,
                          reported_count: int):
        """Update existing stats or create new ones for a campaign."""
        stats = self.get_by_campaign_id(campaign_id)
        if stats:
            stats.total_targets = total_targets
            stats.sent_count = sent_count
            stats.opened_count = opened_count
            stats.clicked_count = clicked_count
            stats.submitted_count = submitted_count
            stats.reported_count = reported_count
        else:
            stats = CampaignStats(
                campaign_id=campaign_id,
                total_targets=total_targets,
                sent_count=sent_count,
                opened_count=opened_count,
                clicked_count=clicked_count,
                submitted_count=submitted_count,
                reported_count=reported_count
            )
            self.session.add(stats)

        self.session.commit()
        return stats
