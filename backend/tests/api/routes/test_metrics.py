from fastapi.testclient import TestClient

from app.core.config import settings


def test_read_metrics_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/metrics/",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    data = r.json()
    assert "total_users" in data
    assert "active_users" in data
    assert "total_items" in data
    assert data["total_users"] >= 1


def test_read_metrics_forbidden_for_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/metrics/",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403
