"""Tests for metric service formatting and collection contracts."""

from __future__ import annotations

import pytest

pytest.importorskip("psutil")

from app.services.system_info import MetricRow, SystemInfoService
from app.utils.formatting import bytes_to_human, seconds_to_uptime


def test_formatting_helpers():
    assert bytes_to_human(1024) == "1.0 KiB"
    assert seconds_to_uptime(3660) == "1h 1m"


def test_system_rows_contract():
    rows = SystemInfoService().system_rows()

    assert rows
    assert all(isinstance(row, MetricRow) for row in rows)
