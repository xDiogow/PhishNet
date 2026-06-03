"""Repository for Campaign — CRUD plus status transition helper."""
import datetime
from app.models.campaign import CampaignStatus, Campaign
from app.repository.base_repository import BaseRepository


class CampaignRepository(BaseRepository[Campaign]):
    def __init__(self):
        super().__init__(Campaign)

    def update_status_by_id(self, campaign_id: int, status: CampaignStatus):
        """Update campaign status and set the appropriate timestamp.

        Sets launched_at when transitioning to RUNNING and stopped_at when
        transitioning to STOPPED. Raises ValueError if the campaign is not found.
        """
        campaign = self.get_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        update_data = {"status": status}
        if status == CampaignStatus.RUNNING:
            update_data["launched_at"] = datetime.datetime.now(datetime.timezone.utc)
        elif status == CampaignStatus.STOPPED:
            update_data["stopped_at"] = datetime.datetime.now(datetime.timezone.utc)
        return self.update_by_id(campaign_id, **update_data)
