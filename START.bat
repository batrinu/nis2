@echo off
setlocal EnableDelayedExpansion

REM ==============================================================================
REM NIS2 Field Audit Tool - Uncle-Friendly Windows Launcher
REM ==============================================================================
REM This script automatically:
REM   1. Finds Python on your system
REM   2. Creates a virtual environment on first run
REM   3. Installs required packages
REM   4. Launches the application
REM ==============================================================================

REM Set UTF-8 code page for proper Romanian character support
REM This ensures diacritics (ăâîșț) display correctly
chcp 65001 >nul 2>&1

title NIS2 Field Audit Tool

echo ========================================
echo   NIS2 Field Audit Tool
echo ========================================
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "APP_DIR=%SCRIPT_DIR%nis2-audit-app"

REM Check if app directory exists
if not exist "%APP_DIR%" (
    echo [ERROR] Application directory not found!
    echo Expected: %APP_DIR%
    echo.
    echo Make sure you extracted the entire archive.
    pause
    exit /b 1
)

REM ============================================================================
REM Step 1: Find Python
REM ============================================================================
echo [INFO] Looking for Python...

REM Try different Python commands (in order of preference)
python --version >nul 2>&1 && (
    set "PYTHON_CMD=python"
    goto :python_found
)

py --version >nul 2>&1 && (
    set "PYTHON_CMD=py"
    goto :python_found
)

python3 --version >nul 2>&1 && (
    set "PYTHON_CMD=python3"
    goto :python_found
)

REM Python not found - show helpful error message
echo.
echo [ERROR] Python not found!
echo.
echo ========================================
echo   Python is Required
echo ========================================
echo.
echo The NIS2 Audit Tool needs Python 3.10 or newer.
echo.
echo Please install Python:
echo.
echo 1. Visit: https://python.org/downloads
echo 2. Download Python 3.10 or newer
echo 3. Run the installer
echo 4. IMPORTANT: Check "Add Python to PATH" at the bottom!
echo 5. Run START.bat again
echo.
echo ========================================
echo.
pause
exit /b 1

:python_found
for /f "tokens=*" %%a in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%a
echo [OK] Found %PYTHON_VERSION%
echo.

REM Check if we're in Windows PowerShell ISE (which doesn't support interactive console apps)
if defined PSISE (
    echo [WARNING] You are running in PowerShell ISE
    echo PowerShell ISE does not support interactive console applications.
    echo Please run START.bat from regular Command Prompt or PowerShell console.
    echo.
    pause
    exit /b 1
)

REM ============================================================================
REM Step 2: Check/Create Virtual Environment
REM ============================================================================

if not exist "%APP_DIR%\.venv" (
    echo ========================================
    echo   First Run Setup
    echo ========================================
    echo.
    echo [INFO] Setting up the application...
    echo [INFO] This will take 1-2 minutes (one-time only)
    echo.
    
    cd /d "%APP_DIR%"
    
    REM Create virtual environment
    echo [1/3] Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        echo.
        echo Try running as Administrator:
        echo Right-click START.bat -^> "Run as administrator"
        echo.
        pause
        exit /b 1
    )
    
    REM Activate and install
    echo [2/3] Activating environment...
    call .venv\Scripts\activate.bat
    
    echo [3/3] Installing packages...
    pip install -q --upgrade pip
    pip install -q -e .
    
    if errorlevel 1 (
        echo.
        echo [ERROR] Package installation failed
        echo.
        echo Possible solutions:
        echo 1. Check your internet connection
        echo 2. Try running as Administrator
        echo 3. Update pip: python -m pip install --upgrade pip
        echo.
        pause
        exit /b 1
    )
    
    echo.
    echo [OK] Setup complete!
    echo.
    timeout /t 2 >nul
)

REM ============================================================================
REM Step 3: Check Terminal Size
REM ============================================================================

REM Get terminal size using PowerShell
for /f "usebackq tokens=*" %%a in (`powershell -Command "($Host.UI.RawUI.WindowSize.Width, $Host.UI.RawUI.WindowSize.Height) -join ','" 2^>nul`) do (
    for /f "tokens=1,2 delims=," %%w in ("%%a") do (
        set "TERM_WIDTH=%%w"
        set "TERM_HEIGHT=%%x"
    )
)

REM Fallback: if PowerShell failed, try mode con
if not defined TERM_HEIGHT (
    for /f "tokens=2 delims=: " %%a in ('mode con ^| findstr "Lines:"') do set "TERM_HEIGHT=%%a"
    for /f "tokens=2 delims=: " %%a in ('mode con ^| findstr "Columns:"') do set "TERM_WIDTH=%%a"
    REM Remove leading space
    set "TERM_HEIGHT=!TERM_HEIGHT: =!"
    set "TERM_WIDTH=!TERM_WIDTH: =!"
)

REM Check minimum size (80x24)
REM Note: If variables are still not set, assume we're okay and continue
if not defined TERM_WIDTH set "TERM_WIDTH=120"
if not defined TERM_HEIGHT set "TERM_HEIGHT=30"

if %TERM_WIDTH% LSS 80 (
    echo [WARNING] Terminal window is too narrow
    echo Current: %TERM_WIDTH% columns
    echo Required: at least 80 columns
    echo.
    echo Please resize your terminal window wider and run again.
    echo.
    pause
    exit /b 1
)

if %TERM_HEIGHT% LSS 24 (
    echo [WARNING] Terminal window is too short
    echo Current: %TERM_HEIGHT% rows
    echo Required: at least 24 rows
    echo.
    echo Please resize your terminal window taller and run again.
    echo.
    pause
    exit /b 1
)

REM ============================================================================
REM Step 4: Launch Application
REM ============================================================================

echo [INFO] Starting NIS2 Field Audit Tool...
echo.

cd /d "%APP_DIR%"

REM Activate virtual environment
REM Note: Using 'call' is crucial - without it, the script would exit after activation
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    echo.
    echo This might be caused by:
    echo 1. Antivirus software blocking the activation script
    echo 2. Corrupted virtual environment
    echo.
    echo Try these solutions:
    echo 1. Temporarily disable antivirus or add exception for this folder
    echo 2. Delete the .venv folder and run START.bat again
    echo 3. Run as Administrator
    echo.
    pause
    exit /b 1
)

REM Verify that we're actually in the virtual environment
REM by checking if the python.exe path contains .venv
for /f "delims=" %%i in ('where python') do set "PYTHON_PATH=%%i"
echo [DEBUG] Using Python: !PYTHON_PATH!
if not defined PYTHON_PATH (
    echo [WARNING] Could not verify Python path. Continuing anyway...
)

REM Set environment variable to help Rich/Textual detect Windows terminal
set "PYTHONIOENCODING=utf-8"
set "FORCE_COLOR=1"

REM Run the app
python -m app.textual_app

REM Capture exit code
set "EXIT_CODE=%errorlevel%"

REM Check if app crashed
if %EXIT_CODE% neq 0 (
    echo.
    echo ========================================
    echo   Application Exited with Error
    echo ========================================
    echo.
    echo Exit code: %EXIT_CODE%
    echo.
    echo Check the log file for details:
    echo %USERPROFILE%\.nis2-audit\logs\nis2-audit.log
    echo.
    echo Try these solutions:
    echo 1. Delete the .venv folder and run START.bat again
    echo 2. Check that your antivirus isn't blocking the app
    echo 3. Run as Administrator
    echo.
    echo If the app crashed immediately, this might help:
    echo - Make sure your terminal supports Unicode (UTF-8)
    echo - Try running from Windows Terminal instead of CMD
    echo.
    pause
)

REM Restore original code page on exit
chcp 437 >nul 2>&1

exit /b %EXIT_CODE%
