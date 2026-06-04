"""Repository for CampaignResult — one row per target per campaign."""
from datetime import datetime
from typing import Optional, List
from app.models.campaign_result import CampaignResult
from app.repository.base_repository import BaseRepository

_ANON_EMAIL = "deleted@anonymized.local"
_ANON_NAME = "[Supprimé]"


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

    def anonymize_by_email(self, email: str, tenant_id: int) -> int:
        """Overwrite PII fields for all results matching email within a tenant.

        Joins through campaigns to enforce tenant isolation. Returns the number
        of rows anonymized. Safe to call multiple times (already-anonymized rows
        are skipped via the email filter).
        """
        from app.models.campaign import Campaign
        rows = (
            self.session.query(CampaignResult)
            .join(Campaign, CampaignResult.campaign_id == Campaign.id)
            .filter(Campaign.tenant_id == tenant_id)
            .filter(CampaignResult.email == email)
            .all()
        )
        for r in rows:
            r.email = _ANON_EMAIL
            r.first_name = _ANON_NAME
            r.last_name = _ANON_NAME
            r.position = None
        self.session.commit()
        return len(rows)

    def anonymize_older_than(self, cutoff: datetime) -> int:
        """Anonymize PII in results whose sent_at predates cutoff (retention purge).

        Skips rows already anonymized. Returns the number of rows affected.
        """
        rows = (
            self.session.query(CampaignResult)
            .filter(CampaignResult.sent_at < cutoff)
            .filter(CampaignResult.email != _ANON_EMAIL)
            .all()
        )
        for r in rows:
            r.email = _ANON_EMAIL
            r.first_name = _ANON_NAME
            r.last_name = _ANON_NAME
            r.position = None
        self.session.commit()
        return len(rows)
