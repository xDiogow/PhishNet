from app.extensions import db
from app.models.user_permission import UserPermission


class UserPermissionRepository:

    def get_permissions(self, user_id, tenant_id):
        rows = db.session.query(UserPermission).filter_by(user_id=user_id, tenant_id=tenant_id).all()
        return [r.permission for r in rows]

    def has_permission(self, user_id, tenant_id, permission):
        result = db.session.query(UserPermission).filter_by(
            user_id=user_id, tenant_id=tenant_id, permission=permission
        ).first()
        return result is not None

    def grant_all(self, user_id, tenant_id, permissions):
        for p in permissions:
            exists = db.session.query(UserPermission).filter_by(
                user_id=user_id, tenant_id=tenant_id, permission=p
            ).first()
            if not exists:
                db.session.add(UserPermission(user_id=user_id, tenant_id=tenant_id, permission=p))
        db.session.commit()

    def set_permissions(self, user_id, tenant_id, permissions):
        db.session.query(UserPermission).filter_by(user_id=user_id, tenant_id=tenant_id).delete()
        for p in permissions:
            db.session.add(UserPermission(user_id=user_id, tenant_id=tenant_id, permission=p))
        db.session.commit()
