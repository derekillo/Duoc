# PlasmaDeck

![PlasmaDeck logo](assets/logos/plasmadeck.svg)

PlasmaDeck is an open source, native Qt dashboard for KDE Plasma. It is designed to stay visible on a secondary monitor and present useful system, platform-health and technical productivity information through an elegant, configurable and modular interface.

PlasmaDeck is **not** an Electron app and is **not** intended to clone KDE System Monitor. It behaves more like a persistent Plasma-inspired information panel: lightweight, readable, read-only and extensible.

## Goals

- Feel native on KDE Plasma 6 with Breeze Light and Breeze Dark.
- Work on Wayland and X11 with HiDPI and multi-monitor setups.
- Provide a clean dashboard for Arch Linux, CachyOS, EndeavourOS, Fedora KDE and similar Plasma distributions.
- Keep the application modular so future cards can be added without rewriting the core.
- Avoid privileged operations and never mutate system configuration.

## Features in v0.1

- Persistent, resizable dashboard window.
- Optional always-on-top, borderless and tray behavior.
- Position, size, monitor, module order and refresh settings persisted in `~/.config/plasmadeck/config.json`.
- Dynamic KDE-aware light/dark theme detection.
- Rotating logs in `~/.local/share/plasmadeck/logs/`.
- Dedicated settings dialog for modules, opacity, refresh cadence, monitor and size.
- MVP modules:
  - System: hostname, uptime, kernel, distribution and session type.
  - CPU: model, usage, frequency and temperature when available.
  - RAM: used, free, total and percentage.
  - Disks: partitions, usage, free space and filesystem type.
  - Network: active interface, local IP and upload/download rates.
- Optional preview modules for v0.2 architecture: updates, Snapper and health.

## Technology stack

- Python 3.13+
- PySide6 / Qt6
- psutil
- JSON configuration
- Standard Python logging

No Electron, Node.js, React, Vue, Angular, embedded browsers or web frameworks are used.

## Installation

### From source

```bash
git clone https://example.org/plasmadeck/plasmadeck.git
cd plasmadeck
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Local user install

```bash
./install.sh
plasmadeck
```

The installer copies the application into `~/.local/share/plasmadeck`, links `~/.local/bin/plasmadeck`, installs the desktop entry and installs the SVG icon into the user icon theme directory.

### Uninstall

```bash
./uninstall.sh
```

User configuration and logs are intentionally preserved.

## Usage

Run:

```bash
python main.py
```

or, after installation:

```bash
plasmadeck
```

Use the **Settings** button or the system tray menu to configure:

- enabled modules,
- module order,
- opacity,
- update interval,
- monitor,
- window size,
- always-visible and borderless modes.

## Configuration

Configuration is stored at:

```text
~/.config/plasmadeck/config.json
```

If the JSON file is invalid, PlasmaDeck backs it up as `config.json.broken` and writes a fresh default configuration.

## Logging and diagnostics

Logs are written to:

```text
~/.local/share/plasmadeck/logs/plasmadeck.log
```

A basic rotating file handler keeps up to three old log files.

## Architecture

PlasmaDeck separates responsibilities into small packages:

```text
app/config    JSON settings and recovery
app/services  read-only Linux metric collectors
app/modules   independent dashboard modules
app/widgets   reusable Qt cards
app/ui        main window and settings dialog
app/themes    KDE/Breeze theme detection and palettes
app/utils     formatting, paths and logging
```

Each module subclasses `DashboardModule` and implements a `collect()` method. Future modules such as GPU AMD, SMART, advanced Btrfs, OBS Studio, Twitch, KDE Connect, Home Assistant, export metrics and plugin loading can be added through the registry without changing the main window shell.

More details are available in [`docs/architecture.md`](docs/architecture.md) and [`docs/modules.md`](docs/modules.md).

## Screenshot placeholders

Screenshots will be added under [`docs/screenshots/`](docs/screenshots/):

- Breeze Dark dashboard on a secondary monitor.
- Breeze Light dashboard.
- Settings dialog with module ordering.

## Roadmap

### v0.2

- Pacman and AUR update card refinements.
- Snapper card refinements.
- Health card with high temperature, high RAM, low disk and failing services indicators.

### Future

- AMD GPU telemetry.
- SMART and disk health.
- Advanced Btrfs details.
- OBS Studio and Twitch cards.
- KDE Connect and Home Assistant cards.
- Detachable widgets.
- Metrics export.
- Flatpak and Arch packaging.
- Plugin system.

## Security

PlasmaDeck is read-only. It does not require root, does not change system settings and does not run dangerous commands. Optional helper commands are informational only.

## License

PlasmaDeck is released under the MIT License. See [`LICENSE`](LICENSE).
