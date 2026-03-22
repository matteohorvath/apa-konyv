@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"
set "ERRORS=0"

echo === Updating apa-konyv ===

REM --- 1. Pull latest code ---
echo.
echo --- Pulling latest changes from git ---

where git >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: git is not installed.
    exit /b 1
)

cd /d "%SCRIPT_DIR%"

git diff --quiet >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: You have local changes. Stashing them before pull.
    git stash
    set "STASHED=1"
) else (
    set "STASHED=0"
)

git pull --ff-only
if %errorlevel% neq 0 (
    echo ERROR: git pull failed. Resolve manually with 'git pull --rebase' or 'git merge'.
    if "%STASHED%"=="1" git stash pop
    exit /b 1
)

if "%STASHED%"=="1" git stash pop

echo Git pull: OK

REM --- 2. Reinstall / sync Python dependencies ---
echo.
echo --- Syncing Python dependencies ---

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo Virtual environment not found. Running full install...
    call "%SCRIPT_DIR%install.bat"
    exit /b %errorlevel%
)

call "%VENV_DIR%\Scripts\activate.bat"
pip install --upgrade pip
pip install -r "%SCRIPT_DIR%requirements.txt"
echo Python dependencies: OK

REM --- 3. Verify everything works ---
echo.
echo --- Running checks ---

where tesseract >nul 2>&1
if %errorlevel% neq 0 (
    echo FAIL: tesseract not found on PATH
    set /a ERRORS+=1
) else (
    echo CHECK: tesseract found
    tesseract --list-langs 2>&1 | findstr /i "hun" >nul
    if %errorlevel% neq 0 (
        echo WARN:  Hungarian language data not detected
    ) else (
        echo CHECK: Hungarian language data present
    )
)

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo FAIL: Python venv missing
    set /a ERRORS+=1
) else (
    echo CHECK: Python venv exists
)

"%VENV_DIR%\Scripts\python.exe" -c "import ocrmypdf" >nul 2>&1
if %errorlevel% neq 0 (
    echo FAIL: ocrmypdf not importable
    set /a ERRORS+=1
) else (
    echo CHECK: ocrmypdf importable
)

if not exist "%SCRIPT_DIR%ocr_pdf.py" (
    echo FAIL: ocr_pdf.py not found
    set /a ERRORS+=1
) else (
    echo CHECK: ocr_pdf.py present
)

echo.
if %ERRORS% gtr 0 (
    echo === Update finished with %ERRORS% error(s). Run install.bat to fix. ===
    exit /b 1
) else (
    echo === Update complete. Everything looks good! ===
)

endlocal
