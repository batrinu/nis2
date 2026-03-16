@echo off
setlocal EnableDelayedExpansion

REM ==============================================================================
REM NIS2 Field Audit Tool - Portable Windows Launcher
REM ==============================================================================
REM This launcher uses the embedded Python distribution (no installation required)
REM ==============================================================================

REM Set UTF-8 code page for proper Romanian character support
REM This ensures diacritics (ăâîșț) display correctly
chcp 65001 >nul 2>&1

REM --- 1. C++ Redistributable Check ---
if not exist "%SystemRoot%\System32\vcruntime140.dll" (
    echo [ERROR] Microsoft Visual C++ Redistributable is missing.
    echo Please install it from: https://aka.ms/vs/17/release/vc_redist.x64.exe
    pause
    exit /b 1
)

REM Check if we're in PowerShell ISE (doesn't support interactive console apps)
if defined PSISE (
    echo [WARNING] You are running in PowerShell ISE
    echo PowerShell ISE does not support interactive console applications.
    echo Please run launch.bat from regular Command Prompt or PowerShell console.
    echo.
    pause
    exit /b 1
)

REM --- 2. Terminal Size Check ---
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

REM If still not defined, use defaults
if not defined TERM_WIDTH set "TERM_WIDTH=120"
if not defined TERM_HEIGHT set "TERM_HEIGHT=30"

REM Check minimum size (80x24)
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

REM --- 3. Environment Setup ---
set "SCRIPT_DIR=%~dp0"
set "PYTHONHOME=%SCRIPT_DIR%python"
set "PYTHONPATH=%SCRIPT_DIR%lib;%SCRIPT_DIR%"
set "PATH=%PYTHONHOME%;%PATH%"

REM Check if portable Python exists
if not exist "%PYTHONHOME%\python.exe" (
    echo [ERROR] Portable Python not found!
    echo Expected: %PYTHONHOME%\python.exe
    echo.
    echo The portable distribution may be corrupted.
    echo Please re-download the application.
    echo.
    pause
    exit /b 1
)

REM Set environment variables for better TUI support
set "PYTHONIOENCODING=utf-8"
set "FORCE_COLOR=1"

REM --- 4. Launch App ---
echo Starting NIS2 Field Audit Tool...
"%PYTHONHOME%\python.exe" -m app.textual_app

REM --- 5. Error Capture ---
if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo   Application Exited with Error
    echo ========================================
    echo.
    echo Exit code: %errorlevel%
    echo.
    echo If the app crashed immediately, this might help:
    echo - Make sure your terminal supports Unicode (UTF-8)
    echo - Try running from Windows Terminal instead of CMD
    echo - Check that your antivirus isn't blocking the app
    echo.
    pause
)

REM Restore original code page on exit
chcp 437 >nul 2>&1

endlocal
