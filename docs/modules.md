# Modules

## MVP v0.1

- System: hostname, uptime, kernel, distribution and Wayland/X11 session.
- CPU: model, usage, frequency and temperature when available.
- RAM: used, free, total and percentage.
- Disks: partitions, used/free space, percentage and filesystem type.
- Network: local IP, active interface and upload/download rates.

## Designed for v0.2

The codebase already includes optional read-only module classes for updates, Snapper and basic health. They are disabled unless users enable them in the settings panel.
