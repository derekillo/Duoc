"""Reusable visual card for dashboard modules."""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout

from app.modules.base import DashboardModule

LOGGER = logging.getLogger(__name__)


class ModuleCard(QFrame):
    """A KDE-like card that renders a dashboard module."""

    def __init__(self, module: DashboardModule) -> None:
        super().__init__()
        self.module = module
        self.setObjectName("ModuleCard")
        self.setMinimumHeight(150)
        self._rows_layout = QGridLayout()
        self._rows_layout.setColumnStretch(1, 1)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)
        title = QLabel(f"{self.module.metadata.icon}  {self.module.metadata.title}")
        title.setObjectName("ModuleTitle")
        layout.addWidget(title)
        layout.addLayout(self._rows_layout)
        layout.addStretch(1)

    def refresh(self) -> None:
        """Collect module data and redraw metric rows."""
        while self._rows_layout.count():
            item = self._rows_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        try:
            rows = self.module.collect()
        except Exception as exc:  # noqa: BLE001 - UI should survive module failures.
            LOGGER.error("Module %s failed: %s", self.module.metadata.module_id, exc)
            rows = []
        if not rows:
            rows = []
        for index, row in enumerate(rows[:8]):
            label = QLabel(row.label)
            label.setObjectName("MetricLabel")
            value = QLabel(row.value)
            value.setObjectName("MetricValue")
            value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            value.setWordWrap(True)
            self._rows_layout.addWidget(label, index, 0)
            self._rows_layout.addWidget(value, index, 1)
