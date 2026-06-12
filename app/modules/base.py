"""Base module contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.services.system_info import MetricRow, SystemInfoService


@dataclass(frozen=True, slots=True)
class ModuleMetadata:
    """Metadata displayed by the dashboard module registry."""

    module_id: str
    title: str
    description: str
    icon: str = "◌"


class DashboardModule(ABC):
    """Abstract base class for independent PlasmaDeck modules."""

    metadata: ModuleMetadata

    def __init__(self, service: SystemInfoService) -> None:
        self.service = service

    @abstractmethod
    def collect(self) -> list[MetricRow]:
        """Collect current rows for this module."""
