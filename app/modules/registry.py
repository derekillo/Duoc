"""Module registry used by the dashboard shell."""

from __future__ import annotations

from collections.abc import Iterable

from app.modules.base import DashboardModule
from app.modules.mvp import (
    CpuModule,
    DiskModule,
    HealthModule,
    MemoryModule,
    NetworkModule,
    SnapperModule,
    SystemModule,
    UpdatesModule,
)
from app.services.system_info import SystemInfoService

MODULE_CLASSES: dict[str, type[DashboardModule]] = {
    cls.metadata.module_id: cls
    for cls in (
        SystemModule,
        CpuModule,
        MemoryModule,
        DiskModule,
        NetworkModule,
        UpdatesModule,
        SnapperModule,
        HealthModule,
    )
}


class ModuleRegistry:
    """Create dashboard module instances from configuration."""

    def __init__(self, service: SystemInfoService | None = None) -> None:
        self.service = service or SystemInfoService()

    def available(self) -> dict[str, type[DashboardModule]]:
        """Return available module classes keyed by identifier."""
        return dict(MODULE_CLASSES)

    def create(self, module_ids: Iterable[str]) -> list[DashboardModule]:
        """Create module instances for known identifiers."""
        modules: list[DashboardModule] = []
        for module_id in module_ids:
            module_class = MODULE_CLASSES.get(module_id)
            if module_class is not None:
                modules.append(module_class(self.service))
        return modules
