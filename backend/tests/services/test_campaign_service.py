"""Tests for CampaignService — service layer, not HTTP API."""
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

from app.extensions import bcrypt, db
from app.models import User, Tenant, Template
from app.models.campaign import Campaign, CampaignStatus
from app.models.campaign_result import CampaignResult
from app.models.campaign_stats import CampaignStats
from app.models.target import Target
from app.services.campaign_service import CampaignService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def svc_tenant(db_session):
    tenant = Tenant(name="Service Test Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def svc_user(db_session, svc_tenant):
    pw = bcrypt.generate_password_hash("pw").decode('utf-8')
    user = User(
        email="svcuser@example.com",
        first_name="Svc",
        last_name="User",
        password_hash=pw,
        tenant_id=svc_tenant.id,
        is_active=True,
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def svc_template(db_session, svc_user, svc_tenant):
    template = Template(
        name="Svc Template",
        subject="Hello {{.FirstName}}",
        email_html="<p>Hi {{.FirstName}}, click {{CLICK_URL}}</p>{{TRACKING_PIXEL}}",
        landing_page_html="<html><form action='{{FORM_ACTION}}'></form></html>",
        tenant_id=svc_tenant.id,
        created_by_user_id=svc_user.id,
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template


@pytest.fixture
def svc_target(db_session, svc_tenant):
    target = Target(
        email="target@example.com",
        first_name="Alice",
        last_name="Smith",
        position="Engineer",
        tenant_id=svc_tenant.id,
    )
    db_session.add(target)
    db_session.commit()
    db_session.refresh(target)
    return target


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCreateCampaignImmediate:
    """Immediate (non-scheduled) campaign creation."""

    def test_create_campaign_immediate_status_running(
        self, db_session, svc_tenant, svc_user, svc_template, svc_target
    ):
        with patch('app.services.email_service.send_phishing_email', return_value=True), \
             patch('time.sleep'):
            campaign = CampaignService().create_campaign(
                name="Immediate Campaign",
                template_id=svc_template.id,
                tenant_id=svc_tenant.id,
                user_id=svc_user.id,
            )
            status = campaign.status
            launched = campaign.launched_at

        assert status == CampaignStatus.RUNNING
        assert launched is not None

    def test_create_campaign_immediate_sent_count(
        self, db_session, svc_tenant, svc_user, svc_template, svc_target
    ):
        with patch('app.services.email_service.send_phishing_email', return_value=True), \
             patch('time.sleep'):
            campaign = CampaignService().create_campaign(
                name="Immediate Count Campaign",
                template_id=svc_template.id,
                tenant_id=svc_tenant.id,
                user_id=svc_user.id,
            )
            stats = db.session.query(CampaignStats).filter_by(campaign_id=campaign.id).first()
            sent = stats.sent_count if stats else None

        assert sent == 1  # one target


class TestCreateCampaignScheduled:
    """Scheduled campaign creation."""

    def test_create_campaign_scheduled_status(
        self, db_session, svc_tenant, svc_user, svc_template, svc_target
    ):
        future = datetime.now(timezone.utc) + timedelta(hours=2)
        with patch('app.services.email_service.send_phishing_email') as mock_send, \
             patch('time.sleep'):
            campaign = CampaignService().create_campaign(
                name="Scheduled Campaign",
                template_id=svc_template.id,
                tenant_id=svc_tenant.id,
                user_id=svc_user.id,
                scheduled_start_at=future,
            )
            status = campaign.status
            launched = campaign.launched_at
            mock_send.assert_not_called()

        assert status == CampaignStatus.SCHEDULED
        assert launched is None

    def test_create_campaign_scheduled_sent_count_zero(
        self, db_session, svc_tenant, svc_user, svc_template, svc_target
    ):
        future = datetime.now(timezone.utc) + timedelta(hours=1)
        with patch('app.services.email_service.send_phishing_email', return_value=True), \
             patch('time.sleep'):
            campaign = CampaignService().create_campaign(
                name="Scheduled No Send",
                template_id=svc_template.id,
                tenant_id=svc_tenant.id,
                user_id=svc_user.id,
                scheduled_start_at=future,
            )
            stats = db.session.query(CampaignStats).filter_by(campaign_id=campaign.id).first()
            sent = stats.sent_count if stats else None

        assert sent == 0


class TestCreateCampaignValidation:
    """ValueError cases."""

    def test_no_targets_raises(self, db_session, svc_tenant, svc_user, svc_template):
        # svc_target fixture NOT used — tenant has no targets
        with pytest.raises(ValueError, match="No targets found"):
            CampaignService().create_campaign(
                name="No Targets",
                template_id=svc_template.id,
                tenant_id=svc_tenant.id,
                user_id=svc_user.id,
            )

    def test_template_not_found_raises(self, db_session, svc_tenant, svc_user, svc_target):
        with pytest.raises(ValueError, match="Template 99999 not found"):
            CampaignService().create_campaign(
                name="Bad Template",
                template_id=99999,
                tenant_id=svc_tenant.id,
                user_id=svc_user.id,
            )


class TestGetCampaignSummary:
    """Summary counts are computed from CampaignResult rows."""

    def test_summary_counts_correctly(self, db_session, svc_tenant, svc_user, svc_template):
        now = datetime.now(timezone.utc)
        campaign = Campaign(
            name="Summary Test",
            tenant_id=svc_tenant.id,
            template_id=svc_template.id,
            status=CampaignStatus.RUNNING,
            created_by_user_id=svc_user.id,
            launched_at=now,
        )
        db.session.add(campaign)
        db.session.commit()
        db.session.refresh(campaign)

        # Three results: one sent-only, one opened, one clicked+submitted
        r1 = CampaignResult(
            campaign_id=campaign.id, email="a@x.com",
            first_name="A", last_name="A", tracking_token="tok1",
            status="Sent", sent_at=now,
        )
        r2 = CampaignResult(
            campaign_id=campaign.id, email="b@x.com",
            first_name="B", last_name="B", tracking_token="tok2",
            status="Opened", sent_at=now, opened_at=now,
        )
        r3 = CampaignResult(
            campaign_id=campaign.id, email="c@x.com",
            first_name="C", last_name="C", tracking_token="tok3",
            status="Submitted Data", sent_at=now, opened_at=now,
            clicked_at=now, submitted_at=now,
        )
        stats = CampaignStats(
            campaign_id=campaign.id, total_targets=3,
            sent_count=3, opened_count=0, clicked_count=0,
            submitted_count=0, reported_count=0,
        )
        db.session.add_all([r1, r2, r3, stats])
        db.session.commit()

        summary = CampaignService().get_campaign_summary(campaign.id)

        assert summary['summary']['total'] == 3
        assert summary['summary']['sent'] == 3
        assert summary['summary']['opened'] == 2
        assert summary['summary']['clicked'] == 1
        assert summary['summary']['submitted_data'] == 1
        assert len(summary['results']) == 3


class TestCompleteCampaign:
    """complete_campaign sets status to STOPPED."""

    def test_complete_campaign_sets_stopped(self, db_session, svc_tenant, svc_user, svc_template):
        campaign = Campaign(
            name="Running Campaign",
            tenant_id=svc_tenant.id,
            template_id=svc_template.id,
            status=CampaignStatus.RUNNING,
            created_by_user_id=svc_user.id,
            launched_at=datetime.now(timezone.utc),
        )
        db.session.add(campaign)
        db.session.commit()
        db.session.refresh(campaign)
        cid = campaign.id

        result = CampaignService().complete_campaign(cid)
        status = result.status
        stopped = result.stopped_at

        assert status == CampaignStatus.STOPPED
        assert stopped is not None


class TestDeleteCampaign:
    """delete_campaign removes the campaign from DB."""

    def test_delete_campaign_removes_it(self, db_session, svc_tenant, svc_user, svc_template):
        campaign = Campaign(
            name="To Delete",
            tenant_id=svc_tenant.id,
            template_id=svc_template.id,
            status=CampaignStatus.RUNNING,
            created_by_user_id=svc_user.id,
        )
        db.session.add(campaign)
        db.session.commit()
        cid = campaign.id

        CampaignService().delete_campaign(cid)

        gone = db.session.query(Campaign).get(cid)
        assert gone is None

    def test_delete_campaign_not_found_raises(self, db_session):
        with pytest.raises(ValueError, match="Campaign 99999 not found"):
            CampaignService().delete_campaign(99999)


class TestCompleteCampaignNotFound:
    def test_complete_campaign_not_found_raises(self, db_session):
        with pytest.raises(ValueError, match="Campaign 99999 not found"):
            CampaignService().complete_campaign(99999)


class TestCreateCampaignTargetIdFilter:
    """target_ids parameter filters targets — covers the id_set branch."""

    def test_create_campaign_with_invalid_target_ids_raises(
        self, db_session, svc_tenant, svc_user, svc_template, svc_target
    ):
        """Passing target_ids that don't belong to the tenant raises ValueError."""
        with pytest.raises(ValueError, match="None of the selected targets"):
            CampaignService().create_campaign(
                name="Bad Target IDs",
                template_id=svc_template.id,
                tenant_id=svc_tenant.id,
                user_id=svc_user.id,
                target_ids=[99999],  # valid format but no match
            )


class TestSendEmailsSlep:
    """Ensure time.sleep is called between emails when there are multiple targets."""

    def test_sleep_called_between_emails(
        self, db_session, svc_tenant, svc_user, svc_template
    ):
        # Add two targets so the loop runs more than once
        t2 = Target(
            email="b@example.com", first_name="Bob", last_name="Jones",
            tenant_id=svc_tenant.id,
        )
        t3 = Target(
            email="c@example.com", first_name="Carol", last_name="Jones",
            tenant_id=svc_tenant.id,
        )
        db.session.add_all([t2, t3])
        db.session.commit()

        with patch('app.services.email_service.send_phishing_email', return_value=True), \
             patch('time.sleep') as mock_sleep:
            CampaignService().create_campaign(
                name="Multi Target",
                template_id=svc_template.id,
                tenant_id=svc_tenant.id,
                user_id=svc_user.id,
            )

        # sleep(1.2) is called once (between email 1 and 2, then between 2 and 3 — i.e. n-1 times)
        assert mock_sleep.call_count >= 1


class TestTickScheduledCampaigns:
    """tick_scheduled_campaigns launches due campaigns and stops expired ones."""

    def test_tick_launches_scheduled_campaign(
        self, db_session, svc_tenant, svc_user, svc_template, svc_target
    ):
        """A SCHEDULED campaign whose start time is in the past should become RUNNING."""
        past = datetime.now(timezone.utc) - timedelta(minutes=5)
        campaign = Campaign(
            name="Due Scheduled",
            tenant_id=svc_tenant.id,
            template_id=svc_template.id,
            status=CampaignStatus.SCHEDULED,
            created_by_user_id=svc_user.id,
            scheduled_start_at=past,
        )
        db.session.add(campaign)
        db.session.commit()

        result = CampaignResult(
            campaign_id=campaign.id,
            email=svc_target.email,
            first_name=svc_target.first_name,
            last_name=svc_target.last_name,
            tracking_token="tick-tok-1",
            status="Pending",
        )
        stats = CampaignStats(
            campaign_id=campaign.id, total_targets=1,
            sent_count=0, opened_count=0, clicked_count=0,
            submitted_count=0, reported_count=0,
        )
        db.session.add_all([result, stats])
        db.session.commit()
        cid = campaign.id

        with patch('app.services.email_service.send_phishing_email', return_value=True), \
             patch('time.sleep'):
            CampaignService().tick_scheduled_campaigns()

        db.session.refresh(campaign)
        assert campaign.status == CampaignStatus.RUNNING
        assert campaign.launched_at is not None

    def test_tick_stops_expired_campaign(self, db_session, svc_tenant, svc_user, svc_template):
        """A RUNNING campaign whose end time has passed should become STOPPED."""
        past = datetime.now(timezone.utc) - timedelta(minutes=1)
        campaign = Campaign(
            name="Expired Running",
            tenant_id=svc_tenant.id,
            template_id=svc_template.id,
            status=CampaignStatus.RUNNING,
            created_by_user_id=svc_user.id,
            launched_at=past,
            scheduled_end_at=past,
        )
        db.session.add(campaign)
        db.session.commit()

        CampaignService().tick_scheduled_campaigns()

        db.session.refresh(campaign)
        assert campaign.status == CampaignStatus.STOPPED
        assert campaign.stopped_at is not None
