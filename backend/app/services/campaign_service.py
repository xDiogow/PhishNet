"""Campaign service — orchestrates campaign creation and lifecycle."""
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from flask import current_app

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

    def create_campaign(
        self,
        name: str,
        template_id: int,
        tenant_id: int,
        user_id: int,
        scheduled_start_at: Optional[datetime] = None,
        scheduled_end_at: Optional[datetime] = None,
        target_ids: Optional[list] = None,
    ) -> Campaign:
        """Create a campaign and launch it immediately, or schedule it for later."""
        template_repo = TemplateRepository()
        target_repo = TargetRepository()

        template = template_repo.get_by_id(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        all_targets = target_repo.get_all_by_tenant_id(tenant_id)
        if not all_targets:
            raise ValueError("No targets found for this tenant. Add targets before creating a campaign.")

        if target_ids:
            id_set = set(target_ids)
            targets = [t for t in all_targets if t.id in id_set]
            if not targets:
                raise ValueError("None of the selected targets belong to this tenant.")
        else:
            targets = all_targets

        now = datetime.now(timezone.utc)
        is_scheduled = bool(scheduled_start_at and scheduled_start_at > now)

        campaign = Campaign(
            name=name,
            tenant_id=tenant_id,
            template_id=template_id,
            status=CampaignStatus.SCHEDULED if is_scheduled else CampaignStatus.RUNNING,
            created_by_user_id=user_id,
            created_at=now,
            launched_at=None if is_scheduled else now,
            scheduled_start_at=scheduled_start_at,
            scheduled_end_at=scheduled_end_at,
        )
        db.session.add(campaign)
        db.session.commit()

        result_objs = []
        for target in targets:
            result = CampaignResult(
                campaign_id=campaign.id,
                email=target.email,
                first_name=target.first_name,
                last_name=target.last_name,
                position=target.position,
                tracking_token=str(uuid.uuid4()),
                status="Pending" if is_scheduled else "Sent",
                sent_at=None if is_scheduled else now,
            )
            result_objs.append(result)
            db.session.add(result)

        if is_scheduled:
            stats = CampaignStats(
                campaign_id=campaign.id,
                total_targets=len(targets),
                sent_count=0,
                opened_count=0, clicked_count=0, submitted_count=0, reported_count=0,
            )
            db.session.add(stats)
            db.session.commit()
            logger.info(f"Campaign '{name}' scheduled for {scheduled_start_at} (id={campaign.id})")
        else:
            db.session.commit()
            sent_count = self._send_emails(template, result_objs)
            stats = CampaignStats(
                campaign_id=campaign.id,
                total_targets=len(targets),
                sent_count=sent_count,
                opened_count=0, clicked_count=0, submitted_count=0, reported_count=0,
            )
            db.session.add(stats)
            db.session.commit()
            logger.info(f"Campaign '{name}' created (id={campaign.id}), {sent_count}/{len(targets)} emails sent")

        return campaign

    def _send_emails(self, template, results: list) -> int:
        """Send phishing emails for the given CampaignResult rows. Returns sent count."""
        sent_count = 0
        for i, result in enumerate(results):
            if i > 0:
                time.sleep(1.2)
            ok = email_service.send_phishing_email(
                email=result.email,
                first_name=result.first_name,
                last_name=result.last_name,
                position=result.position or '',
                tracking_token=result.tracking_token,
                subject=template.subject,
                email_html=template.email_html,
            )
            if ok:
                sent_count += 1
        return sent_count

    def tick_scheduled_campaigns(self) -> None:
        """Called every minute by the scheduler to launch/stop campaigns on schedule."""
        now = datetime.now(timezone.utc)

        to_launch = (
            db.session.query(Campaign)
            .filter(
                Campaign.status == CampaignStatus.SCHEDULED,
                Campaign.scheduled_start_at <= now,
            )
            .all()
        )
        for campaign in to_launch:
            try:
                self._launch_scheduled_campaign(campaign, now)
            except Exception:
                logger.exception(f'Failed to launch scheduled campaign {campaign.id}')

        to_stop = (
            db.session.query(Campaign)
            .filter(
                Campaign.status == CampaignStatus.RUNNING,
                Campaign.scheduled_end_at != None,
                Campaign.scheduled_end_at <= now,
            )
            .all()
        )
        for campaign in to_stop:
            campaign.status = CampaignStatus.STOPPED
            campaign.stopped_at = now
            logger.info(f"Campaign '{campaign.name}' auto-stopped (id={campaign.id})")

        if to_stop:
            db.session.commit()

    def _launch_scheduled_campaign(self, campaign: Campaign, now: datetime) -> None:
        """Send emails for a SCHEDULED campaign that is now due."""
        template = TemplateRepository().get_by_id(campaign.template_id)
        if not template:
            logger.warning(f'Campaign {campaign.id} cannot launch: template not found')
            return

        results = (
            db.session.query(CampaignResult)
            .filter(CampaignResult.campaign_id == campaign.id)
            .all()
        )

        sent_count = self._send_emails(template, results)
        for result in results:
            if result.sent_at is None:
                result.sent_at = now
                result.status = "Sent"

        campaign.status = CampaignStatus.RUNNING
        campaign.launched_at = now

        stats = db.session.query(CampaignStats).filter_by(campaign_id=campaign.id).first()
        if stats:
            stats.sent_count = sent_count

        db.session.commit()
        logger.info(f"Scheduled campaign '{campaign.name}' launched (id={campaign.id}), {sent_count}/{len(results)} emails sent")

    def get_campaign_summary(self, campaign_id: int) -> dict:
        """Return campaign stats and per-target result list from the database."""
        results = (
            db.session.query(CampaignResult)
            .filter(CampaignResult.campaign_id == campaign_id)
            .all()
        )

        total = len(results)
        sent = 0
        opened = 0
        clicked = 0
        submitted = 0
        reported = 0
        for r in results:
            if r.sent_at is not None:
                sent += 1
            if r.opened_at is not None:
                opened += 1
            if r.clicked_at is not None:
                clicked += 1
            if r.submitted_at is not None:
                submitted += 1
            if r.reported_at is not None:
                reported += 1

        stats = db.session.query(CampaignStats).filter_by(campaign_id=campaign_id).first()
        if stats:
            stats.total_targets = total
            stats.sent_count = sent
            stats.opened_count = opened
            stats.clicked_count = clicked
            stats.submitted_count = submitted
            stats.reported_count = reported
            db.session.commit()

        return {
            'summary': {
                'total': total,
                'sent': sent,
                'opened': opened,
                'clicked': clicked,
                'submitted_data': submitted,
                'email_reported': reported,
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
                    'reported_at': r.reported_at.isoformat() if r.reported_at else None,
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
