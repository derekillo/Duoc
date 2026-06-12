"""Theme palette definitions for KDE-like light and dark modes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ThemePalette:
    """Colors used by PlasmaDeck stylesheets."""

    name: str
    background: str
    surface: str
    surface_alt: str
    text: str
    muted: str
    accent: str
    border: str

    def stylesheet(self, opacity: float = 0.94) -> str:
        """Return a Qt stylesheet for the dashboard."""
        alpha = int(min(1.0, max(0.25, opacity)) * 255)
        background_rgba = _hex_to_rgba(self.background, alpha)
        return f"""
        QWidget#DashboardWindow {{
            background-color: {background_rgba};
            color: {self.text};
            font-family: system-ui;
        }}
        QFrame#ModuleCard {{
            background-color: {self.surface};
            border: 1px solid {self.border};
            border-radius: 18px;
        }}
        QLabel#AppTitle {{
            color: {self.text};
            font-size: 24px;
            font-weight: 700;
        }}
        QLabel#ModuleTitle {{
            color: {self.text};
            font-size: 16px;
            font-weight: 700;
        }}
        QLabel#MetricLabel {{ color: {self.muted}; }}
        QLabel#MetricValue {{ color: {self.text}; font-weight: 600; }}
        QPushButton {{
            background-color: {self.surface_alt};
            border: 1px solid {self.border};
            border-radius: 10px;
            padding: 8px 12px;
            color: {self.text};
        }}
        QPushButton:hover {{ border-color: {self.accent}; }}
        QSlider::groove:horizontal {{ background: {self.surface_alt}; height: 6px; border-radius: 3px; }}
        QSlider::handle:horizontal {{ background: {self.accent}; width: 16px; border-radius: 8px; }}
        QCheckBox, QComboBox, QSpinBox {{ color: {self.text}; }}
        """


LIGHT = ThemePalette(
    name="Breeze Light",
    background="#eff0f1",
    surface="#fcfcfc",
    surface_alt="#f3f4f5",
    text="#232629",
    muted="#6f7782",
    accent="#3daee9",
    border="#d4d8dd",
)

DARK = ThemePalette(
    name="Breeze Dark",
    background="#1b1e20",
    surface="#2a2e32",
    surface_alt="#31363b",
    text="#eff0f1",
    muted="#bdc3c7",
    accent="#3daee9",
    border="#4b5157",
)


def _hex_to_rgba(hex_color: str, alpha: int) -> str:
    stripped = hex_color.lstrip("#")
    red = int(stripped[0:2], 16)
    green = int(stripped[2:4], 16)
    blue = int(stripped[4:6], 16)
    return f"rgba({red}, {green}, {blue}, {alpha})"
