@echo off
REM Phiversity FastAPI Server Startup Script for Windows

echo.
echo ========================================
echo Phiversity - AI Video Generator
echo ========================================
echo.
echo Starting FastAPI server on http://localhost:8001
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

REM Select or create virtual environment
set VENV_DIR=
if exist ".venv" set VENV_DIR=.venv
if exist "venv" if "%VENV_DIR%"=="" set VENV_DIR=venv
if exist ".venv-1" if "%VENV_DIR%"=="" set VENV_DIR=.venv-1
if exist ".venv312" if "%VENV_DIR%"=="" set VENV_DIR=.venv312

if "%VENV_DIR%"=="" (
    echo Creating Python virtual environment...
    python -m venv venv
    set VENV_DIR=venv
)

REM Activate virtual environment
call %VENV_DIR%\Scripts\activate.bat

REM Check if dependencies are installed
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Start the server
echo.
echo Starting Phiversity server...
echo Open your browser to: http://localhost:8001
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn scripts.server.app:app --host 0.0.0.0 --port 8001 --reload

pause
