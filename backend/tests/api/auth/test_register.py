"""
Tests for Register API endpoint
"""
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

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
def valid_invitation(db_session, test_tenant):
    """Create a valid invitation"""
    invitation = TenantInvitation(
        invitation_code="valid-invitation-code-12345",
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
def used_invitation(db_session, test_tenant):
    """Create a used invitation"""
    invitation = TenantInvitation(
        invitation_code="used-invitation-code",
        tenant_id=test_tenant.id,
        is_used=True,
        used_at=datetime.now(timezone.utc),
        used_by_user_id=1,
        expires_at=None
    )
    db_session.add(invitation)
    db_session.commit()
    db_session.refresh(invitation)
    return invitation


@pytest.fixture
def existing_user(db_session, test_tenant):
    """Create an existing user"""
    password_hash = bcrypt.generate_password_hash("existingpassword123").decode('utf-8')
    user = User(
        email="existing@example.com",
        first_name="Existing",
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


class TestRegister:
    """Tests for POST /api/auth/register — EF02 (invitation code), EF03 (rate limiting), EF17 (tenant isolation)"""

    def test_register_success(self, client, db_session, test_tenant, valid_invitation):
        """Test successfully registering a user"""
        # Pre-create a user so count() != 0 — the registered user should not become admin
        existing = User(
            email='existing@example.com',
            first_name='Existing',
            last_name='User',
            password_hash=bcrypt.generate_password_hash('password').decode('utf-8'),
            tenant_id=test_tenant.id,
            is_active=True,
            is_admin=True,
        )
        db_session.add(existing)
        db_session.commit()

        register_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': valid_invitation.invitation_code
        }

        response = client.post('/api/auth/register', json=register_data)

        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User registered successfully'
        assert 'access_token' in data
        assert data['user']['email'] == register_data['email']
        assert data['user']['tenant_id'] == test_tenant.id
        assert data['user']['is_admin'] is False

    def test_register_missing_data(self, client):
        """Test register with empty body"""
        response = client.post('/api/auth/register', json={})

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_register_invalid_invitation_code(self, client):
        """Test register with non-existent invitation code"""
        register_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': 'invalid-code-12345'
        }

        response = client.post('/api/auth/register', json=register_data)

        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid invitation code' in data['message']

    def test_register_expired_invitation(self, client, expired_invitation):
        """Test register with expired invitation is rejected"""
        register_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': expired_invitation.invitation_code
        }

        response = client.post('/api/auth/register', json=register_data)

        assert response.status_code == 400
        data = response.get_json()
        assert 'expired' in data['message']

    def test_register_used_invitation(self, client, used_invitation):
        """Test register with already-used invitation is rejected"""
        register_data = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': used_invitation.invitation_code
        }

        response = client.post('/api/auth/register', json=register_data)

        assert response.status_code == 400
        data = response.get_json()
        assert 'already been used' in data['message']

    def test_register_duplicate_email(self, client, valid_invitation, existing_user):
        """Test register with duplicate email is rejected"""
        register_data = {
            'email': existing_user.email,
            'first_name': 'New',
            'last_name': 'User',
            'password': 'password123',
            'invitation_code': valid_invitation.invitation_code
        }

        response = client.post('/api/auth/register', json=register_data)

        assert response.status_code == 409
        data = response.get_json()
        assert 'User with this email already exists' in data['error']
