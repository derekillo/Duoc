"""Tests for module registration."""

from __future__ import annotations

import pytest

pytest.importorskip("psutil")

from app.modules.registry import MODULE_CLASSES, ModuleRegistry


def test_registry_contains_mvp_modules():
    for module_id in ["system", "cpu", "memory", "disks", "network"]:
        assert module_id in MODULE_CLASSES


def test_registry_ignores_unknown_modules():
    modules = ModuleRegistry().create(["system", "unknown"])

    assert len(modules) == 1
    assert modules[0].metadata.module_id == "system"
