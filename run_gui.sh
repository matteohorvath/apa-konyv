#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
VENV_PYTHON="$VENV_DIR/bin/python"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Virtual environment not found. Running install first..."
    bash "$SCRIPT_DIR/install.sh"
fi

exec "$VENV_PYTHON" "$SCRIPT_DIR/ocr_gui.py"
