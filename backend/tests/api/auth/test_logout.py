"""
Tests for POST /api/auth/logout — EF17 (session security), EF01 (authentication)
"""
import pytest
from unittest.mock import patch
from app.extensions import db, bcrypt
from app.models import User, Tenant
from app.repository.session_repository import session_repo


@pytest.fixture
def test_tenant(db_session):
    tenant = Tenant(name="Logout Test Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def regular_user(db_session, test_tenant):
    password_hash = bcrypt.generate_password_hash("password123").decode('utf-8')
    user = User(
        email="logout_user@example.com",
        first_name="Logout",
        last_name="User",
        password_hash=password_hash,
        tenant_id=test_tenant.id,
        is_active=True,
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(client, regular_user):
    response = client.post('/api/auth/login', json={
        'email': 'logout_user@example.com',
        'password': 'password123',
    })
    assert response.status_code == 200
    return response.get_json()['access_token']


class TestLogout:
    """Tests for POST /api/auth/logout"""

    def test_logout_without_token_returns_401(self, client):
        """Unauthenticated request to /logout must be rejected."""
        response = client.post('/api/auth/logout')
        assert response.status_code == 401

    def test_logout_success(self, client, auth_token):
        """Valid token → HTTP 200 and revoke_token called with a JTI string."""
        with patch.object(session_repo, 'revoke_token') as mock_revoke:
            response = client.post(
                '/api/auth/logout',
                headers={'Authorization': f'Bearer {auth_token}'},
            )
        assert response.status_code == 200
        assert response.get_json()['message'] == 'Successfully logged out'
        mock_revoke.assert_called_once()
        jti_arg, ttl_arg = mock_revoke.call_args[0]
        assert isinstance(jti_arg, str) and len(jti_arg) > 0
        assert ttl_arg > 0

    def test_revoked_token_blocked(self, client, app, auth_token):
        """After logout a revoked token must be rejected with HTTP 401."""
        revoked: set = set()

        with patch.object(session_repo, 'revoke_token', side_effect=lambda jti, ttl: revoked.add(jti)), \
             patch.object(session_repo, 'is_token_revoked', side_effect=lambda jti: jti in revoked), \
             patch.dict(app.config, {'SESSION_BLOCKLIST_ENABLED': True}):

            logout_resp = client.post(
                '/api/auth/logout',
                headers={'Authorization': f'Bearer {auth_token}'},
            )
            assert logout_resp.status_code == 200

            protected_resp = client.get(
                '/api/campaigns',
                headers={'Authorization': f'Bearer {auth_token}'},
            )
            assert protected_resp.status_code == 401

    def test_valid_token_still_works_before_logout(self, client, auth_token):
        """A token that has NOT been revoked must still grant access."""
        with patch.object(session_repo, 'is_token_revoked', return_value=False), \
             patch.dict({}, {}):
            response = client.get(
                '/api/campaigns',
                headers={'Authorization': f'Bearer {auth_token}'},
            )
        assert response.status_code == 200
