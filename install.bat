@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"

echo === Checking system dependencies ===

where tesseract >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: tesseract is not installed or not on PATH.
    echo.
    echo Install options:
    echo   1. Download from https://github.com/UB-Mannheim/tesseract/wiki
    echo      During install, check "Additional language data" and select Hungarian.
    echo   2. Or via choco:  choco install tesseract
    echo      Then:          choco install tesseract-languages
    echo.
    echo After installing, make sure tesseract.exe is on your PATH and re-run this script.
    exit /b 1
)

tesseract --list-langs 2>&1 | findstr /i "hun" >nul
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Hungarian language data not found for Tesseract.
    echo Download hun.traineddata from https://github.com/tesseract-ocr/tessdata
    echo and place it in your Tesseract tessdata folder.
    echo.
)

echo Tesseract found: OK

echo.
echo === Setting up Python virtual environment ===

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: python is not installed or not on PATH.
    echo Download from https://www.python.org/downloads/
    exit /b 1
)

python -m venv "%VENV_DIR%"
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment.
    exit /b 1
)

call "%VENV_DIR%\Scripts\activate.bat"
pip install --upgrade pip
pip install -r "%SCRIPT_DIR%requirements.txt"

echo.
echo === Setup complete ===
echo.
echo Usage:
echo   %VENV_DIR%\Scripts\python %SCRIPT_DIR%ocr_pdf.py ^<input.pdf^> ^<output.pdf^>

endlocal
