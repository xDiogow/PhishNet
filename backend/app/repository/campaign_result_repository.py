"""Repository for CampaignResult — one row per target per campaign."""
from typing import Optional, List
from app.models.campaign_result import CampaignResult
from app.repository.base_repository import BaseRepository


class CampaignResultRepository(BaseRepository[CampaignResult]):
    def __init__(self):
        super().__init__(CampaignResult)

    def get_by_token(self, token: str) -> Optional[CampaignResult]:
        """Look up a result by its UUID tracking token (used by tracking endpoints)."""
        return self.session.query(CampaignResult).filter(
            CampaignResult.tracking_token == token
        ).first()

    def get_by_campaign(self, campaign_id: int) -> List[CampaignResult]:
        """Return all results for a campaign, used when computing summary stats."""
        return self.session.query(CampaignResult).filter(
            CampaignResult.campaign_id == campaign_id
        ).all()
