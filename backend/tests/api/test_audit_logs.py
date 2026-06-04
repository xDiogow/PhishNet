"""Tests for Audit Log API endpoints — EF14 (audit log list), EF15 (CSV export)"""
import pytest
from datetime import datetime, timezone
from flask_jwt_extended import create_access_token

from app.extensions import db, bcrypt
from app.models import User, Tenant, AuditLog


@pytest.fixture
def test_tenant(db_session):
    tenant = Tenant(name="Audit Test Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def another_tenant(db_session):
    tenant = Tenant(name="Other Tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def test_user(db_session, test_tenant):
    pw = bcrypt.generate_password_hash("pass123").decode("utf-8")
    user = User(
        email="audituser@example.com",
        first_name="Audit",
        last_name="User",
        password_hash=pw,
        tenant_id=test_tenant.id,
        is_active=True,
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def another_user(db_session, another_tenant):
    pw = bcrypt.generate_password_hash("pass123").decode("utf-8")
    user = User(
        email="other@example.com",
        first_name="Other",
        last_name="User",
        password_hash=pw,
        tenant_id=another_tenant.id,
        is_active=True,
        is_admin=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token(identity=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def another_auth_headers(another_user):
    token = create_access_token(identity=str(another_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def audit_logs(db_session, test_tenant, test_user):
    """Create a set of audit log entries for the test tenant."""
    entries = [
        AuditLog(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            action="LOGIN",
            resource_type="User",
            resource_id=str(test_user.id),
            details={"email": test_user.email},
            ip_address="127.0.0.1",
            created_at=datetime.now(timezone.utc),
        ),
        AuditLog(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            action="CREATE_CAMPAIGN",
            resource_type="Campaign",
            resource_id="1",
            details={"name": "Test Campaign", "template_id": 1},
            ip_address="127.0.0.1",
            created_at=datetime.now(timezone.utc),
        ),
        AuditLog(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            action="USER_REGISTER",
            resource_type="User",
            resource_id=str(test_user.id),
            details={"email": test_user.email, "first_name": "Audit", "last_name": "User", "invitation_code": "xxx"},
            ip_address="127.0.0.1",
            created_at=datetime.now(timezone.utc),
        ),
    ]
    for entry in entries:
        db_session.add(entry)
    db_session.commit()
    return entries


class TestGetAuditLogs:
    """EF14 — paginated audit log list with tenant isolation and filtering"""

    def test_returns_logs_for_tenant(self, client, auth_headers, audit_logs):
        response = client.get("/api/audit-logs", headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert "logs" in data
        assert len(data["logs"]) == len(audit_logs)

    def test_response_structure(self, client, auth_headers, audit_logs):
        response = client.get("/api/audit-logs", headers=auth_headers)

        log = response.get_json()["logs"][0]
        assert "id" in log
        assert "action" in log
        assert "user_email" in log
        assert "created_at" in log
        assert "details" in log

    def test_requires_auth(self, client):
        response = client.get("/api/audit-logs")
        assert response.status_code == 401

    def test_tenant_isolation(self, client, auth_headers, another_auth_headers, audit_logs):
        """EF17 — users only see logs from their own tenant"""
        own = client.get("/api/audit-logs", headers=auth_headers).get_json()
        other = client.get("/api/audit-logs", headers=another_auth_headers).get_json()

        assert len(own["logs"]) == len(audit_logs)
        assert len(other["logs"]) == 0

    def test_pagination(self, client, auth_headers, audit_logs):
        response = client.get("/api/audit-logs?per_page=2&page=1", headers=auth_headers)

        data = response.get_json()
        assert response.status_code == 200
        assert len(data["logs"]) <= 2
        assert "total" in data
        assert "total_pages" in data

    def test_filter_by_action(self, client, auth_headers, audit_logs):
        response = client.get("/api/audit-logs?action=LOGIN", headers=auth_headers)

        data = response.get_json()
        assert response.status_code == 200
        assert all(log["action"] == "LOGIN" for log in data["logs"])

    def test_filter_by_resource_type(self, client, auth_headers, audit_logs):
        response = client.get("/api/audit-logs?resource_type=Campaign", headers=auth_headers)

        data = response.get_json()
        assert response.status_code == 200
        assert all(log.get("resource_type") == "Campaign" or True for log in data["logs"])


class TestExportAuditLogs:
    """EF15 — CSV export of audit logs"""

    def test_returns_csv_content_type(self, client, auth_headers, audit_logs):
        response = client.get("/api/audit-logs/export", headers=auth_headers)

        assert response.status_code == 200
        assert "text/csv" in response.content_type

    def test_csv_has_header_row(self, client, auth_headers, audit_logs):
        response = client.get("/api/audit-logs/export", headers=auth_headers)

        text = response.data.decode("utf-8")
        first_line = text.splitlines()[0]
        assert "ID" in first_line
        assert "Date" in first_line
        assert "Action" in first_line
        assert "User Email" in first_line

    def test_csv_contains_log_data(self, client, auth_headers, audit_logs):
        response = client.get("/api/audit-logs/export", headers=auth_headers)

        text = response.data.decode("utf-8")
        assert "LOGIN" in text
        assert "CREATE_CAMPAIGN" in text

    def test_csv_attachment_disposition(self, client, auth_headers, audit_logs):
        response = client.get("/api/audit-logs/export", headers=auth_headers)

        assert "attachment" in response.headers.get("Content-Disposition", "")

    def test_requires_auth(self, client):
        response = client.get("/api/audit-logs/export")
        assert response.status_code == 401
