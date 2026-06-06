import secrets
from datetime import datetime, timedelta, timezone
from app.repository.tenant_invitation_repository import TenantInvitationRepository
from app.models.tenant_invitation import TenantInvitation


def create_invitation(tenant_id: int, expires_days: int = None):
    """Create a new invitation for a tenant."""
    invitation_repo = TenantInvitationRepository()

    invitation_code = secrets.token_urlsafe(32)

    while invitation_repo.get_by_code(invitation_code):
        invitation_code = secrets.token_urlsafe(32)

    expires_at = None
    if expires_days is not None:
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days)

    invitation = TenantInvitation(
        invitation_code=invitation_code,
        tenant_id=tenant_id,
        is_used=False,
        expires_at=expires_at
    )
    invitation = invitation_repo.create(invitation)

    return {
        'status': 'success',
        'message': 'Invitation created successfully',
        'invitation': invitation
    }


def validate_invitation(invitation_code: str):
    """Validate an invitation code."""
    invitation_repo = TenantInvitationRepository()

    invitation = invitation_repo.get_by_code(invitation_code)

    if not invitation:
        return {
            'status': 'error',
            'message': 'Invalid invitation code',
            'invitation': None
        }

    if invitation.is_used:
        return {
            'status': 'error',
            'message': 'Invitation code has already been used',
            'invitation': None
        }

    if invitation.is_expired():
        return {
            'status': 'error',
            'message': 'Invitation code has expired',
            'invitation': None
        }

    return {
        'status': 'success',
        'message': 'Invitation code is valid',
        'invitation': invitation
    }


def use_invitation(invitation_code: str, user_id: int):
    """Mark an invitation as used."""
    invitation_repo = TenantInvitationRepository()

    invitation = invitation_repo.get_by_code(invitation_code)

    if not invitation:
        return {
            'status': 'error',
            'message': 'Invalid invitation code',
            'invitation': None
        }

    if invitation.is_used:
        return {
            'status': 'error',
            'message': 'Invitation code has already been used',
            'invitation': invitation
        }

    if invitation.is_expired():
        return {
            'status': 'error',
            'message': 'Invitation code has expired',
            'invitation': invitation
        }

    invitation = invitation_repo.mark_as_used(invitation.id, user_id)

    return {
        'status': 'success',
        'message': 'Invitation used successfully',
        'invitation': invitation
    }


def get_invitation_by_code(invitation_code: str):
    """Get an invitation by code."""
    invitation_repo = TenantInvitationRepository()
    return invitation_repo.get_by_code(invitation_code)


def get_invitations_by_tenant(tenant_id: int, is_used: bool = None):
    """Get all invitations for a tenant."""
    invitation_repo = TenantInvitationRepository()
    return invitation_repo.get_by_tenant_id(tenant_id, is_used)
