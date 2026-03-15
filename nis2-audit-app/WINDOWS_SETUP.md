# Windows Setup Guide for NIS2 Field Audit Tool

This guide helps you install the NIS2 Field Audit Tool on Windows. Choose the method that works best for your system.

## Quick Start (Recommended)

### Method 1: Double-Click Setup (Easiest)

1. Download and extract the `nis2-audit-app` folder
2. **Double-click `setup.bat`**
3. Follow the prompts
4. Done!

The setup script will:
- Check if Python 3.10+ is installed
- Install Python if needed (using winget or direct download)
- Install the NIS2 Field Audit Tool
- Create a desktop shortcut

### Method 2: PowerShell (If Method 1 Doesn't Work)

Right-click the Start menu → **Windows Terminal (Admin)** or **PowerShell (Admin)**, then run:

```powershell
# Navigate to the folder
cd C:\Users\YourName\Downloads\nis2-audit-app

# Run setup
.\setup.ps1
```

If you get an execution policy error, use:
```powershell
PowerShell -ExecutionPolicy Bypass -File setup.ps1
```

### Method 3: Manual Installation (Advanced)

If the automatic setup doesn't work:

1. **Install Python 3.10 or newer:**
   - Visit https://python.org/downloads
   - Download Python 3.12
   - Run installer
   - **IMPORTANT:** Check "Add Python to PATH" at the bottom of the first screen
   - Click "Install Now"

2. **Install the tool:**
   ```cmd
   pip install nis2-field-audit
   ```

3. **Run:**
   ```cmd
   nis2-audit
   ```

## Requirements

- **Windows 10** (version 1903 or newer) or **Windows 11**
- **Internet connection** (for downloading Python and the tool)
- **Administrator privileges** (to install Python system-wide)

## Troubleshooting

### "Execution Policy" Error

If you see an error about execution policy, the `setup.bat` file should handle this automatically. If you're running `setup.ps1` directly, use:

```powershell
PowerShell -ExecutionPolicy Bypass -File setup.ps1
```

### Python Not Found After Installation

If Python installs but isn't recognized:

1. Close all Command Prompt and PowerShell windows
2. Open a new window
3. Try again

Python modifies the PATH during installation, but existing windows don't see the change.

### Winget Not Available

If you see "winget not available," the script will automatically download Python from python.org. This is normal on older Windows 10 versions.

### "Access Denied" or Admin Rights

The setup needs administrator privileges to:
- Install Python system-wide
- Add Python to the system PATH

If prompted, click "Yes" on the UAC (User Account Control) dialog.

### Installation Appears to Hang

Python installation can take 3-5 minutes, especially on older systems. The installer shows no progress - please be patient and don't close the window.

### Behind a Corporate Proxy

If you're behind a proxy, set these environment variables before running setup:

```powershell
$env:HTTP_PROXY = "http://proxy.company.com:8080"
$env:HTTPS_PROXY = "http://proxy.company.com:8080"
```

## Verification

After installation, verify it works:

```cmd
python --version
```
Should show: `Python 3.12.x` (or newer)

```cmd
nis2-audit --version
```
Should show the version number.

## Uninstallation

To remove the tool:

```cmd
pip uninstall nis2-field-audit
```

To remove Python (if installed by this setup):
- Windows Settings → Apps → Python → Uninstall

## How the Setup Works

The setup uses a two-layer approach:

1. **setup.bat** (Entry Point)
   - Handles PowerShell execution policy restrictions
   - Tries multiple methods to run the PowerShell script
   - Falls back to direct installation if PowerShell is blocked

2. **setup.ps1** (Main Script)
   - Detects existing Python installations
   - Uses `winget` (Windows Package Manager) when available
   - Falls back to downloading from python.org
   - Installs the package via pip
   - Creates desktop shortcut

This ensures maximum compatibility across different Windows configurations.

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Try the manual installation method
3. Ensure you're running as administrator
4. Check that your Windows is up to date

## Notes

- The setup installs Python for **all users** (system-wide), not just your account
- Python is added to the system PATH automatically
- The tool is installed via pip in the user site-packages (no additional admin needed after Python is installed)
- Internet access is required during setup
