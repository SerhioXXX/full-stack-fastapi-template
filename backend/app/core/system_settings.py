"""In-memory system settings store (RBAC demo stub; not persisted)."""

from app.models import SystemSettings, SystemSettingsUpdate

_settings = SystemSettings()


def get_system_settings() -> SystemSettings:
    return _settings.model_copy()


def update_system_settings(update: SystemSettingsUpdate) -> SystemSettings:
    global _settings
    data = _settings.model_dump()
    data.update(update.model_dump(exclude_unset=True))
    _settings = SystemSettings.model_validate(data)
    return _settings.model_copy()


def reset_system_settings() -> SystemSettings:
    """Test helper to restore defaults between cases."""
    global _settings
    _settings = SystemSettings()
    return _settings.model_copy()
