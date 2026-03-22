#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "=== Checking system dependencies ==="

install_tesseract_macos() {
    if ! command -v brew &>/dev/null; then
        echo "ERROR: Homebrew not found. Install it from https://brew.sh or install tesseract manually."
        exit 1
    fi
    brew list tesseract &>/dev/null    || brew install tesseract
    brew list tesseract-lang &>/dev/null || brew install tesseract-lang

    # Ensure Homebrew Python with tkinter support for the GUI
    local PY_MAJOR_MINOR
    PY_MAJOR_MINOR="$(python3 -c 'import sys;print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "3.11")"
    brew list "python-tk@$PY_MAJOR_MINOR" &>/dev/null 2>&1 || brew install "python-tk@$PY_MAJOR_MINOR" 2>/dev/null || true
}

install_tesseract_linux() {
    if command -v apt-get &>/dev/null; then
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-hun python3-tk
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y tesseract tesseract-langpack-hun python3-tkinter
    elif command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm tesseract tesseract-data-hun tk
    else
        echo "ERROR: Could not detect package manager. Install tesseract and Hungarian language data manually."
        exit 1
    fi
}

case "$(uname -s)" in
    Darwin) install_tesseract_macos ;;
    Linux)  install_tesseract_linux ;;
    *)
        echo "ERROR: Unsupported OS '$(uname -s)'. Use install.bat on Windows."
        exit 1
        ;;
esac

if ! command -v tesseract &>/dev/null; then
    echo "ERROR: tesseract still not found after install attempt."
    exit 1
fi

if ! tesseract --list-langs 2>&1 | grep -qi "hun"; then
    echo "WARNING: Hungarian language data not detected. OCR may not work correctly."
fi

echo "Tesseract found: OK"

echo ""
echo "=== Setting up Python virtual environment ==="

PYTHON=""
# On macOS, prefer Homebrew Python which includes tkinter support for the GUI
if [ "$(uname -s)" = "Darwin" ] && [ -x "/opt/homebrew/bin/python3" ]; then
    PYTHON="/opt/homebrew/bin/python3"
elif [ "$(uname -s)" = "Darwin" ] && [ -x "/usr/local/bin/python3" ]; then
    PYTHON="/usr/local/bin/python3"
else
    for candidate in python3 python; do
        if command -v "$candidate" &>/dev/null; then
            PYTHON="$candidate"
            break
        fi
    done
fi

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python not found. Please install Python 3.8+."
    exit 1
fi

"$PYTHON" -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"

echo ""
echo "=== Setup complete ==="
echo ""
echo "Usage:"
echo "  GUI:     bash $SCRIPT_DIR/run_gui.sh"
echo "  CLI:     $VENV_DIR/bin/python $SCRIPT_DIR/ocr_pdf.py <input.pdf> <output.pdf>"
