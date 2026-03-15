#Requires -Version 5.1
<#
.SYNOPSIS
    Windows Setup Script for NIS2 Field Audit Tool
.DESCRIPTION
    Checks for Python 3.10+, installs if missing via winget or direct download,
    then installs the nis2-field-audit package via pip.
    
    Run with: PowerShell -ExecutionPolicy Bypass -File setup.ps1
    Or simply double-click setup.bat which handles this for you.
.NOTES
    Version: 1.0
    Author: NIS2 Audit Tool
    Requires: Windows 10 (19041+) or Windows 11
#>

[CmdletBinding()]
param(
    [switch]$Force,
    [string]$PythonVersion = "3.12",
    [switch]$NoAdminCheck
)

# Error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$Colors = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
}

function Write-Status {
    param(
        [string]$Message,
        [string]$Type = "Info"
    )
    Write-Host $Message -ForegroundColor $Colors[$Type]
}

function Test-IsAdmin {
    $currentPrincipal = [Security.Principal.WindowsPrincipal]::New(
        [Security.Principal.WindowsIdentity]::GetCurrent()
    )
    return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-PythonInstalled {
    <#
    Checks if Python 3.10+ is installed and available
    Returns: $true if Python 3.10+ found, $false otherwise
    #>
    try {
        # Try 'python' command first
        $pythonVersion = & python --version 2>&1
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 10)) {
                Write-Status "Found Python $major.$minor" "Success"
                return $true
            } else {
                Write-Status "Python version too old: $major.$minor (need 3.10+)" "Warning"
            }
        }
    } catch {
        # Try 'py' launcher
        try {
            $pyVersion = & py --version 2>&1
            if ($pyVersion -match "Python (\d+)\.(\d+)") {
                $major = [int]$Matches[1]
                $minor = [int]$Matches[2]
                if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 10)) {
                    Write-Status "Found Python $major.$minor via py launcher" "Success"
                    return $true
                }
            }
        } catch {
            return $false
        }
    }
    return $false
}

function Test-NmapInstalled {
    <#
    Checks if Nmap is installed and available
    #>
    try {
        $nmapVersion = & nmap --version 2>&1
        if ($nmapVersion -match "Nmap version") {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

function Test-WingetAvailable {
    <#
    Checks if winget (Windows Package Manager) is available
    #>
    try {
        $wingetVersion = & winget --version 2>$null
        if ($wingetVersion) {
            Write-Status "winget version: $wingetVersion" "Info"
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

function Install-PythonViaWinget {
    <#
    Installs Python using winget (Windows Package Manager)
    Requires admin rights for --scope machine
    #>
    param([string]$Version = "3.12")
    
    Write-Status "Installing Python $Version via winget..." "Info"
    
    try {
        # Use machine scope for system-wide install (adds to PATH)
        $process = Start-Process -FilePath "winget" -ArgumentList "install", "Python.Python.$Version", "--scope", "machine", "--silent", "--accept-package-agreements", "--accept-source-agreements" -Wait -PassThru -NoNewWindow
        
        if ($process.ExitCode -eq 0) {
            Write-Status "Python installed successfully via winget" "Success"
            return $true
        } else {
            Write-Status "winget install returned exit code: $($process.ExitCode)" "Warning"
            return $false
        }
    } catch {
        Write-Status "Failed to install via winget: $_" "Error"
        return $false
    }
}

function Install-NmapViaWinget {
    <#
    Installs Nmap using winget
    #>
    Write-Status "Installing Nmap via winget..." "Info"
    try {
        $process = Start-Process -FilePath "winget" -ArgumentList "install", "Insecure.Nmap", "--silent", "--accept-package-agreements", "--accept-source-agreements" -Wait -PassThru -NoNewWindow
        if ($process.ExitCode -eq 0) {
            Write-Status "Nmap installed successfully via winget" "Success"
            return $true
        } else {
            Write-Status "winget install for Nmap returned exit code: $($process.ExitCode)" "Warning"
            return $false
        }
    } catch {
        Write-Status "Failed to install Nmap via winget: $_" "Error"
        return $false
    }
}

function Install-PythonViaDownload {
    <#
    Downloads and installs Python from python.org
    Fallback when winget is not available
    #>
    param([string]$Version = "3.12.7")
    
    Write-Status "Downloading Python installer from python.org..." "Info"
    
    $url = "https://www.python.org/ftp/python/$Version/python-$Version-amd64.exe"
    $installerPath = "$env:TEMP\python-$Version-installer.exe"
    
    try {
        # Download installer
        Invoke-WebRequest -Uri $url -OutFile $installerPath -UseBasicParsing
        Write-Status "Downloaded to $installerPath" "Info"
        
        # Install with proper flags:
        # /quiet - silent install
        # InstallAllUsers=1 - system-wide
        # PrependPath=1 - add to PATH
        # Include_test=0 - skip test suite
        Write-Status "Installing Python (this may take a few minutes)..." "Info"
        $process = Start-Process -FilePath $installerPath -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_test=0", "Include_doc=0" -Wait -PassThru
        
        # Clean up installer
        Remove-Item $installerPath -ErrorAction SilentlyContinue
        
        if ($process.ExitCode -eq 0) {
            Write-Status "Python installed successfully" "Success"
            return $true
        } else {
            Write-Status "Installer returned exit code: $($process.ExitCode)" "Error"
            return $false
        }
    } catch {
        Write-Status "Failed to download or install Python: $_" "Error"
        return $false
    }
}

function Update-EnvironmentPath {
    <#
    Refreshes the PATH environment variable in the current session
    to include newly installed Python
    #>
    Write-Status "Refreshing PATH environment variable..." "Info"
    
    $machinePath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    
    $env:Path = "$machinePath;$userPath"
}

function Install-NIS2AuditTool {
    <#
    Installs the nis2-field-audit package via pip
    #>
    Write-Status "Installing/upgrading pip..." "Info"
    python -m pip install --upgrade pip 2>&1 | Out-Null
    
    Write-Status "Installing NIS2 Field Audit Tool..." "Info"
    $process = Start-Process -FilePath "python" -ArgumentList "-m", "pip", "install", "--upgrade", "nis2-field-audit" -Wait -PassThru -NoNewWindow
    
    if ($process.ExitCode -eq 0) {
        Write-Status "Package installed successfully" "Success"
        return $true
    } else {
        Write-Status "pip install returned exit code: $($process.ExitCode)" "Error"
        return $false
    }
}

function New-DesktopShortcut {
    <#
    Creates a desktop shortcut for nis2-audit
    #>
    try {
        $WshShell = New-Object -ComObject WScript.Shell
        $DesktopPath = [Environment]::GetFolderPath("Desktop")
        $Shortcut = $WshShell.CreateShortcut("$DesktopPath\NIS2 Audit Tool.lnk")
        $Shortcut.TargetPath = "nis2-audit"
        $Shortcut.WorkingDirectory = "%USERPROFILE%"
        $Shortcut.Description = "NIS2 Field Audit Tool"
        $Shortcut.Save()
        Write-Status "Desktop shortcut created" "Success"
    } catch {
        Write-Status "Could not create desktop shortcut: $_" "Warning"
    }
}

function Show-CompletionMessage {
    <#
    Displays final success message with usage instructions
    #>
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Installation Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run the NIS2 Field Audit Tool using:"
    Write-Host "  nis2-audit" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or if that doesn't work, try:"
    Write-Host "  python -m app.textual_app" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# ==================== MAIN SCRIPT ====================

clear
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NIS2 Field Audit Tool Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we need admin rights
$isAdmin = Test-IsAdmin
if (-not $isAdmin -and -not $NoAdminCheck) {
    Write-Status "This script requires administrator privileges to install Python." "Warning"
    Write-Status "Requesting elevation..." "Info"
    
    # Relaunch as admin with Bypass execution policy
    Start-Process -FilePath "PowerShell" -ArgumentList "-ExecutionPolicy", "Bypass", "-File", `"$PSCommandPath`", "-NoAdminCheck" -Verb RunAs -Wait
    exit
}

# Check current Python
Write-Status "Checking for Python..." "Info"
$pythonInstalled = Test-PythonInstalled

if ($pythonInstalled -and -not $Force) {
    Write-Status "Python is already installed (version 3.10+)" "Success"
} else {
    if ($Force) {
        Write-Status "Force flag set, reinstalling Python..." "Warning"
    }
    
    # Try winget first
    if (Test-WingetAvailable) {
        $installed = Install-PythonViaWinget -Version $PythonVersion
        if ($installed) {
            Update-EnvironmentPath
        }
    } else {
        Write-Status "winget not available, falling back to direct download..." "Warning"
        $installed = Install-PythonViaDownload -Version "3.12.7"
        if ($installed) {
            Update-EnvironmentPath
        }
    }
    
    # Verify installation
    if (-not (Test-PythonInstalled)) {
        Write-Status "Python installation failed or not in PATH" "Error"
        Write-Status "Please install Python manually from https://python.org" "Error"
        Write-Status "Make sure to check 'Add Python to PATH' during installation" "Info"
        exit 1
    }
}

# Check for Nmap
Write-Status "Checking for Nmap..." "Info"
if (-not (Test-NmapInstalled)) {
    if (Test-WingetAvailable) {
        $nmapInstalled = Install-NmapViaWinget
        if ($nmapInstalled) {
            Update-EnvironmentPath
        } else {
            Write-Status "Could not install Nmap automatically. Network scans won't work." "Warning"
            Write-Status "Please install manually from https://nmap.org/download.html" "Info"
        }
    } else {
        Write-Status "winget not available, cannot install Nmap automatically." "Warning"
        Write-Status "Please install manually from https://nmap.org/download.html" "Info"
    }
} else {
    Write-Status "Nmap is already installed" "Success"
}

# Install the package
Write-Host ""
$installSuccess = Install-NIS2AuditTool

if ($installSuccess) {
    # Create desktop shortcut
    New-DesktopShortcut
    
    # Show completion
    Show-CompletionMessage
} else {
    Write-Status "Installation failed. Please check the error messages above." "Error"
    Write-Status "You may need to install Python manually from https://python.org" "Info"
    exit 1
}
