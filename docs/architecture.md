# Architecture

PlasmaDeck is a native Qt dashboard with a small core and independent modules.

## Layers

- `main.py`: starts Qt, logging, configuration and the main window.
- `app/config`: dataclass settings plus robust JSON persistence in `~/.config/plasmadeck/config.json`.
- `app/services`: read-only operating system data collectors.
- `app/modules`: independent module classes exposing a `collect()` method.
- `app/widgets`: reusable Qt widgets such as module cards.
- `app/ui`: windows and dialogs.
- `app/themes`: Breeze Light/Dark palette detection and dynamic stylesheet updates.
- `app/utils`: formatting, paths and logging helpers.

## Extensibility

New modules should subclass `DashboardModule`, define `ModuleMetadata`, implement `collect()` and register the class in `app/modules/registry.py`. This keeps future GPU, SMART, Btrfs, OBS, Twitch, KDE Connect and Home Assistant integrations out of the application shell.

## Security model

PlasmaDeck is read-only. Services may inspect `/proc`, `/etc/os-release` and psutil APIs. Optional helpers such as `checkupdates`, `paru -Qua` or `snapper list` are informational and run without root.
