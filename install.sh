#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# System dependencies (macOS)
if command -v brew &>/dev/null; then
    brew list tesseract &>/dev/null    || brew install tesseract
    brew list tesseract-lang &>/dev/null || brew install tesseract-lang
else
    echo "Homebrew not found. Please install tesseract and tesseract-lang manually."
    exit 1
fi

# Create venv and install Python dependencies
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"

echo ""
echo "Setup complete. Usage:"
echo "  $VENV_DIR/bin/python $SCRIPT_DIR/ocr_pdf.py <input.pdf> <output.pdf>"
