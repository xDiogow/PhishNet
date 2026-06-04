"""Tests for tracking endpoints (open pixel, click redirect, landing page, submission)"""
import pytest
import uuid
from datetime import datetime, timezone

from app.extensions import db, bcrypt
from app.models import User, Tenant, Template, Campaign, CampaignStatus
from app.models.campaign_result import CampaignResult
from app.models.campaign_stats import CampaignStats


@pytest.fixture
def test_tenant(db_session):
    tenant = Tenant(name="Tracking Test Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def test_user(db_session, test_tenant):
    password_hash = bcrypt.generate_password_hash("pass").decode('utf-8')
    user = User(
        email="tracker@example.com",
        first_name="Track",
        last_name="User",
        password_hash=password_hash,
        tenant_id=test_tenant.id,
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_template(db_session, test_user):
    template = Template(
        name="Track Template",
        subject="Click me",
        email_html="<html>{{TRACKING_PIXEL}}</html>",
        landing_page_html=(
            "<html><body>"
            "<h2>{{.Email}}</h2>"
            "<h3>{{ EMAIL}}</h3>"
            "<p>{{.FirstName}} {{.LastName}}</p>"
            "<p>{{.Position}}</p>"
            "<form action='{{FORM_ACTION}}' method='POST'><input name='email'/></form>"
            "</body></html>"
        ),
        created_by_user_id=test_user.id
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template


@pytest.fixture
def test_campaign(db_session, test_tenant, test_user, test_template):
    campaign = Campaign(
        name="Track Campaign",
        tenant_id=test_tenant.id,
        created_by_user_id=test_user.id,
        template_id=test_template.id,
        status=CampaignStatus.RUNNING,
        launched_at=datetime.now(timezone.utc)
    )
    db_session.add(campaign)
    db_session.commit()
    db_session.refresh(campaign)

    stats = CampaignStats(
        campaign_id=campaign.id,
        total_targets=1,
        sent_count=1,
        opened_count=0,
        clicked_count=0,
        submitted_count=0,
        reported_count=0
    )
    db_session.add(stats)
    db_session.commit()

    return campaign


@pytest.fixture
def test_result(db_session, test_campaign):
    token = str(uuid.uuid4())
    result = CampaignResult(
        campaign_id=test_campaign.id,
        email="target@example.com",
        first_name="John",
        last_name="Doe",
        position="Engineer",
        tracking_token=token,
        status="Sent",
        sent_at=datetime.now(timezone.utc)
    )
    db_session.add(result)
    db_session.commit()
    db_session.refresh(result)
    return result


class TestOpenPixel:
    """EF10 — open-tracking pixel (1×1 GIF), idempotency"""

    def test_returns_gif(self, client, test_result):
        response = client.get(f'/track/o/{test_result.tracking_token}')

        assert response.status_code == 200
        assert response.content_type == 'image/gif'
        assert response.data[:3] == b'GIF'

    def test_records_open(self, client, test_result, db_session):
        client.get(f'/track/o/{test_result.tracking_token}')

        db_session.refresh(test_result)
        assert test_result.opened_at is not None
        assert test_result.status == 'Opened'

    def test_open_idempotent(self, client, test_result, db_session):
        client.get(f'/track/o/{test_result.tracking_token}')
        db_session.refresh(test_result)
        first_opened_at = test_result.opened_at

        client.get(f'/track/o/{test_result.tracking_token}')
        db_session.refresh(test_result)
        assert test_result.opened_at == first_opened_at

    def test_unknown_token_still_returns_gif(self, client):
        response = client.get('/track/o/nonexistent-token')
        assert response.status_code == 200
        assert response.content_type == 'image/gif'


class TestClickRedirect:
    """EF11 — click tracking and 302 redirect to landing page"""

    def test_redirects_to_landing_page(self, client, test_result):
        response = client.get(f'/track/c/{test_result.tracking_token}')

        assert response.status_code == 302
        assert f'/phish/{test_result.tracking_token}' in response.location

    def test_records_click(self, client, test_result, db_session):
        client.get(f'/track/c/{test_result.tracking_token}')

        db_session.refresh(test_result)
        assert test_result.clicked_at is not None
        assert test_result.status == 'Clicked'

    def test_click_idempotent(self, client, test_result, db_session):
        client.get(f'/track/c/{test_result.tracking_token}')
        db_session.refresh(test_result)
        first_clicked_at = test_result.clicked_at

        client.get(f'/track/c/{test_result.tracking_token}')
        db_session.refresh(test_result)
        assert test_result.clicked_at == first_clicked_at


class TestLandingPage:
    """EF07 (placeholder substitution), EF11 (landing page served), EF12 (form action injection)"""

    def test_serves_landing_page(self, client, test_result):
        response = client.get(f'/phish/{test_result.tracking_token}')

        assert response.status_code == 200
        assert b'<html>' in response.data

    def test_injects_form_action(self, client, test_result):
        response = client.get(f'/phish/{test_result.tracking_token}')

        assert response.status_code == 200
        expected = f'/phish/{test_result.tracking_token}'.encode()
        assert expected in response.data

    def test_injects_email_placeholder(self, client, test_result):
        response = client.get(f'/phish/{test_result.tracking_token}')

        assert response.status_code == 200
        assert test_result.email.encode() in response.data
        assert b'{{.Email}}' not in response.data
        assert b'{{ EMAIL}}' not in response.data

    def test_injects_name_placeholders(self, client, test_result):
        response = client.get(f'/phish/{test_result.tracking_token}')

        assert response.status_code == 200
        assert test_result.first_name.encode() in response.data
        assert test_result.last_name.encode() in response.data
        assert b'{{.FirstName}}' not in response.data
        assert b'{{.LastName}}' not in response.data

    def test_injects_position_placeholder(self, client, test_result):
        response = client.get(f'/phish/{test_result.tracking_token}')

        assert response.status_code == 200
        assert test_result.position.encode() in response.data
        assert b'{{.Position}}' not in response.data

    def test_unknown_token_returns_404(self, client):
        response = client.get('/phish/nonexistent-token')
        assert response.status_code == 404


class TestSubmission:
    """EF12 — credential submission tracking, idempotency, redirect to /caught"""

    def test_records_submission(self, client, test_result, db_session):
        client.post(f'/phish/{test_result.tracking_token}',
                    data={'email': 'target@example.com', 'password': 'secret'})

        db_session.refresh(test_result)
        assert test_result.submitted_at is not None
        assert test_result.status == 'Submitted Data'

    def test_redirects_to_caught(self, client, test_result):
        response = client.post(f'/phish/{test_result.tracking_token}',
                               data={'email': 'target@example.com'})

        assert response.status_code == 302
        assert '/caught' in response.location

    def test_submission_idempotent(self, client, test_result, db_session):
        client.post(f'/phish/{test_result.tracking_token}', data={'email': 'x@x.com'})
        db_session.refresh(test_result)
        first_submitted_at = test_result.submitted_at

        client.post(f'/phish/{test_result.tracking_token}', data={'email': 'x@x.com'})
        db_session.refresh(test_result)
        assert test_result.submitted_at == first_submitted_at
