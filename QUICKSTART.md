# NIS2 Field Audit Tool - Quick Start Guide

## What is this?

The **NIS2 Field Audit Tool** helps you perform cybersecurity audits to comply with the EU NIS2 Directive. It's designed for:

- Network administrators
- Compliance officers
- Security auditors
- IT consultants

## System Requirements

- **Python 3.10 or newer** (free download)
- **Terminal/Command Prompt** (built into your computer)
- **No admin rights required** for basic usage

## Step 1: Start the App

### Windows
1. Double-click **`START.bat`**
2. If Windows asks about security, click "More info" → "Run anyway"

### Mac
1. Double-click **`START.sh`**
2. If you see "cannot be opened", right-click → Open → Open

Or open Terminal and run:
```bash
cd /path/to/nis2-field-audit-tool
./START.sh
```

### Linux
Open a terminal and run:
```bash
cd /path/to/nis2-field-audit-tool
./START.sh
```

## Step 2: First-Time Setup

The first time you run the app:

1. **Wait for setup** - The app will install required packages (1-2 minutes)
2. **Follow the wizard** - A friendly onboarding wizard will guide you
3. **Set your preferences** - Choose theme, font size, and accessibility options

## Step 3: Create Your First Audit Session

Once the app is running:

1. Press **`N`** or select **"New Session"**
2. Enter your **company name**
3. Select your **sector** (Energy, Banking, Healthcare, etc.)
4. Click **"Create Session"**

## Step 4: Add a Device to Audit

1. From the dashboard, press **`D`** or select **"Devices"**
2. Click **"Add Device"**
3. Enter:
   - **Name**: e.g., "Main Router"
   - **IP Address**: e.g., "192.168.1.1"
   - **Type**: Router, Switch, Server, etc.
4. Click **"Save"**

## Step 5: Run a Compliance Check

1. Select your device from the list
2. Press **`C`** or select **"Checklist"**
3. Answer the compliance questions
4. The app will calculate your NIS2 compliance score

## Step 6: Generate a Report

1. Press **`R`** or select **"Reports"**
2. Choose report format (PDF, HTML, or Markdown)
3. Click **"Generate"**
4. The report is saved to your Downloads folder

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↑` `↓` or `Tab` | Navigate menus |
| `Enter` | Select / Confirm |
| `Esc` | Go back / Cancel |
| `F1` | Show help |
| `?` | Show keyboard shortcuts |
| `Q` | Quit |
| `N` | New session |
| `D` | Devices |
| `S` | Scan network |
| `C` | Compliance checklist |
| `F` | Findings |
| `R` | Reports |

## Common Tasks

### Scan Your Network
```
Dashboard → Scan → Enter IP range (e.g., 192.168.1.0/24) → Start Scan
```

### Connect via SSH
```
Dashboard → Connect → Enter IP → Username → Password → Connect
```

### Export Results
```
Reports → Select Format → Choose Location → Generate
```

## Troubleshooting

### "Python not found"
Download and install Python from https://python.org/downloads
- **Windows**: Check "Add Python to PATH" during installation
- **Mac**: Use `brew install python3` or download from python.org
- **Linux**: Run `sudo apt install python3` (Ubuntu/Debian)

### "Permission denied"
- **Windows**: Right-click START.bat → "Run as administrator"
- **Mac/Linux**: Run `chmod +x START.sh` then try again

### "Terminal too small"
Resize your terminal window to at least 80 columns × 24 rows.

### App won't start
1. Check that Python 3.10+ is installed: `python --version`
2. Try deleting the `.venv` folder and running START again
3. Check the log file: `~/.nis2-audit/logs/nis2-audit.log`

## Getting Help

- **In the app**: Press `F1` anytime for context-sensitive help
- **Keyboard shortcuts**: Press `?` to see all shortcuts
- **Documentation**: See README.md for technical details
- **Issues**: Check the log files in `~/.nis2-audit/logs/`

## Tips for Best Results

1. **Start small** - Add one device first to learn the interface
2. **Use the wizard** - The onboarding wizard explains each feature
3. **Save often** - Your work auto-saves every 5 minutes
4. **Export reports** - Generate PDFs to share with your team
5. **Keep credentials safe** - SSH passwords are never stored to disk

---

**Next Steps**: See USER_GUIDE.md for detailed documentation on all features.
