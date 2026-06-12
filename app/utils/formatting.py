"""Formatting helpers for system metrics."""

from __future__ import annotations


def bytes_to_human(value: float) -> str:
    """Convert a byte value into a compact binary unit string."""
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    size = float(value)
    for unit in units:
        if abs(size) < 1024.0 or unit == units[-1]:
            return f"{size:.1f} {unit}" if unit != "B" else f"{size:.0f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PiB"


def seconds_to_uptime(seconds: float) -> str:
    """Format seconds as a human-readable uptime."""
    total = int(max(0, seconds))
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, _ = divmod(rem, 60)
    if days:
        return f"{days}d {hours}h {minutes}m"
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def rate_to_human(bytes_per_second: float) -> str:
    """Format a network byte rate."""
    return f"{bytes_to_human(bytes_per_second)}/s"
