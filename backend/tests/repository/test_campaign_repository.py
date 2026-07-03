"""Tests for CampaignRepository.update_status_by_id."""
import pytest
from datetime import datetime, timezone

from app.extensions import bcrypt, db
from app.models import User, Tenant, Template
from app.models.campaign import Campaign, CampaignStatus
from app.repository.campaign_repository import CampaignRepository


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def repo_tenant(db_session):
    tenant = Tenant(name="Repo Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def repo_user(db_session, repo_tenant):
    pw = bcrypt.generate_password_hash("pw").decode('utf-8')
    user = User(
        email="repouser@example.com",
        first_name="Repo",
        last_name="User",
        password_hash=pw,
        tenant_id=repo_tenant.id,
        is_active=True,
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def repo_template(db_session, repo_user, repo_tenant):
    template = Template(
        name="Repo Template",
        subject="Subject",
        email_html="<html></html>",
        landing_page_html="<html></html>",
        tenant_id=repo_tenant.id,
        created_by_user_id=repo_user.id,
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template


@pytest.fixture
def repo_campaign(db_session, repo_tenant, repo_user, repo_template):
    campaign = Campaign(
        name="Repo Campaign",
        tenant_id=repo_tenant.id,
        template_id=repo_template.id,
        status=CampaignStatus.SCHEDULED,
        created_by_user_id=repo_user.id,
    )
    db_session.add(campaign)
    db_session.commit()
    db_session.refresh(campaign)
    return campaign


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestUpdateStatusById:

    def test_update_status_to_running_sets_launched_at(self, db_session, repo_campaign):
        result = CampaignRepository().update_status_by_id(
            repo_campaign.id, CampaignStatus.RUNNING
        )
        # Read attributes before session might expire
        status = result.status
        launched = result.launched_at

        assert status == CampaignStatus.RUNNING
        assert launched is not None

    def test_update_status_to_stopped_sets_stopped_at(self, db_session, repo_campaign):
        # First transition to RUNNING
        CampaignRepository().update_status_by_id(repo_campaign.id, CampaignStatus.RUNNING)
        # Then stop it
        result = CampaignRepository().update_status_by_id(
            repo_campaign.id, CampaignStatus.STOPPED
        )
        status = result.status
        stopped = result.stopped_at

        assert status == CampaignStatus.STOPPED
        assert stopped is not None

    def test_update_status_not_found_raises(self, db_session):
        with pytest.raises(ValueError, match="99999 not found"):
            CampaignRepository().update_status_by_id(99999, CampaignStatus.RUNNING)
