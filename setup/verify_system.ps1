#!/usr/bin/env pwsh
# Quick Verification Script - Tests all critical system components

Write-Host "`n==================================================" -ForegroundColor Cyan
Write-Host "   PHIVERSITY SYSTEM VERIFICATION" -ForegroundColor Cyan
Write-Host "==================================================`n" -ForegroundColor Cyan

$allPassed = $true

# Test 1: Check if server is running
Write-Host "[1/6] Health Check..." -NoNewline
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:8002/health" -TimeoutSec 5 -ErrorAction Stop
    if ($health.status -eq "ok") {
        Write-Host " PASS" -ForegroundColor Green
    } else {
        Write-Host " FAIL" -ForegroundColor Red
        $allPassed = $false
    }
} catch {
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:8001/health" -TimeoutSec 5 -ErrorAction Stop
        if ($health.status -eq "ok") {
            Write-Host " PASS (port 8001)" -ForegroundColor Green
        } else {
            Write-Host " FAIL" -ForegroundColor Red
            $allPassed = $false
        }
    } catch {
        Write-Host " FAIL - Server not responding" -ForegroundColor Red
        $allPassed = $false
    }
}

# Test 2: Check Python environment
Write-Host "[2/6] Python Environment..." -NoNewline
$pythonExe = ".\venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = ".\.venv\Scripts\python.exe"
}
if (Test-Path $pythonExe) {
    $pyVersion = & $pythonExe --version 2>&1
    Write-Host " PASS ($pyVersion)" -ForegroundColor Green
} else {
    Write-Host " FAIL - Virtual environment not found" -ForegroundColor Red
    $allPassed = $false
}

# Test 3: Check .env file
Write-Host "[3/6] Environment Configuration..." -NoNewline
if (Test-Path ".env") {
    $envContent = Get-Content .env -Raw
    if ($envContent -match "GEMINI_API_KEY" -and $envContent -match "VOICE_ENGINE") {
        Write-Host " PASS" -ForegroundColor Green
    } else {
        Write-Host " WARN - Missing keys" -ForegroundColor Yellow
    }
} else {
    Write-Host " FAIL - .env file not found" -ForegroundColor Red
    $allPassed = $false
}

# Test 4: Check critical dependencies
Write-Host "[4/6] Critical Dependencies..." -NoNewline
try {
    $pipList = & $pythonExe -m pip list 2>&1
    $hasFastAPI = $pipList -match "fastapi"
    $hasManim = $pipList -match "manim"
    $hasUvicorn = $pipList -match "uvicorn"
    if ($hasFastAPI -and $hasManim -and $hasUvicorn) {
        Write-Host " PASS" -ForegroundColor Green
    } else {
        Write-Host " WARN - Some packages missing" -ForegroundColor Yellow
    }
} catch {
    Write-Host " FAIL - Cannot check dependencies" -ForegroundColor Red
}

# Test 5: Check web files
Write-Host "[5/6] Frontend Files..." -NoNewline
if ((Test-Path "web/index.html") -and (Test-Path "web/app.js") -and (Test-Path "web/styles.css")) {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " FAIL - Web files missing" -ForegroundColor Red
    $allPassed = $false
}

# Test 6: Check documentation
Write-Host "[6/6] Documentation Files..." -NoNewline
$docFiles = @(
    "README.md",
    "DEPLOYMENT_CHECKLIST.md",
    "ELEVENLABS_SETUP.md",
    "COMPLETE_FIX_SUMMARY.md"
)
$allDocsPresent = $true
foreach ($doc in $docFiles) {
    if (-not (Test-Path $doc)) {
        $allDocsPresent = $false
        break
    }
}
if ($allDocsPresent) {
    Write-Host " PASS" -ForegroundColor Green
} else {
    Write-Host " WARN - Some documentation missing" -ForegroundColor Yellow
}

# Summary
Write-Host "`n==================================================`n" -ForegroundColor Cyan
if ($allPassed) {
    Write-Host " SYSTEM STATUS: READY FOR DEPLOYMENT" -ForegroundColor Green -BackgroundColor Black
    Write-Host "`n All critical tests passed!" -ForegroundColor Green
} else {
    Write-Host " SYSTEM STATUS: NEEDS ATTENTION" -ForegroundColor Yellow -BackgroundColor Black
    Write-Host "`n Some tests failed. Review errors above." -ForegroundColor Yellow
}

Write-Host "`n==================================================`n" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Open browser: http://localhost:8002" -ForegroundColor White
Write-Host "  2. Test video generation with sample problem" -ForegroundColor White
Write-Host "  3. Review DEPLOYMENT_CHECKLIST.md for deployment" -ForegroundColor White
Write-Host "`n==================================================`n" -ForegroundColor Cyan
