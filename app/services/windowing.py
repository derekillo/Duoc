"""Best-effort window manager integration helpers."""

from __future__ import annotations

import logging
import os
import subprocess

from PySide6.QtWidgets import QWidget

LOGGER = logging.getLogger(__name__)


def request_all_desktops(window: QWidget, enabled: bool) -> None:
    """Ask X11 window managers to show the window on every virtual desktop.

    Wayland intentionally has no generic client-side API for this behavior, so
    this function becomes a no-op there while keeping the preference persisted.
    """
    if not enabled or os.environ.get("XDG_SESSION_TYPE", "").lower() != "x11":
        return
    win_id = int(window.winId())
    try:
        subprocess.run(
            ["xprop", "-id", str(win_id), "-f", "_NET_WM_DESKTOP", "32c", "-set", "_NET_WM_DESKTOP", "0xFFFFFFFF"],
            check=False,
            capture_output=True,
            timeout=2,
        )
    except (FileNotFoundError, subprocess.SubprocessError) as exc:
        LOGGER.debug("Could not request all-desktops window state: %s", exc)
