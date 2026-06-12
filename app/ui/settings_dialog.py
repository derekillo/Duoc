"""Graphical settings panel for PlasmaDeck."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSpinBox,
    QVBoxLayout,
)

from app.config.settings import AppSettings
from app.modules.registry import MODULE_CLASSES


class SettingsDialog(QDialog):
    """Dedicated graphical settings panel."""

    settings_saved = Signal(object)

    def __init__(self, settings: AppSettings, screen_names: list[str], parent=None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("PlasmaDeck Settings")
        self.resize(520, 620)
        self.theme_combo = QComboBox()
        self.opacity_spin = QSpinBox()
        self.interval_spin = QSpinBox()
        self.monitor_combo = QComboBox()
        self.width_spin = QSpinBox()
        self.height_spin = QSpinBox()
        self.always_on_top = QCheckBox("Always visible")
        self.all_desktops = QCheckBox("Show on all desktops")
        self.frameless = QCheckBox("Borderless dashboard")
        self.start_with_session = QCheckBox("Start with session")
        self.modules_list = QListWidget()
        self._build_ui(screen_names)

    def _build_ui(self, screen_names: list[str]) -> None:
        layout = QVBoxLayout(self)

        general = QGroupBox("General")
        form = QFormLayout(general)
        self.theme_combo.addItems(["auto", "light", "dark"])
        self.theme_combo.setCurrentText(self.settings.general.theme)
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(self.settings.general.update_interval_seconds)
        self.opacity_spin.setRange(25, 100)
        self.opacity_spin.setSuffix("%")
        self.opacity_spin.setValue(round(self.settings.window.opacity * 100))
        form.addRow("Theme", self.theme_combo)
        form.addRow("Refresh", self.interval_spin)
        form.addRow("Opacity", self.opacity_spin)
        layout.addWidget(general)

        window = QGroupBox("Window")
        window_form = QFormLayout(window)
        self.monitor_combo.addItems(screen_names or ["Default"])
        if self.settings.window.monitor:
            self.monitor_combo.setCurrentText(self.settings.window.monitor)
        self.width_spin.setRange(360, 7680)
        self.width_spin.setValue(self.settings.window.width)
        self.height_spin.setRange(280, 4320)
        self.height_spin.setValue(self.settings.window.height)
        self.always_on_top.setChecked(self.settings.window.always_on_top)
        self.all_desktops.setChecked(self.settings.window.all_desktops)
        self.frameless.setChecked(self.settings.window.frameless)
        self.start_with_session.setChecked(self.settings.general.start_with_session)
        window_form.addRow("Monitor", self.monitor_combo)
        window_form.addRow("Width", self.width_spin)
        window_form.addRow("Height", self.height_spin)
        window_form.addRow("", self.always_on_top)
        window_form.addRow("", self.all_desktops)
        window_form.addRow("", self.frameless)
        window_form.addRow("", self.start_with_session)
        layout.addWidget(window)

        modules = QGroupBox("Modules")
        modules_layout = QVBoxLayout(modules)
        modules_layout.addWidget(QLabel("Enable modules and drag to reorder them."))
        self.modules_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        ordered = list(self.settings.modules.order)
        for module_id in MODULE_CLASSES:
            if module_id not in ordered:
                ordered.append(module_id)
        for module_id in ordered:
            cls = MODULE_CLASSES[module_id]
            item = QListWidgetItem(cls.metadata.title)
            item.setData(32, module_id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            state = (
                Qt.CheckState.Checked
                if self.settings.modules.active.get(module_id, module_id in self.settings.modules.order)
                else Qt.CheckState.Unchecked
            )
            item.setCheckState(state)
            self.modules_list.addItem(item)
        modules_layout.addWidget(self.modules_list)
        layout.addWidget(modules, stretch=1)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save(self) -> None:
        self.settings.general.theme = self.theme_combo.currentText()
        self.settings.general.update_interval_seconds = self.interval_spin.value()
        self.settings.window.opacity = self.opacity_spin.value() / 100
        self.settings.window.monitor = self.monitor_combo.currentText()
        self.settings.window.width = self.width_spin.value()
        self.settings.window.height = self.height_spin.value()
        self.settings.window.always_on_top = self.always_on_top.isChecked()
        self.settings.window.all_desktops = self.all_desktops.isChecked()
        self.settings.window.frameless = self.frameless.isChecked()
        self.settings.general.start_with_session = self.start_with_session.isChecked()
        order: list[str] = []
        active: dict[str, bool] = {}
        for row in range(self.modules_list.count()):
            item = self.modules_list.item(row)
            module_id = item.data(32)
            order.append(module_id)
            active[module_id] = item.checkState() == Qt.CheckState.Checked
        self.settings.modules.order = order
        self.settings.modules.active = active
        self.settings_saved.emit(self.settings)
        self.accept()
