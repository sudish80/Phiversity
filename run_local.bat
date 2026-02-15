@echo off
REM Phiversity Local Startup Script
echo.
echo ==================================================
echo   🚀 Starting Phiversity Locally
echo ==================================================
echo.

REM Check Python
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Install dependencies if needed
echo.
echo 📦 Checking dependencies...
python -m pip install -q fastapi uvicorn pydantic python-dotenv groq

echo.
echo ✅ Starting FastAPI Server...
echo.
echo 🌐 Access the web app at:
echo    👉 http://localhost:8000
echo.
echo 📚 API Documentation at:
echo    👉 http://localhost:8000/docs
echo.
echo ⏹️  Press Ctrl+C to stop the server
echo.

REM Start the server
python -m uvicorn scripts.server.app:app --host 0.0.0.0 --port 8000 --reload
