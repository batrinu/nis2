# Windows Setup Guide for NIS2 Field Audit Tool

This guide helps you install the NIS2 Field Audit Tool on Windows. Choose the method that works best for your system.

## 📦 Installation Options

### Option 1: EXE Installer (Easiest - Recommended for Uncles)

The professional Windows installer handles everything automatically:

1. **Download** `NIS2-Audit-Tool-Setup.exe`
2. **Double-click** to run
3. **Click "Yes"** on the UAC prompt (needs admin rights)
4. **Follow the wizard** → Click through Welcome → Checks → Install → Finish
5. **Launch** from Desktop shortcut!

The installer automatically:
- ✅ Checks system requirements
- ✅ Downloads & installs Visual C++ Redistributable (if needed)
- ✅ Extracts portable Python (no system Python required!)
- ✅ Creates Desktop & Start Menu shortcuts
- ✅ Adds proper uninstaller

**[📖 Detailed Installer Guide](WINDOWS_INSTALLER.md)**

---

### Option 2: Portable Version (No Installation Required)

For using on a USB drive or without admin rights:

1. Download `nis2-portable.zip`
2. Extract to any folder
3. Double-click `launch.bat`

No installation, no admin rights needed, leaves no trace on the computer.

---

### Option 3: Manual Setup (Development)

1. Download and extract the `nis2-audit-app` folder
2. **Double-click `START.bat`**
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

## 🐛 Troubleshooting

### "Terminal window is too short" / Shows "%h rows"

**Fixed in latest version!** This was a bug in the batch script where `%%h` should have been `%%x`. 

If you see this error:
1. Update to the latest version from GitHub
2. Or resize your terminal to be larger (80 columns × 24 lines minimum)
3. Or run from regular Command Prompt instead of PowerShell ISE

### Romanian Characters Display as � or ?

The tool now automatically sets UTF-8 code page (`chcp 65001`) on startup. If you still see issues:

1. **Windows Terminal** (recommended): Download from Microsoft Store
2. **Command Prompt**: Should work automatically
3. **PowerShell**: May need to set `[Console]::OutputEncoding = [System.Text.Encoding]::UTF8`

### "Execution Policy" Error

If you see an error about execution policy, the `START.bat` file should handle this automatically. If you're running PowerShell scripts directly, use:

```powershell
PowerShell -ExecutionPolicy Bypass -File setup.ps1
```

### PowerShell ISE Not Supported

**PowerShell ISE** (the blue/white scripting environment) doesn't support interactive terminal applications. Use one of these instead:
- Windows Terminal (recommended)
- Regular PowerShell (black window)
- Command Prompt (CMD)

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

### Antivirus Blocking the App

Some antivirus software may flag Python scripts. If you see:
- "Access denied" errors
- Files being quarantined
- Virtual environment activation failing

**Solution**: Add an exclusion for the `nis2-audit-app` folder in your antivirus settings.

For Windows Defender:
1. Windows Security → Virus & threat protection
2. Manage settings → Add or remove exclusions
3. Add folder exclusion → Select your `nis2-audit-app` folder

### Behind a Corporate Proxy

If you're behind a proxy, set these environment variables before running setup:

```powershell
$env:HTTP_PROXY = "http://proxy.company.com:8080"
$env:HTTPS_PROXY = "http://proxy.company.com:8080"
```

### Colors Look Wrong or Don't Display

The script sets `FORCE_COLOR=1` automatically. If colors still don't work:
1. Use Windows Terminal instead of CMD
2. Or set environment variable manually: `$env:FORCE_COLOR=1`

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

## 📝 Important Notes

### What's Fixed Recently

**March 2026 Updates:**
- ✅ Fixed terminal size detection bug (`%%h` → `%%x`)
- ✅ Added UTF-8 support for Romanian characters (ăâîșț)
- ✅ Added PowerShell ISE detection with helpful error
- ✅ Added `FORCE_COLOR` for better TUI colors
- ✅ Added antivirus guidance in error messages
- ✅ Added fallback `mode con` for terminal size

### Technical Details

- The EXE installer uses **portable Python** - no system Python required!
- `START.bat` uses system Python and creates a virtual environment
- Both methods automatically handle UTF-8 encoding for Romanian language support
- All launchers check terminal size and provide helpful messages

### Requirements Summary

| Method | Admin Rights | Internet | Python Install |
|--------|-------------|----------|----------------|
| EXE Installer | ✅ Yes | ✅ First run | ❌ Not needed |
| Portable ZIP | ❌ No | ❌ No | ❌ Not needed |
| START.bat | ✅ Yes | ✅ Yes | ✅ System-wide |

### Still Having Issues?

1. Check the **[Troubleshooting Section](#-troubleshooting)** above
2. Try the **[EXE Installer](WINDOWS_INSTALLER.md)** - it's the most reliable
3. Ensure Windows is up to date
4. Check that you have at least Windows 10 version 1903
