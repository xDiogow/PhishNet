"""
Tests for Campaign API endpoints
"""
import pytest
from unittest.mock import Mock, patch
from flask_jwt_extended import create_access_token
from datetime import datetime

from app.extensions import db, bcrypt
from app.models import User, Tenant, Instance, Template, Campaign, CampaignStatus


@pytest.fixture
def test_tenant(db_session):
    """Create a test tenant"""
    tenant = Tenant(name="Test Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def test_instance(db_session):
    """Create a test Gophish instance"""
    instance = Instance(
        name="Test Instance",
        base_url="https://test-gophish.example.com",
        api_key="test-api-key",
        redirect_url="https://test-redirect.example.com",
        is_active=True
    )
    db_session.add(instance)
    db_session.commit()
    db_session.refresh(instance)
    return instance


@pytest.fixture
def test_user(db_session, test_tenant):
    """Create a test user"""
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
    return user


@pytest.fixture
def test_template(db_session, test_instance, test_user):
    """Create a test template"""
    template = Template(
        name="Test Template",
        gophish_instance_id=test_instance.id,
        gophish_email_template_id=1,
        gophish_landing_page_id=1,
        created_by_user_id=test_user.id
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template


@pytest.fixture
def test_campaign(db_session, test_tenant, test_instance, test_user, test_template):
    """Create a test campaign"""
    campaign = Campaign(
        name="Test Campaign",
        tenant_id=test_tenant.id,
        created_by_user_id=test_user.id,
        gophish_instance_id=test_instance.id,
        gophish_campaign_id=1,
        status=CampaignStatus.RUNNING,
        template_id=test_template.id,
        launched_at=datetime.utcnow()
    )
    db_session.add(campaign)
    db_session.commit()
    db_session.refresh(campaign)
    return campaign


@pytest.fixture
def auth_headers(test_user):
    """Create authorization headers with JWT token"""
    token = create_access_token(identity=str(test_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def another_tenant(db_session):
    """Create another test tenant for isolation testing"""
    tenant = Tenant(name="Another Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def another_user(db_session, another_tenant):
    """Create another test user for isolation testing"""
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


@pytest.fixture
def another_auth_headers(another_user):
    """Create authorization headers for another user"""
    token = create_access_token(identity=str(another_user.id))
    return {'Authorization': f'Bearer {token}'}


class TestGetAllCampaigns:
    """Tests for GET /api/campaigns"""

    def test_get_all_campaigns_success(self, client, auth_headers, test_campaign):
        """Test successfully getting all campaigns"""
        response = client.get('/api/campaigns', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'campaigns' in data
        assert len(data['campaigns']) == 1
        assert data['campaigns'][0]['id'] == test_campaign.id

    def test_get_all_campaigns_requires_auth(self, client):
        """Test that getting campaigns requires authentication"""
        response = client.get('/api/campaigns')

        assert response.status_code == 401

    def test_get_all_campaigns_tenant_isolation(self, client, auth_headers,
                                                test_campaign, db_session,
                                                another_tenant, another_user,
                                                test_instance, test_template):
        """Test that users only see campaigns from their own tenant"""
        another_campaign = Campaign(
            name="Another Campaign",
            tenant_id=another_tenant.id,
            created_by_user_id=another_user.id,
            gophish_instance_id=test_instance.id,
            gophish_campaign_id=2,
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
    """Tests for GET /api/campaigns/<id>"""

    def test_get_campaign_success(self, client, auth_headers, test_campaign):
        """Test successfully getting a campaign by ID"""
        response = client.get(f'/api/campaigns/{test_campaign.id}', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == test_campaign.id
        assert data['name'] == test_campaign.name
        assert data['status'] == test_campaign.status.value

    def test_get_campaign_not_found(self, client, auth_headers):
        """Test getting a non-existent campaign returns 404"""
        response = client.get('/api/campaigns/99999', headers=auth_headers)

        assert response.status_code == 404

    def test_get_campaign_tenant_isolation(self, client, auth_headers,
                                           db_session, another_tenant, another_user,
                                           test_instance, test_template):
        """Test that users cannot access campaigns from other tenants"""
        another_campaign = Campaign(
            name="Another Campaign",
            tenant_id=another_tenant.id,
            created_by_user_id=another_user.id,
            gophish_instance_id=test_instance.id,
            gophish_campaign_id=2,
            status=CampaignStatus.RUNNING,
            template_id=test_template.id
        )
        db_session.add(another_campaign)
        db_session.commit()

        response = client.get(f'/api/campaigns/{another_campaign.id}', headers=auth_headers)
        assert response.status_code == 404


class TestGetCampaignSummary:
    """Tests for GET /api/campaigns/<id>/summary"""

    @patch('app.services.gophish.campaigns.CampaignService.get_campaign_summary_and_results')
    def test_get_campaign_summary_success(self, mock_get_data, client, auth_headers, test_campaign):
        """Test successfully getting campaign summary"""
        mock_get_data.return_value = {
            'summary': {'total': 100, 'sent': 95, 'opened': 50, 'clicked': 25, 'submitted': 10},
            'results': [{'id': 'test123', 'email': 'test@example.com',
                         'first_name': 'John', 'last_name': 'Doe',
                         'status': 'Submitted Data', 'position': ''}]
        }

        response = client.get(f'/api/campaigns/{test_campaign.id}/summary', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'summary' in data
        assert 'results' in data

    def test_get_campaign_summary_not_found(self, client, auth_headers):
        """Test getting summary for non-existent campaign returns 404"""
        response = client.get('/api/campaigns/99999/summary', headers=auth_headers)

        assert response.status_code == 404


class TestCreateCampaign:
    """Tests for POST /api/campaigns"""

    @patch('app.services.gophish.groups.GroupsService.create_group')
    @patch('app.services.gophish.campaigns.CampaignService.create_campaign')
    @patch('app.services.gophish.templates.TemplatesService.get_template_by_id')
    def test_create_campaign_success(self, mock_get_template, mock_create_campaign,
                                     mock_create_group, client, auth_headers, test_user,
                                     test_tenant, test_instance, test_template, db_session):
        """Test successfully creating a campaign"""
        test_tenant.instance_id = test_instance.id
        db_session.commit()

        mock_get_template.return_value = test_template
        mock_group = Mock()
        mock_group.id = 1
        mock_create_group.return_value = mock_group
        mock_create_campaign.return_value = {'status': 'success', 'campaign': {'id': 1, 'name': 'New Campaign'}}

        response = client.post('/api/campaigns',
                               json={'name': 'New Campaign', 'template_id': test_template.id},
                               headers=auth_headers)

        assert response.status_code == 201
        data = response.get_json()
        assert data['status'] == 'success'

    def test_create_campaign_missing_data(self, client, auth_headers):
        """Test creating campaign with empty body"""
        response = client.post('/api/campaigns', json={}, headers=auth_headers)

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_create_campaign_template_not_found(self, client, auth_headers):
        """Test creating campaign with non-existent template returns 404"""
        response = client.post('/api/campaigns',
                               json={'name': 'Test Campaign', 'template_id': 99999},
                               headers=auth_headers)

        assert response.status_code == 404
        data = response.get_json()
        assert 'Template not found' in data['error']

    def test_create_campaign_no_instance(self, client, auth_headers, test_template,
                                          test_tenant, db_session):
        """Test creating campaign when tenant has no instance configured"""
        test_tenant.instance_id = None
        db_session.commit()

        response = client.post('/api/campaigns',
                               json={'name': 'Test Campaign', 'template_id': test_template.id},
                               headers=auth_headers)

        assert response.status_code == 400
        data = response.get_json()
        assert 'Tenant instance not configured' in data['error']

    def test_create_campaign_requires_auth(self, client, test_template):
        """Test that creating campaign requires authentication"""
        response = client.post('/api/campaigns',
                               json={'name': 'Test Campaign', 'template_id': test_template.id})

        assert response.status_code == 401


class TestDeleteCampaign:
    """Tests for DELETE /api/campaigns/<id>"""

    @patch('app.services.gophish.campaigns.CampaignService.delete_campaign')
    def test_delete_campaign_success(self, mock_delete_campaign, client, auth_headers, test_campaign):
        """Test successfully deleting a campaign"""
        mock_delete_campaign.return_value = {'status': 'success'}

        response = client.delete(f'/api/campaigns/{test_campaign.id}', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    def test_delete_campaign_tenant_isolation(self, client, auth_headers, db_session,
                                               another_tenant, another_user, test_instance,
                                               test_template):
        """Test that users cannot delete campaigns from other tenants"""
        another_campaign = Campaign(
            name="Another Campaign",
            tenant_id=another_tenant.id,
            created_by_user_id=another_user.id,
            gophish_instance_id=test_instance.id,
            gophish_campaign_id=2,
            status=CampaignStatus.RUNNING,
            template_id=test_template.id
        )
        db_session.add(another_campaign)
        db_session.commit()

        response = client.delete(f'/api/campaigns/{another_campaign.id}', headers=auth_headers)
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestCompleteCampaign:
    """Tests for POST /api/campaigns/<id>/complete"""

    @patch('app.services.gophish.campaigns.CampaignService.complete_campaign')
    def test_complete_campaign_success(self, mock_complete_campaign, client, auth_headers, test_campaign):
        """Test successfully completing a campaign"""
        mock_complete_campaign.return_value = {'status': 'success'}

        response = client.post(f'/api/campaigns/{test_campaign.id}/complete', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    def test_complete_campaign_tenant_isolation(self, client, auth_headers, db_session,
                                                another_tenant, another_user, test_instance,
                                                test_template):
        """Test that users cannot complete campaigns from other tenants"""
        another_campaign = Campaign(
            name="Another Campaign",
            tenant_id=another_tenant.id,
            created_by_user_id=another_user.id,
            gophish_instance_id=test_instance.id,
            gophish_campaign_id=2,
            status=CampaignStatus.RUNNING,
            template_id=test_template.id
        )
        db_session.add(another_campaign)
        db_session.commit()

        response = client.post(f'/api/campaigns/{another_campaign.id}/complete', headers=auth_headers)
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
