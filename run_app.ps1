# Phiversity - Auto Start Server
# Run this script in PowerShell to start the application

Write-Host "Starting Phiversity Application..." -ForegroundColor Green
Write-Host ""

# Determine virtual environment directory
$venvDir = if (Test-Path ".venv") { ".venv" } else { ".venv312" }

if (-not (Test-Path "$venvDir\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment from $venvDir..." -ForegroundColor Cyan
& "$venvDir\Scripts\Activate.ps1"

# Check and install dependencies
Write-Host "Checking dependencies..." -ForegroundColor Cyan
& python -m pip install -q -e . 2>$null

# Display server info
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Phiversity Server Starting..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "The application will be available at:" -ForegroundColor White
Write-Host "http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Run the server
& python -m uvicorn scripts.server.app:app --host 127.0.0.1 --port 8000 --reload

Read-Host "Press Enter to exit"
