from datetime import datetime, timezone
from app.repository.base_repository import BaseRepository
from app.models.tenant_invitation import TenantInvitation


class TenantInvitationRepository(BaseRepository[TenantInvitation]):
    """Repository for TenantInvitation model."""

    def __init__(self):
        """Initialize the repository."""
        super().__init__(TenantInvitation)

    def get_by_code(self, invitation_code: str):
        """Get an invitation by invitation code."""
        return self.session.query(self.model).filter(
            self.model.invitation_code == invitation_code
        ).first()

    def get_by_tenant_id(self, tenant_id: int, is_used: bool = None):
        """Get all invitations for a tenant, optionally filtered by is_used."""
        query = self.session.query(self.model).filter(
            self.model.tenant_id == tenant_id
        )
        if is_used is not None:
            query = query.filter(self.model.is_used == is_used)
        return query.all()

    def mark_as_used(self, invitation_id: int, user_id: int):
        """Mark an invitation as used."""
        return self.update_by_id(
            invitation_id,
            is_used=True,
            used_at=datetime.now(timezone.utc),
            used_by_user_id=user_id
        )
