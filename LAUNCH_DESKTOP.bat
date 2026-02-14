@echo off
REM Launch Phiversity Desktop App

title Phiversity Desktop Launcher

echo Starting Phiversity Desktop App...

REM Find virtual environment
set VENV_DIR=
if exist ".venv" set VENV_DIR=.venv
if exist "venv" if "%VENV_DIR%"=="" set VENV_DIR=venv
if exist ".venv-1" if "%VENV_DIR%"=="" set VENV_DIR=.venv-1

if "%VENV_DIR%"=="" (
    echo Virtual environment not found!
    echo Running with system Python...
    python launch_desktop.py
) else (
    echo Found virtual environment: %VENV_DIR%
    %VENV_DIR%\Scripts\python.exe launch_desktop.py
)

pause
