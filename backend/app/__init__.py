import logging
from flask import Flask, jsonify
from .config import Config
from .extensions import db, migrate, jwt, bcrypt, cors
from .api import register_blueprints
from .commands import register_commands


def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or Config)

    logging.basicConfig(
        level=getattr(logging, app.config.get('LOG_LEVEL', 'INFO')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    with app.app_context():
        from app.models import Base, User, Target, Tenant, Template, Campaign, TenantInvitation
        app.logger.info('Models loaded for migrations')

    register_blueprints(app)
    register_commands(app)

    # Register error handlers
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.exception('Unhandled exception occurred')
        return jsonify({
            'error': str(e),
            'type': type(e).__name__
        }), 500

    @app.errorhandler(404)
    def handle_404(e):
        from flask import request
        app.logger.info(f'Resource not found: {request.path}')
        return jsonify({
            'error': 'Resource not found',
            'message': str(e)
        }), 404

    @app.errorhandler(500)
    def handle_500(e):
        app.logger.exception('Internal server error')
        return jsonify({
            'error': 'Internal server error',
            'message': str(e) if app.config.get('DEBUG') else 'An error occurred'
        }), 500

    return app