@echo off
setlocal EnableDelayedExpansion

REM ============================================
REM NIS2 Field Audit Tool - Windows Setup
REM ============================================
REM This batch file handles PowerShell execution
REM policy and launches the actual setup script.
REM 
REM You can run this by:
REM   1. Double-clicking setup.bat
REM   2. Running "setup.bat" from Command Prompt
REM   3. Running "setup.bat" from PowerShell
REM ============================================

title NIS2 Field Audit Tool Setup

echo ========================================
echo   NIS2 Field Audit Tool Setup
echo ========================================
echo.

REM Check Windows version
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%setup.ps1"

REM Check if PowerShell script exists
if not exist "%PS_SCRIPT%" (
    echo [ERROR] setup.ps1 not found in: %SCRIPT_DIR%
    echo Make sure both setup.bat and setup.ps1 are in the same folder.
    pause
    exit /b 1
)

REM Method 1: Try to run PowerShell with Bypass policy
REM This is the cleanest method and works on most systems
echo [INFO] Starting installation...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0setup.ps1" 2>nul
if %errorlevel% == 0 goto :success

REM Method 2: If Bypass failed, try to read script content and pipe to PowerShell
REM This bypasses execution policy entirely since no file is being "executed"
echo [INFO] Trying alternative method...
echo.

type "%PS_SCRIPT%" | powershell -Command - 2>nul
if %errorlevel% == 0 goto :success

REM Method 3: Direct installation without PowerShell script
REM This is the fallback for very restricted systems
echo.
echo [WARNING] PowerShell execution blocked. Trying direct installation...
echo.

goto :direct_install

:direct_install
REM Check for Python
echo [INFO] Checking for Python...
python --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Python found
    goto :pip_install
)

py --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Python launcher (py) found
    set PYTHON_CMD=py
    goto :pip_install
)

echo [INFO] Python not found. Checking for winget...

REM Try to install Python via winget
winget --version >nul 2>&1
if %errorlevel% == 0 (
    echo [INFO] Installing Python via winget...
    echo [INFO] This may take a few minutes...
    winget install Python.Python.3.12 --scope machine --silent --accept-package-agreements --accept-source-agreements
    if %errorlevel% == 0 (
        echo [OK] Python installed
        goto :refresh_path
    )
)

echo.
echo [ERROR] Could not install Python automatically.
echo.
echo Please install Python manually:
echo 1. Visit https://python.org/downloads
echo 2. Download Python 3.10 or newer
echo 3. Run the installer
echo 4. IMPORTANT: Check "Add Python to PATH" at the bottom of the installer
echo 5. Run this setup again
echo.
pause
exit /b 1

:refresh_path
REM Refresh PATH in current session
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul ^| findstr /i path') do set "PATH=%%b"
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul ^| findstr /i path') do set "PATH=!PATH!;%%b"

:nmap_check
REM Check for Nmap
echo [INFO] Checking for Nmap...
nmap --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Nmap found
    goto :pip_install
)

echo [INFO] Nmap not found. Checking for winget...
winget --version >nul 2>&1
if %errorlevel% == 0 (
    echo [INFO] Installing Nmap via winget...
    winget install Insecure.Nmap --silent --accept-package-agreements --accept-source-agreements
    if %errorlevel% == 0 (
        echo [OK] Nmap installed
        goto :refresh_path_nmap
    ) else (
        echo [WARNING] Failed to install Nmap via winget. Network scans will not work.
        goto :pip_install
    )
) else (
    echo [WARNING] winget not found. Please install Nmap manually from https://nmap.org/download.html
    goto :pip_install
)

:refresh_path_nmap
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul ^| findstr /i path') do set "PATH=%%b"
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul ^| findstr /i path') do set "PATH=!PATH!;%%b"

:pip_install
echo.
echo [INFO] Installing NIS2 Field Audit Tool...
echo.

if defined PYTHON_CMD (
    %PYTHON_CMD% -m pip install --upgrade pip
    %PYTHON_CMD% -m pip install --upgrade nis2-field-audit
) else (
    python -m pip install --upgrade pip
    python -m pip install --upgrade nis2-field-audit
)

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Installation failed.
    echo.
    pause
    exit /b 1
)

:success
echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo You can now run the tool by typing:
echo   nis2-audit
echo.
echo Or if that doesn't work:
echo   python -m app.textual_app
echo.

REM Create desktop shortcut
echo [INFO] Creating desktop shortcut...
(
echo Set oWS = WScript.CreateObject("WScript.Shell"^)
echo sLinkFile = oWS.SpecialFolders("Desktop"^) ^& "\NIS2 Audit Tool.lnk"
echo Set oLink = oWS.CreateShortcut(sLinkFile^)
echo oLink.TargetPath = "nis2-audit"
echo oLink.WorkingDirectory = "%USERPROFILE%"
echo oLink.Description = "NIS2 Field Audit Tool"
echo oLink.Save
) > "%TEMP%\CreateShortcut.vbs"

cscript //nologo "%TEMP%\CreateShortcut.vbs" 2>nul
del "%TEMP%\CreateShortcut.vbs" 2>nul

echo [OK] Desktop shortcut created
echo.
pause
exit /b 0
