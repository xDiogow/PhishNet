"""
Tests for Login API endpoint
"""
import pytest
from flask_jwt_extended import create_access_token

from app.extensions import db, bcrypt
from app.models import User, Tenant


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
    """Create a regular user"""
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
def inactive_user(db_session, test_tenant):
    """Create an inactive user"""
    password_hash = bcrypt.generate_password_hash("inactivepassword123").decode('utf-8')
    user = User(
        email="inactive@example.com",
        first_name="Inactive",
        last_name="User",
        password_hash=password_hash,
        tenant_id=test_tenant.id,
        is_active=False,
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


class TestLogin:
    """Tests for POST /api/auth/login"""

    def test_login_success(self, client, regular_user):
        """Test successfully logging in"""
        login_data = {
            'email': regular_user.email,
            'password': 'userpassword123'
        }

        response = client.post('/api/auth/login', json=login_data)

        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Login successful'
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['email'] == regular_user.email
        assert data['user']['id'] == regular_user.id
        assert 'id' in data['user']
        assert 'first_name' in data['user']
        assert 'last_name' in data['user']
        assert 'tenant_id' in data['user']
        assert 'is_admin' in data['user']
        assert 'is_operator' in data['user']

    def test_login_operator_flag(self, client, operator_user):
        """Test that operator flag is set correctly on login"""
        response = client.post('/api/auth/login', json={
            'email': operator_user.email,
            'password': 'operatorpassword123'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['is_operator'] is True
        assert data['user']['is_admin'] is False

    def test_login_missing_data(self, client):
        """Test login with empty body"""
        response = client.post('/api/auth/login', json={})

        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_login_invalid_credentials(self, client, regular_user):
        """Test login with wrong password"""
        response = client.post('/api/auth/login', json={
            'email': regular_user.email,
            'password': 'wrongpassword'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert 'Invalid credentials' in data['error']

    def test_login_inactive_user(self, client, inactive_user):
        """Test login with inactive user is rejected"""
        response = client.post('/api/auth/login', json={
            'email': inactive_user.email,
            'password': 'inactivepassword123'
        })

        assert response.status_code == 403
        data = response.get_json()
        assert 'User account is inactive' in data['error']

    def test_login_with_wrong_tenant_id(self, client, regular_user, another_tenant):
        """Test login with wrong tenant_id is rejected"""
        response = client.post('/api/auth/login', json={
            'email': regular_user.email,
            'password': 'userpassword123',
            'tenant_id': another_tenant.id
        })

        assert response.status_code == 401
        data = response.get_json()
        assert 'Invalid credentials' in data['error']
