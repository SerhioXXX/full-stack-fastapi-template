"""Critical RBAC allow/deny scenarios (Phase 6)."""

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.core.rbac import Permission, permissions_for
from app.models import Role
from tests.utils.user import (
    authentication_headers_for_role,
    create_user_with_role,
)
from tests.utils.utils import random_email, random_lower_string


def test_member_cannot_list_users(client: TestClient, db: Session) -> None:
    headers, _ = authentication_headers_for_role(
        client=client, db=db, role=Role.MEMBER
    )
    r = client.get(f"{settings.API_V1_STR}/users/", headers=headers)
    assert r.status_code == 403


def test_manager_can_list_users_but_cannot_create(
    client: TestClient, db: Session
) -> None:
    headers, _ = authentication_headers_for_role(
        client=client, db=db, role=Role.MANAGER
    )

    r = client.get(f"{settings.API_V1_STR}/users/", headers=headers)
    assert r.status_code == 200
    assert "data" in r.json()

    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=headers,
        json={
            "email": random_email(),
            "password": random_lower_string(),
            "role": Role.MEMBER.value,
        },
    )
    assert r.status_code == 403


def test_admin_can_create_user_and_access_system_settings(
    client: TestClient, db: Session
) -> None:
    headers, _ = authentication_headers_for_role(
        client=client, db=db, role=Role.ADMIN
    )

    email = random_email()
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=headers,
        json={
            "email": email,
            "password": random_lower_string(),
            "role": Role.MANAGER.value,
        },
    )
    assert r.status_code == 200
    created = r.json()
    assert created["email"] == email
    assert created["role"] == Role.MANAGER.value

    r = client.get(f"{settings.API_V1_STR}/settings/system", headers=headers)
    assert r.status_code == 200
    assert "site_name" in r.json()

    r = client.patch(
        f"{settings.API_V1_STR}/settings/system",
        headers=headers,
        json={"maintenance_mode": False},
    )
    assert r.status_code == 200


def test_member_can_update_own_profile_but_not_another_user(
    client: TestClient, db: Session
) -> None:
    headers, member = authentication_headers_for_role(
        client=client, db=db, role=Role.MEMBER
    )
    other, _ = create_user_with_role(db, role=Role.MEMBER)

    r = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=headers,
        json={"full_name": "Member Updated"},
    )
    assert r.status_code == 200
    assert r.json()["full_name"] == "Member Updated"
    assert r.json()["id"] == str(member.id)

    r = client.patch(
        f"{settings.API_V1_STR}/users/{other.id}",
        headers=headers,
        json={"full_name": "Hacked"},
    )
    assert r.status_code == 403


def test_manager_can_read_metrics_member_cannot(
    client: TestClient, db: Session
) -> None:
    manager_headers, _ = authentication_headers_for_role(
        client=client, db=db, role=Role.MANAGER
    )
    member_headers, _ = authentication_headers_for_role(
        client=client, db=db, role=Role.MEMBER
    )

    r = client.get(f"{settings.API_V1_STR}/metrics/", headers=manager_headers)
    assert r.status_code == 200
    assert "total_users" in r.json()

    r = client.get(f"{settings.API_V1_STR}/metrics/", headers=member_headers)
    assert r.status_code == 403


def test_users_me_permissions_match_role_matrix(
    client: TestClient, db: Session
) -> None:
    for role in Role:
        headers, _ = authentication_headers_for_role(
            client=client, db=db, role=role
        )
        r = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
        assert r.status_code == 200
        body = r.json()
        assert body["role"] == role.value
        assert set(body["permissions"]) == set(permissions_for(role))
        # Spot-check a couple of matrix edges.
        if role == Role.MEMBER:
            assert Permission.USERS_LIST not in body["permissions"]
            assert Permission.PROFILE_UPDATE in body["permissions"]
        if role == Role.MANAGER:
            assert Permission.USERS_LIST in body["permissions"]
            assert Permission.USERS_CREATE not in body["permissions"]
            assert Permission.SETTINGS_WRITE not in body["permissions"]
        if role == Role.ADMIN:
            assert Permission.SETTINGS_WRITE in body["permissions"]
            assert Permission.USERS_CREATE in body["permissions"]


def test_manager_cannot_access_system_settings(
    client: TestClient, db: Session
) -> None:
    headers, _ = authentication_headers_for_role(
        client=client, db=db, role=Role.MANAGER
    )
    r = client.get(f"{settings.API_V1_STR}/settings/system", headers=headers)
    assert r.status_code == 403
