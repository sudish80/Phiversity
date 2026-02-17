@echo off
REM Fine-tune Domain-Restricted LLM - Windows Launcher
REM Double-click this file or run from PowerShell: .\run_finetune.bat

echo ===============================================================================
echo   DOMAIN-RESTRICTED LLM FINE-TUNING
echo ===============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python detected. Starting fine-tuning script...
echo.

REM Run the Python script
python finetune_terminal.py

echo.
echo ===============================================================================
echo Script completed. Press any key to exit.
pause >nul
