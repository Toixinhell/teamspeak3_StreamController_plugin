#!/usr/bin/env sh
set -eu

PLUGINS_ROOT="${HOME}/.var/app/com.core447.StreamController/data/plugins"
PLUGIN_DIR="${PLUGINS_ROOT}/com_toix_teamspeak3_clientquery"
OLD_PLUGIN_DIR="${PLUGINS_ROOT}/teamspeak3_StreamController_plugin"
SRC_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

mkdir -p "$PLUGIN_DIR"
rm -rf "$OLD_PLUGIN_DIR"

rsync -a --delete \
  --exclude '.git' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.mypy_cache' \
  --exclude '.pytest_cache' \
  "$SRC_DIR/" "$PLUGIN_DIR/"

echo "Installed plugin to: $PLUGIN_DIR"
echo "Now fully restart StreamController."
