"""Repository for Template — CRUD operations on phishing templates."""
from app.models.template import Template
from app.repository.base_repository import BaseRepository


class TemplateRepository(BaseRepository[Template]):
    def __init__(self):
        super().__init__(Template)

    def get_by_name(self, name: str):
        """Return a template by exact name match, or None."""
        return self.session.query(Template).filter(Template.name == name).first()
