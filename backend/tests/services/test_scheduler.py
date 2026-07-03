"""Tests for the APScheduler-backed campaign scheduler."""
import pytest
from unittest.mock import patch
from app.scheduler import start_scheduler, _scheduler, _tick


class TestStartScheduler:

    def test_start_scheduler_runs_without_error(self, app):
        """start_scheduler should register the job and start without raising."""
        try:
            start_scheduler(app)
            assert _scheduler.running
        finally:
            if _scheduler.running:
                _scheduler.shutdown(wait=False)


class TestTick:

    def test_tick_calls_tick_scheduled_campaigns(self, app):
        """_tick should call CampaignService().tick_scheduled_campaigns() inside app_context."""
        with patch('app.services.campaign_service.CampaignService.tick_scheduled_campaigns') as mock_tick:
            _tick(app)
            mock_tick.assert_called_once()

    def test_tick_handles_exception_gracefully(self, app):
        """_tick must not propagate exceptions — it logs them instead."""
        with patch(
            'app.services.campaign_service.CampaignService.tick_scheduled_campaigns',
            side_effect=RuntimeError("DB down"),
        ):
            # Should not raise
            _tick(app)
