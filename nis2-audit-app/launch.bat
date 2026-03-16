@echo off
setlocal EnableDelayedExpansion

REM =============================================================================
REM NIS2 Field Audit Tool - Simple Launcher for Windows
REM =============================================================================
REM This script:
REM   1. Checks for Python
REM   2. Creates virtual environment on first run
REM   3. Installs dependencies
REM   4. Launches the application
REM =============================================================================

REM Set UTF-8 for Romanian character support
chcp 65001 >nul 2>&1

title NIS2 Field Audit Tool

echo ========================================
echo   NIS2 Field Audit Tool
echo ========================================
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo.
    echo Please install Python 3.10 or newer:
    echo https://python.org/downloads
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
echo [OK] Found %PYTHON_VERSION%

REM Create virtual environment if needed
if not exist ".venv\Scripts\python.exe" (
    echo.
    echo ========================================
    echo   First Run Setup
echo ========================================
    echo.
    echo Setting up virtual environment...
    echo This will take 1-2 minutes (one-time only)
    echo.
    
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        echo Try running as Administrator
        pause
        exit /b 1
    )
    
    echo Installing dependencies...
    call .venv\Scripts\activate.bat
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        echo Check your internet connection
        pause
        exit /b 1
    )
    
    echo.
    echo [OK] Setup complete!
    echo.
    timeout /t 2 >nul
)

REM Activate and run
call .venv\Scripts\activate.bat

REM Set environment for better Windows terminal support
set "PYTHONIOENCODING=utf-8"
set "FORCE_COLOR=1"

echo.
echo Starting NIS2 Field Audit Tool...
echo.

python -m app.main

REM Capture exit code
set "EXIT_CODE=%errorlevel%"

if %EXIT_CODE% neq 0 (
    echo.
    echo ========================================
    echo   Application exited with error %EXIT_CODE%
    echo ========================================
    echo.
    echo Try deleting the .venv folder and running again.
    pause
)

exit /b %EXIT_CODE%
