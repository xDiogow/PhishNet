"""Repository for Template — CRUD operations on phishing templates."""
from app.models.template import Template
from app.repository.base_repository import BaseRepository


class TemplateRepository(BaseRepository):
    def __init__(self):
        super().__init__(Template)

    def get_by_name(self, name: str):
        return self.session.query(Template).filter(Template.name == name).first()

    def get_all_for_tenant(self, tenant_id: int) -> list:
        """Global templates (tenant_id IS NULL) + tenant's own, globals first."""
        global_templates = (
            self.session.query(Template)
            .filter(Template.tenant_id == None)
            .order_by(Template.name)
            .all()
        )
        tenant_templates = (
            self.session.query(Template)
            .filter(Template.tenant_id == tenant_id)
            .order_by(Template.name)
            .all()
        )
        return global_templates + tenant_templates

    def get_by_id_for_tenant(self, template_id: int, tenant_id: int):
        """Return template if global OR belongs to the given tenant, else None."""
        global_template = (
            self.session.query(Template)
            .filter(Template.id == template_id, Template.tenant_id == None)
            .first()
        )
        if global_template:
            return global_template
        return (
            self.session.query(Template)
            .filter(Template.id == template_id, Template.tenant_id == tenant_id)
            .first()
        )
