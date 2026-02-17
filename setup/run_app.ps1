# Phiversity - Auto Start Server
# Run this script in PowerShell to start the application

Write-Host "Starting Phiversity Application..." -ForegroundColor Green
Write-Host ""

# Determine virtual environment directory
$venvDir = $null
if (Test-Path ".venv") {
    $venvDir = ".venv"
} elseif (Test-Path "venv") {
    $venvDir = "venv"
} elseif (Test-Path ".venv-1") {
    $venvDir = ".venv-1"
} elseif (Test-Path ".venv312") {
    $venvDir = ".venv312"
}

if (-not $venvDir -or -not (Test-Path "$venvDir\Scripts\Activate.ps1")) {
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
Write-Host "Opening browser in 3 seconds..." -ForegroundColor Yellow
Write-Host ""

# Wait 3 seconds
Start-Sleep -Seconds 3

# Open browser
Start-Process "http://127.0.0.1:8000"

# Run the server
Write-Host "Server is running. Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

& python -m uvicorn scripts.server.app:app --host 127.0.0.1 --port 8000 --reload

Read-Host "Press Enter to exit"
