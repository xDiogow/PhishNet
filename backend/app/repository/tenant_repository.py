from app.repository.base_repository import BaseRepository
from app.models.tenant import Tenant


class TenantRepository(BaseRepository):
    """Repository for Tenant model."""

    def __init__(self):
        """Initialize the repository."""
        super().__init__(Tenant)

    def get_by_name(self, name: str):
        """Get a tenant by name."""
        return self.session.query(self.model).filter(self.model.name == name).first()

    def get_or_create_by_name(self, name: str):
        """Get a tenant by name or create it if it doesn't exist."""
        tenant = self.get_by_name(name)
        if not tenant:
            tenant = Tenant(name=name)
            tenant = self.create(tenant)
        return tenant
