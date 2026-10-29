from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import require_permission
from app.core.rbac import Permission
from app.core.system_settings import get_system_settings, update_system_settings
from app.models import SystemSettings, SystemSettingsUpdate

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get(
    "/system",
    dependencies=[Depends(require_permission(Permission.SETTINGS_WRITE))],
    response_model=SystemSettings,
)
def read_system_settings() -> Any:
    """
    Read global system settings (admin-only stub).
    """
    return get_system_settings()


@router.patch(
    "/system",
    dependencies=[Depends(require_permission(Permission.SETTINGS_WRITE))],
    response_model=SystemSettings,
)
def patch_system_settings(settings_in: SystemSettingsUpdate) -> Any:
    """
    Update global system settings (admin-only stub; in-memory only).
    """
    return update_system_settings(settings_in)
