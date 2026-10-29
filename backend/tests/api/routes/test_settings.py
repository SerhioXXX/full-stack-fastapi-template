from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.system_settings import reset_system_settings


def test_read_system_settings_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    reset_system_settings()
    r = client.get(
        f"{settings.API_V1_STR}/settings/system",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["maintenance_mode"] is False
    assert "site_name" in data


def test_patch_system_settings_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    reset_system_settings()
    r = client.patch(
        f"{settings.API_V1_STR}/settings/system",
        headers=superuser_token_headers,
        json={"site_name": "RBAC Demo", "maintenance_mode": True},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["site_name"] == "RBAC Demo"
    assert data["maintenance_mode"] is True


def test_system_settings_forbidden_for_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    reset_system_settings()
    r = client.get(
        f"{settings.API_V1_STR}/settings/system",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403

    r = client.patch(
        f"{settings.API_V1_STR}/settings/system",
        headers=normal_user_token_headers,
        json={"maintenance_mode": True},
    )
    assert r.status_code == 403
