from app.repository.base_repository import BaseRepository
from app.models.user import User


class UserRepository(BaseRepository):
    """Repository for User model."""

    def __init__(self):
        """Initialize the repository."""
        super().__init__(User)

    def get_by_email(self, email: str):
        """Get a user by email."""
        return self.session.query(self.model).filter(self.model.email == email).first()

    def get_all_by_tenant_id(self, tenant_id: int, active_only: bool = False):
        """Get all users by tenant_id."""
        query = self.session.query(self.model).filter(self.model.tenant_id == tenant_id)
        if active_only:
            query = query.filter(self.model.is_active == True)
        return query.all()
