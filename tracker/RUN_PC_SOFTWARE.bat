@echo off
REM =========================================
REM PC SOFTWARE QUICK START
REM =========================================
REM এটি একটি batch file যা সবকিছু automatically শুরু করে

echo.
echo ===================================
echo   EMPLOYEE PROGRESS TRACKER
echo   PC Software Launcher
echo ===================================
echo.

REM Check if we're in the right directory
if not exist "tracker\main.py" (
    echo ERROR: main.py not found!
    echo Please run this from: D:\Employee-Progress-Tracker\
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv-1\Scripts\Activate" (
    echo Creating virtual environment...
    python -m venv .venv-1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv-1\Scripts\Activate.bat

REM Check and install requirements
echo Checking dependencies...
pip install -q PyQt6 requests Pillow pygetwindow wmi lz4 2>nul

REM Navigate to tracker folder
cd tracker

REM Run the application
echo.
echo Starting Employee Progress Tracker...
echo.
python main.py

REM If app exits, show message
pause
