"""Tests for CampaignStatsRepository."""
import pytest
from datetime import datetime, timezone

from app.extensions import bcrypt, db
from app.models import User, Tenant, Template
from app.models.campaign import Campaign, CampaignStatus
from app.models.campaign_stats import CampaignStats
from app.repository.campaign_stats_repository import CampaignStatsRepository


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def stats_tenant(db_session):
    tenant = Tenant(name="Stats Repo Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def stats_user(db_session, stats_tenant):
    pw = bcrypt.generate_password_hash("pw").decode('utf-8')
    user = User(
        email="statsuser@example.com",
        first_name="Stats",
        last_name="User",
        password_hash=pw,
        tenant_id=stats_tenant.id,
        is_active=True,
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def stats_template(db_session, stats_user, stats_tenant):
    template = Template(
        name="Stats Template",
        subject="Subject",
        email_html="<html></html>",
        landing_page_html="<html></html>",
        tenant_id=stats_tenant.id,
        created_by_user_id=stats_user.id,
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template


@pytest.fixture
def stats_campaign(db_session, stats_tenant, stats_user, stats_template):
    campaign = Campaign(
        name="Stats Campaign",
        tenant_id=stats_tenant.id,
        template_id=stats_template.id,
        status=CampaignStatus.RUNNING,
        created_by_user_id=stats_user.id,
        launched_at=datetime.now(timezone.utc),
    )
    db_session.add(campaign)
    db_session.commit()
    db_session.refresh(campaign)
    return campaign


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGetByCampaignId:

    def test_found(self, db_session, stats_campaign):
        stats = CampaignStats(
            campaign_id=stats_campaign.id,
            total_targets=5,
            sent_count=3,
            opened_count=1,
            clicked_count=0,
            submitted_count=0,
            reported_count=0,
        )
        db_session.add(stats)
        db_session.commit()

        result = CampaignStatsRepository().get_by_campaign_id(stats_campaign.id)

        assert result is not None
        assert result.campaign_id == stats_campaign.id
        assert result.total_targets == 5
        assert result.sent_count == 3

    def test_not_found(self, db_session):
        result = CampaignStatsRepository().get_by_campaign_id(99999)
        assert result is None


class TestUpdateOrCreate:

    def test_creates_new(self, db_session, stats_campaign):
        result = CampaignStatsRepository().update_or_create(
            campaign_id=stats_campaign.id,
            total_targets=10,
            sent_count=8,
            opened_count=4,
            clicked_count=2,
            submitted_count=1,
            reported_count=0,
        )

        assert result.campaign_id == stats_campaign.id
        assert result.total_targets == 10
        assert result.sent_count == 8
        assert result.opened_count == 4
        assert result.clicked_count == 2
        assert result.submitted_count == 1

    def test_updates_existing(self, db_session, stats_campaign):
        stats = CampaignStats(
            campaign_id=stats_campaign.id,
            total_targets=5,
            sent_count=5,
            opened_count=1,
            clicked_count=0,
            submitted_count=0,
            reported_count=0,
        )
        db_session.add(stats)
        db_session.commit()

        updated = CampaignStatsRepository().update_or_create(
            campaign_id=stats_campaign.id,
            total_targets=5,
            sent_count=5,
            opened_count=3,
            clicked_count=2,
            submitted_count=1,
            reported_count=0,
        )

        assert updated.opened_count == 3
        assert updated.clicked_count == 2
        assert updated.submitted_count == 1
