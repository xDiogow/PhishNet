"""Tests for Campaign API endpoints"""
import pytest
from unittest.mock import patch
from flask_jwt_extended import create_access_token
from datetime import datetime, timezone

from app.extensions import bcrypt
from app.models import User, Tenant, Template, Campaign, CampaignStatus
from app.models.user_permission import ALL_PERMISSIONS
from app.repository.user_permission_repository import UserPermissionRepository


@pytest.fixture
def test_tenant(db_session):
    tenant = Tenant(name="Test Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def test_user(db_session, test_tenant):
    password_hash = bcrypt.generate_password_hash("testpassword123").decode('utf-8')
    user = User(
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password_hash=password_hash,
        tenant_id=test_tenant.id,
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    UserPermissionRepository().grant_all(user.id, test_tenant.id, ALL_PERMISSIONS)
    return user


@pytest.fixture
def test_template(db_session, test_user, test_tenant):
    template = Template(
        name="Test Template",
        subject="Test Subject",
        email_html="<html>Email</html>",
        landing_page_html="<html><form action='{{FORM_ACTION}}'></form></html>",
        tenant_id=test_tenant.id,
        created_by_user_id=test_user.id,
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template


@pytest.fixture
def test_campaign(db_session, test_tenant, test_user, test_template):
    campaign = Campaign(
        name="Test Campaign",
        tenant_id=test_tenant.id,
        created_by_user_id=test_user.id,
        status=CampaignStatus.RUNNING,
        template_id=test_template.id,
        launched_at=datetime.now(timezone.utc)
    )
    db_session.add(campaign)
    db_session.commit()
    db_session.refresh(campaign)
    return campaign


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token(identity=str(test_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def another_tenant(db_session):
    tenant = Tenant(name="Another Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def another_user(db_session, another_tenant):
    password_hash = bcrypt.generate_password_hash("testpassword123").decode('utf-8')
    user = User(
        email="another@example.com",
        first_name="Another",
        last_name="User",
        password_hash=password_hash,
        tenant_id=another_tenant.id,
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


class TestGetAllCampaigns:
    """EF13 (campaign list), EF17 (tenant isolation)"""

    def test_get_all_campaigns_success(self, client, auth_headers, test_campaign):
        response = client.get('/api/campaigns', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'campaigns' in data
        assert len(data['campaigns']) == 1
        assert data['campaigns'][0]['id'] == test_campaign.id

    def test_get_all_campaigns_requires_auth(self, client):
        response = client.get('/api/campaigns')
        assert response.status_code == 401

    def test_get_all_campaigns_tenant_isolation(self, client, auth_headers, test_campaign,
                                                db_session, another_tenant, another_user,
                                                test_template):
        another_campaign = Campaign(
            name="Another Campaign",
            tenant_id=another_tenant.id,
            created_by_user_id=another_user.id,
            status=CampaignStatus.RUNNING,
            template_id=test_template.id
        )
        db_session.add(another_campaign)
        db_session.commit()

        response = client.get('/api/campaigns', headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['campaigns']) == 1
        assert data['campaigns'][0]['id'] == test_campaign.id


class TestGetCampaign:
    """EF08 (campaign detail), EF17 (tenant isolation)"""

    def test_get_campaign_success(self, client, auth_headers, test_campaign):
        response = client.get(f'/api/campaigns/{test_campaign.id}', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == test_campaign.id
        assert data['name'] == test_campaign.name
        assert data['status'] == test_campaign.status.value

    def test_get_campaign_not_found(self, client, auth_headers):
        response = client.get('/api/campaigns/99999', headers=auth_headers)
        assert response.status_code == 404

    def test_get_campaign_tenant_isolation(self, client, auth_headers, db_session,
                                           another_tenant, another_user, test_template):
        another_campaign = Campaign(
            name="Another Campaign",
            tenant_id=another_tenant.id,
            created_by_user_id=another_user.id,
            status=CampaignStatus.RUNNING,
            template_id=test_template.id
        )
        db_session.add(another_campaign)
        db_session.commit()

        response = client.get(f'/api/campaigns/{another_campaign.id}', headers=auth_headers)
        assert response.status_code == 404


class TestGetCampaignSummary:
    """EF13 — real-time stats (sent / opened / clicked / submitted)"""

    def test_get_campaign_summary_success(self, client, auth_headers, test_campaign):
        with patch('app.services.campaign_service.CampaignService.get_campaign_summary') as mock:
            mock.return_value = {
                'summary': {'total': 1, 'sent': 1, 'opened': 0, 'clicked': 0, 'submitted': 0},
                'results': []
            }
            response = client.get(f'/api/campaigns/{test_campaign.id}/summary', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'summary' in data
        assert 'results' in data

    def test_get_campaign_summary_not_found(self, client, auth_headers):
        response = client.get('/api/campaigns/99999/summary', headers=auth_headers)
        assert response.status_code == 404


class TestCreateCampaign:
    """EF08 — campaign creation and immediate launch"""

    def test_create_campaign_success(self, client, auth_headers, test_template, test_tenant,
                                     test_user, db_session):
        with patch('app.services.campaign_service.CampaignService.create_campaign') as mock:
            from app.models import Campaign, CampaignStatus
            campaign = Campaign(
                name="New Campaign",
                tenant_id=test_tenant.id,
                created_by_user_id=test_user.id,
                template_id=test_template.id,
                status=CampaignStatus.RUNNING,
                launched_at=datetime.now(timezone.utc)
            )
            db_session.add(campaign)
            db_session.flush()
            mock.return_value = campaign

            response = client.post('/api/campaigns',
                                   json={'name': 'New Campaign', 'template_id': test_template.id},
                                   headers=auth_headers)

        assert response.status_code == 201
        data = response.get_json()
        assert data['status'] == 'success'

    def test_create_campaign_missing_name(self, client, auth_headers):
        response = client.post('/api/campaigns', json={}, headers=auth_headers)
        assert response.status_code == 400
        assert 'error' in response.get_json()

    def test_create_campaign_template_not_found(self, client, auth_headers):
        response = client.post('/api/campaigns',
                               json={'name': 'Test Campaign', 'template_id': 99999},
                               headers=auth_headers)
        assert response.status_code == 404

    def test_create_campaign_requires_auth(self, client, test_template):
        response = client.post('/api/campaigns',
                               json={'name': 'Test Campaign', 'template_id': test_template.id})
        assert response.status_code == 401


class TestDeleteCampaign:
    """EF08 (campaign lifecycle), EF17 (tenant isolation)"""

    def test_delete_campaign_success(self, client, auth_headers, test_campaign):
        with patch('app.services.campaign_service.CampaignService.delete_campaign'):
            response = client.delete(f'/api/campaigns/{test_campaign.id}', headers=auth_headers)

        assert response.status_code == 200
        assert response.get_json()['status'] == 'success'

    def test_delete_campaign_tenant_isolation(self, client, auth_headers, db_session,
                                               another_tenant, another_user, test_template):
        another_campaign = Campaign(
            name="Another Campaign",
            tenant_id=another_tenant.id,
            created_by_user_id=another_user.id,
            status=CampaignStatus.RUNNING,
            template_id=test_template.id
        )
        db_session.add(another_campaign)
        db_session.commit()

        response = client.delete(f'/api/campaigns/{another_campaign.id}', headers=auth_headers)
        assert response.status_code == 404


class TestCompleteCampaign:
    """EF09 — stop a running campaign"""

    def test_complete_campaign_success(self, client, auth_headers, test_campaign):
        with patch('app.services.campaign_service.CampaignService.complete_campaign') as mock:
            mock.return_value = test_campaign
            response = client.post(f'/api/campaigns/{test_campaign.id}/complete', headers=auth_headers)

        assert response.status_code == 200
        assert response.get_json()['status'] == 'success'

    def test_complete_campaign_tenant_isolation(self, client, auth_headers, db_session,
                                                another_tenant, another_user, test_template):
        another_campaign = Campaign(
            name="Another Campaign",
            tenant_id=another_tenant.id,
            created_by_user_id=another_user.id,
            status=CampaignStatus.RUNNING,
            template_id=test_template.id
        )
        db_session.add(another_campaign)
        db_session.commit()

        response = client.post(f'/api/campaigns/{another_campaign.id}/complete', headers=auth_headers)
        assert response.status_code == 404
