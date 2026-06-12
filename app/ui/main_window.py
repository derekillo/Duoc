"""Main persistent dashboard window."""

from __future__ import annotations

import logging

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QAction, QCloseEvent, QIcon, QGuiApplication
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QScrollArea,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from app.config.manager import ConfigManager
from app.config.settings import AppSettings
from app.modules.registry import ModuleRegistry
from app.services.autostart import set_autostart
from app.services.windowing import request_all_desktops
from app.themes.service import ThemeService
from app.ui.settings_dialog import SettingsDialog
from app.utils.paths import ASSETS_DIR
from app.widgets.module_card import ModuleCard

LOGGER = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Persistent KDE Plasma dashboard window."""

    def __init__(self, config: ConfigManager, registry: ModuleRegistry) -> None:
        super().__init__()
        self.config = config
        self.settings = config.settings
        self.registry = registry
        self.theme_service = ThemeService(self.settings.general.theme, self)
        self.cards: list[ModuleCard] = []
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_modules)
        self.setObjectName("DashboardWindow")
        self.setWindowTitle("PlasmaDeck")
        self.setWindowIcon(QIcon(str(ASSETS_DIR / "icons" / "plasmadeck.svg")))
        self._build_ui()
        self._build_tray()
        self._restore_geometry()
        self._apply_window_flags()
        set_autostart(self.settings.general.start_with_session)
        self._apply_theme()
        self.theme_service.theme_changed.connect(lambda _palette: self._apply_theme())
        self.refresh_timer.start(self.settings.general.update_interval_seconds * 1000)
        self.refresh_modules()

    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("DashboardWindow")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(22, 20, 22, 22)
        root_layout.setSpacing(18)

        header = QHBoxLayout()
        title = QLabel("PlasmaDeck")
        title.setObjectName("AppTitle")
        subtitle = QLabel("Native KDE Plasma dashboard")
        subtitle.setObjectName("MetricLabel")
        title_box = QVBoxLayout()
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch(1)
        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.open_settings)
        header.addWidget(settings_button)
        root_layout.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.content = QWidget()
        self.grid = QGridLayout(self.content)
        self.grid.setSpacing(16)
        self.scroll.setWidget(self.content)
        root_layout.addWidget(self.scroll, stretch=1)
        self.setCentralWidget(root)
        self.rebuild_modules()

    def _build_tray(self) -> None:
        self.tray = QSystemTrayIcon(self.windowIcon(), self)
        menu = QMenu()
        show_action = QAction("Show PlasmaDeck", self)
        show_action.triggered.connect(self.showNormal)
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(show_action)
        menu.addAction(settings_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def _restore_geometry(self) -> None:
        self.resize(self.settings.window.width, self.settings.window.height)
        target = self._target_screen()
        if self.settings.window.x is not None and self.settings.window.y is not None:
            self.move(self.settings.window.x, self.settings.window.y)
        elif target is not None:
            geometry = target.availableGeometry()
            self.move(geometry.x() + 48, geometry.y() + 48)

    def _target_screen(self):
        screens = QGuiApplication.screens()
        if self.settings.window.monitor:
            for screen in screens:
                if screen.name() == self.settings.window.monitor:
                    return screen
        return screens[-1] if screens else None

    def _apply_window_flags(self) -> None:
        flags = Qt.WindowType.Window
        if self.settings.window.always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        if self.settings.window.frameless:
            flags |= Qt.WindowType.FramelessWindowHint
        self.setWindowFlags(flags)
        self.setWindowOpacity(self.settings.window.opacity)
        request_all_desktops(self, self.settings.window.all_desktops)

    def _apply_theme(self) -> None:
        palette = self.theme_service.current
        self.setStyleSheet(palette.stylesheet(self.settings.window.opacity))

    def rebuild_modules(self) -> None:
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        active_ids = [
            module_id
            for module_id in self.settings.modules.order
            if self.settings.modules.active.get(module_id, False)
        ]
        self.cards = [ModuleCard(module) for module in self.registry.create(active_ids)]
        for index, card in enumerate(self.cards):
            self.grid.addWidget(card, index // 2, index % 2)

    def refresh_modules(self) -> None:
        """Refresh all enabled module cards."""
        for card in self.cards:
            card.refresh()

    def open_settings(self) -> None:
        """Open the dedicated graphical settings panel."""
        screen_names = [screen.name() for screen in QGuiApplication.screens()]
        dialog = SettingsDialog(self.settings, screen_names, self)
        dialog.settings_saved.connect(self.apply_settings)
        dialog.exec()

    def apply_settings(self, settings: AppSettings) -> None:
        """Apply settings from the settings dialog and persist them."""
        self.settings = settings
        self.config.save(settings)
        set_autostart(settings.general.start_with_session)
        self.theme_service.set_mode(settings.general.theme)
        self.refresh_timer.start(settings.general.update_interval_seconds * 1000)
        self._apply_window_flags()
        self._apply_theme()
        self.resize(settings.window.width, settings.window.height)
        self.rebuild_modules()
        self.show()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 - Qt API name.
        """Persist geometry and optionally minimize to tray."""
        self.settings.window.width = self.width()
        self.settings.window.height = self.height()
        self.settings.window.x = self.x()
        self.settings.window.y = self.y()
        self.config.save(self.settings)
        if self.settings.window.minimize_to_tray and self.tray.isVisible():
            event.ignore()
            self.hide()
            LOGGER.info("Dashboard hidden to system tray")
        else:
            super().closeEvent(event)
