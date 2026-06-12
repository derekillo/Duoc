"""Built-in MVP modules."""

from __future__ import annotations

from app.modules.base import DashboardModule, ModuleMetadata
from app.services.system_info import MetricRow


class SystemModule(DashboardModule):
    metadata = ModuleMetadata("system", "System", "Host, uptime, kernel and session", "●")

    def collect(self) -> list[MetricRow]:
        return self.service.system_rows()


class CpuModule(DashboardModule):
    metadata = ModuleMetadata("cpu", "CPU", "Processor usage, frequency and temperature", "◆")

    def collect(self) -> list[MetricRow]:
        return self.service.cpu_rows()


class MemoryModule(DashboardModule):
    metadata = ModuleMetadata("memory", "RAM", "Memory usage and availability", "■")

    def collect(self) -> list[MetricRow]:
        return self.service.memory_rows()


class DiskModule(DashboardModule):
    metadata = ModuleMetadata("disks", "Disks", "Mounted partition usage", "▰")

    def collect(self) -> list[MetricRow]:
        return self.service.disk_rows()


class NetworkModule(DashboardModule):
    metadata = ModuleMetadata("network", "Network", "Interface, IP and transfer rates", "▲")

    def collect(self) -> list[MetricRow]:
        return self.service.network_rows()


class UpdatesModule(DashboardModule):
    metadata = ModuleMetadata("updates", "Updates", "Pacman and AUR update counters", "↻")

    def collect(self) -> list[MetricRow]:
        return self.service.update_rows()


class SnapperModule(DashboardModule):
    metadata = ModuleMetadata("snapper", "Snapper", "Snapshot overview", "◷")

    def collect(self) -> list[MetricRow]:
        return self.service.snapper_rows()


class HealthModule(DashboardModule):
    metadata = ModuleMetadata("health", "Health", "System health warnings", "♥")

    def collect(self) -> list[MetricRow]:
        return self.service.health_rows()
