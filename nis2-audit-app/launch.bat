@echo off
setlocal

rem --- 1. C++ Redistributable Check ---
if not exist "%SystemRoot%\System32\vcruntime140.dll" (
    echo [ERROR] Microsoft Visual C++ Redistributable is missing.
    echo Please install it from: https://aka.ms/vs/17/release/vc_redist.x64.exe
    pause
    exit /b 1
)

rem --- 2. Environment Setup ---
set "SCRIPT_DIR=%~dp0"
set "PYTHONHOME=%SCRIPT_DIR%python"
set "PYTHONPATH=%SCRIPT_DIR%lib;%SCRIPT_DIR%"
set "PATH=%PYTHONHOME%;%PATH%"

rem --- 3. Launch App ---
echo Starting NIS2 Field Audit Tool...
"%PYTHONHOME%\python.exe" -m app.textual_app

rem --- 4. Error Capture ---
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The application exited with code %errorlevel%.
    pause
)

endlocal
