import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    RATELIMIT_STORAGE_URI = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    SESSION_BLOCKLIST_ENABLED = True

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "app.db"}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173').split(',')

    # SMTP / Email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.mailtrap.io')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False') == 'True'  # port 465 implicit SSL
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_FROM = os.getenv('MAIL_FROM', 'phishnet@company.com')
    MAIL_TIMEOUT = int(os.getenv('MAIL_TIMEOUT', 30))  # seconds per SMTP connection

    # Base URL used to build tracking links embedded in phishing emails (backend)
    APP_BASE_URL = os.getenv('APP_BASE_URL', 'http://localhost:5000')
    # Frontend URL used for post-submission redirects (e.g. /caught page)
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost')

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    """Configuration for testing"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret-key'
    LOG_LEVEL = 'DEBUG'
    REDIS_URL = 'redis://localhost:6379/1'  # separate DB index for tests
    RATELIMIT_STORAGE_URI = 'memory://'
    SESSION_BLOCKLIST_ENABLED = False  # avoids Redis dependency in unit tests
