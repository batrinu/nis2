# Windows EXE Installer for NIS2 Field Audit Tool

This guide explains how to create an uncle-friendly EXE installer for the NIS2 Field Audit Tool on Windows.

## 🎯 What the Installer Does

The EXE installer provides a professional Windows setup wizard that:

1. **Checks System Requirements**
   - Windows 10 or later
   - Administrator rights
   - Internet connection

2. **Installs Dependencies Automatically**
   - Visual C++ Redistributable (if missing)
   - Downloads from Microsoft if needed

3. **Installs the Application**
   - Extracts portable Python (no system Python needed!)
   - Copies all application files
   - Creates configuration

4. **Creates Shortcuts**
   - Desktop shortcut
   - Start Menu entry
   - Uninstaller in Control Panel

## 📦 Option 1: NSIS Installer (Recommended)

**NSIS** (Nullsoft Scriptable Install System) creates a lightweight, fast installer.

### Prerequisites

```bash
# On Windows, install NSIS:
winget install NSIS.NSIS

# Or on Ubuntu/Debian (for cross-compilation):
sudo apt-get install nsis
```

### Building the Installer

```bash
# From the project root
cd scripts
makensis NIS2_Installer.nsi

# Output: dist/NIS2-Audit-Tool-Setup.exe
```

### What Gets Included

You need to have the portable build ready first:

```bash
# Build the portable version
python scripts/build_windows_portable.py

# Then build the installer
cd scripts
makensis NIS2_Installer.nsi
```

### Features

- ✅ Professional Windows installer look
- ✅ Dependency check with visual feedback
- ✅ Automatic VCRedist download & install
- ✅ Desktop & Start Menu shortcuts
- ✅ Proper uninstaller
- ✅ Add/Remove Programs entry
- ✅ ~50KB installer overhead

---

## 📦 Option 2: Python GUI Installer

A custom Python-based installer with a modern Tkinter GUI.

### Prerequisites

```bash
pip install pyinstaller
```

### Building

```bash
python scripts/build_installer_exe.py
```

### Features

- ✅ Modern GUI wizard
- ✅ Real-time progress bars
- ✅ Detailed status messages
- ✅ Handles errors gracefully

---

## 🚀 Using the Installer

### For End Users (Your Uncle)

1. **Download** the `NIS2-Audit-Tool-Setup.exe`
2. **Double-click** to run
3. **Click "Yes"** on the UAC prompt (needs admin rights)
4. **Follow the wizard**:
   - Welcome page → Click Next
   - System checks → Wait for green checkmarks
   - Choose install location (default is fine)
   - Wait for installation to complete
   - Click Finish
5. **Launch** from Desktop shortcut!

### What If Something Goes Wrong?

The installer handles common issues:

| Issue | What Happens |
|-------|--------------|
| No internet | Shows warning, continues with local files |
| VCRedist fails | Shows manual download link |
| Not admin | Shows error, asks to run as administrator |
| Low disk space | Shows warning before install |

---

## 🔧 How the Installer Works

```
User runs NIS2-Audit-Tool-Setup.exe
           ↓
    ┌─────────────────┐
    │  Welcome Page   │
    └────────┬────────┘
             ↓
    ┌─────────────────┐
    │  System Checks  │ ← Checks Windows, VCRedist, Internet
    └────────┬────────┘
             ↓
    ┌─────────────────┐
    │ Choose Location │
    └────────┬────────┘
             ↓
    ┌─────────────────┐
    │  Install Files  │ ← Extract Python, copy app files
    └────────┬────────┘
             ↓
    ┌─────────────────┐
    │ Create Shortcuts│
    └────────┬────────┘
             ↓
    ┌─────────────────┐
    │    Complete!    │
    └─────────────────┘
```

---

## 📋 Customization

### Change Install Location

Edit `NIS2_Installer.nsi`:

```nsis
; Change this line
!define INSTALL_DIR "$PROGRAMFILES64\\MyCustomFolder"
```

### Add Custom Checks

In the `CheckDependenciesPage` function:

```nsis
; Add your custom check
${NSD_CreateLabel} 0 110u 100% 20u "My Custom Check"
Pop $0
${If} $MyCondition
    ${NSD_SetText} $0 "✓ Custom: OK"
    SetCtlColors $0 008000 transparent
${Else}
    ${NSD_SetText} $0 "✗ Custom: Failed"
    SetCtlColors $0 FF0000 transparent
${EndIf}
```

### Bundle VCRedist Offline

Instead of downloading, bundle the VCRedist installer:

```nsis
; Download it once
; Place in: scripts/vcredist_x64.exe
; Then in NIS2_Installer.nsi:
File "vcredist_x64.exe"
ExecWait '"$INSTDIR\\vcredist_x64.exe" /install /quiet /norestart'
```

---

## 🆚 Installer Comparison

| Feature | NSIS | Python GUI |
|---------|------|------------|
| Size | ~50KB + payload | ~10MB (includes Python) |
| Build Time | Fast | Slow |
| Look & Feel | Native Windows | Modern custom |
| Dependencies | None | PyInstaller |
| Cross-compile | Yes (Linux→Windows) | No |
| Recommended | ✅ Yes | For special cases |

---

## 🐛 Troubleshooting

### "makensis not found"

Add NSIS to your PATH or use full path:
```bash
"C:\Program Files (x86)\NSIS\makensis.exe" NIS2_Installer.nsi
```

### "File not found" errors

Make sure you built the portable version first:
```bash
python scripts/build_windows_portable.py
```

### Installer doesn't run on target machine

The target needs:
- Windows 10 or later (recommended)
- Administrator rights to install

---

## 📝 Summary for Uncle

**To create the installer:**
```bash
# Build portable version
python scripts/build_windows_portable.py

# Build installer
cd scripts
makensis NIS2_Installer.nsi

# Find result in: dist/NIS2-Audit-Tool-Setup.exe
```

**To use the installer:**
1. Send `NIS2-Audit-Tool-Setup.exe` to uncle
2. He double-clicks it
3. Follows the wizard
4. Done! Shortcut on Desktop.

---

## 🔗 Resources

- [NSIS Documentation](https://nsis.sourceforge.io/Docs/)
- [NSIS Modern UI](https://nsis.sourceforge.io/Docs/Modern%20UI%202/Readme.html)
- [VCRedist Silent Install](https://docs.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files)
