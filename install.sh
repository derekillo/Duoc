#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/plasmadeck"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
ICON_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/scalable/apps"

mkdir -p "$APP_DIR" "$BIN_DIR" "$DESKTOP_DIR" "$ICON_DIR"
rsync -a --exclude '.git' --exclude '.venv' ./ "$APP_DIR/"
ln -sf "$APP_DIR/main.py" "$BIN_DIR/plasmadeck"
chmod +x "$APP_DIR/main.py"
cp plasmadeck.desktop "$DESKTOP_DIR/plasmadeck.desktop"
cp assets/icons/plasmadeck.svg "$ICON_DIR/plasmadeck.svg"

echo "PlasmaDeck installed. Ensure $BIN_DIR is in PATH, then run: plasmadeck"
