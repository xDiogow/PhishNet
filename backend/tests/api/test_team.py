"""
Tests for Team API endpoints
"""
import pytest
from flask_jwt_extended import create_access_token

from datetime import datetime, timezone

from app.extensions import bcrypt
from app.models import User, Tenant, Target, Campaign, CampaignStatus, CampaignResult, Template
from app.models.user_permission import ALL_PERMISSIONS
from app.repository.user_permission_repository import UserPermissionRepository


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
    UserPermissionRepository().grant_all(user.id, test_tenant.id, ALL_PERMISSIONS)
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
    """Create a user from another tenant with full permissions in their tenant"""
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
    UserPermissionRepository().grant_all(user.id, another_tenant.id, ALL_PERMISSIONS)
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
    """Tests for GET /api/team — EF06 (target management), EF17 (tenant isolation)"""

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
        assert 'manage_team' in members[operator_user.id]['permissions']
        assert members[test_user.id]['permissions'] == []


class TestGdprEraseTarget:
    """EF16 — GDPR Art. 17 right to erasure: PII anonymization + target deletion"""

    @pytest.fixture
    def target(self, db_session, test_tenant):
        t = Target(
            email="victim@example.com",
            first_name="Jean",
            last_name="Dupont",
            position="Engineer",
            tenant_id=test_tenant.id,
        )
        db_session.add(t)
        db_session.commit()
        db_session.refresh(t)
        return t

    @pytest.fixture
    def campaign_with_result(self, db_session, test_tenant, test_user, target):
        """Campaign result linked to the target's email."""
        tmpl = Template(
            name="GDPR Template",
            subject="Test",
            email_html="<p>test</p>",
            landing_page_html="<p>test</p>",
            created_by_user_id=test_user.id,
        )
        db_session.add(tmpl)
        db_session.commit()
        db_session.refresh(tmpl)

        campaign = Campaign(
            name="GDPR Campaign",
            tenant_id=test_tenant.id,
            template_id=tmpl.id,
            created_by_user_id=test_user.id,
            status=CampaignStatus.RUNNING,
            launched_at=datetime.now(timezone.utc),
        )
        db_session.add(campaign)
        db_session.commit()
        db_session.refresh(campaign)

        result = CampaignResult(
            campaign_id=campaign.id,
            email=target.email,
            first_name=target.first_name,
            last_name=target.last_name,
            position=target.position,
            tracking_token="gdpr-test-token-unique-1234",
            status="Sent",
            sent_at=datetime.now(timezone.utc),
        )
        db_session.add(result)
        db_session.commit()
        db_session.refresh(result)
        return result

    def test_gdpr_erase_deletes_target(self, client, operator_auth_headers, target, db_session):
        response = client.delete(
            f"/api/team/targets/{target.id}/gdpr",
            headers=operator_auth_headers,
        )

        assert response.status_code == 200
        deleted = db_session.get(Target, target.id)
        assert deleted is None

    def test_gdpr_erase_anonymizes_pii_in_campaign_results(
        self, client, operator_auth_headers, target, campaign_with_result, db_session
    ):
        client.delete(f"/api/team/targets/{target.id}/gdpr", headers=operator_auth_headers)

        db_session.expire_all()
        result = db_session.get(CampaignResult, campaign_with_result.id)
        assert result.email != "victim@example.com"
        assert result.first_name != "Jean"
        assert result.last_name != "Dupont"

    def test_gdpr_erase_reports_anonymized_count(
        self, client, operator_auth_headers, target, campaign_with_result
    ):
        response = client.delete(
            f"/api/team/targets/{target.id}/gdpr", headers=operator_auth_headers
        )

        data = response.get_json()
        assert "anonymized_results" in data
        assert data["anonymized_results"] >= 1

    def test_gdpr_erase_tenant_isolation(self, client, another_auth_headers, target):
        """EF17 — cannot erase a target belonging to another tenant"""
        response = client.delete(
            f"/api/team/targets/{target.id}/gdpr",
            headers=another_auth_headers,
        )

        assert response.status_code == 404

    def test_gdpr_erase_requires_auth(self, client, target):
        response = client.delete(f"/api/team/targets/{target.id}/gdpr")
        assert response.status_code == 401
