"""Background scheduler — ticks every minute to launch/stop scheduled campaigns."""
import logging
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)
_scheduler = BackgroundScheduler()


def _tick(app):
    with app.app_context():
        try:
            from app.services.campaign_service import CampaignService
            CampaignService().tick_scheduled_campaigns()
        except Exception:
            logger.exception('Scheduler tick failed')


def start_scheduler(app) -> None:
    _scheduler.add_job(
        _tick, 'interval', minutes=1, args=[app],
        id='campaign_tick', replace_existing=True,
    )
    _scheduler.start()
    logger.info('Campaign scheduler started (interval: 1 min)')
