"""
Tests for Team API endpoints
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
def another_tenant(db_session):
    """Create another test tenant for isolation testing"""
    tenant = Tenant(name="Another Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


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
def auth_headers(test_user):
    """Create authorization headers with JWT token"""
    token = create_access_token(identity=str(test_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def operator_auth_headers(operator_user):
    """Create authorization headers for operator user"""
    token = create_access_token(identity=str(operator_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def admin_auth_headers(admin_user):
    """Create authorization headers for admin user"""
    token = create_access_token(identity=str(admin_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def another_auth_headers(another_user):
    """Create authorization headers for another tenant's user"""
    token = create_access_token(identity=str(another_user.id))
    return {'Authorization': f'Bearer {token}'}


class TestGetTeamMembers:
    """Tests for GET /api/team"""

    def test_get_team_members_success(self, client, auth_headers, test_user,
                                       operator_user, admin_user, inactive_user):
        """Test successfully getting team members including inactive users"""
        response = client.get('/api/team', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'team_members' in data
        member_ids = {member['id'] for member in data['team_members']}
        assert test_user.id in member_ids
        assert operator_user.id in member_ids
        assert admin_user.id in member_ids
        assert inactive_user.id in member_ids

    def test_get_team_members_requires_auth(self, client):
        """Test that getting team members requires authentication"""
        response = client.get('/api/team')

        assert response.status_code == 401

    def test_get_team_members_tenant_isolation(self, client, auth_headers, another_auth_headers,
                                                test_user, operator_user, admin_user, inactive_user,
                                                another_user):
        """Test that users only see team members from their own tenant"""
        response = client.get('/api/team', headers=auth_headers)

        assert response.status_code == 200
        member_ids = {m['id'] for m in response.get_json()['team_members']}
        assert another_user.id not in member_ids

        response2 = client.get('/api/team', headers=another_auth_headers)
        assert response2.status_code == 200
        member_ids2 = {m['id'] for m in response2.get_json()['team_members']}
        assert len(member_ids2) == 1
        assert another_user.id in member_ids2

    def test_get_team_members_no_password_hash(self, client, auth_headers, test_user):
        """Test that password hash is not included in response"""
        response = client.get('/api/team', headers=auth_headers)

        assert response.status_code == 200
        for member in response.get_json()['team_members']:
            assert 'password_hash' not in member
            assert 'password' not in member

    def test_get_team_members_operator_status(self, client, operator_auth_headers,
                                               test_user, operator_user):
        """Test that operator status is correctly identified in response"""
        response = client.get('/api/team', headers=operator_auth_headers)

        assert response.status_code == 200
        members = {m['id']: m for m in response.get_json()['team_members']}
        assert members[operator_user.id]['is_operator'] is True
        assert members[test_user.id]['is_operator'] is False
