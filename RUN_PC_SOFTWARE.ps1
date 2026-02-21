# =========================================
# PC SOFTWARE QUICK START (PowerShell)
# =========================================
# এটি একটি PowerShell script যা সবকিছু automatically শুরু করে

Write-Host ""
Write-Host "===================================" -ForegroundColor Cyan
Write-Host "  EMPLOYEE PROGRESS TRACKER" -ForegroundColor Cyan
Write-Host "  PC Software Launcher" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "tracker\main.py")) {
    Write-Host "ERROR: main.py not found!" -ForegroundColor Red
    Write-Host "Please run this from: D:\Employee-Progress-Tracker\" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path ".venv-1\Scripts\Activate.ps1")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv-1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv-1\Scripts\Activate.ps1"

# Check and install requirements
Write-Host "Checking dependencies..." -ForegroundColor Yellow
pip install -q PyQt6 requests Pillow pygetwindow wmi lz4

# Navigate to tracker folder
Set-Location tracker

# Show startup message
Write-Host ""
Write-Host "Starting Employee Progress Tracker..." -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "✅ Backend should be running at: http://127.0.0.1:8000/" -ForegroundColor Cyan
Write-Host "✅ Login with Employee credentials" -ForegroundColor Cyan
Write-Host "✅ Tasks will sync every 5 seconds (REALTIME!)" -ForegroundColor Cyan
Write-Host ""

# Run the application
python main.py

# If app exits
Write-Host ""
Write-Host "Application closed." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
