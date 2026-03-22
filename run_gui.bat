@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "VENV_PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
    echo Virtual environment not found. Running install first...
    call "%SCRIPT_DIR%install.bat"
)

start "" "%VENV_PYTHON%" "%SCRIPT_DIR%ocr_gui.py"

endlocal
