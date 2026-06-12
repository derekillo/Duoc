"""Tests for theme palette helpers."""

from __future__ import annotations

from app.themes.palette import DARK, LIGHT


def test_light_stylesheet_contains_breeze_accent():
    css = LIGHT.stylesheet(0.75)

    assert "#3daee9" in css
    assert "rgba(" in css


def test_dark_palette_is_named_breeze_dark():
    assert DARK.name == "Breeze Dark"
