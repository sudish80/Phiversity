@echo off
REM Phiversity - Auto Start Server

echo Starting Phiversity Application...
echo.

REM Check if virtual environment exists
set VENV_DIR=
if exist ".venv" set VENV_DIR=.venv
if exist "venv" if "%VENV_DIR%"=="" set VENV_DIR=venv
if exist ".venv-1" if "%VENV_DIR%"=="" set VENV_DIR=.venv-1
if exist ".venv312" if "%VENV_DIR%"=="" set VENV_DIR=.venv312

if "%VENV_DIR%"=="" (
    echo Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment from %VENV_DIR%...
call %VENV_DIR%\Scripts\activate.bat

REM Check if dependencies are installed
echo Checking dependencies...
%VENV_DIR%\Scripts\pip install -q -e . 2>nul

REM Display server info
echo.
echo ========================================
echo Phiversity Server Starting...
echo ========================================
echo.
echo The application will be available at:
echo http://127.0.0.1:8000
echo.
echo Opening browser in 3 seconds...
echo.
timeout /t 3 /nobreak

REM Open browser
start http://127.0.0.1:8000

REM Run the server
echo.
echo Server is running. Press Ctrl+C to stop.
echo ========================================
echo.

%VENV_DIR%\Scripts\python -m uvicorn scripts.server.app:app --host 127.0.0.1 --port 8000 --reload

pause

