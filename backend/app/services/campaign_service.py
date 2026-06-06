"""Campaign service — orchestrates campaign creation, tracking, and lifecycle.

Campaigns are launched immediately on creation: a CampaignResult row with a
unique UUID tracking_token is created per target, then phishing emails are
sent via email_service. Tracking events (open/click/submit) are recorded by
the tracking blueprint; this service provides read and lifecycle operations.
"""
import logging
import uuid
from datetime import datetime, timezone


from app.extensions import db
from app.models.campaign import Campaign, CampaignStatus
from app.models.campaign_result import CampaignResult
from app.models.campaign_stats import CampaignStats
from app.repository.campaign_repository import CampaignRepository
from app.repository.template_repository import TemplateRepository
from app.repository.target_repository import TargetRepository
from app.services import email_service

logger = logging.getLogger(__name__)


class CampaignService:
    """Service layer for campaign operations."""

    def create_campaign(self, name: str, template_id: int, tenant_id: int, user_id: int) -> Campaign:
        """Create a campaign, send phishing emails to all tenant targets, and record results."""
        template_repo = TemplateRepository()
        target_repo = TargetRepository()

        template = template_repo.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        targets = target_repo.get_all_by_tenant_id(tenant_id)
        if not targets:
            raise ValueError("No targets found for this tenant. Add targets before creating a campaign.")

        now = datetime.now(timezone.utc)
        campaign = Campaign(
            name=name,
            tenant_id=tenant_id,
            template_id=template_id,
            status=CampaignStatus.RUNNING,
            created_by_user_id=user_id,
            created_at=now,
            launched_at=now,
        )
        db.session.add(campaign)
        db.session.flush()  # get campaign.id before creating results

        sent_count = 0
        results = []
        for target in targets:
            token = str(uuid.uuid4())
            result = CampaignResult(
                campaign_id=campaign.id,
                email=target.email,
                first_name=target.first_name,
                last_name=target.last_name,
                position=getattr(target, 'position', None),
                tracking_token=token,
                status="Sent",
                sent_at=now,
            )
            results.append(result)
            db.session.add(result)

        db.session.flush()

        # Send emails (failures are logged but don't abort the campaign)
        for result, target in zip(results, targets):
            ok = email_service.send_phishing_email(
                email=target.email,
                first_name=target.first_name,
                last_name=target.last_name,
                position=getattr(target, 'position', '') or '',
                tracking_token=result.tracking_token,
                subject=template.subject,
                email_html=template.email_html,
            )
            if ok:
                sent_count += 1

        stats = CampaignStats(
            campaign_id=campaign.id,
            total_targets=len(targets),
            sent_count=sent_count,
            opened_count=0,
            clicked_count=0,
            submitted_count=0,
            reported_count=0,
        )
        db.session.add(stats)
        db.session.commit()

        logger.info(f"Campaign '{name}' created (id={campaign.id}), {sent_count}/{len(targets)} emails sent")
        return campaign

    def get_campaign_summary(self, campaign_id: int) -> dict:
        """Compute stats from CampaignResult rows and return summary + result list."""
        results = (
            db.session.query(CampaignResult)
            .filter(CampaignResult.campaign_id == campaign_id)
            .all()
        )

        total = len(results)
        sent = sum(1 for r in results if r.sent_at is not None)
        opened = sum(1 for r in results if r.opened_at is not None)
        clicked = sum(1 for r in results if r.clicked_at is not None)
        submitted = sum(1 for r in results if r.submitted_at is not None)

        # Keep stats table in sync
        stats = db.session.get(CampaignStats, campaign_id)
        if stats:
            stats.total_targets = total
            stats.sent_count = sent
            stats.opened_count = opened
            stats.clicked_count = clicked
            stats.submitted_count = submitted
            db.session.commit()

        return {
            'summary': {
                'total': total,
                'sent': sent,
                'opened': opened,
                'clicked': clicked,
                'submitted_data': submitted,
                'email_reported': 0,
            },
            'results': [
                {
                    'id': r.id,
                    'email': r.email,
                    'first_name': r.first_name,
                    'last_name': r.last_name,
                    'position': r.position,
                    'status': r.status,
                    'sent_at': r.sent_at.isoformat() if r.sent_at else None,
                    'opened_at': r.opened_at.isoformat() if r.opened_at else None,
                    'clicked_at': r.clicked_at.isoformat() if r.clicked_at else None,
                    'submitted_at': r.submitted_at.isoformat() if r.submitted_at else None,
                }
                for r in results
            ],
        }

    def complete_campaign(self, campaign_id: int) -> Campaign:
        """Stop a running campaign."""
        campaign_repo = CampaignRepository()
        campaign = campaign_repo.get_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        campaign.status = CampaignStatus.STOPPED
        campaign.stopped_at = datetime.now(timezone.utc)
        db.session.commit()
        return campaign

    def delete_campaign(self, campaign_id: int) -> None:
        """Delete a campaign and cascade to results/stats."""
        campaign_repo = CampaignRepository()
        campaign = campaign_repo.get_by_id(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")
        db.session.delete(campaign)
        db.session.commit()
