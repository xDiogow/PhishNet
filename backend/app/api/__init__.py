from flask import Flask

def register_blueprints(app: Flask):
    from .auth import bp as auth_bp
    from .campaigns import bp as campaigns_bp
    from .tenants.tenants import bp as tenants_bp
    from .tenants.tenant_invitations import bp as tenant_invitations_bp
    from .templates import bp as templates_bp
    from .team import bp as team_bp
    from .audit_logs import bp as audit_logs_bp
    from .tracking import bp as tracking_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(campaigns_bp)
    app.register_blueprint(tenants_bp)
    app.register_blueprint(tenant_invitations_bp)
    app.register_blueprint(templates_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(audit_logs_bp)
    app.register_blueprint(tracking_bp)
