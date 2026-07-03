from typing import Optional, List
from app.repository.base_repository import BaseRepository
from app.models.target import Target


class TargetRepository(BaseRepository):
    """Repository for Target model."""

    def __init__(self):
        """Initialize the repository."""
        super().__init__(Target)

    def get_by_email(self, email: str, tenant_id: int) -> Optional[Target]:
        """Get a target by email and tenant_id."""
        return self.session.query(self.model).filter(
            self.model.email == email,
            self.model.tenant_id == tenant_id
        ).first()

    def get_all_by_tenant_id(self, tenant_id: int) -> List[Target]:
        """Get all targets by tenant_id."""
        return self.session.query(self.model).filter(
            self.model.tenant_id == tenant_id
        ).all()
