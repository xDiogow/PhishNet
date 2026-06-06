"""Tests for Template API endpoints"""
import pytest
from flask_jwt_extended import create_access_token

from app.extensions import bcrypt
from app.models import User, Tenant, Template


@pytest.fixture
def test_tenant(db_session):
    tenant = Tenant(name="Test Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def admin_user(db_session, test_tenant):
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
def test_template(db_session, admin_user):
    template = Template(
        name="Test Template",
        subject="Test Subject",
        email_html="<html>Email content</html>",
        landing_page_html="<html><form action='{{FORM_ACTION}}'></form></html>",
        created_by_user_id=admin_user.id
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template


@pytest.fixture
def admin_headers(admin_user):
    token = create_access_token(identity=str(admin_user.id))
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def regular_headers(regular_user):
    token = create_access_token(identity=str(regular_user.id))
    return {'Authorization': f'Bearer {token}'}


class TestGetAllTemplates:
    """EF07 — template listing"""

    def test_get_all_templates_success(self, client, regular_headers, test_template):
        response = client.get('/api/templates', headers=regular_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert 'templates' in data
        assert len(data['templates']) == 1
        assert data['templates'][0]['id'] == test_template.id
        assert data['templates'][0]['name'] == test_template.name

    def test_get_all_templates_requires_auth(self, client):
        response = client.get('/api/templates')
        assert response.status_code == 401


class TestGetTemplate:
    """EF07 — template detail (admin only)"""

    def test_get_template_success(self, client, admin_headers, test_template):
        response = client.get(f'/api/templates/{test_template.id}', headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == test_template.id
        assert 'email_template' in data
        assert data['email_template']['subject'] == test_template.subject
        assert 'landing_page' in data

    def test_get_template_not_found(self, client, admin_headers):
        response = client.get('/api/templates/99999', headers=admin_headers)
        assert response.status_code == 404

    def test_get_template_requires_auth(self, client, test_template):
        response = client.get(f'/api/templates/{test_template.id}')
        assert response.status_code == 401

    def test_get_template_requires_admin(self, client, regular_headers, test_template):
        response = client.get(f'/api/templates/{test_template.id}', headers=regular_headers)
        assert response.status_code == 403
        assert 'Admin access required' in response.get_json()['error']


class TestCreateTemplate:
    """EF07 — template creation with HTML email and landing page (admin only)"""

    def test_create_template_success(self, client, admin_headers):
        template_data = {
            'name': 'New Template',
            'email_template_data': {
                'subject': 'Test Subject',
                'html': '<html>Email content</html>'
            },
            'landing_page_data': {
                'html': '<html>Landing page</html>'
            }
        }

        response = client.post('/api/templates', json=template_data, headers=admin_headers)

        assert response.status_code == 201
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['template']['name'] == 'New Template'
        assert data['template']['email_template']['subject'] == 'Test Subject'

    def test_create_template_missing_data(self, client, admin_headers):
        response = client.post('/api/templates', json={}, headers=admin_headers)
        assert response.status_code == 400

    def test_create_template_missing_subject(self, client, admin_headers):
        response = client.post('/api/templates', json={
            'name': 'Test',
            'email_template_data': {'html': '<html/>'},
            'landing_page_data': {'html': '<html/>'}
        }, headers=admin_headers)
        assert response.status_code == 400

    def test_create_template_requires_auth(self, client):
        response = client.post('/api/templates', json={
            'name': 'Test',
            'email_template_data': {'subject': 'S', 'html': '<html/>'},
            'landing_page_data': {'html': '<html/>'}
        })
        assert response.status_code == 401

    def test_create_template_requires_admin(self, client, regular_headers):
        response = client.post('/api/templates', json={
            'name': 'Test',
            'email_template_data': {'subject': 'S', 'html': '<html/>'},
            'landing_page_data': {'html': '<html/>'}
        }, headers=regular_headers)
        assert response.status_code == 403
        assert 'Admin access required' in response.get_json()['error']


class TestUpdateTemplate:
    """EF07 — template update (admin only)"""

    def test_update_template_name(self, client, admin_headers, test_template):
        response = client.put(f'/api/templates/{test_template.id}',
                              json={'name': 'Updated Name'},
                              headers=admin_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['template']['name'] == 'Updated Name'

    def test_update_template_email(self, client, admin_headers, test_template):
        response = client.put(f'/api/templates/{test_template.id}',
                              json={'email_template_data': {'subject': 'New Subject', 'html': '<html>new</html>'}},
                              headers=admin_headers)

        assert response.status_code == 200
        assert response.get_json()['template']['email_template']['subject'] == 'New Subject'

    def test_update_template_no_data(self, client, admin_headers, test_template):
        response = client.put(f'/api/templates/{test_template.id}',
                              json={}, headers=admin_headers)
        assert response.status_code == 400

    def test_update_template_requires_admin(self, client, regular_headers, test_template):
        response = client.put(f'/api/templates/{test_template.id}',
                              json={'name': 'Updated'}, headers=regular_headers)
        assert response.status_code == 403


class TestDeleteTemplate:
    """EF07 — template deletion (admin only)"""

    def test_delete_template_success(self, client, admin_headers, test_template):
        response = client.delete(f'/api/templates/{test_template.id}', headers=admin_headers)

        assert response.status_code == 200
        assert response.get_json()['status'] == 'success'

    def test_delete_template_not_found(self, client, admin_headers):
        response = client.delete('/api/templates/99999', headers=admin_headers)
        assert response.status_code == 404

    def test_delete_template_requires_auth(self, client, test_template):
        response = client.delete(f'/api/templates/{test_template.id}')
        assert response.status_code == 401

    def test_delete_template_requires_admin(self, client, regular_headers, test_template):
        response = client.delete(f'/api/templates/{test_template.id}', headers=regular_headers)
        assert response.status_code == 403
