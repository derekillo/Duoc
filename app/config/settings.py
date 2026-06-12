"""Configuration models for PlasmaDeck."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


DEFAULT_MODULES = ["system", "cpu", "memory", "disks", "network"]


@dataclass(slots=True)
class WindowSettings:
    """Persisted dashboard window settings."""

    width: int = 980
    height: int = 640
    x: int | None = None
    y: int | None = None
    monitor: str | None = None
    always_on_top: bool = False
    all_desktops: bool = True
    frameless: bool = False
    opacity: float = 0.94
    minimize_to_tray: bool = True


@dataclass(slots=True)
class GeneralSettings:
    """General runtime settings."""

    theme: str = "auto"
    update_interval_seconds: int = 2
    start_with_session: bool = False
    language: str = "auto"


@dataclass(slots=True)
class ModuleSettings:
    """Module activation and ordering settings."""

    active: dict[str, bool] = field(
        default_factory=lambda: {module: True for module in DEFAULT_MODULES}
    )
    order: list[str] = field(default_factory=lambda: list(DEFAULT_MODULES))


@dataclass(slots=True)
class AppSettings:
    """Root settings object persisted as JSON."""

    window: WindowSettings = field(default_factory=WindowSettings)
    general: GeneralSettings = field(default_factory=GeneralSettings)
    modules: ModuleSettings = field(default_factory=ModuleSettings)

    def to_dict(self) -> dict[str, Any]:
        """Return settings as a JSON-serializable dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppSettings":
        """Build settings from a dictionary while preserving defaults."""
        defaults = cls()
        window_data = data.get("window", {}) if isinstance(data, dict) else {}
        general_data = data.get("general", {}) if isinstance(data, dict) else {}
        modules_data = data.get("modules", {}) if isinstance(data, dict) else {}

        window = WindowSettings(**_filtered(WindowSettings, window_data, defaults.window))
        general = GeneralSettings(**_filtered(GeneralSettings, general_data, defaults.general))
        modules = ModuleSettings(**_filtered(ModuleSettings, modules_data, defaults.modules))

        for module in DEFAULT_MODULES:
            modules.active.setdefault(module, True)
            if module not in modules.order:
                modules.order.append(module)

        general.update_interval_seconds = max(1, int(general.update_interval_seconds))
        window.opacity = min(1.0, max(0.25, float(window.opacity)))
        return cls(window=window, general=general, modules=modules)


def _filtered(model: type, values: dict[str, Any], defaults: Any) -> dict[str, Any]:
    """Filter unknown dataclass keys and fill missing values from defaults."""
    result = asdict(defaults)
    if isinstance(values, dict):
        allowed = set(result)
        result.update({key: value for key, value in values.items() if key in allowed})
    return result
