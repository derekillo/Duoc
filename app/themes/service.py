"""KDE-aware theme detection and change notification."""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QGuiApplication

from app.themes.palette import DARK, LIGHT, ThemePalette

LOGGER = logging.getLogger(__name__)


class ThemeService(QObject):
    """Detect Breeze Light/Dark and emit updates while Plasma changes theme."""

    theme_changed = Signal(object)

    def __init__(self, mode: str = "auto", parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.mode = mode
        self._current = self.detect()
        self._timer = QTimer(self)
        self._timer.setInterval(2000)
        self._timer.timeout.connect(self._poll_theme)
        self._timer.start()

    @property
    def current(self) -> ThemePalette:
        """Return the currently selected palette."""
        return self._current

    def set_mode(self, mode: str) -> None:
        """Set theme mode: auto, light or dark."""
        self.mode = mode
        self._apply_if_changed(self.detect())

    def detect(self) -> ThemePalette:
        """Detect the best palette from explicit mode, KDE config and Qt hints."""
        if self.mode == "light":
            return LIGHT
        if self.mode == "dark":
            return DARK
        kde_scheme = _read_kde_color_scheme().lower()
        if "dark" in kde_scheme or "breezedark" in kde_scheme:
            return DARK
        if "light" in kde_scheme or "breeze" in kde_scheme:
            return LIGHT
        hints = QGuiApplication.styleHints() if QGuiApplication.instance() else None
        if hints is not None and hints.colorScheme().name.lower() == "dark":
            return DARK
        return DARK if _plasma_look_and_feel_is_dark() else LIGHT

    def _poll_theme(self) -> None:
        self._apply_if_changed(self.detect())

    def _apply_if_changed(self, palette: ThemePalette) -> None:
        if palette.name != self._current.name:
            LOGGER.info("Theme changed to %s", palette.name)
            self._current = palette
            self.theme_changed.emit(palette)


def _read_kde_color_scheme() -> str:
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    kdeglobals = config_home / "kdeglobals"
    if kdeglobals.exists():
        in_general = False
        for line in kdeglobals.read_text(encoding="utf-8", errors="ignore").splitlines():
            stripped = line.strip()
            if stripped == "[General]":
                in_general = True
                continue
            if stripped.startswith("["):
                in_general = False
            if in_general and stripped.startswith("ColorScheme="):
                return stripped.split("=", 1)[1]
    return ""


def _plasma_look_and_feel_is_dark() -> bool:
    try:
        result = subprocess.run(
            ["kreadconfig6", "--group", "KDE", "--key", "LookAndFeelPackage"],
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return False
    return "dark" in result.stdout.lower()
