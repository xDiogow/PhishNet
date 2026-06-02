"""
One-time bootstrap script.
Creates a tenant and generates an invitation code so the first user can register.

Usage (from the backend/ directory):
    python scripts/bootstrap.py
    python scripts/bootstrap.py --tenant "My Company"
"""

import sys
import os
import argparse
import secrets

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.tenant import Tenant
from app.models.tenant_invitation import TenantInvitation

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tenant', default='Default', help='Tenant name (default: Default)')
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        # Create tenant if it doesn't exist
        tenant = db.session.query(Tenant).filter_by(name=args.tenant).first()
        if not tenant:
            tenant = Tenant(name=args.tenant)
            db.session.add(tenant)
            db.session.flush()
            print(f"Created tenant: '{args.tenant}' (id={tenant.id})")
        else:
            print(f"Using existing tenant: '{args.tenant}' (id={tenant.id})")

        # Generate invitation code
        code = secrets.token_urlsafe(24)
        invitation = TenantInvitation(invitation_code=code, tenant_id=tenant.id)
        db.session.add(invitation)
        db.session.commit()

        print(f"\nInvitation code: {code}")
        print("\nUse this code on the Register page to create your account.")

if __name__ == '__main__':
    main()
