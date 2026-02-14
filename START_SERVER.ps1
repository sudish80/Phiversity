# Phiversity FastAPI Server Startup Script for Windows PowerShell

Write-Host ""
Write-Host "========================================"
Write-Host "Phiversity - AI Video Generator" -ForegroundColor Cyan
Write-Host "========================================"
Write-Host ""
Write-Host "Starting FastAPI server on http://localhost:8001"
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[+] Python found: $pythonVersion"
}
catch {
    Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Select or create virtual environment
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

if (-not $venvDir) {
    Write-Host ""
    Write-Host "Creating Python virtual environment..."
    python -m venv venv
    $venvDir = "venv"
}

# Activate virtual environment
Write-Host "Activating virtual environment from $venvDir..."
& "$venvDir\Scripts\Activate.ps1"

# Check if dependencies are installed
Write-Host "Checking dependencies..."
$fastAPICheck = pip show fastapi 2>&1 | Select-Object -First 1
if (-not $fastAPICheck) {
    Write-Host "Installing dependencies (this may take a minute)..."
    pip install -r requirements.txt
}

# Start the server
Write-Host ""
Write-Host "Starting Phiversity server..." -ForegroundColor Green
Write-Host "Open your browser to: http://localhost:8001" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server"
Write-Host ""

python -m uvicorn scripts.server.app:app --host 0.0.0.0 --port 8001 --reload

Read-Host "Server stopped. Press Enter to exit"
