"""
Tests for Instance API endpoints
"""
import pytest
from flask_jwt_extended import create_access_token

from app.extensions import db, bcrypt
from app.models import User, Tenant, Instance, Campaign, CampaignStatus, Template
from app.repository.instance_repository import InstanceRepository


@pytest.fixture
def test_tenant(db_session):
    """Create a test tenant"""
    tenant = Tenant(name="Test Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def admin_user(db_session, test_tenant):
    """Create an admin user"""
    password_hash = bcrypt.generate_password_hash("adminpassword123").decode('utf-8')
    user = User(
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        password_hash=password_hash,
        tenant_id=test_tenant.id,
        is_active=True,
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_user(db_session, test_tenant):
    """Create a regular (non-admin) user"""
    password_hash = bcrypt.generate_password_hash("userpassword123").decode('utf-8')
    user = User(
        email="user@example.com",
        first_name="Regular",
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
def admin_headers(admin_user):
    """Create authorization headers with admin JWT token"""
    token = create_access_token(identity=str(admin_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def regular_headers(regular_user):
    """Create authorization headers with regular user JWT token"""
    token = create_access_token(identity=str(regular_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def test_instance(db_session):
    """Create a test Gophish instance"""
    instance = Instance(
        name="Test Instance",
        base_url="https://test-gophish.example.com",
        api_key="test-api-key-12345",
        redirect_url="https://test-redirect.example.com",
        is_active=True
    )
    db_session.add(instance)
    db_session.commit()
    db_session.refresh(instance)
    return instance


@pytest.fixture
def another_instance(db_session):
    """Create another test instance"""
    instance = Instance(
        name="Another Instance",
        base_url="https://another-gophish.example.com",
        api_key="another-api-key-67890",
        redirect_url="https://another-redirect.example.com",
        is_active=False
    )
    db_session.add(instance)
    db_session.commit()
    db_session.refresh(instance)
    return instance


@pytest.fixture
def test_template(db_session, test_instance, admin_user):
    """Create a test template"""
    template = Template(
        name="Test Template",
        gophish_instance_id=test_instance.id,
        gophish_email_template_id=1,
        gophish_landing_page_id=1,
        created_by_user_id=admin_user.id
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template


class TestGetAllInstances:
    """Tests for GET /api/instances"""

    def test_get_all_instances_success(self, client, admin_headers, test_instance, another_instance):
        """Test successfully getting all instances as admin"""
        response = client.get('/api/instances', headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'instances' in data
        assert len(data['instances']) == 2

    def test_get_all_instances_requires_auth(self, client):
        """Test that getting instances requires authentication"""
        response = client.get('/api/instances')

        assert response.status_code == 401

    def test_get_all_instances_requires_admin(self, client, regular_headers):
        """Test that getting instances requires admin access"""
        response = client.get('/api/instances', headers=regular_headers)

        assert response.status_code == 403
        assert 'Admin access required' in response.get_json()['error']


class TestGetInstance:
    """Tests for GET /api/instances/<id>"""

    def test_get_instance_success(self, client, admin_headers, test_instance):
        """Test successfully getting an instance by ID"""
        response = client.get(f'/api/instances/{test_instance.id}', headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == test_instance.id
        assert data['name'] == test_instance.name
        assert data['base_url'] == test_instance.base_url

    def test_get_instance_not_found(self, client, admin_headers):
        """Test getting a non-existent instance returns 404"""
        response = client.get('/api/instances/99999', headers=admin_headers)

        assert response.status_code == 404
        assert 'Instance not found' in response.get_json()['error']


class TestCreateInstance:
    """Tests for POST /api/instances"""

    def test_create_instance_success(self, client, admin_headers):
        """Test successfully creating an instance"""
        instance_data = {
            'name': 'New Instance',
            'base_url': 'https://new-instance.example.com',
            'api_key': 'new-api-key-abcdef',
            'redirect_url': 'https://new-redirect.example.com',
            'is_active': True
        }

        response = client.post('/api/instances', json=instance_data, headers=admin_headers)

        assert response.status_code == 201
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['instance']['name'] == instance_data['name']

    def test_create_instance_missing_data(self, client, admin_headers):
        """Test creating instance with empty body"""
        response = client.post('/api/instances', json={}, headers=admin_headers)

        assert response.status_code == 400
        assert response.get_json()['error'] == 'No data provided'

    def test_create_instance_invalid_base_url(self, client, admin_headers):
        """Test creating instance with invalid base_url"""
        response = client.post('/api/instances', json={
            'name': 'Test Instance',
            'base_url': 'invalid-url',
            'api_key': 'test-key',
            'redirect_url': 'https://redirect.example.com'
        }, headers=admin_headers)

        assert response.status_code == 400
        assert 'Invalid base_url' in response.get_json()['error']

    def test_create_instance_duplicate_name(self, client, admin_headers, test_instance):
        """Test creating instance with duplicate name is rejected"""
        response = client.post('/api/instances', json={
            'name': test_instance.name,
            'base_url': 'https://different.example.com',
            'api_key': 'different-key',
            'redirect_url': 'https://different-redirect.example.com'
        }, headers=admin_headers)

        assert response.status_code == 400
        assert 'Instance with this name already exists' in response.get_json()['error']

    def test_create_instance_requires_admin(self, client, regular_headers):
        """Test that creating instance requires admin access"""
        response = client.post('/api/instances', json={
            'name': 'Test Instance',
            'base_url': 'https://test.example.com',
            'api_key': 'test-key',
            'redirect_url': 'https://redirect.example.com'
        }, headers=regular_headers)

        assert response.status_code == 403
        assert 'Admin access required' in response.get_json()['error']


class TestUpdateInstance:
    """Tests for PUT /api/instances/<id>"""

    def test_update_instance_success(self, client, admin_headers, test_instance):
        """Test successfully updating an instance"""
        update_data = {
            'name': 'Updated Instance',
            'base_url': 'https://updated.example.com',
            'api_key': 'updated-api-key',
            'is_active': False,
            'redirect_url': 'https://updated-redirect.example.com'
        }

        response = client.put(f'/api/instances/{test_instance.id}',
                              json=update_data, headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['instance']['name'] == update_data['name']

    def test_update_instance_not_found(self, client, admin_headers):
        """Test updating a non-existent instance returns 404"""
        response = client.put('/api/instances/99999', json={'name': 'Updated'}, headers=admin_headers)

        assert response.status_code == 404
        assert 'Instance not found' in response.get_json()['error']

    def test_update_instance_duplicate_name(self, client, admin_headers, test_instance, another_instance):
        """Test updating instance with a name that belongs to another instance"""
        response = client.put(f'/api/instances/{test_instance.id}',
                              json={'name': another_instance.name}, headers=admin_headers)

        assert response.status_code == 400
        assert 'Instance with this name already exists' in response.get_json()['error']

    def test_update_instance_requires_admin(self, client, regular_headers, test_instance):
        """Test that updating instance requires admin access"""
        response = client.put(f'/api/instances/{test_instance.id}',
                              json={'name': 'Updated'}, headers=regular_headers)

        assert response.status_code == 403
        assert 'Admin access required' in response.get_json()['error']


class TestDeleteInstance:
    """Tests for DELETE /api/instances/<id>"""

    def test_delete_instance_success(self, client, admin_headers, db_session):
        """Test successfully deleting an instance"""
        instance = Instance(
            name="To Delete",
            base_url="https://delete.example.com",
            api_key="delete-key",
            redirect_url="https://delete-redirect.example.com",
            is_active=True
        )
        db_session.add(instance)
        db_session.commit()
        db_session.refresh(instance)

        response = client.delete(f'/api/instances/{instance.id}', headers=admin_headers)

        assert response.status_code == 200
        assert response.get_json()['status'] == 'success'
        assert InstanceRepository().get_by_id(instance.id) is None

    def test_delete_instance_not_found(self, client, admin_headers):
        """Test deleting a non-existent instance returns 404"""
        response = client.delete('/api/instances/99999', headers=admin_headers)

        assert response.status_code == 404
        assert 'Instance not found' in response.get_json()['error']

    def test_delete_instance_with_running_campaigns(self, client, admin_headers, test_instance,
                                                     db_session, test_tenant, admin_user, test_template):
        """Test that instance with running campaigns cannot be deleted"""
        campaign = Campaign(
            name="Running Campaign",
            tenant_id=test_tenant.id,
            created_by_user_id=admin_user.id,
            gophish_instance_id=test_instance.id,
            gophish_campaign_id=1,
            status=CampaignStatus.RUNNING,
            template_id=test_template.id
        )
        db_session.add(campaign)
        db_session.commit()

        response = client.delete(f'/api/instances/{test_instance.id}', headers=admin_headers)

        assert response.status_code == 400
        data = response.get_json()
        assert 'Cannot delete instance with running campaigns' in data['error']

    def test_delete_instance_with_templates(self, client, admin_headers, test_instance,
                                            db_session, admin_user):
        """Test that instance with templates cannot be deleted"""
        template = Template(
            name="Test Template",
            gophish_instance_id=test_instance.id,
            gophish_email_template_id=1,
            gophish_landing_page_id=1,
            created_by_user_id=admin_user.id
        )
        db_session.add(template)
        db_session.commit()

        response = client.delete(f'/api/instances/{test_instance.id}', headers=admin_headers)

        assert response.status_code == 400
        data = response.get_json()
        assert 'Cannot delete instance with associated templates' in data['error']

    def test_delete_instance_requires_admin(self, client, regular_headers, test_instance):
        """Test that deleting instance requires admin access"""
        response = client.delete(f'/api/instances/{test_instance.id}', headers=regular_headers)

        assert response.status_code == 403
        assert 'Admin access required' in response.get_json()['error']


class TestToggleInstanceStatus:
    """Tests for PATCH /api/instances/<id>/toggle"""

    def test_toggle_instance_status_activate(self, client, admin_headers, another_instance):
        """Test activating an inactive instance"""
        assert another_instance.is_active is False

        response = client.patch(f'/api/instances/{another_instance.id}/toggle',
                                headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['instance']['is_active'] is True

    def test_toggle_instance_status_not_found(self, client, admin_headers):
        """Test toggling status of non-existent instance returns 404"""
        response = client.patch('/api/instances/99999/toggle', headers=admin_headers)

        assert response.status_code == 404
        assert 'Instance not found' in response.get_json()['error']

    def test_toggle_instance_status_requires_admin(self, client, regular_headers, test_instance):
        """Test that toggling instance status requires admin access"""
        response = client.patch(f'/api/instances/{test_instance.id}/toggle',
                                headers=regular_headers)

        assert response.status_code == 403
        assert 'Admin access required' in response.get_json()['error']
