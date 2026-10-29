"""Role → permission policy map (single source of truth for authorization)."""

from __future__ import annotations

from app.models import Role, User


class Permission:
    USERS_LIST = "users:list"
    USERS_CREATE = "users:create"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"
    METRICS_READ = "metrics:read"
    PROFILE_UPDATE = "profile:update"
    SETTINGS_WRITE = "settings:write"


ROLE_PERMISSIONS: dict[Role, frozenset[str]] = {
    Role.ADMIN: frozenset(
        {
            Permission.USERS_LIST,
            Permission.USERS_CREATE,
            Permission.USERS_UPDATE,
            Permission.USERS_DELETE,
            Permission.METRICS_READ,
            Permission.PROFILE_UPDATE,
            Permission.SETTINGS_WRITE,
        }
    ),
    Role.MANAGER: frozenset(
        {
            Permission.USERS_LIST,
            Permission.METRICS_READ,
            Permission.PROFILE_UPDATE,
        }
    ),
    Role.MEMBER: frozenset(
        {
            Permission.PROFILE_UPDATE,
        }
    ),
}


def permissions_for(role: Role) -> frozenset[str]:
    return ROLE_PERMISSIONS.get(role, frozenset())


def has_permission(user: User, permission: str) -> bool:
    return permission in permissions_for(user.role)
