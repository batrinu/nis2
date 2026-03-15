# Quick Start Guide - NIS2 Field Audit Tool

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies

```bash
cd /home/ser5/projects/nis2/nis2-audit-app
pip install -r requirements.txt
```

Or use the virtual environment (recommended):

```bash
cd /home/ser5/projects/nis2/nis2-audit-app
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Run the Application

**Option A: Using the run script (Recommended)**
```bash
./run.sh
```

**Option B: Using Python directly**
```bash
python3 -m app.textual_app
```

**Option C: Using the CLI**
```bash
python3 -m app.cli
```

### Step 3: Explore the TUI

Once running, you'll see:
1. **Splash Screen** - Retro boot sequence
2. **Dashboard** - Your audit session hub
3. Press **`N`** to create your first audit!

---

## ⌨️ Essential Keyboard Shortcuts

### Global
| Key | Action |
|-----|--------|
| `F1` | Help |
| `?` | Keyboard shortcuts |
| `Esc` | Go back / Cancel |

### Dashboard
| Key | Action |
|-----|--------|
| `N` | New audit session |
| `R` | Refresh |
| `Q` | Quit |

### Checklist
| Key | Action |
|-----|--------|
| `Y` | Answer Yes |
| `N` | Answer No |
| `P` | Answer Partial |
| `?` | Answer N/A |
| `→` | Next question |
| `←` | Previous question |
| `Ctrl+S` | Save progress |

---

## 🛠️ Prerequisites

### Required
- **Python 3.10+**
- **pip**

### Optional (for full functionality)
- **nmap** - For network scanning
  ```bash
  # Ubuntu/Debian
  sudo apt install nmap
  
  # macOS
  brew install nmap
  
  # Windows
  # Download from https://nmap.org/download.html
  ```

---

## 🐛 Troubleshooting

### "Module not found" errors
```bash
# Make sure you're in the right directory
cd /home/ser5/projects/nis2/nis2-audit-app

# Install dependencies
pip install -r requirements.txt
```

### Permission denied on run.sh
```bash
chmod +x run.sh
./run.sh
```

### Terminal too small
The app needs at least **80x24** terminal size. Resize your terminal window.

### Colors look wrong
The app uses 256-color terminal codes. Make sure your terminal supports it:
```bash
# Test color support
echo $TERM
# Should show: xterm-256color or similar
```

---

## 📋 Available Commands

### TUI Mode (Interactive)
```bash
./run.sh
# or
python3 -m app.textual_app
```

### CLI Mode (Scripting)
```bash
# Create new audit
python3 -m app.cli new --name "My Company" --sector energy --employees 100 --turnover 50000000

# List audits
python3 -m app.cli list

# Show audit details
python3 -m app.cli show <session-id>

# Scan network
python3 -m app.cli scan <session-id> --target 192.168.1.0/24

# Generate report
python3 -m app.cli report <session-id> --output report.md

# Get help
python3 -m app.cli --help
```

---

## 🎯 Demo Mode

See all screens without launching the full app:

```bash
python3 demo_screens.py
```

---

## 📁 Project Structure

```
nis2-audit-app/
├── run.sh              # ⭐ Main launcher
├── demo_screens.py     # Visual demo
├── requirements.txt    # Dependencies
├── app/
│   ├── textual_app.py  # Main TUI app
│   ├── cli.py          # CLI commands
│   ├── tui/            # Screens & components
│   ├── storage/        # Database
│   ├── audit/          # Compliance logic
│   └── scanner/        # Network scanning
└── tests/              # Test suite
```

---

## 💡 Tips

1. **First Run**: The app creates a database at `~/.local/share/nis2-audit/`
2. **Auto-save**: Your progress is saved every 30 seconds in forms
3. **Help**: Press `F1` on any screen for context-sensitive help
4. **Export**: Reports can be saved as Markdown, JSON, or HTML
5. **Keyboard**: Most actions have keyboard shortcuts - look for hints at the bottom!

---

## 🎨 Terminal Requirements

- **Minimum size**: 80 columns × 24 rows
- **Recommended**: 100+ columns × 30+ rows
- **Color support**: 256 colors or true color
- **Font**: Monospace font with Unicode support

---

**Enjoy auditing!** 🛡️
