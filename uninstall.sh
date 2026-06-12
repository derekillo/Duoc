#!/usr/bin/env bash
set -euo pipefail

rm -f "$HOME/.local/bin/plasmadeck"
rm -f "${XDG_DATA_HOME:-$HOME/.local/share}/applications/plasmadeck.desktop"
rm -f "${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/scalable/apps/plasmadeck.svg"
rm -rf "${XDG_DATA_HOME:-$HOME/.local/share}/plasmadeck"

echo "PlasmaDeck application files removed. User config and logs were kept intentionally."
