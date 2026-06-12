"""User-session autostart integration."""

from __future__ import annotations

import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)
AUTOSTART_DIR = Path.home() / ".config" / "autostart"
AUTOSTART_FILE = AUTOSTART_DIR / "plasmadeck.desktop"


def set_autostart(enabled: bool) -> None:
    """Enable or disable PlasmaDeck in the user's desktop-session autostart."""
    AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)
    if enabled:
        AUTOSTART_FILE.write_text(
            "\n".join(
                [
                    "[Desktop Entry]",
                    "Type=Application",
                    "Name=PlasmaDeck",
                    "Comment=Start PlasmaDeck dashboard with the Plasma session",
                    "Exec=plasmadeck",
                    "Icon=plasmadeck",
                    "Terminal=false",
                    "X-GNOME-Autostart-enabled=true",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        LOGGER.info("Enabled PlasmaDeck user-session autostart")
    elif AUTOSTART_FILE.exists():
        AUTOSTART_FILE.unlink()
        LOGGER.info("Disabled PlasmaDeck user-session autostart")
