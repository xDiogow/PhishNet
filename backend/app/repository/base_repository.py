from app.extensions import db


class BaseRepository:
    """Base class for all repositories. Provides generic CRUD over a SQLAlchemy model."""

    def __init__(self, model):
        self.model = model

    @property
    def session(self):
        return db.session

    def get_by_id(self, id, **filters):
        query = self.session.query(self.model).filter(self.model.id == id)
        for attr_name, attr_value in filters.items():
            if not hasattr(self.model, attr_name):
                raise ValueError(f"Model {self.model.__name__} has no attribute '{attr_name}'")
            query = query.filter(getattr(self.model, attr_name) == attr_value)
        return query.first()

    def get_all(self, **filters):
        query = self.session.query(self.model)
        for attr_name, attr_value in filters.items():
            if not hasattr(self.model, attr_name):
                raise ValueError(f"Model {self.model.__name__} has no attribute '{attr_name}'")
            query = query.filter(getattr(self.model, attr_name) == attr_value)
        return query.all()

    def create(self, obj):
        self.session.add(obj)
        self.session.commit()
        return obj

    def update_by_id(self, id, **kwargs):
        obj = self.get_by_id(id)
        if not obj:
            raise ValueError(f"No record found with ID {id}")
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.session.commit()
        return obj

    def delete(self, id):
        obj = self.get_by_id(id)
        self.session.delete(obj)
        self.session.commit()

    def count(self):
        return self.session.query(self.model).count()
