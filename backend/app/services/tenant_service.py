"""Tenant management service.

Handles tenant creation (including the initial invitation code generation)
and simple read operations. Tenant deletion is handled directly by the
tenants API route because it needs to enforce the no-users constraint.
"""
import secrets
import logging
from datetime import datetime, timedelta, timezone
from app.repository.tenant_repository import TenantRepository
from app.repository.tenant_invitation_repository import TenantInvitationRepository
from app.models.tenant import Tenant
from app.models.tenant_invitation import TenantInvitation

logger = logging.getLogger(__name__)


def create_tenant(name: str, invitation_expires_days: int = None):
    """Create a new tenant and generate its first invitation code.

    Returns a dict with keys: status, message, tenant, invitation.
    On name conflict returns status='error' without raising.
    ``invitation_expires_days=None`` creates a code with no expiry.
    """
    tenant_repo = TenantRepository()
    invitation_repo = TenantInvitationRepository()

    existing_tenant = tenant_repo.get_by_name(name)
    if existing_tenant:
        return {
            'status': 'error',
            'message': f'Tenant with name "{name}" already exists',
            'tenant': None,
            'invitation': None
        }

    tenant = Tenant(name=name)
    tenant = tenant_repo.create(tenant)

    invitation_code = secrets.token_urlsafe(32)
    
    expires_at = None
    if invitation_expires_days is not None:
        expires_at = datetime.now(timezone.utc) + timedelta(days=invitation_expires_days)
    
    invitation = TenantInvitation(
        invitation_code=invitation_code,
        tenant_id=tenant.id,
        is_used=False,
        expires_at=expires_at
    )
    invitation = invitation_repo.create(invitation)
    
    return {
        'status': 'success',
        'message': 'Tenant created successfully',
        'tenant': tenant,
        'invitation': invitation
    }


def get_tenant_by_id(tenant_id: int):
    """Return a single Tenant by primary key, or None."""
    tenant_repo = TenantRepository()
    return tenant_repo.get_by_id(tenant_id)


def get_all_tenants():
    """Return all tenants ordered by creation date."""
    tenant_repo = TenantRepository()
    return tenant_repo.get_all()
