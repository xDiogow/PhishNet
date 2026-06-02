"""
Tests for Tenant API endpoints
"""
import pytest
from unittest.mock import patch
from flask_jwt_extended import create_access_token

from app.extensions import db, bcrypt
from app.models import User, Tenant, TenantInvitation


@pytest.fixture
def admin_user(db_session):
    """Create an admin user"""
    tenant = Tenant(name="Admin Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)

    password_hash = bcrypt.generate_password_hash("adminpassword123").decode('utf-8')
    user = User(
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        password_hash=password_hash,
        tenant_id=tenant.id,
        is_active=True,
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_user(db_session):
    """Create a regular (non-admin) user"""
    tenant = Tenant(name="Regular Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)

    password_hash = bcrypt.generate_password_hash("userpassword123").decode('utf-8')
    user = User(
        email="user@example.com",
        first_name="Regular",
        last_name="User",
        password_hash=password_hash,
        tenant_id=tenant.id,
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_tenant(db_session):
    """Create a test tenant"""
    tenant = Tenant(name="Test Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def another_tenant(db_session):
    """Create another test tenant"""
    tenant = Tenant(name="Another Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


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


class TestCreateTenant:
    """Tests for POST /api/tenants"""

    @patch('app.api.tenants.tenants.create_tenant')
    def test_create_tenant_success(self, mock_create_tenant, client, admin_headers):
        """Test successfully creating a tenant"""
        tenant = Tenant(name="New Tenant")
        invitation = TenantInvitation(
            invitation_code="test-invitation-code-12345",
            tenant_id=1,
            is_used=False,
            expires_at=None
        )

        mock_create_tenant.return_value = {
            'status': 'success',
            'message': 'Tenant created successfully',
            'tenant': tenant,
            'invitation': invitation
        }

        response = client.post('/api/tenants', json={'name': 'New Tenant'}, headers=admin_headers)

        assert response.status_code == 201
        data = response.get_json()
        assert 'tenant' in data
        assert 'invitation' in data
        assert data['tenant']['name'] == tenant.name

    def test_create_tenant_missing_data(self, client, admin_headers):
        """Test creating tenant with empty body"""
        response = client.post('/api/tenants', json={}, headers=admin_headers)

        assert response.status_code == 400
        assert response.get_json()['error'] == 'No data provided'

    @patch('app.api.tenants.tenants.create_tenant')
    def test_create_tenant_duplicate_name(self, mock_create_tenant, client, admin_headers):
        """Test creating tenant with duplicate name is rejected"""
        mock_create_tenant.return_value = {
            'status': 'error',
            'message': 'Tenant with name "Existing Tenant" already exists',
            'tenant': None,
            'invitation': None
        }

        response = client.post('/api/tenants', json={'name': 'Existing Tenant'}, headers=admin_headers)

        assert response.status_code == 409
        assert 'Existing Tenant' in response.get_json()['error']

    def test_create_tenant_requires_auth(self, client):
        """Test that creating tenant requires authentication"""
        response = client.post('/api/tenants', json={'name': 'New Tenant'})

        assert response.status_code == 401

    def test_create_tenant_requires_admin(self, client, regular_headers):
        """Test that creating tenant requires admin access"""
        response = client.post('/api/tenants', json={'name': 'New Tenant'},
                               headers=regular_headers)

        assert response.status_code == 403
        assert 'Admin access required' in response.get_json()['error']


class TestGetAllTenants:
    """Tests for GET /api/tenants"""

    def test_get_all_tenants_success(self, client, admin_headers, test_tenant, another_tenant):
        """Test successfully getting all tenants"""
        response = client.get('/api/tenants', headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'tenants' in data
        tenant_ids = {t['id'] for t in data['tenants']}
        assert test_tenant.id in tenant_ids
        assert another_tenant.id in tenant_ids

    def test_get_all_tenants_requires_auth(self, client):
        """Test that getting tenants requires authentication"""
        response = client.get('/api/tenants')

        assert response.status_code == 401

    def test_get_all_tenants_requires_admin(self, client, regular_headers):
        """Test that getting tenants requires admin access"""
        response = client.get('/api/tenants', headers=regular_headers)

        assert response.status_code == 403
        assert 'Admin access required' in response.get_json()['error']


class TestGetTenant:
    """Tests for GET /api/tenants/<id>"""

    def test_get_tenant_success(self, client, admin_headers, test_tenant):
        """Test successfully getting a tenant by ID"""
        response = client.get(f'/api/tenants/{test_tenant.id}', headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == test_tenant.id
        assert data['name'] == test_tenant.name

    def test_get_tenant_not_found(self, client, admin_headers):
        """Test getting a non-existent tenant returns 404"""
        response = client.get('/api/tenants/99999', headers=admin_headers)

        assert response.status_code == 404
        assert 'Tenant not found' in response.get_json()['error']


class TestUpdateTenant:
    """Tests for PUT /api/tenants/<id>"""

    def test_update_tenant_success(self, client, admin_headers, test_tenant):
        """Test successfully updating a tenant"""
        response = client.put(f'/api/tenants/{test_tenant.id}',
                              json={'name': 'Updated Tenant Name'}, headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['tenant']['name'] == 'Updated Tenant Name'

    def test_update_tenant_not_found(self, client, admin_headers):
        """Test updating a non-existent tenant returns 404"""
        response = client.put('/api/tenants/99999', json={'name': 'Updated'}, headers=admin_headers)

        assert response.status_code == 404
        assert 'Tenant not found' in response.get_json()['error']

    def test_update_tenant_no_data(self, client, admin_headers, test_tenant):
        """Test updating tenant with empty body"""
        response = client.put(f'/api/tenants/{test_tenant.id}', json={}, headers=admin_headers)

        assert response.status_code == 400
        assert response.get_json()['error'] == 'No data provided'

    def test_update_tenant_duplicate_name(self, client, admin_headers, test_tenant, another_tenant):
        """Test updating tenant with a name that belongs to another tenant"""
        response = client.put(f'/api/tenants/{test_tenant.id}',
                              json={'name': another_tenant.name}, headers=admin_headers)

        assert response.status_code == 400
        assert 'Tenant with this name already exists' in response.get_json()['error']

    def test_update_tenant_requires_admin(self, client, regular_headers, test_tenant):
        """Test that updating tenant requires admin access"""
        response = client.put(f'/api/tenants/{test_tenant.id}',
                              json={'name': 'Updated'}, headers=regular_headers)

        assert response.status_code == 403
        assert 'Admin access required' in response.get_json()['error']


class TestDeleteTenant:
    """Tests for DELETE /api/tenants/<id>"""

    def test_delete_tenant_success(self, client, admin_headers, db_session):
        """Test successfully deleting a tenant"""
        tenant = Tenant(name="To Delete")
        db_session.add(tenant)
        db_session.commit()
        db_session.refresh(tenant)

        response = client.delete(f'/api/tenants/{tenant.id}', headers=admin_headers)

        assert response.status_code == 200
        assert response.get_json()['status'] == 'success'

        from app.repository.tenant_repository import TenantRepository
        assert TenantRepository().get_by_id(tenant.id) is None

    def test_delete_tenant_not_found(self, client, admin_headers):
        """Test deleting a non-existent tenant returns 404"""
        response = client.delete('/api/tenants/99999', headers=admin_headers)

        assert response.status_code == 404
        assert 'Tenant not found' in response.get_json()['error']

    def test_delete_tenant_with_users(self, client, admin_headers, test_tenant, db_session):
        """Test that tenant with users cannot be deleted"""
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

        response = client.delete(f'/api/tenants/{test_tenant.id}', headers=admin_headers)

        assert response.status_code == 400
        assert 'Cannot delete tenant with associated users' in response.get_json()['error']

    def test_delete_tenant_requires_admin(self, client, regular_headers, test_tenant):
        """Test that deleting tenant requires admin access"""
        response = client.delete(f'/api/tenants/{test_tenant.id}', headers=regular_headers)

        assert response.status_code == 403
        assert 'Admin access required' in response.get_json()['error']
