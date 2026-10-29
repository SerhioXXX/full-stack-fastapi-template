from app.core.rbac import ROLE_PERMISSIONS, Permission, has_permission, permissions_for
from app.models import Role, User


def test_role_permissions_matrix() -> None:
    assert Permission.USERS_LIST in permissions_for(Role.ADMIN)
    assert Permission.USERS_LIST in permissions_for(Role.MANAGER)
    assert Permission.USERS_LIST not in permissions_for(Role.MEMBER)

    assert Permission.USERS_CREATE in permissions_for(Role.ADMIN)
    assert Permission.USERS_CREATE not in permissions_for(Role.MANAGER)
    assert Permission.USERS_CREATE not in permissions_for(Role.MEMBER)

    assert Permission.METRICS_READ in permissions_for(Role.MANAGER)
    assert Permission.METRICS_READ not in permissions_for(Role.MEMBER)

    assert Permission.PROFILE_UPDATE in permissions_for(Role.MEMBER)
    assert Permission.SETTINGS_WRITE in permissions_for(Role.ADMIN)
    assert Permission.SETTINGS_WRITE not in permissions_for(Role.MANAGER)


def test_every_role_has_an_entry() -> None:
    assert set(ROLE_PERMISSIONS) == set(Role)


def test_has_permission_uses_user_role() -> None:
    manager = User(
        email="manager@example.com",
        hashed_password="x",
        role=Role.MANAGER,
    )
    assert has_permission(manager, Permission.USERS_LIST)
    assert not has_permission(manager, Permission.USERS_CREATE)
