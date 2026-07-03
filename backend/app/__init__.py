import logging
from flask import Flask, jsonify
from sqlalchemy import text
from .config import Config
from .extensions import db, migrate, jwt, bcrypt, cors, limiter
from .api import register_blueprints
from .commands import register_commands


def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or Config)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)

    from app.repository.session_repository import session_repo

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        from flask import current_app
        if not current_app.config.get('SESSION_BLOCKLIST_ENABLED', True):
            return False
        return session_repo.is_token_revoked(jwt_payload["jti"])
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "supports_credentials": True,
        }
    })

    with app.app_context():
        from app.models import Base, User, Target, Tenant, Template, Campaign, TenantInvitation
        app.logger.info('Models loaded for migrations')

    register_blueprints(app)
    register_commands(app)

    if not app.config.get('TESTING'):
        from app.scheduler import start_scheduler
        start_scheduler(app)

    @app.route('/api/health')
    def health():
        checks = {}
        status_code = 200

        try:
            db.session.execute(text('SELECT 1'))
            checks['database'] = 'ok'
        except Exception:
            checks['database'] = 'error'
            status_code = 503

        try:
            import redis as redis_lib
            r = redis_lib.from_url(
                app.config.get('REDIS_URL', 'redis://localhost:6379/0'),
                socket_connect_timeout=2,
            )
            r.ping()
            checks['redis'] = 'ok'
        except Exception:
            checks['redis'] = 'error'
            status_code = 503

        return jsonify({
            'status': 'healthy' if status_code == 200 else 'unhealthy',
            'checks': checks,
        }), status_code

    # Register error handlers
    @app.errorhandler(Exception)
    def handle_exception(e):
        from werkzeug.exceptions import HTTPException
        if isinstance(e, HTTPException):
            return e
        app.logger.exception('Unhandled exception occurred')
        return jsonify({'error': 'An unexpected error occurred'}), 500

    @app.errorhandler(404)
    def handle_404(e):
        from flask import request
        app.logger.info(f'Resource not found: {request.path}')
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def handle_500(e):
        app.logger.exception('Internal server error')
        return jsonify({'error': 'Internal server error'}), 500

    return app
