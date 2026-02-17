@echo off
REM ========================================
REM PHIVERSITY - Complete Application Launcher
REM AI-Powered Educational Video Generator
REM ========================================

color 0B
title Phiversity - AI Video Generator

:MENU
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║              🎬 PHIVERSITY - AI VIDEO GENERATOR 🎬         ║
echo ║                                                            ║
echo ║              Transform Questions into Amazing Videos       ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo    What would you like to do?
echo.
echo    [1] 🚀 Launch Web Application (Recommended)
echo    [2] 📱 Launch Desktop Mode (Fullscreen)
echo    [3] 🔧 Setup and Install Dependencies
echo    [4] 🔑 Configure API Keys
echo    [5] ✅ Test System Status
echo    [6] 📚 View Documentation
echo    [7] 🎯 Quick Demo
echo    [8] ❌ Exit
echo.
echo ════════════════════════════════════════════════════════════
echo.

set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" goto LAUNCH_WEB
if "%choice%"=="2" goto LAUNCH_DESKTOP
if "%choice%"=="3" goto SETUP
if "%choice%"=="4" goto CONFIG_KEYS
if "%choice%"=="5" goto TEST_STATUS
if "%choice%"=="6" goto DOCS
if "%choice%"=="7" goto DEMO
if "%choice%"=="8" goto EXIT
goto MENU

:LAUNCH_WEB
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo 🚀 Launching Phiversity Web Application...
echo ═══════════════════════════════════════════════════════════
echo.

REM Find virtual environment
set VENV_DIR=
if exist ".venv" set VENV_DIR=.venv
if exist "venv" if "%VENV_DIR%"=="" set VENV_DIR=venv
if exist ".venv-1" if "%VENV_DIR%"=="" set VENV_DIR=.venv-1
if exist ".venv312" if "%VENV_DIR%"=="" set VENV_DIR=.venv312

if "%VENV_DIR%"=="" (
    echo ❌ Virtual environment not found!
    echo.
    echo Please run option [3] to setup first.
    pause
    goto MENU
)

echo ✓ Found virtual environment: %VENV_DIR%
echo ✓ Activating environment...
call %VENV_DIR%\Scripts\activate.bat

echo ✓ Checking dependencies...
%VENV_DIR%\Scripts\pip install -q -e . 2>nul

echo.
echo ════════════════════════════════════════════════════════════
echo ✅ SERVER STARTING
echo ════════════════════════════════════════════════════════════
echo.
echo    🌐 Web Interface: http://127.0.0.1:8000
echo    📡 API Endpoint:  http://127.0.0.1:8000/api
echo.
echo    Opening browser in 3 seconds...
echo.
echo    Press Ctrl+C to stop the server
echo ════════════════════════════════════════════════════════════
echo.

timeout /t 3 /nobreak >nul
start http://127.0.0.1:8000

%VENV_DIR%\Scripts\python -m uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
goto MENU

:LAUNCH_DESKTOP
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo 📱 Launching Desktop Mode...
echo ═══════════════════════════════════════════════════════════
echo.

set VENV_DIR=
if exist ".venv" set VENV_DIR=.venv
if exist "venv" if "%VENV_DIR%"=="" set VENV_DIR=venv
if exist ".venv-1" if "%VENV_DIR%"=="" set VENV_DIR=.venv-1
if exist ".venv312" if "%VENV_DIR%"=="" set VENV_DIR=.venv312

if "%VENV_DIR%"=="" (
    echo ❌ Virtual environment not found!
    echo Please run option [3] to setup first.
    pause
    goto MENU
)

call %VENV_DIR%\Scripts\activate.bat
%VENV_DIR%\Scripts\pip install -q -e . 2>nul

echo ✓ Starting server in background...
start /B %VENV_DIR%\Scripts\python -m uvicorn api.app:app --host 127.0.0.1 --port 8000 2>nul

timeout /t 3 /nobreak >nul

echo ✓ Launching desktop app...
start /MAX http://127.0.0.1:8000

echo.
echo Desktop mode launched! Close browser to exit.
echo.
pause
goto MENU

:SETUP
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo 🔧 Setup and Installation
echo ═══════════════════════════════════════════════════════════
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    echo.
    echo Please install Python 3.9+ from:
    echo https://www.python.org/downloads/
    echo.
    pause
    goto MENU
)

echo ✓ Python found:
python --version
echo.

REM Create or find virtual environment
set VENV_DIR=
if exist ".venv" set VENV_DIR=.venv
if exist "venv" if "%VENV_DIR%"=="" set VENV_DIR=venv
if exist ".venv-1" if "%VENV_DIR%"=="" set VENV_DIR=.venv-1

if "%VENV_DIR%"=="" (
    echo Creating virtual environment...
    python -m venv .venv
    set VENV_DIR=.venv
    echo ✓ Virtual environment created: .venv
) else (
    echo ✓ Virtual environment found: %VENV_DIR%
)

echo.
echo Activating environment...
call %VENV_DIR%\Scripts\activate.bat

echo.
echo Installing dependencies...
echo This may take a few minutes...
echo.

%VENV_DIR%\Scripts\python -m pip install --upgrade pip
%VENV_DIR%\Scripts\pip install -e .
%VENV_DIR%\Scripts\pip install uvicorn fastapi aiofiles python-dotenv

echo.
echo ════════════════════════════════════════════════════════════
echo ✅ SETUP COMPLETE!
echo ════════════════════════════════════════════════════════════
echo.
echo Next step: Configure API keys (Option 4)
echo.
pause
goto MENU

:CONFIG_KEYS
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo 🔑 Configure API Keys
echo ═══════════════════════════════════════════════════════════
echo.

if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env from template...
        copy .env.example .env >nul
        echo ✓ .env file created
    ) else (
        echo Creating new .env file...
        (
            echo # Phiversity Configuration
            echo.
            echo # LLM API Keys (at least one required^)
            echo OPENAI_API_KEY=your_openai_key_here
            echo DEEPSEEK_API_KEY=your_deepseek_key_here
            echo GEMINI_API_KEY=your_gemini_key_here
            echo.
            echo # Voice API Keys (optional^)
            echo ELEVENLABS_API_KEY=your_elevenlabs_key_here
            echo.
            echo # Model Configuration
            echo OPENAI_MODEL=gpt-4o-mini
            echo DEEPSEEK_MODEL=deepseek-chat
            echo GEMINI_MODEL=gemini-1.5-flash
            echo VOICE_ENGINE=gtts
        ) > .env
        echo ✓ .env file created
    )
) else (
    echo ✓ .env file already exists
)

echo.
echo Opening .env file in notepad...
echo Please add your API keys and save the file.
echo.
notepad .env

echo.
echo ════════════════════════════════════════════════════════════
echo API Keys Configuration:
echo ════════════════════════════════════════════════════════════
echo.
echo Required (at least one):
echo   • OpenAI API Key    : https://platform.openai.com/api-keys
echo   • DeepSeek API Key  : https://platform.deepseek.com
echo   • Gemini API Key    : https://makersuite.google.com/app/apikey
echo.
echo Optional (for better voice):
echo   • ElevenLabs Key    : https://elevenlabs.io/
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
goto MENU

:TEST_STATUS
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo ✅ Testing System Status...
echo ═══════════════════════════════════════════════════════════
echo.

set VENV_DIR=
if exist ".venv" set VENV_DIR=.venv
if exist "venv" if "%VENV_DIR%"=="" set VENV_DIR=venv
if exist ".venv-1" if "%VENV_DIR%"=="" set VENV_DIR=.venv-1

if "%VENV_DIR%"=="" (
    echo ❌ Virtual environment not found!
    echo Please run option [3] to setup first.
    pause
    goto MENU
)

call %VENV_DIR%\Scripts\activate.bat

echo Testing dependencies...
echo.

%VENV_DIR%\Scripts\python -c "import fastapi; print('✓ FastAPI:', fastapi.__version__)"
%VENV_DIR%\Scripts\python -c "import manim; print('✓ Manim:', manim.__version__)"
%VENV_DIR%\Scripts\python -c "import openai; print('✓ OpenAI SDK installed')" 2>nul || echo ✗ OpenAI SDK not found

echo.
echo Checking API keys...
echo.

if exist "test\verify_llm_keys.py" (
    %VENV_DIR%\Scripts\python test\verify_llm_keys.py
) else (
    echo ℹ Test script not found
)

echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
goto MENU

:DOCS
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo 📚 Documentation
echo ═══════════════════════════════════════════════════════════
echo.
echo Opening documentation files...
echo.
if exist "README.md" start README.md
if exist "START_HERE.md" start START_HERE.md
if exist "GETTING_STARTED.md" start GETTING_STARTED.md
echo.
echo Available documentation:
echo.
if exist "README.md" echo   ✓ README.md
if exist "START_HERE.md" echo   ✓ START_HERE.md
if exist "GETTING_STARTED.md" echo   ✓ GETTING_STARTED.md
if exist "QUICK_INTEGRATION_GUIDE.md" echo   ✓ QUICK_INTEGRATION_GUIDE.md
echo.
pause
goto MENU

:DEMO
cls
echo.
echo ═══════════════════════════════════════════════════════════
echo 🎯 Quick Demo
echo ═══════════════════════════════════════════════════════════
echo.
echo This will generate a sample video with the question:
echo "Explain angular momentum conservation in collisions"
echo.
pause

set VENV_DIR=
if exist ".venv" set VENV_DIR=.venv
if exist "venv" if "%VENV_DIR%"=="" set VENV_DIR=venv
if exist ".venv-1" if "%VENV_DIR%"=="" set VENV_DIR=.venv-1

if "%VENV_DIR%"=="" (
    echo ❌ Virtual environment not found!
    echo Please run option [3] to setup first.
    pause
    goto MENU
)

call %VENV_DIR%\Scripts\activate.bat

echo Running demo...
echo.
%VENV_DIR%\Scripts\python -m scripts.pipeline --question "Explain angular momentum conservation in collisions" --out-dir media/videos/demo

echo.
echo ════════════════════════════════════════════════════════════
echo Demo complete! Check media/videos/demo for output.
echo ════════════════════════════════════════════════════════════
echo.
pause
goto MENU

:EXIT
cls
echo.
echo ════════════════════════════════════════════════════════════
echo.
echo   Thank you for using Phiversity! 🎬
echo.
echo   Visit: https://github.com/phiversity
echo.
echo ════════════════════════════════════════════════════════════
echo.
timeout /t 2 /nobreak >nul
exit

