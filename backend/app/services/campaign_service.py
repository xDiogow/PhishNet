"""Campaign service — orchestrates campaign creation, tracking, and lifecycle.

Campaigns can be launched immediately or scheduled for a future date.
- Immediate: status=RUNNING, emails sent on creation.
- Scheduled: status=SCHEDULED, no emails sent; the scheduler ticks every minute
  and calls tick_scheduled_campaigns() to launch/stop campaigns on time.

Tracking events (open/click/submit) are recorded by the tracking blueprint.
"""
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

import redis as redis_lib
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
    """Service layer for campaign operations."""

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
        """Create a campaign.

        If scheduled_start_at is in the future the campaign is stored as
        SCHEDULED and no emails are sent yet. The scheduler will call
        tick_scheduled_campaigns() to launch it at the right time.
        Otherwise the campaign launches immediately (status=RUNNING).

        target_ids: optional list of target IDs to include. If None or empty,
        all targets for the tenant are used.
        """
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
        db.session.flush()

        # Always pre-create CampaignResult rows (tokens are assigned now so links
        # can be embedded in emails at send time — whether immediate or scheduled).
        result_objs = []
        for target in targets:
            result = CampaignResult(
                campaign_id=campaign.id,
                email=target.email,
                first_name=target.first_name,
                last_name=target.last_name,
                position=getattr(target, 'position', None),
                tracking_token=str(uuid.uuid4()),
                status="Pending" if is_scheduled else "Sent",
                sent_at=None if is_scheduled else now,
            )
            result_objs.append(result)
            db.session.add(result)

        db.session.flush()

        if is_scheduled:
            stats = CampaignStats(
                campaign_id=campaign.id,
                total_targets=len(targets),
                sent_count=0,
                opened_count=0, clicked_count=0, submitted_count=0, reported_count=0,
            )
            db.session.add(stats)
            db.session.commit()
            logger.info(
                f"Campaign '{name}' scheduled for {scheduled_start_at} (id={campaign.id})"
            )
        else:
            sent_count = self._send_emails(template, result_objs)
            stats = CampaignStats(
                campaign_id=campaign.id,
                total_targets=len(targets),
                sent_count=sent_count,
                opened_count=0, clicked_count=0, submitted_count=0, reported_count=0,
            )
            db.session.add(stats)
            db.session.commit()
            logger.info(
                f"Campaign '{name}' created (id={campaign.id}), {sent_count}/{len(targets)} emails sent"
            )

        return campaign

    def _send_emails(self, template, results: list) -> int:
        """Send phishing emails for the given CampaignResult rows. Returns sent count."""
        sent_count = 0
        for result in results:
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

        # Launch campaigns whose start time has arrived
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

        # Auto-stop campaigns past their end date
        to_stop = (
            db.session.query(Campaign)
            .filter(
                Campaign.status == CampaignStatus.RUNNING,
                Campaign.scheduled_end_at.isnot(None),
                Campaign.scheduled_end_at <= now,
            )
            .all()
        )
        for campaign in to_stop:
            campaign.status = CampaignStatus.STOPPED
            campaign.stopped_at = now
            self.invalidate_summary_cache(campaign.id)
            logger.info(f"Campaign '{campaign.name}' auto-stopped at scheduled end (id={campaign.id})")

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

        stats = db.session.get(CampaignStats, campaign.id)
        if stats:
            stats.sent_count = sent_count

        db.session.commit()
        self.invalidate_summary_cache(campaign.id)
        logger.info(
            f"Scheduled campaign '{campaign.name}' launched (id={campaign.id}), "
            f"{sent_count}/{len(results)} emails sent"
        )

    # Redis TTL for campaign summary cache (seconds).
    # Short enough to stay fresh for live campaigns; long enough to cut DB load.
    _SUMMARY_TTL = 30

    def _redis(self):
        url = current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        return redis_lib.from_url(url, decode_responses=True, socket_connect_timeout=2)

    @staticmethod
    def summary_cache_key(campaign_id: int) -> str:
        return f"campaign:{campaign_id}:summary"

    def invalidate_summary_cache(self, campaign_id: int) -> None:
        """Delete the cached summary so the next request recomputes from DB."""
        try:
            self._redis().delete(self.summary_cache_key(campaign_id))
        except redis_lib.exceptions.ConnectionError:
            pass

    def get_campaign_summary(self, campaign_id: int) -> dict:
        """Return campaign stats + per-target result list.

        Checks Redis first (TTL=30 s). On miss, queries DB, updates the
        CampaignStats table, and caches the result.
        """
        cache_key = self.summary_cache_key(campaign_id)
        try:
            cached = self._redis().get(cache_key)
            if cached:
                return json.loads(cached)
        except redis_lib.exceptions.ConnectionError:
            pass

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

        data = {
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

        try:
            self._redis().setex(cache_key, self._SUMMARY_TTL, json.dumps(data))
        except redis_lib.exceptions.ConnectionError:
            pass

        return data

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
