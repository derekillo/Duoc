"""Tests for robust settings persistence."""

from __future__ import annotations

from app.config.manager import ConfigManager
from app.config.settings import AppSettings


def test_config_round_trip(tmp_path):
    path = tmp_path / "config.json"
    manager = ConfigManager(path)
    settings = AppSettings()
    settings.window.width = 1200
    settings.window.opacity = 0.5
    manager.save(settings)

    loaded = ConfigManager(path).load()

    assert loaded.window.width == 1200
    assert loaded.window.opacity == 0.5


def test_invalid_config_recovers(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("not json", encoding="utf-8")

    loaded = ConfigManager(path).load()

    assert loaded.window.width == AppSettings().window.width
    assert path.exists()
    assert path.with_suffix(".json.broken").exists()
