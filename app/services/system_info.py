"""Read-only system information collection services."""

from __future__ import annotations

import os
import platform
import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import psutil

from app.utils.formatting import bytes_to_human, rate_to_human, seconds_to_uptime


@dataclass(frozen=True, slots=True)
class MetricRow:
    """A displayable metric row."""

    label: str
    value: str
    accent: str | None = None


class SystemInfoService:
    """Collect read-only Linux desktop metrics for dashboard modules."""

    def __init__(self) -> None:
        self._last_net = psutil.net_io_counters(pernic=True)
        self._last_net_time = time.monotonic()

    def system_rows(self) -> list[MetricRow]:
        """Return host, kernel, distribution and session information."""
        uptime = time.time() - psutil.boot_time()
        return [
            MetricRow("Hostname", socket.gethostname()),
            MetricRow("Uptime", seconds_to_uptime(uptime)),
            MetricRow("Kernel", platform.release()),
            MetricRow("Distribution", _distribution_name()),
            MetricRow("Session", _session_type()),
        ]

    def cpu_rows(self) -> list[MetricRow]:
        """Return CPU model, usage, frequency and temperature information."""
        freq = psutil.cpu_freq()
        temperature = _cpu_temperature()
        return [
            MetricRow("Model", _cpu_model()),
            MetricRow("Usage", f"{psutil.cpu_percent(interval=None):.0f}%"),
            MetricRow("Frequency", f"{freq.current:.0f} MHz" if freq else "Unavailable"),
            MetricRow("Temperature", temperature),
        ]

    def memory_rows(self) -> list[MetricRow]:
        """Return memory usage information."""
        memory = psutil.virtual_memory()
        return [
            MetricRow("Used", bytes_to_human(memory.used)),
            MetricRow("Free", bytes_to_human(memory.available)),
            MetricRow("Total", bytes_to_human(memory.total)),
            MetricRow("Usage", f"{memory.percent:.0f}%"),
        ]

    def disk_rows(self) -> list[MetricRow]:
        """Return mounted physical partition usage information."""
        rows: list[MetricRow] = []
        for partition in psutil.disk_partitions(all=False):
            if partition.fstype in {"", "tmpfs", "devtmpfs", "squashfs"}:
                continue
            try:
                usage = psutil.disk_usage(partition.mountpoint)
            except OSError:
                continue
            rows.append(
                MetricRow(
                    partition.mountpoint,
                    f"{bytes_to_human(usage.used)} used · "
                    f"{bytes_to_human(usage.free)} free · {usage.percent:.0f}% · "
                    f"{partition.fstype}",
                )
            )
        return rows or [MetricRow("Partitions", "No readable partitions")]

    def network_rows(self) -> list[MetricRow]:
        """Return active interface, local IP and transfer rates."""
        now = time.monotonic()
        current = psutil.net_io_counters(pernic=True)
        elapsed = max(0.001, now - self._last_net_time)
        interface = _active_interface()
        previous = self._last_net.get(interface) if interface else None
        counter = current.get(interface) if interface else None
        upload = download = 0.0
        if previous and counter:
            upload = max(0, counter.bytes_sent - previous.bytes_sent) / elapsed
            download = max(0, counter.bytes_recv - previous.bytes_recv) / elapsed
        self._last_net = current
        self._last_net_time = now
        return [
            MetricRow("Interface", interface or "Unavailable"),
            MetricRow("Local IP", _local_ip(interface)),
            MetricRow("Upload", rate_to_human(upload)),
            MetricRow("Download", rate_to_human(download)),
        ]

    def update_rows(self) -> list[MetricRow]:
        """Return package update counts when optional tools are available."""
        return [
            MetricRow("Pacman", _safe_count_command(["checkupdates"])),
            MetricRow("AUR", _safe_count_command(["paru", "-Qua"])),
        ]

    def snapper_rows(self) -> list[MetricRow]:
        """Return basic Snapper snapshot status when available."""
        result = _safe_command(["snapper", "list", "--csvout"])
        if not result:
            return [MetricRow("Snapshots", "Snapper unavailable")]
        lines = [line for line in result.splitlines() if line.strip()]
        last = lines[-1].split("|")[0].strip() if len(lines) > 1 else "None"
        return [MetricRow("Count", str(max(0, len(lines) - 1))), MetricRow("Latest", last)]

    def health_rows(self) -> list[MetricRow]:
        """Return simple health warnings without changing system state."""
        warnings: list[str] = []
        memory = psutil.virtual_memory()
        if memory.percent >= 85:
            warnings.append(f"RAM high ({memory.percent:.0f}%)")
        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)
            except OSError:
                continue
            if usage.percent >= 90:
                warnings.append(f"Low disk space on {partition.mountpoint}")
        temp = _cpu_temperature_value()
        if temp is not None and temp >= 85:
            warnings.append(f"CPU temperature high ({temp:.0f}°C)")
        return [MetricRow("Status", "Healthy" if not warnings else " · ".join(warnings))]


def _distribution_name() -> str:
    os_release = Path("/etc/os-release")
    if os_release.exists():
        data = os_release.read_text(encoding="utf-8", errors="ignore")
        for line in data.splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.split("=", 1)[1].strip().strip('"')
    return platform.platform()


def _session_type() -> str:
    session = os.environ.get("XDG_SESSION_TYPE", "unknown")
    return session.capitalize()


def _cpu_model() -> str:
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.exists():
        for line in cpuinfo.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.lower().startswith("model name"):
                return line.split(":", 1)[1].strip()
    return platform.processor() or "Unavailable"


def _cpu_temperature_value() -> float | None:
    try:
        temperatures = psutil.sensors_temperatures(fahrenheit=False)
    except (AttributeError, OSError):
        return None
    for entries in temperatures.values():
        for entry in entries:
            label = (entry.label or "").lower()
            if "cpu" in label or "package" in label or entry.current:
                return float(entry.current)
    return None


def _cpu_temperature() -> str:
    value = _cpu_temperature_value()
    return f"{value:.0f}°C" if value is not None else "Unavailable"


def _active_interface() -> str | None:
    stats = psutil.net_if_stats()
    addresses = psutil.net_if_addrs()
    for name, stat in stats.items():
        if not stat.isup or name == "lo":
            continue
        if any(addr.family == socket.AF_INET for addr in addresses.get(name, [])):
            return name
    return None


def _local_ip(interface: str | None) -> str:
    if interface:
        for address in psutil.net_if_addrs().get(interface, []):
            if address.family == socket.AF_INET:
                return address.address
    return "Unavailable"


def _safe_command(command: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=8,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None
    if completed.returncode not in {0, 2}:
        return None
    return completed.stdout.strip()


def _safe_count_command(command: list[str]) -> str:
    output = _safe_command(command)
    if output is None:
        return "Tool unavailable"
    if not output:
        return "0 pending"
    return f"{len(output.splitlines())} pending"
