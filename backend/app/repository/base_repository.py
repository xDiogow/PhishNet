from typing import Generic, TypeVar

from sqlalchemy.orm import Session
from app.extensions import db

ModelType = TypeVar('ModelType')


class BaseRepository(Generic[ModelType]):
    """Base repository class."""

    def __init__(self, model: ModelType):
        """Initialize the repository."""
        self.model = model

    @property
    def session(self) -> Session:
        """Get the current database session."""
        return db.session

    def get_by_id(self, id: int, **filters):
        """Get a model by its ID."""
        query = self.session.query(self.model).filter(self.model.id == id)

        for attr_name, attr_value in filters.items():
            if not hasattr(self.model, attr_name):
                raise ValueError(
                    f"Model {self.model.__name__} has no attribute '{attr_name}'"
                )
            query = query.filter(getattr(self.model, attr_name) == attr_value)

        return query.first()

    def get_all(self, **filters):
        """Get all records."""
        query = self.session.query(self.model)

        for attr_name, attr_value in filters.items():
            if hasattr(self.model, attr_name):
                query = query.filter(getattr(self.model, attr_name) == attr_value)
            else:
                raise ValueError(f"Model {self.model.__name__} has no attribute '{attr_name}'")

        return query.all()

    def create(self, obj: ModelType):
        """Create a new record."""
        self.session.add(obj)
        self.session.commit()
        return obj

    def update_by_id(self, id: int, **kwargs):
        """Update a record by ID."""
        rows = (self.session.query(self.model)
        .filter(self.model.id == id)
        .update(kwargs, synchronize_session="fetch")) # we need to use synchronize_session="fetch" to update in-memory records

        if rows == 0:
            raise ValueError(f"No record found with ID {id}")

        self.session.commit()
        return self.get_by_id(id)

    def delete(self, id: int):
        """Delete a record by ID."""
        self.session.delete(self.get_by_id(id))
        self.session.commit()

    def count(self):
        """Count total records."""
        return self.session.query(self.model).count()
