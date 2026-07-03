"""Tests for Template API endpoints — EF07 (template management)"""
import pytest
from flask_jwt_extended import create_access_token

from app.extensions import bcrypt, db
from app.models import User, Tenant, Template
from app.models.campaign import Campaign, CampaignStatus
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
def other_tenant(db_session):
    tenant = Tenant(name="Other Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def admin_user(db_session, test_tenant):
    """Platform admin (is_admin=True) — creates global templates."""
    password_hash = bcrypt.generate_password_hash("adminpassword123").decode('utf-8')
    user = User(
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        password_hash=password_hash,
        tenant_id=test_tenant.id,
        is_active=True,
        is_admin=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def regular_user(db_session, test_tenant):
    """Tenant user with no permissions."""
    password_hash = bcrypt.generate_password_hash("userpassword123").decode('utf-8')
    user = User(
        email="user@example.com",
        first_name="Regular",
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
def operator_user(db_session, test_tenant):
    """Tenant user with manage_templates permission."""
    password_hash = bcrypt.generate_password_hash("oppassword123").decode('utf-8')
    user = User(
        email="operator@example.com",
        first_name="Operator",
        last_name="User",
        password_hash=password_hash,
        tenant_id=test_tenant.id,
        is_active=True,
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    UserPermissionRepository().grant_all(user.id, test_tenant.id, ALL_PERMISSIONS)
    return user


@pytest.fixture
def other_operator(db_session, other_tenant):
    """Operator in a different tenant."""
    password_hash = bcrypt.generate_password_hash("otherpassword123").decode('utf-8')
    user = User(
        email="other@example.com",
        first_name="Other",
        last_name="Operator",
        password_hash=password_hash,
        tenant_id=other_tenant.id,
        is_active=True,
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    UserPermissionRepository().grant_all(user.id, other_tenant.id, ALL_PERMISSIONS)
    return user


@pytest.fixture
def global_template(db_session, admin_user):
    """Platform template (tenant_id=None), editable only by platform admin."""
    template = Template(
        name="Global Template",
        subject="Global Subject",
        email_html="<html>Global email</html>",
        landing_page_html="<html><form action='{{FORM_ACTION}}'></form></html>",
        tenant_id=None,
        created_by_user_id=admin_user.id,
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template


@pytest.fixture
def tenant_template(db_session, operator_user, test_tenant):
    """Tenant-private template."""
    template = Template(
        name="Tenant Template",
        subject="Tenant Subject",
        email_html="<html>Tenant email</html>",
        landing_page_html="<html><form action='{{FORM_ACTION}}'></form></html>",
        tenant_id=test_tenant.id,
        created_by_user_id=operator_user.id,
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template


# Alias for backwards-compat with campaign tests that use test_template
@pytest.fixture
def test_template(global_template):
    return global_template


@pytest.fixture
def admin_headers(admin_user):
    token = create_access_token(identity=str(admin_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def regular_headers(regular_user):
    token = create_access_token(identity=str(regular_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def operator_headers(operator_user):
    token = create_access_token(identity=str(operator_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def other_operator_headers(other_operator):
    token = create_access_token(identity=str(other_operator.id))
    return {'Authorization': f'Bearer {token}'}


class TestGetAllTemplates:
    """EF07 — template listing: global + tenant's own, not other tenants'."""

    def test_see_global_templates(self, client, regular_headers, global_template):
        response = client.get('/api/templates', headers=regular_headers)
        assert response.status_code == 200
        ids = [t['id'] for t in response.get_json()['templates']]
        assert global_template.id in ids

    def test_see_own_tenant_templates(self, client, operator_headers, global_template, tenant_template):
        response = client.get('/api/templates', headers=operator_headers)
        assert response.status_code == 200
        ids = [t['id'] for t in response.get_json()['templates']]
        assert global_template.id in ids
        assert tenant_template.id in ids

    def test_cannot_see_other_tenant_templates(self, client, other_operator_headers, tenant_template):
        """Tenant isolation — other tenant's private template must not appear."""
        response = client.get('/api/templates', headers=other_operator_headers)
        assert response.status_code == 200
        ids = [t['id'] for t in response.get_json()['templates']]
        assert tenant_template.id not in ids

    def test_is_global_flag(self, client, operator_headers, global_template, tenant_template):
        response = client.get('/api/templates', headers=operator_headers)
        data = {t['id']: t for t in response.get_json()['templates']}
        assert data[global_template.id]['is_global'] is True
        assert data[tenant_template.id]['is_global'] is False

    def test_requires_auth(self, client):
        assert client.get('/api/templates').status_code == 401


class TestGetTemplate:
    """EF07 — template detail."""

    def test_admin_gets_global_template(self, client, admin_headers, global_template):
        response = client.get(f'/api/templates/{global_template.id}', headers=admin_headers)
        assert response.status_code == 200
        assert response.get_json()['id'] == global_template.id

    def test_operator_gets_global_template(self, client, operator_headers, global_template):
        response = client.get(f'/api/templates/{global_template.id}', headers=operator_headers)
        assert response.status_code == 200

    def test_operator_gets_own_tenant_template(self, client, operator_headers, tenant_template):
        response = client.get(f'/api/templates/{tenant_template.id}', headers=operator_headers)
        assert response.status_code == 200

    def test_other_tenant_cannot_get_tenant_template(self, client, other_operator_headers, tenant_template):
        response = client.get(f'/api/templates/{tenant_template.id}', headers=other_operator_headers)
        assert response.status_code == 404

    def test_no_permission_returns_403(self, client, regular_headers, global_template):
        response = client.get(f'/api/templates/{global_template.id}', headers=regular_headers)
        assert response.status_code == 403
        assert 'Permission denied' in response.get_json()['error']

    def test_not_found(self, client, admin_headers):
        assert client.get('/api/templates/99999', headers=admin_headers).status_code == 404

    def test_requires_auth(self, client, global_template):
        assert client.get(f'/api/templates/{global_template.id}').status_code == 401


class TestCreateTemplate:
    """EF07 — template creation."""

    PAYLOAD = {
        'name': 'New Template',
        'email_template_data': {'subject': 'Test Subject', 'html': '<html>Email</html>'},
        'landing_page_data': {'html': '<html>Landing</html>'},
    }

    def test_admin_creates_global_template(self, client, admin_headers):
        response = client.post('/api/templates', json=self.PAYLOAD, headers=admin_headers)
        assert response.status_code == 201
        t = response.get_json()['template']
        assert t['name'] == 'New Template'
        assert t['is_global'] is True
        assert t['tenant_id'] is None

    def test_operator_creates_tenant_template(self, client, operator_headers, test_tenant):
        response = client.post('/api/templates', json=self.PAYLOAD, headers=operator_headers)
        assert response.status_code == 201
        t = response.get_json()['template']
        assert t['is_global'] is False
        assert t['tenant_id'] == test_tenant.id

    def test_no_permission_returns_403(self, client, regular_headers):
        response = client.post('/api/templates', json=self.PAYLOAD, headers=regular_headers)
        assert response.status_code == 403

    def test_missing_data(self, client, admin_headers):
        assert client.post('/api/templates', json={}, headers=admin_headers).status_code == 400

    def test_missing_subject(self, client, admin_headers):
        payload = {**self.PAYLOAD, 'email_template_data': {'html': '<html/>'}}
        assert client.post('/api/templates', json=payload, headers=admin_headers).status_code == 400

    def test_requires_auth(self, client):
        assert client.post('/api/templates', json=self.PAYLOAD).status_code == 401


@pytest.fixture
def running_campaign(db_session, test_tenant, admin_user, global_template):
    campaign = Campaign(
        name='Active Campaign',
        tenant_id=test_tenant.id,
        template_id=global_template.id,
        status=CampaignStatus.RUNNING,
        created_by_user_id=admin_user.id,
    )
    db_session.add(campaign)
    db_session.commit()
    db_session.refresh(campaign)
    return campaign


class TestUpdateTemplate:
    """EF07 — template update."""

    def test_admin_updates_global_template(self, client, admin_headers, global_template):
        response = client.put(f'/api/templates/{global_template.id}',
                              json={'name': 'Updated'}, headers=admin_headers)
        assert response.status_code == 200
        assert response.get_json()['template']['name'] == 'Updated'

    def test_operator_updates_own_tenant_template(self, client, operator_headers, tenant_template):
        response = client.put(f'/api/templates/{tenant_template.id}',
                              json={'name': 'Updated Tenant'}, headers=operator_headers)
        assert response.status_code == 200

    def test_operator_cannot_update_global_template(self, client, operator_headers, global_template):
        response = client.put(f'/api/templates/{global_template.id}',
                              json={'name': 'Hacked'}, headers=operator_headers)
        assert response.status_code == 403

    def test_other_tenant_cannot_update_tenant_template(self, client, other_operator_headers, tenant_template):
        response = client.put(f'/api/templates/{tenant_template.id}',
                              json={'name': 'Hacked'}, headers=other_operator_headers)
        assert response.status_code == 404

    def test_no_permission_returns_403(self, client, regular_headers, global_template):
        response = client.put(f'/api/templates/{global_template.id}',
                              json={'name': 'x'}, headers=regular_headers)
        assert response.status_code == 403

    def test_no_data_returns_400(self, client, admin_headers, global_template):
        assert client.put(f'/api/templates/{global_template.id}',
                          json={}, headers=admin_headers).status_code == 400

    def test_blocked_while_running(self, client, admin_headers, global_template, running_campaign):
        response = client.put(f'/api/templates/{global_template.id}',
                              json={'name': 'Blocked'}, headers=admin_headers)
        assert response.status_code == 409
        assert 'running campaign' in response.get_json()['error'].lower()

    def test_allowed_after_stopped(self, client, admin_headers, global_template, running_campaign, db_session):
        running_campaign.status = CampaignStatus.STOPPED
        db_session.commit()
        response = client.put(f'/api/templates/{global_template.id}',
                              json={'name': 'Now allowed'}, headers=admin_headers)
        assert response.status_code == 200


class TestDeleteTemplate:
    """EF07 — template deletion."""

    def test_admin_deletes_global_template(self, client, admin_headers, global_template):
        response = client.delete(f'/api/templates/{global_template.id}', headers=admin_headers)
        assert response.status_code == 200

    def test_operator_deletes_own_tenant_template(self, client, operator_headers, tenant_template):
        response = client.delete(f'/api/templates/{tenant_template.id}', headers=operator_headers)
        assert response.status_code == 200

    def test_operator_cannot_delete_global_template(self, client, operator_headers, global_template):
        response = client.delete(f'/api/templates/{global_template.id}', headers=operator_headers)
        assert response.status_code == 403

    def test_other_tenant_cannot_delete_tenant_template(self, client, other_operator_headers, tenant_template):
        response = client.delete(f'/api/templates/{tenant_template.id}', headers=other_operator_headers)
        assert response.status_code == 404

    def test_no_permission_returns_403(self, client, regular_headers, global_template):
        assert client.delete(f'/api/templates/{global_template.id}',
                             headers=regular_headers).status_code == 403

    def test_not_found(self, client, admin_headers):
        assert client.delete('/api/templates/99999', headers=admin_headers).status_code == 404

    def test_requires_auth(self, client, global_template):
        assert client.delete(f'/api/templates/{global_template.id}').status_code == 401

    def test_blocked_while_running(self, client, admin_headers, global_template, running_campaign):
        response = client.delete(f'/api/templates/{global_template.id}', headers=admin_headers)
        assert response.status_code == 409
