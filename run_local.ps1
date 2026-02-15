# Phiversity Local Startup Script (PowerShell)

Write-Host "`n" -ForegroundColor Cyan
Write-Host "=================================================="  -ForegroundColor Cyan
Write-Host "   🚀 Starting Phiversity Locally" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Please install Python 3.10+" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install core dependencies
Write-Host "`n📦 Installing/checking dependencies..." -ForegroundColor Cyan
python -m pip install -q fastapi uvicorn pydantic python-dotenv groq 2>$null

Write-Host "`n✅ Dependencies ready!" -ForegroundColor Green

Write-Host "`n" -ForegroundColor Cyan
Write-Host "🌐 WEB APPLICATION URLs:" -ForegroundColor Green
Write-Host "   Main App:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "   API Docs:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "`n📝 API ENDPOINTS:" -ForegroundColor Green
Write-Host "   GET  /           - Access web UI" -ForegroundColor Cyan
Write-Host "   POST /run        - Generate animation" -ForegroundColor Cyan
Write-Host "   POST /test-llm   - Test LLM connection" -ForegroundColor Cyan
Write-Host "`n⏹️  Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the server
Write-Host "Starting FastAPI Server..." -ForegroundColor Cyan
Write-Host ("=" * 50) -ForegroundColor DarkGray
Write-Host ""

python -m uvicorn scripts.server.app:app --host 0.0.0.0 --port 8000 --reload
