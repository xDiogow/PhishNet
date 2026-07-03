"""Tenant-related helper functions"""


def verify_tenant_ownership(resource_tenant_id: int, user_tenant_id: int) -> bool:
    return resource_tenant_id == user_tenant_id
