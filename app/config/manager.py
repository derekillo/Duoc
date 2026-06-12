"""Robust JSON configuration loading and saving."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from app.config.settings import AppSettings

LOGGER = logging.getLogger(__name__)
CONFIG_DIR = Path.home() / ".config" / "plasmadeck"
CONFIG_FILE = CONFIG_DIR / "config.json"


class ConfigManager:
    """Manage PlasmaDeck configuration stored in the user's config directory."""

    def __init__(self, path: Path = CONFIG_FILE) -> None:
        self.path = path
        self.settings = AppSettings()

    def load(self) -> AppSettings:
        """Load settings from disk with recovery for malformed JSON."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.save(self.settings)
            return self.settings
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Config root must be an object")
            self.settings = AppSettings.from_dict(data)
        except Exception as exc:  # noqa: BLE001 - recovery must catch any read/parse error.
            LOGGER.warning("Recovering from invalid configuration: %s", exc)
            backup = self.path.with_suffix(".json.broken")
            try:
                self.path.replace(backup)
            except OSError as backup_exc:
                LOGGER.error("Could not back up invalid config: %s", backup_exc)
            self.settings = AppSettings()
            self.save(self.settings)
        return self.settings

    def save(self, settings: AppSettings | None = None) -> None:
        """Persist settings atomically."""
        if settings is not None:
            self.settings = settings
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(".json.tmp")
        temp_path.write_text(
            json.dumps(self.settings.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temp_path.replace(self.path)

    def update(self, values: dict[str, Any]) -> AppSettings:
        """Merge a dictionary into settings and save."""
        data = self.settings.to_dict()
        for section, section_values in values.items():
            if isinstance(section_values, dict) and isinstance(data.get(section), dict):
                data[section].update(section_values)
            else:
                data[section] = section_values
        self.settings = AppSettings.from_dict(data)
        self.save()
        return self.settings
