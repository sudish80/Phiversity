@echo off
REM Phiversity - Auto Start Server

echo Starting Phiversity Application...
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    if not exist ".venv312" (
        echo Virtual environment not found!
        echo Please run: python -m venv .venv
        pause
        exit /b 1
    )
    set VENV_DIR=.venv312
) else (
    set VENV_DIR=.venv
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

