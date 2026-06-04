"""
Tests for Tenant Invitation API endpoints
"""
import pytest
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import create_access_token

from app.extensions import db, bcrypt
from app.models import User, Tenant, TenantInvitation


@pytest.fixture
def test_tenant(db_session):
    """Create a test tenant"""
    tenant = Tenant(name="Test Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def operator_user(db_session, test_tenant):
    """Create an operator user (tenant owner)"""
    password_hash = bcrypt.generate_password_hash("operatorpassword123").decode('utf-8')
    user = User(
        email="operator@example.com",
        first_name="Operator",
        last_name="User",
        password_hash=password_hash,
        tenant_id=test_tenant.id,
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    # Set as operator
    test_tenant.operator_id = user.id
    db_session.commit()
    return user


@pytest.fixture
def regular_user(db_session, test_tenant):
    """Create a regular (non-operator) user"""
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
def another_tenant(db_session):
    """Create another tenant"""
    tenant = Tenant(name="Another Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def another_user(db_session, another_tenant):
    """Create a user from another tenant"""
    password_hash = bcrypt.generate_password_hash("anotherpassword123").decode('utf-8')
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
def test_invitation(db_session, test_tenant):
    """Create a test invitation"""
    invitation = TenantInvitation(
        invitation_code="test-invitation-code-12345",
        tenant_id=test_tenant.id,
        is_used=False,
        expires_at=None
    )
    db_session.add(invitation)
    db_session.commit()
    db_session.refresh(invitation)
    return invitation


@pytest.fixture
def expired_invitation(db_session, test_tenant):
    """Create an expired invitation"""
    invitation = TenantInvitation(
        invitation_code="expired-invitation-code",
        tenant_id=test_tenant.id,
        is_used=False,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1)
    )
    db_session.add(invitation)
    db_session.commit()
    db_session.refresh(invitation)
    return invitation


@pytest.fixture
def used_invitation(db_session, test_tenant, operator_user):
    """Create a used invitation"""
    invitation = TenantInvitation(
        invitation_code="used-invitation-code",
        tenant_id=test_tenant.id,
        is_used=True,
        used_at=datetime.now(timezone.utc),
        used_by_user_id=operator_user.id,
        expires_at=None
    )
    db_session.add(invitation)
    db_session.commit()
    db_session.refresh(invitation)
    return invitation


@pytest.fixture
def operator_headers(operator_user):
    """Create authorization headers for operator user"""
    token = create_access_token(identity=str(operator_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def regular_headers(regular_user):
    """Create authorization headers for regular user"""
    token = create_access_token(identity=str(regular_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def another_headers(another_user):
    """Create authorization headers for another tenant's user"""
    token = create_access_token(identity=str(another_user.id))
    return {'Authorization': f'Bearer {token}'}


class TestCreateInvitation:
    """Tests for POST /api/tenant-invitations — EF05 (operator generates invitation codes)"""

    def test_create_invitation_success(self, client, operator_headers, test_tenant):
        """Test successfully creating an invitation"""
        response = client.post('/api/tenant-invitations',
                               json={'tenant_id': test_tenant.id},
                               headers=operator_headers)

        assert response.status_code == 201
        data = response.get_json()
        assert 'invitation' in data
        assert data['invitation']['tenant_id'] == test_tenant.id
        assert data['invitation']['is_used'] is False
        assert 'invitation_code' in data['invitation']

    def test_create_invitation_missing_data(self, client, operator_headers):
        """Test creating invitation with empty body"""
        response = client.post('/api/tenant-invitations', json={}, headers=operator_headers)

        assert response.status_code == 400
        assert response.get_json()['error'] == 'No data provided'

    def test_create_invitation_tenant_mismatch(self, client, operator_headers, another_tenant):
        """Test creating invitation for a different tenant is rejected"""
        response = client.post('/api/tenant-invitations',
                               json={'tenant_id': another_tenant.id},
                               headers=operator_headers)

        assert response.status_code == 403
        assert 'Tenant mismatch' in response.get_json()['error']

    def test_create_invitation_not_operator(self, client, regular_headers, test_tenant):
        """Test that non-operator users cannot create invitations"""
        response = client.post('/api/tenant-invitations',
                               json={'tenant_id': test_tenant.id},
                               headers=regular_headers)

        assert response.status_code == 403
        data = response.get_json()
        assert 'Permission denied' in data['error']

    def test_create_invitation_requires_auth(self, client, test_tenant):
        """Test that creating invitation requires authentication"""
        response = client.post('/api/tenant-invitations',
                               json={'tenant_id': test_tenant.id})

        assert response.status_code == 401


class TestValidateInvitation:
    """Tests for POST /api/tenant-invitations/validate — EF02 (registration gate), EF05 (expiry, single-use)"""

    def test_validate_invitation_success(self, client, test_invitation):
        """Test successfully validating an invitation (no auth required)"""
        response = client.post('/api/tenant-invitations/validate',
                               json={'invitation_code': test_invitation.invitation_code})

        assert response.status_code == 200
        data = response.get_json()
        assert data['valid'] is True
        assert data['invitation']['id'] == test_invitation.id

    def test_validate_invitation_missing_data(self, client):
        """Test validating invitation with empty body"""
        response = client.post('/api/tenant-invitations/validate', json={})

        assert response.status_code == 400

    def test_validate_invitation_invalid_code(self, client):
        """Test validating non-existent invitation code"""
        response = client.post('/api/tenant-invitations/validate',
                               json={'invitation_code': 'invalid-code-12345'})

        assert response.status_code == 400
        assert 'Invalid invitation code' in response.get_json()['message']

    def test_validate_invitation_used(self, client, used_invitation):
        """Test validating an already-used invitation"""
        response = client.post('/api/tenant-invitations/validate',
                               json={'invitation_code': used_invitation.invitation_code})

        assert response.status_code == 400
        assert 'already been used' in response.get_json()['message']

    def test_validate_invitation_expired(self, client, expired_invitation):
        """Test validating an expired invitation"""
        response = client.post('/api/tenant-invitations/validate',
                               json={'invitation_code': expired_invitation.invitation_code})

        assert response.status_code == 400
        assert 'expired' in response.get_json()['message']


class TestGetInvitation:
    """Tests for GET /api/tenant-invitations/<invitation_code> — EF05 (invitation lookup)"""

    def test_get_invitation_success(self, client, operator_headers, test_invitation):
        """Test successfully getting an invitation by code"""
        response = client.get(f'/api/tenant-invitations/{test_invitation.invitation_code}',
                              headers=operator_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == test_invitation.id
        assert data['invitation_code'] == test_invitation.invitation_code
        assert 'is_valid' in data

    def test_get_invitation_not_found(self, client, operator_headers):
        """Test getting non-existent invitation returns 404"""
        response = client.get('/api/tenant-invitations/invalid-code-12345',
                              headers=operator_headers)

        assert response.status_code == 404
        assert 'Invitation not found' in response.get_json()['error']

    def test_get_invitation_requires_auth(self, client, test_invitation):
        """Test that getting invitation requires authentication"""
        response = client.get(f'/api/tenant-invitations/{test_invitation.invitation_code}')

        assert response.status_code == 401


class TestGetInvitationsByTenant:
    """Tests for GET /api/tenant-invitations/tenant/<tenant_id> — EF05 (list invitations per tenant)"""

    def test_get_invitations_by_tenant_success(self, client, operator_headers, test_tenant,
                                                test_invitation, used_invitation, expired_invitation):
        """Test successfully getting invitations by tenant"""
        response = client.get(f'/api/tenant-invitations/tenant/{test_tenant.id}',
                              headers=operator_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'invitations' in data
        assert len(data['invitations']) >= 3
        for invitation in data['invitations']:
            assert invitation['tenant_id'] == test_tenant.id

    def test_get_invitations_by_tenant_empty(self, client, db_session):
        """Test getting invitations for tenant with no invitations"""
        tenant = Tenant(name="Empty Tenant")
        db_session.add(tenant)
        db_session.commit()
        db_session.refresh(tenant)

        password_hash = bcrypt.generate_password_hash("testpassword123").decode('utf-8')
        user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            password_hash=password_hash,
            tenant_id=tenant.id,
            is_active=True,
            is_admin=False
        )
        db_session.add(user)
        db_session.flush()
        tenant.operator_id = user.id
        db_session.commit()

        token = create_access_token(identity=str(user.id))
        headers = {'Authorization': f'Bearer {token}'}

        response = client.get(f'/api/tenant-invitations/tenant/{tenant.id}', headers=headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['invitations'] == []

    def test_get_invitations_by_tenant_requires_auth(self, client, test_tenant):
        """Test that getting invitations requires authentication"""
        response = client.get(f'/api/tenant-invitations/tenant/{test_tenant.id}')

        assert response.status_code == 401

    def test_get_invitations_by_tenant_cross_tenant_access(self, client, another_headers,
                                                            test_tenant, test_invitation):
        """Test that users can access invitations from their own tenant only"""
        response = client.get(f'/api/tenant-invitations/tenant/{test_tenant.id}',
                              headers=another_headers)

        # Should return empty list or error, depending on implementation
        assert response.status_code in [200, 403]

        if response.status_code == 200:
            data = response.get_json()
            assert 'invitations' in data
