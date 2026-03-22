#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "=== Updating apa-konyv ==="

# --- 1. Pull latest code ---
echo ""
echo "--- Pulling latest changes from git ---"
cd "$SCRIPT_DIR"

if ! command -v git &>/dev/null; then
    echo "ERROR: git is not installed."
    exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
    echo "WARNING: You have local changes. Stashing them before pull."
    git stash
    STASHED=1
else
    STASHED=0
fi

git pull --ff-only || {
    echo "ERROR: git pull failed. You may have diverged from the remote."
    echo "       Resolve manually with 'git pull --rebase' or 'git merge'."
    [ "$STASHED" -eq 1 ] && git stash pop
    exit 1
}

[ "$STASHED" -eq 1 ] && git stash pop

echo "Git pull: OK"

# --- 2. Reinstall / sync Python dependencies ---
echo ""
echo "--- Syncing Python dependencies ---"

if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Running full install..."
    bash "$SCRIPT_DIR/install.sh"
    exit 0
fi

"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
echo "Python dependencies: OK"

# --- 3. Verify everything works ---
echo ""
echo "--- Running checks ---"

ERRORS=0

if ! command -v tesseract &>/dev/null; then
    echo "FAIL: tesseract not found on PATH"
    ERRORS=$((ERRORS + 1))
else
    echo "CHECK: tesseract found"
    if ! tesseract --list-langs 2>&1 | grep -qi "hun"; then
        echo "WARN:  Hungarian language data not detected"
    else
        echo "CHECK: Hungarian language data present"
    fi
fi

if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "FAIL: Python venv missing"
    ERRORS=$((ERRORS + 1))
else
    echo "CHECK: Python venv exists"
fi

if ! "$VENV_DIR/bin/python" -c "import ocrmypdf" 2>/dev/null; then
    echo "FAIL: ocrmypdf not importable"
    ERRORS=$((ERRORS + 1))
else
    echo "CHECK: ocrmypdf importable"
fi

if [ ! -f "$SCRIPT_DIR/ocr_pdf.py" ]; then
    echo "FAIL: ocr_pdf.py not found"
    ERRORS=$((ERRORS + 1))
else
    echo "CHECK: ocr_pdf.py present"
fi

echo ""
if [ "$ERRORS" -gt 0 ]; then
    echo "=== Update finished with $ERRORS error(s). Run install.sh to fix. ==="
    exit 1
else
    echo "=== Update complete. Everything looks good! ==="
fi
