"""
Test configuration and fixtures for PhishNet Backend
"""
import pytest
import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.models import Base


@pytest.fixture
def app():
    """Create and configure a test app instance"""
    app = create_app(TestingConfig)

    # Initialize database for testing
    with app.app_context():
        Base.metadata.create_all(bind=db.engine)

    yield app

    # Cleanup
    with app.app_context():
        db.session.remove()
        Base.metadata.drop_all(bind=db.engine)


@pytest.fixture
def client(app):
    """Create a test client for the app"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def db_session(app):
    """Create a database session for testing"""
    with app.app_context():
        yield db.session
        db.session.rollback()
