# 🚀 NIS2 Field Audit Tool - One-Command Starter

## Quick Start (One Command!)

```bash
./start.py
```

Or use the shell wrapper:

```bash
./start.sh
```

That's it! The script will:
1. ✅ Check Python version (needs 3.10+)
2. ✅ Check if pip is available
3. ✅ Install missing dependencies automatically
4. ✅ Check for optional nmap (for network scanning)
5. ✅ Create necessary directories
6. ✅ Check terminal size
7. 🎮 Launch the NIS2 Field Audit Tool!

---

## What the Script Does

### Automatic Dependency Management

The `start.py` script automatically handles:

- **Python version check**: Ensures Python 3.10+ is installed
- **Pip availability**: Verifies pip is working
- **Package installation**: Installs all required packages:
  - textual (TUI framework)
  - typer (CLI framework)
  - rich (text formatting)
  - pydantic (data validation)
  - paramiko, netmiko (SSH connections)
  - cryptography (encryption)
  - And more...

- **Optional dependencies**: Warns about nmap (needed for network scanning)

### Visual Feedback

The script provides clear, color-coded output:

```
╔══════════════════════════════════════════════════════════════════╗
║                    🛡️  NIS2 FIELD AUDIT TOOL  🛡️                ║
║                       Universal Starter                          ║
╚══════════════════════════════════════════════════════════════════╝

Checking Python version...
✓ Python 3.12.3 (OK)

Checking pip...
✓ pip is available

Checking dependencies...
✓ All dependencies are installed

Checking optional dependency: nmap...
⚠ nmap not found (optional)
  Network scanning requires nmap

Setting up directories...
✓ Data directory: /home/user/.local/share/nis2-audit

Checking terminal size...
✓ Terminal size: 120x30 (OK)

==============================================================
✓ All checks passed!
==============================================================

Starting NIS2 Field Audit Tool...

Launching... Press F1 for help, Q to quit
```

---

## Requirements

### Must Have
- **Python 3.10 or higher**
- **pip** (Python package manager)

### Optional (for full functionality)
- **nmap** - For network discovery scanning

---

## Platform Support

| Platform | Command | Status |
|----------|---------|--------|
| Linux | `./start.py` | ✅ Fully supported |
| macOS | `python3 start.py` | ✅ Fully supported |
| Windows | `python start.py` | ✅ Fully supported |
| Windows PowerShell | `python .\start.py` | ✅ Fully supported |

---

## Troubleshooting

### "Permission denied"
```bash
chmod +x start.py
./start.py
```

### "Python not found"
Make sure Python 3.10+ is installed:
```bash
# Check version
python3 --version

# If too old, install newer version from python.org
```

### "pip not found"
Install pip:
```bash
# Ubuntu/Debian
sudo apt install python3-pip

# macOS (pip comes with Python installer)
# Download from python.org

# Windows
# pip comes with Python installer
```

### Dependencies fail to install
Try manually:
```bash
pip install -r requirements.txt
```

Then run `start.py` again.

### Terminal too small
Resize your terminal to at least **80 columns × 24 rows**.

---

## After Starting

Once the app launches:

1. **Splash Screen**: Watch the retro boot sequence
2. **Dashboard**: Press `N` to create your first audit
3. **Help**: Press `F1` on any screen for help
4. **Shortcuts**: Press `?` for keyboard shortcuts
5. **Quit**: Press `Q` or `Ctrl+C` to exit

---

## Alternative: Manual Start

If you prefer to start manually after installing dependencies:

```bash
# Install dependencies once
pip install -r requirements.txt

# Then run directly
python3 -m app.textual_app
```

---

## What's Installed?

The starter script is completely self-contained and doesn't modify your system:

- No system-wide changes
- No registry modifications
- Data stored in `~/.local/share/nis2-audit/`
- Virtual environments not required (but work fine)

---

**Enjoy your NIS2 audits!** 🛡️
